from __future__ import annotations

from sqlalchemy import text

from apps.api.app.domain.models import DraftReply
from apps.api.app.infrastructure.database import SessionFactory


HOURLY_LABOR_COST_YUAN = 40000 / 22 / 8

SEED_KNOWLEDGE = (
    ("发货规则", "您好，正常情况下当天 16:00 前付款的订单会优先当天发出；如果物流 24 小时没有更新，我们会继续帮您跟进。"),
    ("物流查询", "您好，我已经看到您的物流状态，会继续帮您关注更新；如果出现异常会第一时间转人工处理。"),
    ("尺码咨询", "您好，尺码建议优先参考商品详情页尺码表；如果您告诉我身高体重和穿着偏好，我可以帮您给出建议。"),
)

SEED_MEMORY = (
    ("店铺语气", "回复客户时保持克制、清楚，不承诺未经审批的补偿金额。"),
)


def build_customer_draft_reply(
    message_id: str,
    content: str,
    confidence: float,
    automation_decision: str,
    intent: str,
    order_external_id: str | None,
    logistics_status: str | None,
    company_id: str | None = None,
) -> DraftReply:
    if _requires_human(content, automation_decision):
        return DraftReply(
            message_id=message_id,
            content="这个问题涉及退款、赔偿、投诉或金额承诺，需要商家确认后再回复。",
            confidence=confidence,
            automation_decision="human_review",
            reason="命中高风险规则，禁止 AI 自动承诺退款、赔偿或优惠金额。",
            required_human_review=True,
            knowledge_hit=None,
            memory_hit=_find_memory(content, company_id),
            saved_minutes=0,
            estimated_saving_yuan=0,
        )

    knowledge_hit, knowledge_content = _find_knowledge(content, intent, company_id)
    memory_hit = _find_memory(content, company_id)
    reply = _compose_reply(content, intent, order_external_id, logistics_status, knowledge_content)
    saved_minutes = _saved_minutes(intent)
    return DraftReply(
        message_id=message_id,
        content=reply,
        confidence=max(confidence, 0.86 if knowledge_hit else confidence),
        automation_decision="auto_reply",
        reason="命中低风险范围，并复用了知识库或记忆，可生成自动回复草稿。",
        required_human_review=False,
        knowledge_hit=knowledge_hit,
        memory_hit=memory_hit,
        saved_minutes=saved_minutes,
        estimated_saving_yuan=round(saved_minutes / 60 * HOURLY_LABOR_COST_YUAN),
    )


def _requires_human(content: str, automation_decision: str) -> bool:
    if automation_decision == "human_review":
        return True
    return any(keyword in content for keyword in ("赔", "补偿", "退款", "退货", "投诉", "差评", "便宜", "优惠金额"))


def _compose_reply(content: str, intent: str, order_external_id: str | None, logistics_status: str | None, knowledge: str | None) -> str:
    if intent == "logistics" or "物流" in content or "发货" in content:
        order_text = f"订单 {order_external_id} " if order_external_id else ""
        status_text = f"当前状态是：{logistics_status}。" if logistics_status else ""
        return f"您好，{order_text}{status_text}{knowledge or SEED_KNOWLEDGE[1][1]}"
    if intent == "order" or "订单" in content:
        return f"您好，您的订单 {order_external_id or ''} 已查询到，我们会按订单状态继续为您跟进。"
    return knowledge or "您好，这个问题我可以先按店铺知识库为您回复；如涉及金额、退款或投诉，会立即转人工确认。"


def _saved_minutes(intent: str) -> int:
    return 5 if intent in {"logistics", "order"} else 4


def _find_knowledge(content: str, intent: str, company_id: str | None) -> tuple[str | None, str | None]:
    if SessionFactory is not None and company_id:
        with SessionFactory() as session:
            row = session.execute(
                text("""
                  select ks.title, kc.content
                  from knowledge_chunks kc
                  join knowledge_sources ks on ks.id = kc.knowledge_source_id
                  where kc.company_id = :company_id
                    and (:content ilike '%' || split_part(kc.content, '，', 1) || '%' or kc.content ilike :keyword)
                  order by kc.created_at desc
                  limit 1
                """),
                {"company_id": company_id, "content": content, "keyword": f"%{_intent_keyword(intent)}%"},
            ).mappings().one_or_none()
            if row:
                return str(row["title"]), str(row["content"])
    preferred_title = {"logistics": "物流查询", "order": "物流查询", "faq": "发货规则"}.get(intent)
    if preferred_title:
        for title, item in SEED_KNOWLEDGE:
            if title == preferred_title:
                return title, item
    for title, item in SEED_KNOWLEDGE:
        if _matches(content, intent, title, item):
            return title, item
    return None, None


def _find_memory(content: str, company_id: str | None) -> str | None:
    if SessionFactory is not None and company_id:
        with SessionFactory() as session:
            row = session.execute(
                text("""
                  select title
                  from memories
                  where company_id = :company_id
                  order by updated_at desc
                  limit 1
                """),
                {"company_id": company_id},
            ).mappings().one_or_none()
            if row:
                return str(row["title"])
    return SEED_MEMORY[0][0]


def _matches(content: str, intent: str, title: str, item: str) -> bool:
    combined = f"{content} {intent}"
    return any(keyword in combined for keyword in (title[:2], "发货", "物流", "尺码", "订单")) and any(
        keyword in item for keyword in ("发", "物流", "尺码", "订单")
    )


def _intent_keyword(intent: str) -> str:
    return {"faq": "商品", "logistics": "物流", "order": "订单"}.get(intent, intent or "客户")
