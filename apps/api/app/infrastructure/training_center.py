from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select, text

from apps.api.app.domain.validation import TrainingAssetCandidate, TrainingCenterSummary, TrainingSample
from apps.api.app.infrastructure.database import AgentRecord, LearningEventRecord, SessionFactory
from apps.api.app.infrastructure.memory_store import LEARNING_EVENTS


TRAINING_SAMPLES: tuple[TrainingSample, ...] = (
    TrainingSample(
        id="training-1",
        source_type="message",
        agent_name="AI 客服",
        action="edited",
        original_content="亲，物流慢可以帮您催一下。",
        final_content="您好，我已经为您查询订单，包裹今天会从仓库发出。若 24 小时无物流更新，我会继续跟进。",
        training_target="memory",
        status="ready",
        created_at="2026-07-12T10:00:00+08:00",
    ),
    TrainingSample(
        id="training-2",
        source_type="after_sale_case",
        agent_name="AI 售后",
        action="manual_answered",
        original_content="可以给您补偿 20 元。",
        final_content="涉及补偿金额需要先核实图片证据和订单状态，确认后由老板审批。",
        training_target="workflow",
        status="ready",
        created_at="2026-07-12T10:18:00+08:00",
    ),
    TrainingSample(
        id="training-3",
        source_type="operation_signal",
        agent_name="AI 运营",
        action="accepted",
        original_content="客户多次咨询尺码但未下单。",
        final_content="标记为高意向客户，生成私域跟进话术，但优惠券和投流预算必须审批。",
        training_target="knowledge",
        status="needs_review",
        created_at="2026-07-12T10:36:00+08:00",
    ),
)
COMMITTED_TRAINING_ASSETS: set[str] = set()


def get_training_center_summary(company_id: str | None = None) -> TrainingCenterSummary:
    samples = _read_real_samples(company_id)
    if not samples:
        samples = TRAINING_SAMPLES
    usable = tuple(sample for sample in samples if sample.status == "ready")
    return TrainingCenterSummary(
        total_samples=len(samples),
        usable_samples=len(usable),
        memory_candidates=sum(1 for sample in samples if sample.training_target == "memory"),
        knowledge_candidates=sum(1 for sample in samples if sample.training_target == "knowledge"),
        workflow_candidates=sum(1 for sample in samples if sample.training_target == "workflow"),
        estimated_quality_gain=round(len(usable) / max(len(samples), 1), 4),
        samples=samples,
        asset_candidates=tuple(_asset_candidate(sample) for sample in samples),
        next_actions=(
            "把老板修改过的客服回复沉淀为 Memory。",
            "把售后审批规则沉淀为 Workflow。",
            "把高频商品、物流、优惠问题沉淀为 Knowledge。",
        ),
    )


def commit_training_asset(company_id: str | None, candidate_id: str) -> TrainingAssetCandidate | None:
    samples = _read_real_samples(company_id)
    if not samples:
        samples = TRAINING_SAMPLES
    candidate = next((_asset_candidate(sample) for sample in samples if f"asset-{sample.id}" == candidate_id), None)
    if candidate is None or candidate.status == "needs_review":
        return None
    if SessionFactory is None:
        COMMITTED_TRAINING_ASSETS.add(candidate.id)
        return _committed_candidate(candidate)
    _commit_to_postgres(company_id, candidate)
    return _committed_candidate(candidate)


def _read_real_samples(company_id: str | None) -> tuple[TrainingSample, ...]:
    if SessionFactory is None:
        return tuple(_sample_from_memory_event(event) for event in LEARNING_EVENTS)

    with SessionFactory() as session:
        query = (
            select(LearningEventRecord, AgentRecord.slug)
            .outerjoin(AgentRecord, AgentRecord.id == LearningEventRecord.agent_id)
            .order_by(LearningEventRecord.id.desc())
            .limit(100)
        )
        if company_id:
            query = query.where(LearningEventRecord.company_id == company_id)
        rows = session.execute(query).all()
    return tuple(_sample_from_record(record, slug) for record, slug in rows)


def _sample_from_memory_event(event) -> TrainingSample:
    return TrainingSample(
        id=event.id,
        source_type=_source_type(event.source_type),
        agent_name=_agent_name(event.agent_id, event.source_type),
        action=event.action,
        original_content=event.original_content,
        final_content=event.final_content,
        training_target=_training_target(event.source_type, event.action, event.original_content, event.final_content),
        status=_sample_status(event.action, event.original_content, event.final_content),
        created_at=event.created_at,
    )


def _sample_from_record(record: LearningEventRecord, agent_slug: str | None) -> TrainingSample:
    return TrainingSample(
        id=record.id,
        source_type=_source_type(record.source_type),
        agent_name=_agent_name(agent_slug or "", record.source_type),
        action=record.action,
        original_content=record.original_content,
        final_content=record.final_content,
        training_target=_training_target(record.source_type, record.action, record.original_content, record.final_content),
        status=_sample_status(record.action, record.original_content, record.final_content),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def _source_type(value: str) -> str:
    if value in {"message", "after_sale_case", "operation_signal"}:
        return value
    return "message"


def _agent_name(agent_id: str, source_type: str) -> str:
    if "after" in agent_id or source_type == "after_sale_case":
        return "AI 售后"
    if "operator" in agent_id or source_type == "operation_signal":
        return "AI 运营"
    return "AI 客服"


def _training_target(source_type: str, action: str, original_content: str, final_content: str) -> str:
    content = f"{original_content} {final_content}"
    if source_type == "after_sale_case" or any(keyword in content for keyword in ("退款", "退货", "赔偿", "投诉", "审批")):
        return "workflow"
    if action == "accepted" or any(keyword in content for keyword in ("商品", "尺码", "物流", "优惠", "发货")):
        return "knowledge"
    return "memory"


def _sample_status(action: str, original_content: str, final_content: str) -> str:
    if action == "rejected" or len(final_content.strip()) < 8 or original_content.strip() == final_content.strip():
        return "needs_review"
    return "ready"


def _asset_candidate(sample: TrainingSample) -> TrainingAssetCandidate:
    status = "committed" if f"asset-{sample.id}" in COMMITTED_TRAINING_ASSETS else "candidate" if sample.status == "ready" else "needs_review"
    target_title = {"knowledge": "知识", "memory": "记忆", "workflow": "流程"}[sample.training_target]
    return TrainingAssetCandidate(
        id=f"asset-{sample.id}",
        target=sample.training_target,
        title=f"{sample.agent_name}{target_title}候选：{_short_title(sample.final_content)}",
        content=sample.final_content,
        source_sample_id=sample.id,
        status=status,
        business_value=_business_value(sample.training_target),
    )


def _committed_candidate(candidate: TrainingAssetCandidate) -> TrainingAssetCandidate:
    return TrainingAssetCandidate(
        id=candidate.id,
        target=candidate.target,
        title=candidate.title,
        content=candidate.content,
        source_sample_id=candidate.source_sample_id,
        status="committed",
        business_value=candidate.business_value,
    )


def _commit_to_postgres(company_id: str | None, candidate: TrainingAssetCandidate) -> None:
    if SessionFactory is None:
        return
    resolved_company_id = company_id or "00000000-0000-0000-0000-000000000001"
    with SessionFactory.begin() as session:
        existing = _existing_postgres_asset(session, resolved_company_id, candidate)
        if existing:
            COMMITTED_TRAINING_ASSETS.add(candidate.id)
            return
        if candidate.target == "memory":
            session.execute(
                text("""
                  insert into memories (id, company_id, memory_type, title, content, confidence)
                  values (:id, :company_id, 'business', :title, :content, 0.9200)
                """),
                {
                    "id": str(uuid4()),
                    "company_id": resolved_company_id,
                    "title": f"{candidate.title} [source:{candidate.source_sample_id}]",
                    "content": candidate.content,
                },
            )
        elif candidate.target == "knowledge":
            source_id = str(uuid4())
            session.execute(
                text("""
                  insert into knowledge_sources (id, company_id, title, source_type, uri, status)
                  values (:id, :company_id, :title, 'training_center', :uri, 'pending_embedding')
                """),
                {
                    "id": source_id,
                    "company_id": resolved_company_id,
                    "title": f"{candidate.title} [source:{candidate.source_sample_id}]",
                    "uri": f"training://{candidate.source_sample_id}",
                },
            )
            session.execute(
                text("""
                  insert into knowledge_chunks (id, company_id, knowledge_source_id, content, metadata)
                  values (:id, :company_id, :source_id, :content, cast(:metadata as jsonb))
                """),
                {
                    "id": str(uuid4()),
                    "company_id": resolved_company_id,
                    "source_id": source_id,
                    "content": candidate.content,
                    "metadata": json.dumps({"source_sample_id": candidate.source_sample_id}, ensure_ascii=False),
                },
            )
        else:
            session.execute(
                text("""
                  insert into workflows (id, company_id, name, status, definition)
                  values (:id, :company_id, :name, 'draft', cast(:definition as jsonb))
                """),
                {
                    "id": str(uuid4()),
                    "company_id": resolved_company_id,
                    "name": f"{candidate.title} [source:{candidate.source_sample_id}]",
                    "definition": json.dumps(
                        {
                            "source": "training_center",
                            "source_sample_id": candidate.source_sample_id,
                            "rule": candidate.content,
                            "requires_approval": True,
                        },
                        ensure_ascii=False,
                    ),
                },
            )
    COMMITTED_TRAINING_ASSETS.add(candidate.id)


def _existing_postgres_asset(session, company_id: str, candidate: TrainingAssetCandidate) -> bool:
    if candidate.target == "memory":
        return bool(
            session.execute(
                text("select 1 from memories where company_id=:company_id and title like :source limit 1"),
                {"company_id": company_id, "source": f"%[source:{candidate.source_sample_id}]%"},
            ).scalar_one_or_none()
        )
    if candidate.target == "knowledge":
        return bool(
            session.execute(
                text("select 1 from knowledge_sources where company_id=:company_id and uri=:uri limit 1"),
                {"company_id": company_id, "uri": f"training://{candidate.source_sample_id}"},
            ).scalar_one_or_none()
        )
    return bool(
        session.execute(
            text("select 1 from workflows where company_id=:company_id and definition->>'source_sample_id'=:sample_id limit 1"),
            {"company_id": company_id, "sample_id": candidate.source_sample_id},
        ).scalar_one_or_none()
    )


def _short_title(content: str) -> str:
    normalized = " ".join(content.split())
    return normalized[:28] + ("..." if len(normalized) > 28 else "")


def _business_value(target: str) -> str:
    if target == "workflow":
        return "减少退款、赔偿、投诉等高风险动作的人工判断成本。"
    if target == "knowledge":
        return "让 AI 下次遇到相同商品、物流、优惠问题时更快回答。"
    return "保留老板真实处理经验，让 AI 回复更接近店铺风格。"
