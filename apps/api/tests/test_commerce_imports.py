from io import BytesIO
import json
from pathlib import Path

from fastapi.testclient import TestClient
from openpyxl import Workbook

from apps.api.app.infrastructure.official_platform_sync import _normalize_record
from apps.api.app.infrastructure.platform_security import sign_douyin_request, sign_taobao_request
from apps.api.app.main import app


client = TestClient(app)


def test_csv_preview_supports_gb18030_and_suggests_mapping() -> None:
    content = "订单号,订单状态,实付金额,买家昵称\nTB001,待发货,129.00,张女士\n".encode("gb18030")
    response = client.post(
        "/v1/imports/preview?file_name=taobao-orders.csv&platform=taobao&data_type=orders",
        content=content,
        headers={"content-type": "application/octet-stream"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["encoding"] == "gb18030"
    assert body["suggested_mapping"]["external_id"] == "订单号"
    assert body["sample_rows"][0]["买家昵称"] == "张女士"


def test_preview_rejects_unsafe_file_type() -> None:
    response = client.post(
        "/v1/imports/preview?file_name=orders.xlsm&platform=xianyu&data_type=orders",
        content=b"not-an-excel-file",
    )

    assert response.status_code == 400
    assert "CSV" in response.json()["detail"]


def test_catalog_endpoints_are_paginated_and_platform_filter_isolated() -> None:
    response = client.get("/v1/orders?platform=douyin&page=1&page_size=20")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["platform"] == "douyin"


def test_commerce_dataset_readiness_uses_catalog_and_message_sources() -> None:
    response = client.get("/v1/commerce-dataset/readiness")

    assert response.status_code == 200
    body = response.json()
    assert body["total_kinds"] == 6
    assert body["replay_ready_count"] >= 4
    assert body["estimated_replay_cases"] > 0
    assert any(item["kind"] == "orders" and item["record_count"] > 0 for item in body["items"])


def test_formal_import_is_blocked_without_database_and_redis() -> None:
    response = client.post(
        "/v1/imports/files?file_name=orders.csv&platform=xianyu&data_type=orders&shop_name=test",
        content="订单号,订单状态,实付金额\nXY001,已完成,68\n".encode(),
        headers={
            "X-Field-Mapping": "%7B%22external_id%22%3A%22%E8%AE%A2%E5%8D%95%E5%8F%B7%22%2C%22status%22%3A%22%E8%AE%A2%E5%8D%95%E7%8A%B6%E6%80%81%22%2C%22total_amount%22%3A%22%E5%AE%9E%E4%BB%98%E9%87%91%E9%A2%9D%22%7D"
        },
    )

    assert response.status_code == 503
    assert "数据库" in response.json()["detail"] or "Redis" in response.json()["detail"]


def test_platform_signatures_are_deterministic() -> None:
    parameters = {"method": "test.method", "app_key": "demo", "timestamp": "2026-07-11 12:00:00"}

    assert sign_taobao_request(parameters, "secret") == "074F28172217BC379042331D630AD48FED252F5FA633CBADC066117CE7EB81B8"
    assert sign_douyin_request(parameters, "secret") == "074f28172217bc379042331d630ad48fed252f5fa633cbadc066117ce7eb81b8"


def test_xlsx_preview_reads_values_without_executing_formula() -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["订单号", "订单状态", "实付金额"])
    sheet.append(["XY002", "已完成", "=60+8"])
    buffer = BytesIO()
    workbook.save(buffer)

    response = client.post(
        "/v1/imports/preview?file_name=xianyu-orders.xlsx&platform=xianyu&data_type=orders",
        content=buffer.getvalue(),
        headers={"content-type": "application/octet-stream"},
    )

    assert response.status_code == 200
    assert response.json()["encoding"] == "xlsx"
    assert response.json()["sample_rows"][0]["实付金额"] == ""


def test_json_preview_accepts_array_and_suggests_mapping() -> None:
    content = json.dumps(
        [
            {"order_id": "DY001", "status": "已付款", "total_amount": 199.5, "buyer_name": "周先生"},
            {"order_id": "DY002", "status": "已发货", "total_amount": 88, "buyer_name": "吴女士"},
        ],
        ensure_ascii=False,
    ).encode()

    response = client.post(
        "/v1/imports/preview?file_name=douyin-orders.json&platform=douyin&data_type=orders",
        content=content,
        headers={"content-type": "application/octet-stream"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["encoding"] == "json"
    assert body["suggested_mapping"]["external_id"] == "order_id"
    assert body["suggested_mapping"]["total_amount"] == "total_amount"
    assert body["sample_rows"][0]["buyer_name"] == "周先生"


def test_preview_absorbs_mall_app_order_field_aliases() -> None:
    content = json.dumps(
        [
            {
                "orderSn": "MALL001",
                "memberUsername": "old-buyer",
                "status": 2,
                "payAmount": 168.5,
                "paymentTime": "2026-07-13 10:00:00",
            }
        ],
        ensure_ascii=False,
    ).encode()

    response = client.post(
        "/v1/imports/preview?file_name=mall-orders.json&platform=taobao&data_type=orders",
        content=content,
        headers={"content-type": "application/octet-stream"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["suggested_mapping"]["external_id"] == "orderSn"
    assert body["suggested_mapping"]["customer_name"] == "memberUsername"
    assert body["suggested_mapping"]["total_amount"] == "payAmount"
    assert body["suggested_mapping"]["paid_at"] == "paymentTime"


def test_preview_absorbs_mall_app_after_sale_field_aliases() -> None:
    content = json.dumps(
        [
            {
                "id": 1001,
                "orderSn": "MALL001",
                "status": 0,
                "reason": "商品破损",
                "description": "包装损坏",
                "proofPics": "pic-a,pic-b",
            }
        ],
        ensure_ascii=False,
    ).encode()

    response = client.post(
        "/v1/imports/preview?file_name=mall-return.json&platform=taobao&data_type=after_sales",
        content=content,
        headers={"content-type": "application/octet-stream"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["suggested_mapping"]["external_id"] == "id"
    assert body["suggested_mapping"]["order_external_id"] == "orderSn"
    assert body["suggested_mapping"]["reason"] == "reason"


def test_json_preview_accepts_wrapped_rows() -> None:
    content = json.dumps({"rows": [{"customer_id": "C001", "name": "老客户", "tags": ["高价值", "复购"]}]}, ensure_ascii=False).encode()

    response = client.post(
        "/v1/imports/preview?file_name=customers.json&platform=taobao&data_type=customers",
        content=content,
        headers={"content-type": "application/octet-stream"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["headers"] == ["customer_id", "name", "tags"]
    assert body["sample_rows"][0]["tags"] == '["高价值","复购"]'


def test_json_preview_rejects_non_object_rows() -> None:
    response = client.post(
        "/v1/imports/preview?file_name=orders.json&platform=xianyu&data_type=orders",
        content=b'["bad-row"]',
        headers={"content-type": "application/octet-stream"},
    )

    assert response.status_code == 400
    assert "JSON" in response.json()["detail"]


def test_official_order_payload_is_normalized_without_address_copy() -> None:
    rows = _normalize_record(
        "taobao",
        "orders",
        {
            "tid": "TB100",
            "status": "WAIT_SELLER_SEND_GOODS",
            "payment": "129.00",
            "pay_time": "2026-07-11 12:00:00",
            "receiver_address": "不应复制的地址",
        },
    )

    assert rows[0]["external_id"] == "TB100"
    assert "receiver_address" not in rows[0]


def test_multiplatform_migration_contains_tenant_and_idempotency_guards() -> None:
    migration = Path("supabase/migrations/202607110001_multiplatform_import.sql").read_text(encoding="utf-8")

    assert "alter type public.connector_platform add value if not exists 'douyin'" in migration
    assert "alter table public.order_items enable row level security" not in migration  # 通过统一循环启用
    assert "alter table public.%I enable row level security" in migration
    assert "products_company_connection_external_idx" in migration
    assert "import_jobs_company_status_idx" in migration
