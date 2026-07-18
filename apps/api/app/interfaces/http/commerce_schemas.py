from typing import Any, Literal

from pydantic import BaseModel, Field


Platform = Literal["taobao", "douyin", "xianyu"]
DataType = Literal["products", "orders", "order_items", "customers", "shipments", "after_sales"]


class OAuthStartResponse(BaseModel):
    authorization_url: str
    platform: Platform


class ImportPreviewResponse(BaseModel):
    file_name: str
    encoding: str
    headers: tuple[str, ...]
    sample_rows: tuple[dict[str, str], ...]
    suggested_mapping: dict[str, str]
    required_fields: tuple[str, ...]
    warnings: tuple[str, ...]


class ImportSyncRequest(BaseModel):
    platform: Literal["taobao", "douyin"]
    platform_connection_id: str
    data_types: list[DataType] = Field(min_length=1)


class ImportJobResponse(BaseModel):
    id: str
    platform: Platform
    import_mode: Literal["api_sync", "file"]
    data_type: DataType
    status: Literal["queued", "running", "partial_success", "succeeded", "failed"]
    progress: int
    total_count: int
    success_count: int
    failure_count: int
    file_name: str | None = None
    error_summary: str | None = None
    created_at: str


class CatalogPageResponse(BaseModel):
    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int


class DatasetReadinessItemResponse(BaseModel):
    kind: Literal["products", "orders", "customers", "messages", "after_sales", "shipments"]
    label: str
    record_count: int
    readiness: int
    replay_ready: bool
    owner: str
    missing_reason: str | None


class CommerceDatasetReadinessResponse(BaseModel):
    average_readiness: int
    replay_ready_count: int
    total_kinds: int
    estimated_replay_cases: int
    items: tuple[DatasetReadinessItemResponse, ...]
    next_actions: tuple[str, ...]
