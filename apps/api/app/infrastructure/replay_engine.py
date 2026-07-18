from __future__ import annotations

from sqlalchemy import text

from apps.api.app.domain.replay import ReplayCase, ReplayDecision, ReplayResult, ReplaySummary
from apps.api.app.infrastructure.commerce_catalog import list_catalog
from apps.api.app.infrastructure.database import SessionFactory
from apps.api.app.infrastructure.memory_store import AFTER_SALE_CASES, INBOX_ITEMS


HOURLY_LABOR_COST_YUAN = 40000 / 22 / 8
REPLAY_CASES: tuple[ReplayCase, ...] = (
    ReplayCase(
        id="replay-customer-1",
        case_type="customer_message",
        title="物流咨询",
        input_text="客户问：今天下单什么时候发货？能不能帮我催一下？",
        human_result="人工客服查询订单后回复预计当天出库，用时 4 分钟。",
        expected_decision="auto_reply",
        expected_minutes=4,
    ),
    ReplayCase(
        id="replay-customer-2",
        case_type="customer_message",
        title="赔偿诉求",
        input_text="客户说：物流太慢了，必须赔我 20 元。",
        human_result="人工客服转交主管确认，没有直接承诺赔偿，用时 8 分钟。",
        expected_decision="human_review",
        expected_minutes=8,
    ),
    ReplayCase(
        id="replay-after-sale-1",
        case_type="after_sale_case",
        title="退货申请",
        input_text="客户申请尺码不合适退货，订单已签收 2 天。",
        human_result="售后判断符合 7 天无理由，建议同意退货，用时 12 分钟。",
        expected_decision="approval_required",
        expected_minutes=12,
    ),
    ReplayCase(
        id="replay-after-sale-2",
        case_type="after_sale_case",
        title="投诉升级",
        input_text="客户投诉商品有瑕疵并要求补偿，否则给差评。",
        human_result="售后主管要求先看图片证据，不承诺金额，用时 15 分钟。",
        expected_decision="approval_required",
        expected_minutes=15,
    ),
    ReplayCase(
        id="replay-operation-1",
        case_type="operation_signal",
        title="高意向客户",
        input_text="同一客户 7 天内 3 次咨询尺码、发货和优惠，但未下单。",
        human_result="运营人工标记为高意向客户，准备私域跟进话术，用时 18 分钟。",
        expected_decision="operation_suggestion",
        expected_minutes=18,
    ),
)


def run_replay_summary(company_id: str = "00000000-0000-0000-0000-000000000001") -> ReplaySummary:
    cases = _build_replay_cases_from_business_data(company_id)
    if not cases:
        cases = REPLAY_CASES
    results = tuple(_replay_case(case) for case in cases)
    total = len(results)
    correct = sum(1 for result in results if result.is_correct)
    auto_count = sum(1 for result in results if not result.requires_human)
    manual_count = total - auto_count
    saved_minutes = sum(result.saved_minutes for result in results)
    return ReplaySummary(
        total_cases=total,
        correct_cases=correct,
        accuracy=round(correct / total, 4) if total else 0,
        auto_rate=round(auto_count / total, 4) if total else 0,
        manual_rate=round(manual_count / total, 4) if total else 0,
        saved_minutes=saved_minutes,
        estimated_saving_yuan=round(saved_minutes / 60 * HOURLY_LABOR_COST_YUAN),
        results=results,
    )


def _build_replay_cases_from_business_data(company_id: str) -> tuple[ReplayCase, ...]:
    cases: list[ReplayCase] = []
    cases.extend(_message_replay_cases(company_id))
    cases.extend(_after_sale_replay_cases(company_id))
    cases.extend(_shipment_replay_cases(company_id))
    cases.extend(_operation_replay_cases(company_id))
    return tuple(cases[:50])


def _message_replay_cases(company_id: str) -> list[ReplayCase]:
    if SessionFactory is None:
        return [
            ReplayCase(
                id=f"replay-message-{item.id}",
                case_type="customer_message",
                title=f"客服消息：{item.customer_name}",
                input_text=item.content,
                human_result=_human_message_result(item.status, item.automation_decision),
                expected_decision="human_review" if item.automation_decision == "human_review" else "auto_reply",
                expected_minutes=8 if item.automation_decision == "human_review" else 4,
            )
            for item in INBOX_ITEMS.values()
        ]
    with SessionFactory() as session:
        rows = session.execute(
            text("""
              select id::text, content, intent::text, automation_decision::text, final_content, ai_draft_content
              from messages
              where company_id = :company_id
              order by id desc
              limit 30
            """),
            {"company_id": company_id},
        ).mappings().all()
    return [
        ReplayCase(
            id=f"replay-message-{row['id']}",
            case_type="customer_message",
            title=f"客服消息：{row['intent']}",
            input_text=str(row["content"]),
            human_result=str(row.get("final_content") or row.get("ai_draft_content") or "历史客服完成处理。"),
            expected_decision="human_review" if row["automation_decision"] == "human_review" else "auto_reply",
            expected_minutes=8 if row["automation_decision"] == "human_review" else 4,
        )
        for row in rows
    ]


def _after_sale_replay_cases(company_id: str) -> list[ReplayCase]:
    if SessionFactory is None:
        return [
            ReplayCase(
                id=f"replay-after-sale-{case.id}",
                case_type="after_sale_case",
                title=case.title,
                input_text=f"{case.description} AI 建议：{case.ai_suggestion}",
                human_result="售后需要商家审批后处理。",
                expected_decision="approval_required",
                expected_minutes=15 if case.risk_level == "high" else 12,
            )
            for case in AFTER_SALE_CASES.values()
        ]
    with SessionFactory() as session:
        rows = session.execute(
            text("""
              select id::text, title, description, risk_level, ai_suggestion
              from after_sale_cases
              where company_id = :company_id
              order by id desc
              limit 30
            """),
            {"company_id": company_id},
        ).mappings().all()
    return [
        ReplayCase(
            id=f"replay-after-sale-{row['id']}",
            case_type="after_sale_case",
            title=str(row["title"]),
            input_text=f"{row['description']} AI 建议：{row['ai_suggestion']}",
            human_result="售后需要商家审批后处理。",
            expected_decision="approval_required",
            expected_minutes=15 if row["risk_level"] == "high" else 12,
        )
        for row in rows
    ]


def _shipment_replay_cases(company_id: str) -> list[ReplayCase]:
    shipments, _ = list_catalog("shipments", company_id, None, None, None, 1, 20)
    cases: list[ReplayCase] = []
    for shipment in shipments:
        status = str(shipment.get("status", ""))
        cases.append(
            ReplayCase(
                id=f"replay-shipment-{shipment.get('id')}",
                case_type="customer_message",
                title=f"物流回放：{shipment.get('order_external_id')}",
                input_text=f"客户咨询订单 {shipment.get('order_external_id')} 物流，当前状态：{status}，运单号：{shipment.get('tracking_number')}",
                human_result="人工客服查询物流后回复客户。",
                expected_decision="auto_reply" if status not in {"异常", "丢件", "退回"} else "human_review",
                expected_minutes=5,
            )
        )
    return cases


def _operation_replay_cases(company_id: str) -> list[ReplayCase]:
    customers, _ = list_catalog("customers", company_id, None, None, None, 1, 20)
    cases: list[ReplayCase] = []
    for customer in customers:
        order_count = int(customer.get("order_count") or 0)
        total_spent = float(customer.get("total_spent") or 0)
        if order_count >= 2 or total_spent >= 150:
            cases.append(
                ReplayCase(
                    id=f"replay-operation-{customer.get('id')}",
                    case_type="operation_signal",
                    title=f"客户运营回放：{customer.get('name')}",
                    input_text=f"客户 {customer.get('name')} 历史下单 {order_count} 次，累计消费 ¥{total_spent:.0f}，需要判断是否进入私域跟进。",
                    human_result="运营人工识别客户价值并制定跟进策略。",
                    expected_decision="operation_suggestion",
                    expected_minutes=18,
                )
            )
    return cases


def _human_message_result(status: str, decision: str) -> str:
    if decision == "human_review" or status == "needs_human":
        return "历史人工客服接管处理，避免 AI 越权承诺。"
    return "历史客服完成低风险回复。"


def _replay_case(case: ReplayCase) -> ReplayResult:
    decision, ai_result, requires_human = _decide(case)
    is_correct = decision == case.expected_decision
    saved_minutes = case.expected_minutes if is_correct else max(case.expected_minutes // 2, 0)
    return ReplayResult(
        id=case.id,
        case_type=case.case_type,
        title=case.title,
        input_text=case.input_text,
        human_result=case.human_result,
        ai_decision=decision,
        ai_result=ai_result,
        is_correct=is_correct,
        requires_human=requires_human,
        saved_minutes=saved_minutes,
        evaluation_note=_evaluation_note(is_correct, requires_human),
    )


def _decide(case: ReplayCase) -> tuple[ReplayDecision, str, bool]:
    text = case.input_text
    if any(keyword in text for keyword in ("赔", "补偿", "差评", "瑕疵", "投诉")):
        return (
            "approval_required" if case.case_type == "after_sale_case" else "human_review",
            "涉及赔偿、投诉或金额承诺，AI 只给建议，必须人工确认后回复。",
            True,
        )
    if case.case_type == "operation_signal":
        return (
            "operation_suggestion",
            "识别为高意向客户，建议生成私域跟进话术和小预算投流草稿，预算动作必须审批。",
            False,
        )
    if case.case_type == "after_sale_case":
        # 售后动作会影响退款、退货、赔偿和店铺评分，V0 阶段必须统一进入老板审批。
        return (
            "approval_required",
            "售后动作需要审批，AI 输出建议但不直接退款、退货或承诺赔偿。",
            True,
        )
    if any(keyword in text for keyword in ("发货", "物流", "订单")):
        return (
            "auto_reply",
            "属于低风险订单/物流咨询，AI 可以生成回复草稿并记录处理结果。",
            False,
        )
    return "human_review", "AI 不确定问题类型，暂停自动处理并交给人工。", True


def _evaluation_note(is_correct: bool, requires_human: bool) -> str:
    if not is_correct:
        return "AI 判断与历史人工结果不一致，需要进入 Training Center 修正。"
    if requires_human:
        return "AI 正确拦截高风险动作，减少越权退款、赔偿或投诉风险。"
    return "AI 可处理低风险重复工作，节省人工响应时间。"
