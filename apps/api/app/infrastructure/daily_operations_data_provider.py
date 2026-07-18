from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from apps.api.app.infrastructure.live_metric_snapshots import latest_live_metric_payload


DailyOperationsSourceMode = Literal["database", "empty", "unavailable"]
SessionProvider = Callable[[], Session]


@dataclass(frozen=True)
class DailyOperationsSourceData:
    source_mode: DailyOperationsSourceMode
    pre_live: dict | None
    live_metrics: dict | None
    post_live: dict | None
    product_count: int
    order_count: int
    after_sale_count: int
    warnings: tuple[str, ...]


# 把已导入的商品、订单、售后数据转换成每日运营 Workflow 输入。
def load_daily_operations_source_data(session_provider: SessionProvider, company_id: str) -> DailyOperationsSourceData:
    try:
        with session_provider() as session:
            products = session.execute(
                text(
                    """
                    select title, price, inventory_count
                    from products
                    where company_id = :company_id
                    order by updated_at desc
                    limit 20
                    """
                ),
                {"company_id": company_id},
            ).mappings().all()
            order_summary = session.execute(
                text(
                    """
                    select
                      count(*)::int as order_count,
                      coalesce(sum(total_amount), 0) as sales_amount
                    from orders
                    where company_id = :company_id
                      and coalesce(paid_at, created_at) >= now() - interval '30 days'
                    """
                ),
                {"company_id": company_id},
            ).mappings().one()
            after_sale_summary = session.execute(
                text(
                    """
                    select
                      count(*)::int as after_sale_count,
                      count(*) filter (where case_type = 'refund')::int as refund_count,
                      count(*) filter (where case_type = 'complaint')::int as complaint_count
                    from after_sale_cases
                    where company_id = :company_id
                      and created_at >= now() - interval '30 days'
                    """
                ),
                {"company_id": company_id},
            ).mappings().one()
    except SQLAlchemyError:
        return DailyOperationsSourceData(
            source_mode="unavailable",
            pre_live=None,
            live_metrics=None,
            post_live=None,
            product_count=0,
            order_count=0,
            after_sale_count=0,
            warnings=("数据库读取失败，已回退到安全基线巡检。",),
        )

    product_count = len(products)
    order_count = int(order_summary["order_count"] or 0)
    after_sale_count = int(after_sale_summary["after_sale_count"] or 0)

    if product_count == 0 and order_count == 0:
        return DailyOperationsSourceData(
            source_mode="empty",
            pre_live=None,
            live_metrics=None,
            post_live=None,
            product_count=0,
            order_count=0,
            after_sale_count=after_sale_count,
            warnings=("还没有可用于每日运营的商品或订单数据。",),
        )

    pre_live = _build_pre_live_payload(products) if product_count else None
    live_metrics = latest_live_metric_payload(company_id)
    post_live = _build_post_live_payload(order_summary, after_sale_summary, products) if order_count else None
    warnings: list[str] = []
    if product_count == 0:
        warnings.append("缺少商品数据，无法执行开播前库存和价格检查。")
    if live_metrics is None:
        warnings.append("还没有可用的直播中指标快照，将跳过在线人数、停留率和互动扫描。")
    if order_count == 0:
        warnings.append("近 30 天没有订单数据，无法生成下播复盘。")

    return DailyOperationsSourceData(
        source_mode="database",
        pre_live=pre_live,
        live_metrics=live_metrics,
        post_live=post_live,
        product_count=product_count,
        order_count=order_count,
        after_sale_count=after_sale_count,
        warnings=tuple(warnings),
    )


def _build_pre_live_payload(products) -> dict:
    return {
        "products": tuple(
            {
                "title": str(row["title"]),
                "inventory_count": int(row["inventory_count"] or 0),
                "safe_stock": 20,
                "regular_price": float(row["price"] or 0),
                "live_price": _live_price(row["price"]),
            }
            for row in products
        ),
        "coupons": (),
        "script_text": "今日直播话术需按真实商品卖点讲解，不承诺绝对效果，不使用极限词。",
        "gift_ready": False,
        "product_order_ready": len(products) >= 3,
    }


def _build_post_live_payload(order_summary, after_sale_summary, products) -> dict:
    order_count = int(order_summary["order_count"] or 0)
    sales_amount = float(order_summary["sales_amount"] or 0)
    refund_count = int(after_sale_summary["refund_count"] or 0)
    complaint_count = int(after_sale_summary["complaint_count"] or 0)
    top_product_title = str(products[0]["title"]) if products else "近 30 天主推商品"
    return {
        "sales_amount_yuan": sales_amount,
        "order_count": order_count,
        "viewer_count": max(order_count * 50, order_count, 1),
        "refund_count": refund_count,
        "top_product_title": top_product_title,
        "negative_comment_count": complaint_count,
        "host_script_score": 78,
    }


def _live_price(price: object) -> float:
    value = Decimal(str(price or 0))
    return float((value * Decimal("0.9")).quantize(Decimal("0.01")))
