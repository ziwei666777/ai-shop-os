from __future__ import annotations

from dataclasses import asdict
from typing import TypeVar

from sqlalchemy import text

from apps.api.app.domain.commerce_imports import CustomerView, OrderView, ProductView, ShipmentView
from apps.api.app.infrastructure.database import SessionFactory


CatalogItem = TypeVar("CatalogItem", ProductView, OrderView, CustomerView, ShipmentView)


SEED_PRODUCTS = (
    ProductView("product-1", "taobao", "淘宝主店", "TB-P-1001", "轻量防晒外套", "FS-001", 129.0, 86, "在售", "2026-07-11T09:30:00+08:00"),
    ProductView("product-2", "douyin", "抖音旗舰店", "DY-P-2031", "夏季冰感直筒裤", "BK-2031", 99.0, 24, "在售", "2026-07-11T09:18:00+08:00"),
    ProductView("product-3", "xianyu", "闲鱼店铺", "XY-P-0188", "样衣清仓连衣裙", "QK-188", 68.0, 3, "库存偏低", "2026-07-10T21:06:00+08:00"),
)

SEED_ORDERS = (
    OrderView("order-1", "taobao", "淘宝主店", "TB20260711001", "小林同学", "待发货", 228.0, "2026-07-11T09:02:00+08:00", "2026-07-11T09:05:00+08:00"),
    OrderView("order-2", "douyin", "抖音旗舰店", "DY20260711016", "周女士", "运输中", 99.0, "2026-07-11T08:41:00+08:00", "2026-07-11T09:12:00+08:00"),
    OrderView("order-3", "xianyu", "闲鱼店铺", "XY20260710008", "海边的风", "已完成", 68.0, "2026-07-10T18:20:00+08:00", "2026-07-11T08:20:00+08:00"),
)

SEED_CUSTOMERS = (
    CustomerView("customer-1", "taobao", "淘宝主店", "TB-U-9001", "小林同学", 5, 836.0, ("复购客户",), "2026-07-11T09:05:00+08:00"),
    CustomerView("customer-2", "douyin", "抖音旗舰店", "DY-U-2871", "周女士", 2, 198.0, ("直播间客户",), "2026-07-11T09:12:00+08:00"),
    CustomerView("customer-3", "xianyu", "闲鱼店铺", "XY-U-1730", "海边的风", 1, 68.0, ("新客户",), "2026-07-11T08:20:00+08:00"),
)

SEED_SHIPMENTS = (
    ShipmentView("shipment-1", "douyin", "抖音旗舰店", "DY-S-001", "DY20260711016", "中通快递", "ZT202607110016", "运输中", "2026-07-11T09:00:00+08:00", None),
)


def list_catalog(
    kind: str,
    company_id: str,
    platform: str | None,
    status: str | None,
    keyword: str | None,
    page: int,
    page_size: int,
) -> tuple[list[dict[str, object]], int]:
    if SessionFactory is not None:
        return _list_postgres(kind, company_id, platform, status, keyword, page, page_size)

    source = {
        "products": SEED_PRODUCTS,
        "orders": SEED_ORDERS,
        "customers": SEED_CUSTOMERS,
        "shipments": SEED_SHIPMENTS,
    }[kind]
    items = [asdict(item) for item in source]
    if platform:
        items = [item for item in items if item["platform"] == platform]
    if status and kind in ("products", "orders", "shipments"):
        items = [item for item in items if item.get("status") == status]
    if keyword:
        lowered = keyword.casefold()
        items = [item for item in items if lowered in " ".join(str(value) for value in item.values()).casefold()]
    total = len(items)
    start = (page - 1) * page_size
    return items[start : start + page_size], total


def _list_postgres(
    kind: str,
    company_id: str,
    platform: str | None,
    status: str | None,
    keyword: str | None,
    page: int,
    page_size: int,
) -> tuple[list[dict[str, object]], int]:
    query_by_kind = {
        "products": """
          select p.id::text, p.platform::text, coalesce(pc.shop_identifier, '未命名店铺') shop_name,
                 p.external_id, p.title, coalesce(p.sku, '') sku, p.price::float,
                 p.inventory_count, case when p.inventory_count > 0 then '在售' else '缺货' end status,
                 p.updated_at::text
          from products p left join platform_connections pc on pc.id = p.platform_connection_id
        """,
        "orders": """
          select o.id::text, o.platform::text, coalesce(pc.shop_identifier, '未命名店铺') shop_name,
                 o.external_id, coalesce(c.name, '未知客户') customer_name, o.status,
                 o.total_amount::float, o.paid_at::text, o.updated_at::text
          from orders o left join customers c on c.id = o.customer_id
          left join platform_connections pc on pc.id = o.platform_connection_id
        """,
        "customers": """
          select c.id::text, c.platform::text, coalesce(pc.shop_identifier, '未命名店铺') shop_name,
                 c.external_id, c.name, count(o.id)::int order_count,
                 coalesce(sum(o.total_amount), 0)::float total_spent, c.tags, c.updated_at::text
          from customers c left join orders o on o.customer_id = c.id
          left join platform_connections pc on pc.id = c.platform_connection_id
        """,
        "shipments": """
          select s.id::text, o.platform::text, coalesce(pc.shop_identifier, '未命名店铺') shop_name,
                 s.external_id, coalesce(o.external_id, '') order_external_id,
                 coalesce(s.carrier_name, '') carrier_name, coalesce(s.tracking_number, '') tracking_number,
                 s.status, s.shipped_at::text, s.delivered_at::text
          from shipments s left join orders o on o.id = s.order_id
          left join platform_connections pc on pc.id = s.platform_connection_id
        """,
    }[kind]
    company_alias = {"products": "p", "orders": "o", "customers": "c", "shipments": "s"}[kind]
    filters = [f"{company_alias}.company_id = :company_id"]
    params: dict[str, object] = {"company_id": company_id, "limit": page_size, "offset": (page - 1) * page_size}
    if platform:
        platform_alias = "o" if kind == "shipments" else company_alias
        filters.append(f"{platform_alias}.platform::text = :platform")
        params["platform"] = platform
    if status and kind in ("orders", "shipments"):
        filters.append(f"{company_alias}.status = :status")
        params["status"] = status
    if keyword:
        searchable = {
            "products": "concat_ws(' ', p.external_id, p.title, p.sku)",
            "orders": "concat_ws(' ', o.external_id, c.name, o.status)",
            "customers": "concat_ws(' ', c.external_id, c.name)",
            "shipments": "concat_ws(' ', s.external_id, s.tracking_number, o.external_id)",
        }[kind]
        filters.append(f"{searchable} ilike :keyword")
        params["keyword"] = f"%{keyword}%"
    where_sql = " where " + " and ".join(filters)
    group_sql = " group by c.id, pc.shop_identifier" if kind == "customers" else ""
    with SessionFactory() as session:
        all_rows = session.execute(text(query_by_kind + where_sql + group_sql), params).mappings().all()
    total = len(all_rows)
    paged_rows = all_rows[(page - 1) * page_size : page * page_size]
    return [dict(row) for row in paged_rows], total

