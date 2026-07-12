from __future__ import annotations

import json
import time
from datetime import datetime, timezone, timedelta
from typing import Any

import httpx
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from apps.api.app.infrastructure.config import get_settings
from apps.api.app.infrastructure.database import SessionFactory
from apps.api.app.infrastructure.platform_security import TokenCipher, sign_douyin_request, sign_taobao_request


TAOBAO_METHODS = {
    "products": "taobao.items.seller.list.get",
    "orders": "taobao.trades.sold.get",
    "order_items": "taobao.trades.sold.get",
    "customers": "taobao.trades.sold.get",
    "shipments": "taobao.logistics.orders.detail.get",
    "after_sales": "taobao.refunds.receive.get",
}

DOUYIN_METHODS = {
    "products": "product.listV2",
    "orders": "order.searchList",
    "order_items": "order.searchList",
    "customers": "order.searchList",
    "shipments": "order.searchList",
    "after_sales": "afterSale.searchList",
}


class OfficialSyncError(RuntimeError):
    pass


class AuthorizationExpiredError(OfficialSyncError):
    pass


def run_official_sync(job: dict[str, object]) -> tuple[int, int, str | None]:
    connection = _load_connection(str(job["company_id"]), str(job["platform_connection_id"]))
    token = TokenCipher().decrypt(str(connection["access_token_encrypted"]))
    page = int((job.get("cursor") or {}).get("page", 1))
    success_count = 0
    failure_count = 0
    errors: list[str] = []

    # 单次任务设置页数上限，防止平台异常响应造成无限循环。
    for _ in range(100):
        records, has_more = _fetch_page(str(job["platform"]), str(job["data_type"]), token, page)
        if not records:
            break
        with SessionFactory.begin() as session:
            for index, source in enumerate(records, start=1):
                try:
                    normalized_rows = _normalize_record(str(job["platform"]), str(job["data_type"]), source)
                    if not normalized_rows:
                        raise ValueError("平台记录缺少必要编号")
                    for normalized in normalized_rows:
                        with session.begin_nested():
                            # 延迟导入避免与任务模块形成模块加载环。
                            from apps.api.app.infrastructure.import_jobs import _upsert_row

                            _upsert_row(session, job, normalized)
                            success_count += 1
                except (ValueError, TypeError, KeyError, SQLAlchemyError) as error:
                    failure_count += 1
                    if len(errors) < 10:
                        errors.append(f"第 {page} 页第 {index} 条：{error}")
            session.execute(
                text("update import_jobs set cursor=cast(:cursor as jsonb), progress=:progress where id=:id"),
                {"id": job["id"], "cursor": json.dumps({"page": page + 1}), "progress": min(95, page)},
            )
        if not has_more:
            break
        page += 1

    with SessionFactory.begin() as session:
        session.execute(
            text("update platform_connections set last_synced_at=now(), last_error=null where id=:id"),
            {"id": job["platform_connection_id"]},
        )
    return success_count, failure_count, "；".join(errors) or None


def _fetch_page(platform: str, data_type: str, token: str, page: int) -> tuple[list[dict[str, Any]], bool]:
    method = (TAOBAO_METHODS if platform == "taobao" else DOUYIN_METHODS)[data_type]
    response = _call_with_retry(platform, method, token, page)
    _raise_platform_error(platform, response)
    records = _extract_records(platform, data_type, response)
    return records, len(records) >= 50


def _call_with_retry(platform: str, method: str, token: str, page: int) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with httpx.Client(timeout=httpx.Timeout(20.0, connect=8.0)) as client:
                if platform == "taobao":
                    return _call_taobao(client, method, token, page)
                return _call_douyin(client, method, token, page)
        except (httpx.TimeoutException, httpx.NetworkError) as error:
            last_error = error
            time.sleep(2**attempt)
        except httpx.HTTPStatusError as error:
            if error.response.status_code not in (429, 500, 502, 503, 504):
                raise OfficialSyncError(f"平台请求失败（HTTP {error.response.status_code}）") from error
            last_error = error
            time.sleep(2**attempt)
    raise OfficialSyncError("平台网络连续失败，请稍后从断点继续。") from last_error


def _call_taobao(client: httpx.Client, method: str, token: str, page: int) -> dict[str, Any]:
    settings = get_settings()
    if not settings.taobao_app_key or not settings.taobao_app_secret:
        raise OfficialSyncError("淘宝应用凭证尚未配置。")
    parameters = {
        "method": method,
        "app_key": settings.taobao_app_key,
        "session": token,
        "timestamp": datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"),
        "format": "json",
        "v": "2.0",
        "sign_method": "hmac-sha256",
        "page_no": str(page),
        "page_size": "50",
        "fields": "num_iid,title,outer_id,price,num,tid,status,payment,pay_time,buyer_nick,buyer_open_uid,orders,invoice_no,company_name,refund_id,reason",
    }
    parameters["sign"] = sign_taobao_request(parameters, settings.taobao_app_secret)
    response = client.post("https://eco.taobao.com/router/rest", data=parameters)
    response.raise_for_status()
    return response.json()


def _call_douyin(client: httpx.Client, method: str, token: str, page: int) -> dict[str, Any]:
    settings = get_settings()
    if not settings.douyin_app_key or not settings.douyin_app_secret:
        raise OfficialSyncError("抖店应用凭证尚未配置。")
    param_json = json.dumps({"page": page, "page_size": 50}, separators=(",", ":"), ensure_ascii=False)
    parameters = {
        "method": method,
        "app_key": settings.douyin_app_key,
        "access_token": token,
        "timestamp": datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"),
        "v": "2",
        "sign_method": "hmac-sha256",
        "param_json": param_json,
    }
    parameters["sign"] = sign_douyin_request(parameters, settings.douyin_app_secret)
    response = client.post(f"https://openapi-fxg.jinritemai.com/{method.replace('.', '/')}", params=parameters)
    response.raise_for_status()
    return response.json()


def _raise_platform_error(platform: str, payload: dict[str, Any]) -> None:
    if platform == "taobao":
        error = payload.get("error_response")
        if not error:
            return
        code = str(error.get("code", ""))
        message = str(error.get("sub_msg") or error.get("msg") or "平台调用失败")
    else:
        code = str(payload.get("err_no", 0))
        if code in ("0", ""):
            return
        message = str(payload.get("message") or "平台调用失败")
    if any(keyword in (code + message).lower() for keyword in ("token", "session", "auth", "invalid-session")):
        raise AuthorizationExpiredError("平台授权已失效，请重新授权店铺。")
    raise OfficialSyncError(f"平台接口返回错误：{message[:160]}")


def _extract_records(platform: str, data_type: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    if platform == "douyin":
        data = payload.get("data") or {}
        for key in ("list", "shop_order_list", "product_list", "aftersale_list", "order_list"):
            if isinstance(data.get(key), list):
                return data[key]
        return []
    response = next((value for key, value in payload.items() if key.endswith("_response") and isinstance(value, dict)), {})
    containers = ("trades", "items", "refunds", "shippings", "logistics_orders")
    for container_key in containers:
        container = response.get(container_key)
        if isinstance(container, dict):
            for value in container.values():
                if isinstance(value, list):
                    return value
        if isinstance(container, list):
            return container
    return []


def _normalize_record(platform: str, data_type: str, source: dict[str, Any]) -> list[dict[str, str]]:
    if data_type == "products":
        return [{
            "external_id": _pick(source, "num_iid", "product_id", "id"),
            "title": _pick(source, "title", "name"), "sku": _pick(source, "outer_id", "sku_id", "sku"),
            "price": _pick(source, "price", "discount_price"), "inventory_count": _pick(source, "num", "stock_num", "inventory"),
        }]
    if data_type == "orders":
        return [{
            "external_id": _pick(source, "tid", "order_id", "shop_order_id"),
            "status": _pick(source, "status", "order_status"), "total_amount": _pick(source, "payment", "pay_amount", "order_amount"),
            "paid_at": _pick(source, "pay_time", "pay_time_str"),
        }]
    if data_type == "customers":
        return [{
            "external_id": _pick(source, "buyer_open_uid", "buyer_id", "user_id", "buyer_nick"),
            "name": _pick(source, "buyer_nick", "buyer_name", "user_name") or "平台客户", "tags": "",
        }]
    if data_type == "after_sales":
        return [{
            "external_id": _pick(source, "refund_id", "aftersale_id", "after_sale_id"),
            "order_external_id": _pick(source, "tid", "order_id", "related_order_id"),
            "case_type": "refund", "status": _normalize_after_sale_status(_pick(source, "status", "aftersale_status")),
            "reason": _pick(source, "reason", "refund_reason", "comment"),
        }]
    if data_type == "shipments":
        return [{
            "external_id": _pick(source, "out_sid", "tracking_no", "logistics_id", "invoice_no"),
            "order_external_id": _pick(source, "tid", "order_id", "shop_order_id"),
            "carrier_name": _pick(source, "company_name", "logistics_company"),
            "tracking_number": _pick(source, "out_sid", "tracking_no", "invoice_no"), "status": _pick(source, "status", "logistics_status") or "unknown",
        }]
    children = source.get("orders") or source.get("order_detail_list") or source.get("product_list") or []
    if isinstance(children, dict):
        children = next((value for value in children.values() if isinstance(value, list)), [])
    order_id = _pick(source, "tid", "order_id", "shop_order_id")
    return [{
        "external_id": _pick(child, "oid", "order_detail_id", "sku_order_id", "id"), "order_external_id": order_id,
        "title": _pick(child, "title", "product_name"), "sku": _pick(child, "outer_sku_id", "sku_id", "sku"),
        "quantity": _pick(child, "num", "item_num", "quantity") or "1", "unit_price": _pick(child, "price", "order_amount") or "0",
    } for child in children if isinstance(child, dict)]


def _pick(source: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = source.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def _normalize_after_sale_status(value: str) -> str:
    lowered = value.lower()
    if any(word in lowered for word in ("success", "closed", "finish", "resolved", "完成", "关闭")):
        return "resolved"
    if any(word in lowered for word in ("wait", "audit", "review", "等待", "审核")):
        return "waiting_merchant"
    return "open"


def _load_connection(company_id: str, connection_id: str) -> dict[str, Any]:
    with SessionFactory() as session:
        row = session.execute(
            text("""
              select id::text, platform::text, access_token_encrypted from platform_connections
              where id=:id and company_id=:company_id and status='connected'
            """),
            {"id": connection_id, "company_id": company_id},
        ).mappings().one_or_none()
    if not row or not row["access_token_encrypted"]:
        raise OfficialSyncError("店铺未授权或令牌不存在。")
    return dict(row)
