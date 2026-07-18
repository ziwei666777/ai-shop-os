from __future__ import annotations

from sqlalchemy import text

from apps.api.app.domain.commerce_dataset import CommerceDatasetReadiness, DatasetReadinessItem
from apps.api.app.infrastructure.commerce_catalog import list_catalog
from apps.api.app.infrastructure.database import SessionFactory
from apps.api.app.infrastructure.memory_store import AFTER_SALE_CASES, INBOX_ITEMS


def get_commerce_dataset_readiness(company_id: str) -> CommerceDatasetReadiness:
    counts = {
        "products": _catalog_total("products", company_id),
        "orders": _catalog_total("orders", company_id),
        "customers": _catalog_total("customers", company_id),
        "shipments": _catalog_total("shipments", company_id),
        "messages": _table_count(company_id, "messages", fallback=len(INBOX_ITEMS)),
        "after_sales": _table_count(company_id, "after_sale_cases", fallback=len(AFTER_SALE_CASES)),
    }
    items = (
        _item("products", "商品数据", counts["products"], 5, "AI客服 / AI运营"),
        _item("orders", "订单数据", counts["orders"], 5, "AI客服 / Replay"),
        _item("customers", "客户数据", counts["customers"], 5, "AI运营"),
        _item("messages", "客服消息", counts["messages"], 20, "AI客服 / Training"),
        _item("after_sales", "售后数据", counts["after_sales"], 5, "AI售后 / Evaluation"),
        _item("shipments", "物流数据", counts["shipments"], 5, "AI客服 / AI售后"),
    )
    replay_ready_count = sum(1 for item in items if item.replay_ready)
    average = round(sum(item.readiness for item in items) / len(items))
    estimated_cases = min(counts["orders"], counts["messages"]) + counts["after_sales"] + counts["shipments"]
    return CommerceDatasetReadiness(
        average_readiness=average,
        replay_ready_count=replay_ready_count,
        total_kinds=len(items),
        estimated_replay_cases=estimated_cases,
        items=items,
        next_actions=_next_actions(items),
    )


def _catalog_total(kind: str, company_id: str) -> int:
    _, total = list_catalog(kind, company_id, None, None, None, 1, 1)
    return total


def _table_count(company_id: str, table_name: str, fallback: int) -> int:
    if SessionFactory is None:
        return fallback
    with SessionFactory() as session:
        return int(
            session.execute(
                text(f"select count(*) from {table_name} where company_id = :company_id"),
                {"company_id": company_id},
            ).scalar_one()
        )


def _item(kind: str, label: str, count: int, target: int, owner: str) -> DatasetReadinessItem:
    readiness = min(round(count / target * 100), 100)
    return DatasetReadinessItem(
        kind=kind,
        label=label,
        record_count=count,
        readiness=readiness,
        replay_ready=count > 0,
        owner=owner,
        missing_reason=None if count > 0 else f"缺少{label}，AI 无法用真实数据验证。",
    )


def _next_actions(items: tuple[DatasetReadinessItem, ...]) -> tuple[str, ...]:
    missing = [item.label for item in items if not item.replay_ready]
    if missing:
        return (
            f"优先导入：{'、'.join(missing[:3])}。",
            "导入后重新查看回放验证和 AI 评分。",
            "每天保留老板修改样本，用于训练中心沉淀。",
        )
    return (
        "当前基础数据已具备回放条件，下一步导入更多历史客服消息。",
        "用 Replay 对比 AI 和人工处理结果。",
        "用 Evaluation 每天统计节省分钟数和节省金额。",
    )

