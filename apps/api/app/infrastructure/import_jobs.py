from __future__ import annotations

import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from apps.api.app.infrastructure.config import get_settings
from apps.api.app.infrastructure.database import SessionFactory
from apps.api.app.infrastructure.import_file_parser import REQUIRED_FIELDS, parse_import_rows
from apps.api.app.infrastructure.platform_security import IntegrationUnavailableError


STAGING_DIRECTORY = Path(tempfile.gettempdir()) / "ai-shop-os-imports"


def ensure_import_runtime() -> None:
    if SessionFactory is None:
        raise IntegrationUnavailableError("数据库尚未连接：可以预览文件，但暂时不能正式导入。")


def create_file_import_job(
    company_id: str,
    platform: str,
    shop_name: str,
    data_type: str,
    file_name: str,
    content: bytes,
    field_mapping: dict[str, str],
    platform_connection_id: str | None,
) -> dict[str, object]:
    ensure_import_runtime()
    missing = [field for field in REQUIRED_FIELDS[data_type] if not field_mapping.get(field)]
    if missing:
        raise ValueError(f"缺少必填字段映射：{', '.join(missing)}")

    job_id = str(uuid4())
    connection_id = _ensure_connection(company_id, platform, shop_name, platform_connection_id)
    suffix = Path(file_name).suffix.lower()
    STAGING_DIRECTORY.mkdir(parents=True, exist_ok=True)
    staged_path = STAGING_DIRECTORY / f"{job_id}{suffix}"
    staged_path.write_bytes(content)
    cursor = {"staged_file_path": str(staged_path)}
    now = datetime.now(timezone.utc)
    with SessionFactory.begin() as session:
        session.execute(
            text("""
              insert into import_jobs (
                id, company_id, platform_connection_id, platform, import_mode, data_type,
                status, progress, field_mapping, cursor, file_name, file_sha256
              ) values (
                :id, :company_id, :connection_id, cast(:platform as connector_platform), 'file', :data_type,
                'queued', 0, cast(:field_mapping as jsonb), cast(:cursor as jsonb), :file_name, :file_sha256
              )
            """),
            {
                "id": job_id,
                "company_id": company_id,
                "connection_id": connection_id,
                "platform": platform,
                "data_type": data_type,
                "field_mapping": json.dumps(field_mapping, ensure_ascii=False),
                "cursor": json.dumps(cursor, ensure_ascii=False),
                "file_name": Path(file_name).name,
                "file_sha256": hashlib.sha256(content).hexdigest(),
            },
        )
    _dispatch_job(job_id, company_id)
    return _get_job(company_id, job_id) or {"id": job_id, "created_at": now.isoformat()}


def create_sync_jobs(company_id: str, platform: str, connection_id: str, data_types: list[str]) -> list[dict[str, object]]:
    ensure_import_runtime()
    with SessionFactory() as session:
        exists = session.execute(
            text("""
              select 1 from platform_connections
              where id = :connection_id and company_id = :company_id and platform::text = :platform and status = 'connected'
            """),
            {"connection_id": connection_id, "company_id": company_id, "platform": platform},
        ).scalar_one_or_none()
    if exists is None:
        raise ValueError("平台连接不存在、未授权或不属于当前公司。")

    job_ids: list[str] = []
    with SessionFactory.begin() as session:
        for data_type in data_types:
            job_id = str(uuid4())
            job_ids.append(job_id)
            session.execute(
                text("""
                  insert into import_jobs (
                    id, company_id, platform_connection_id, platform, import_mode, data_type, status, progress
                  ) values (
                    :id, :company_id, :connection_id, cast(:platform as connector_platform), 'api_sync', :data_type, 'queued', 0
                  )
                """),
                {"id": job_id, "company_id": company_id, "connection_id": connection_id, "platform": platform, "data_type": data_type},
            )
    for job_id in job_ids:
        _dispatch_job(job_id, company_id)
    return [job for job_id in job_ids if (job := _get_job(company_id, job_id))]


def list_import_jobs(company_id: str) -> list[dict[str, object]]:
    if SessionFactory is None:
        return []
    with SessionFactory() as session:
        rows = session.execute(
            text("""
              select id::text, platform::text, import_mode, data_type, status, progress,
                     total_count, success_count, failure_count, file_name, error_summary, created_at::text
              from import_jobs where company_id = :company_id order by created_at desc limit 100
            """),
            {"company_id": company_id},
        ).mappings().all()
    return [dict(row) for row in rows]


def get_import_job(company_id: str, job_id: str) -> dict[str, object] | None:
    return _get_job(company_id, job_id)


def run_import_job(job_id: str, company_id: str) -> None:
    if SessionFactory is None:
        return
    with SessionFactory.begin() as session:
        job = session.execute(
            text("select * from import_jobs where id = :id and company_id = :company_id for update"),
            {"id": job_id, "company_id": company_id},
        ).mappings().one_or_none()
        if job is None or job["status"] != "queued":
            return
        session.execute(
            text("update import_jobs set status = 'running', progress = 1, started_at = now() where id = :id"),
            {"id": job_id},
        )

    if job["import_mode"] == "api_sync":
        _run_api_job(dict(job))
        return
    _run_file_job(dict(job))


def _run_file_job(job: dict[str, object]) -> None:
    cursor = job.get("cursor") or {}
    staged_path = Path(str(cursor.get("staged_file_path", "")))
    try:
        rows = parse_import_rows(str(job["file_name"]), staged_path.read_bytes())
        success_count = 0
        failure_count = 0
        errors: list[str] = []
        with SessionFactory.begin() as session:
            for index, source_row in enumerate(rows, start=2):
                mapped = {target: source_row.get(source, "") for target, source in dict(job["field_mapping"]).items()}
                try:
                    with session.begin_nested():
                        _upsert_row(session, job, mapped)
                    success_count += 1
                except (ValueError, TypeError, SQLAlchemyError) as error:
                    failure_count += 1
                    if len(errors) < 10:
                        errors.append(f"第 {index} 行：{error}")
            status = "succeeded" if failure_count == 0 else "partial_success" if success_count else "failed"
            session.execute(
                text("""
                  update import_jobs set status = :status, progress = 100, total_count = :total,
                    success_count = :success, failure_count = :failure, error_summary = :error,
                    finished_at = now() where id = :id
                """),
                {
                    "id": job["id"], "status": status, "total": len(rows), "success": success_count,
                    "failure": failure_count, "error": "；".join(errors) or None,
                },
            )
    except Exception as error:
        _mark_failed(str(job["id"]), f"文件处理失败：{str(error)[:300]}")
    finally:
        staged_path.unlink(missing_ok=True)


def _run_api_job(job: dict[str, object]) -> None:
    try:
        from apps.api.app.infrastructure.official_platform_sync import AuthorizationExpiredError, run_official_sync

        success_count, failure_count, error_summary = run_official_sync(job)
        status = "succeeded" if failure_count == 0 else "partial_success" if success_count else "failed"
        with SessionFactory.begin() as session:
            session.execute(
                text("""
                  update import_jobs set status=:status, progress=100, total_count=:total,
                    success_count=:success, failure_count=:failure, error_summary=:error, finished_at=now()
                  where id=:id
                """),
                {"id": job["id"], "status": status, "total": success_count + failure_count,
                 "success": success_count, "failure": failure_count, "error": error_summary},
            )
    except Exception as error:
        message = str(error)[:300]
        _mark_failed(str(job["id"]), message)
        if error.__class__.__name__ == "AuthorizationExpiredError":
            with SessionFactory.begin() as session:
                session.execute(
                    text("update platform_connections set status='pending', last_error=:error where id=:id"),
                    {"id": job["platform_connection_id"], "error": message},
                )


def _upsert_row(session, job: dict[str, object], row: dict[str, str]) -> None:
    data_type = str(job["data_type"])
    external_id = row.get("external_id", "").strip()
    if not external_id:
        raise ValueError("平台编号不能为空")
    common = {
        "id": str(uuid4()), "company_id": str(job["company_id"]), "connection_id": str(job["platform_connection_id"]),
        "platform": str(job["platform"]), "external_id": external_id,
        "metadata": json.dumps({"import_job_id": str(job["id"])}, ensure_ascii=False),
    }
    if data_type == "products":
        session.execute(text("""
          insert into products (id, company_id, platform_connection_id, platform, external_id, title, sku, price, inventory_count, source_metadata)
          values (:id, :company_id, :connection_id, cast(:platform as connector_platform), :external_id, :title, :sku, :price, :inventory, cast(:metadata as jsonb))
          on conflict (company_id, platform_connection_id, external_id) where platform_connection_id is not null and external_id is not null
          do update set title=excluded.title, sku=excluded.sku, price=excluded.price, inventory_count=excluded.inventory_count,
                        source_metadata=excluded.source_metadata, updated_at=now()
        """), {**common, "title": row.get("title") or "未命名商品", "sku": row.get("sku") or None,
                 "price": _number(row.get("price"), 0), "inventory": _integer(row.get("inventory_count"), 0)})
        return
    if data_type == "customers":
        session.execute(text("""
          insert into customers (id, company_id, platform_connection_id, platform, external_id, name, tags, source_metadata)
          values (:id, :company_id, :connection_id, cast(:platform as connector_platform), :external_id, :name, :tags, cast(:metadata as jsonb))
          on conflict (company_id, platform_connection_id, external_id) where platform_connection_id is not null and external_id is not null
          do update set name=excluded.name, tags=excluded.tags, source_metadata=excluded.source_metadata, updated_at=now()
        """), {**common, "name": row.get("name") or "未知客户", "tags": [tag.strip() for tag in row.get("tags", "").split(",") if tag.strip()]})
        return
    if data_type == "orders":
        session.execute(text("""
          insert into orders (id, company_id, platform_connection_id, platform, external_id, status, total_amount, paid_at, source_metadata)
          values (:id, :company_id, :connection_id, cast(:platform as connector_platform), :external_id, :status, :amount, nullif(:paid_at, '')::timestamptz, cast(:metadata as jsonb))
          on conflict (company_id, platform_connection_id, external_id) where platform_connection_id is not null and external_id is not null
          do update set status=excluded.status, total_amount=excluded.total_amount, paid_at=excluded.paid_at,
                        source_metadata=excluded.source_metadata, updated_at=now()
        """), {**common, "status": row.get("status") or "unknown", "amount": _number(row.get("total_amount"), 0), "paid_at": row.get("paid_at", "")})
        return
    order_external_id = row.get("order_external_id", "").strip()
    order_id = session.execute(text("""
      select id::text from orders where company_id=:company_id and platform_connection_id=:connection_id and external_id=:external_id
    """), {"company_id": common["company_id"], "connection_id": common["connection_id"], "external_id": order_external_id}).scalar_one_or_none()
    if not order_id:
        raise ValueError(f"找不到关联订单 {order_external_id}")
    if data_type == "order_items":
        session.execute(text("""
          insert into order_items (id, company_id, order_id, platform_connection_id, external_id, title, sku, quantity, unit_price, source_metadata)
          values (:id, :company_id, :order_id, :connection_id, :external_id, :title, :sku, :quantity, :price, cast(:metadata as jsonb))
          on conflict (company_id, platform_connection_id, external_id) do update set title=excluded.title, sku=excluded.sku,
            quantity=excluded.quantity, unit_price=excluded.unit_price, source_metadata=excluded.source_metadata, updated_at=now()
        """), {**common, "order_id": order_id, "title": row.get("title") or "未命名商品", "sku": row.get("sku") or None,
                 "quantity": _integer(row.get("quantity"), 1), "price": _number(row.get("unit_price"), 0)})
        return
    if data_type == "shipments":
        session.execute(text("""
          insert into shipments (id, company_id, order_id, platform_connection_id, external_id, carrier_name, tracking_number, status, source_metadata)
          values (:id, :company_id, :order_id, :connection_id, :external_id, :carrier, :tracking, :status, cast(:metadata as jsonb))
          on conflict (company_id, platform_connection_id, external_id) do update set carrier_name=excluded.carrier_name,
            tracking_number=excluded.tracking_number, status=excluded.status, source_metadata=excluded.source_metadata, updated_at=now()
        """), {**common, "order_id": order_id, "carrier": row.get("carrier_name") or None,
                 "tracking": row.get("tracking_number") or None, "status": row.get("status") or "unknown"})
        return
    case_type = row.get("case_type") if row.get("case_type") in {"refund", "return", "logistics_issue", "complaint", "compensation"} else "refund"
    status = row.get("status") if row.get("status") in {"open", "waiting_merchant", "resolved"} else "open"
    session.execute(text("""
      insert into after_sale_cases (id, company_id, platform_connection_id, platform, order_id, external_id, case_type,
        status, title, description, risk_level, ai_suggestion, approval_required, source_metadata)
      values (:id, :company_id, :connection_id, cast(:platform as connector_platform), :order_id, :external_id,
        cast(:case_type as after_sale_case_type), cast(:status as after_sale_status), :title, :description, 'medium',
        '请商家审核后处理，AI 不会自动退款。', true, cast(:metadata as jsonb))
      on conflict (company_id, platform_connection_id, external_id) where platform_connection_id is not null and external_id is not null
      do update set status=excluded.status, description=excluded.description, source_metadata=excluded.source_metadata, updated_at=now()
    """), {**common, "order_id": order_id, "case_type": case_type, "status": status,
             "title": f"平台售后单 {external_id}", "description": row.get("reason") or "平台导入的售后任务"})


def _ensure_connection(company_id: str, platform: str, shop_name: str, connection_id: str | None) -> str:
    with SessionFactory.begin() as session:
        if connection_id:
            found = session.execute(text("select id::text from platform_connections where id=:id and company_id=:company_id"),
                                    {"id": connection_id, "company_id": company_id}).scalar_one_or_none()
            if not found:
                raise ValueError("所选店铺不属于当前公司。")
            return str(found)
        found = session.execute(text("""
          select id::text from platform_connections where company_id=:company_id and platform::text=:platform and shop_identifier=:shop
        """), {"company_id": company_id, "platform": platform, "shop": shop_name}).scalar_one_or_none()
        if found:
            return str(found)
        new_id = str(uuid4())
        session.execute(text("""
          insert into platform_connections (id, company_id, platform, status, shop_identifier, scopes, authorization_mode)
          values (:id, :company_id, cast(:platform as connector_platform), 'connected', :shop, '{}', 'file')
        """), {"id": new_id, "company_id": company_id, "platform": platform, "shop": shop_name})
        return new_id


def _enqueue(job_id: str, company_id: str) -> None:
    from redis import Redis
    from rq import Queue
    from rq.serializers import JSONSerializer

    connection = Redis.from_url(get_settings().redis_url)
    Queue("commerce-imports", connection=connection, serializer=JSONSerializer).enqueue(
        "apps.api.app.infrastructure.import_jobs.run_import_job", job_id, company_id,
        job_timeout="30m", result_ttl=86400, failure_ttl=604800,
    )


def _dispatch_job(job_id: str, company_id: str) -> None:
    settings = get_settings()
    if settings.redis_url:
        try:
            _enqueue(job_id, company_id)
            return
        except Exception:
            # 真实商家试用阶段不能因为队列未启动而卡死导入；队列失败时退回同步处理。
            pass
    run_import_job(job_id, company_id)


def _get_job(company_id: str, job_id: str) -> dict[str, object] | None:
    if SessionFactory is None:
        return None
    with SessionFactory() as session:
        row = session.execute(text("""
          select id::text, platform::text, import_mode, data_type, status, progress, total_count,
                 success_count, failure_count, file_name, error_summary, created_at::text
          from import_jobs where company_id=:company_id and id=:id
        """), {"company_id": company_id, "id": job_id}).mappings().one_or_none()
    return dict(row) if row else None


def _mark_failed(job_id: str, message: str) -> None:
    with SessionFactory.begin() as session:
        session.execute(text("""
          update import_jobs set status='failed', progress=100, error_summary=:message, finished_at=now() where id=:id
        """), {"id": job_id, "message": message[:500]})


def _number(value: str | None, default: float) -> float:
    if value is None or not value.strip():
        return default
    cleaned = value.replace(",", "").replace("¥", "").replace("￥", "").strip()
    number = float(cleaned)
    if number < 0:
        raise ValueError("金额不能为负数")
    return number


def _integer(value: str | None, default: int) -> int:
    if value is None or not value.strip():
        return default
    number = int(float(value.strip()))
    if number < 0:
        raise ValueError("数量不能为负数")
    return number
