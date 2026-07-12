from dataclasses import dataclass, field
from typing import Literal


CommercePlatform = Literal["taobao", "douyin", "xianyu"]
ImportDataType = Literal["products", "orders", "order_items", "customers", "shipments", "after_sales"]
ImportMode = Literal["api_sync", "file"]
ImportStatus = Literal["queued", "running", "partial_success", "succeeded", "failed"]


@dataclass(frozen=True)
class ImportPreview:
    file_name: str
    encoding: str
    headers: tuple[str, ...]
    sample_rows: tuple[dict[str, str], ...]
    suggested_mapping: dict[str, str]
    required_fields: tuple[str, ...]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class ImportJobView:
    id: str
    platform: CommercePlatform
    import_mode: ImportMode
    data_type: ImportDataType
    status: ImportStatus
    progress: int
    total_count: int
    success_count: int
    failure_count: int
    file_name: str | None
    error_summary: str | None
    created_at: str


@dataclass(frozen=True)
class ProductView:
    id: str
    platform: CommercePlatform
    shop_name: str
    external_id: str
    title: str
    sku: str
    price: float
    inventory_count: int
    status: str
    updated_at: str


@dataclass(frozen=True)
class OrderView:
    id: str
    platform: CommercePlatform
    shop_name: str
    external_id: str
    customer_name: str
    status: str
    total_amount: float
    paid_at: str | None
    updated_at: str


@dataclass(frozen=True)
class CustomerView:
    id: str
    platform: CommercePlatform
    shop_name: str
    external_id: str
    name: str
    order_count: int
    total_spent: float
    tags: tuple[str, ...] = field(default_factory=tuple)
    updated_at: str = ""


@dataclass(frozen=True)
class ShipmentView:
    id: str
    platform: CommercePlatform
    shop_name: str
    external_id: str
    order_external_id: str
    carrier_name: str
    tracking_number: str
    status: str
    shipped_at: str | None
    delivered_at: str | None

