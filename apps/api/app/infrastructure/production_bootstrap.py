from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from apps.api.app.infrastructure.config import get_settings
from apps.api.app.infrastructure.database import SessionFactory


EVIDENCE_CHAIN_TABLES = (
    "live_workflow_runs",
    "approval_records",
    "after_sale_decision_outcomes",
    "warehouse_notifications",
    "ceo_daily_report_snapshots",
    "live_metric_snapshots",
)

REQUIRED_TABLES = (
    "companies",
    "agents",
    "agent_prompts",
    "agent_kpis",
    "customers",
    "products",
    "orders",
    "conversations",
    "messages",
    "platform_connections",
    "after_sale_cases",
    "learning_events",
    "agent_feedback_metrics",
    "order_items",
    "shipments",
    "import_jobs",
)

REQUIRED_COLUMNS = {
    "platform_connections": ("authorization_mode", "token_expires_at", "last_synced_at", "last_error"),
    "messages": ("platform", "platform_message_id", "intent", "automation_decision", "ai_draft_content"),
    "customers": ("platform", "platform_connection_id", "source_metadata"),
    "orders": ("platform", "platform_connection_id", "source_metadata"),
    "products": ("platform", "platform_connection_id", "source_metadata"),
    "after_sale_cases": ("external_id", "platform_connection_id", "source_metadata"),
}

DEFAULT_AGENTS = (
    {
        "slug": "ai-boss",
        "name": "AI老板",
        "type": "boss",
        "status": "online",
        "description": "每天汇总经营状况、风险、节省金额和需要老板审批的事项。",
        "prompt": "你是电商老板助手。只汇报真实数据、风险和下一步建议，不编造订单、利润或平台结果。",
        "kpi_name": "老板每日打开率",
        "kpi_value": 0,
    },
    {
        "slug": "ai-customer",
        "name": "AI客服",
        "type": "customer",
        "status": "online",
        "description": "处理售前咨询、订单问题、物流问题和低风险FAQ，高风险问题必须交给人工。",
        "prompt": "你是电商客服。只能根据商品、订单、物流和知识库回答；退款、赔偿、投诉、差评必须请求老板确认。",
        "kpi_name": "低风险自动处理率",
        "kpi_value": 0,
    },
    {
        "slug": "ai-after-sale",
        "name": "AI售后",
        "type": "after_sale",
        "status": "online",
        "description": "识别退款、退货、物流异常、投诉和赔偿风险，给出处理建议并等待审批。",
        "prompt": "你是电商售后。先判断风险，再给老板建议；任何涉及退款、赔偿、投诉的话术不得自动执行。",
        "kpi_name": "售后分类准确率",
        "kpi_value": 0,
    },
    {
        "slug": "ai-operator",
        "name": "AI运营",
        "type": "operator",
        "status": "paused",
        "description": "分析商品、订单、客户和导入数据，生成私域获客、投流和商品优化建议。",
        "prompt": "你是电商运营。基于真实经营数据输出建议；预算、价格、广告投放动作必须进入老板审批。",
        "kpi_name": "运营建议采纳率",
        "kpi_value": 0,
    },
)


@dataclass(frozen=True)
class ProductionBootstrapResult:
    status: str
    database: bool
    company_id: str
    missing_tables: tuple[str, ...]
    missing_columns: tuple[str, ...]
    seeded_agents: int
    bridge_connection_ready: bool
    evidence_chain_ready: bool
    evidence_chain_blockers: tuple[str, ...]
    next_actions: tuple[str, ...]

def find_missing_evidence_tables(session: Any) -> tuple[str, ...]:
    """Return evidence tables that are not present in the connected database."""
    return tuple(_find_missing_named_tables(session, EVIDENCE_CHAIN_TABLES))


def assess_evidence_chain_readiness(
    database_ready: bool,
    missing_evidence_tables: tuple[str, ...] = (),
) -> tuple[bool, tuple[str, ...]]:
    settings = get_settings()
    blockers: list[str] = []
    if not database_ready:
        blockers.append("DATABASE_URL must connect before real workflow evidence can be trusted.")
    for table in missing_evidence_tables:
        blockers.append(f"Missing evidence table: {table}.")
    required_storage = {
        "LIVE_WORKFLOW_LOG_STORAGE": settings.live_workflow_log_storage,
        "APPROVAL_RECORD_STORAGE": settings.approval_record_storage,
        "AFTER_SALE_DECISION_STORAGE": settings.after_sale_decision_storage,
        "CEO_REPORT_SNAPSHOT_STORAGE": settings.ceo_report_snapshot_storage,
        "LIVE_METRIC_SNAPSHOT_STORAGE": settings.live_metric_snapshot_storage,
    }
    for name, value in required_storage.items():
        if value != "postgres":
            blockers.append(f"{name}=postgres is required for production evidence chain; current={value}.")
    if settings.warehouse_notification_delivery_mode != "http_api":
        blockers.append(
            "WAREHOUSE_NOTIFICATION_DELIVERY_MODE=http_api is required before warehouse notices can reach WMS/ERP."
        )
    if not settings.warehouse_notification_wms_api_url:
        blockers.append("WAREHOUSE_NOTIFICATION_WMS_API_URL is required for real warehouse delivery.")
    if not settings.warehouse_notification_wms_api_key:
        blockers.append("WAREHOUSE_NOTIFICATION_WMS_API_KEY is required for authenticated warehouse delivery.")
    return not blockers, tuple(blockers)

def run_production_bootstrap(apply_changes: bool = True) -> ProductionBootstrapResult:
    """生产开机工具：只做幂等初始化，不修改表结构，不输出任何密钥。"""
    settings = get_settings()
    company_id = settings.merchant_bridge_company_id or settings.local_company_id

    if SessionFactory is None:
        return ProductionBootstrapResult(
            status="blocked",
            database=False,
            company_id=company_id,
            missing_tables=(),
            missing_columns=(),
            seeded_agents=0,
            bridge_connection_ready=bool(settings.merchant_bridge_api_key),
            evidence_chain_ready=assess_evidence_chain_readiness(False)[0],
            evidence_chain_blockers=assess_evidence_chain_readiness(False)[1],
            next_actions=(
                "把 Supabase PostgreSQL 的真实 DATABASE_URL 写入后端环境变量。",
                "确认 apps/api/.env 或云平台环境变量中的 DATABASE_URL 不再包含 YOUR_DATABASE_PASSWORD。",
                "数据库连接好以后重新运行 npm run api:bootstrap。",
            ),
        )

    try:
        with SessionFactory.begin() as session:
            session.execute(text("select 1")).scalar_one()
            missing_tables = _find_missing_tables(session)
            missing_columns = _find_missing_columns(session)
            missing_evidence_tables = find_missing_evidence_tables(session)
            evidence_ready, evidence_blockers = assess_evidence_chain_readiness(True, tuple(missing_evidence_tables))
            if missing_tables or missing_columns:
                return ProductionBootstrapResult(
                    status="blocked",
                    database=True,
                    company_id=company_id,
                    missing_tables=tuple(missing_tables),
                    missing_columns=tuple(missing_columns),
                    seeded_agents=0,
                    bridge_connection_ready=bool(settings.merchant_bridge_api_key),
                    evidence_chain_ready=evidence_ready,
                    evidence_chain_blockers=evidence_blockers,
                    next_actions=(
                        "先在 Supabase SQL Editor 执行 supabase/migrations 下的三份 migration。",
                        "确认 202607090001、202607090002、202607110001 都执行成功。",
                        "执行完成后重新运行 npm run api:bootstrap。",
                    ),
                )

            seeded_agents = 0
            bridge_ready = bool(settings.merchant_bridge_api_key)
            if apply_changes:
                _ensure_company(session, company_id)
                seeded_agents = _ensure_default_agents(session, company_id)
                bridge_ready = _ensure_message_bridge(session, company_id) and bridge_ready
                _ensure_daily_snapshot(session, company_id)

            production_ready = bridge_ready and evidence_ready
            return ProductionBootstrapResult(
                status="ready" if production_ready else "blocked",
                database=True,
                company_id=company_id,
                missing_tables=(),
                missing_columns=(),
                seeded_agents=seeded_agents,
                bridge_connection_ready=bridge_ready,
                evidence_chain_ready=evidence_ready,
                evidence_chain_blockers=evidence_blockers,
                next_actions=() if production_ready else _production_next_actions(bridge_ready, evidence_blockers),
            )
    except SQLAlchemyError:
        return ProductionBootstrapResult(
            status="blocked",
            database=False,
            company_id=company_id,
            missing_tables=(),
            missing_columns=(),
            seeded_agents=0,
            bridge_connection_ready=bool(settings.merchant_bridge_api_key),
            evidence_chain_ready=assess_evidence_chain_readiness(False)[0],
            evidence_chain_blockers=assess_evidence_chain_readiness(False)[1],
            next_actions=(
                "数据库可以配置但连接失败，请检查 Supabase 数据库密码、项目地址、SSL 和网络访问。",
                "不要把 service_role 或数据库密码发到聊天里，只写入本机或云平台环境变量。",
            ),
        )

def _production_next_actions(bridge_ready: bool, evidence_blockers: tuple[str, ...]) -> tuple[str, ...]:
    actions: list[str] = []
    if not bridge_ready:
        actions.extend(
            (
                "生成一条高强度 MERCHANT_BRIDGE_API_KEY，并写入后端云平台环境变量。",
                "把同一条桥接密钥填到商家控制台的系统设置里。",
                "重新部署后端后访问 /health/ready，确认 bridge_key=true。",
            )
        )
    actions.extend(evidence_blockers)
    return tuple(actions)

def _find_missing_tables(session: Any) -> list[str]:
    return _find_missing_named_tables(session, REQUIRED_TABLES)


def _find_missing_named_tables(session: Any, table_names: tuple[str, ...]) -> list[str]:
    rows = session.execute(
        text(
            """
            select table_name
            from information_schema.tables
            where table_schema = 'public'
              and table_name = any(:table_names)
            """
        ),
        {"table_names": list(table_names)},
    ).scalars()
    existing = set(rows)
    return [table for table in table_names if table not in existing]


def _find_missing_columns(session: Any) -> list[str]:
    missing: list[str] = []
    for table_name, columns in REQUIRED_COLUMNS.items():
        rows = session.execute(
            text(
                """
                select column_name
                from information_schema.columns
                where table_schema = 'public'
                  and table_name = :table_name
                  and column_name = any(:column_names)
                """
            ),
            {"table_name": table_name, "column_names": list(columns)},
        ).scalars()
        existing = set(rows)
        missing.extend(f"{table_name}.{column}" for column in columns if column not in existing)
    return missing


def _ensure_company(session: Any, company_id: str) -> None:
    session.execute(
        text(
            """
            insert into companies (id, name)
            values (:company_id, 'AI Commerce OS 试用商家')
            on conflict (id) do update set
              name = excluded.name,
              updated_at = now()
            """
        ),
        {"company_id": company_id},
    )


def _ensure_default_agents(session: Any, company_id: str) -> int:
    seeded_count = 0
    for agent in DEFAULT_AGENTS:
        agent_id = session.execute(
            text(
                """
                insert into agents (id, company_id, slug, name, type, status, description)
                values (:id, :company_id, :slug, :name, cast(:type as agent_type), cast(:status as agent_status), :description)
                on conflict (company_id, slug) do update set
                  name = excluded.name,
                  type = excluded.type,
                  status = excluded.status,
                  description = excluded.description,
                  updated_at = now()
                returning id::text
                """
            ),
            {
                "id": str(uuid4()),
                "company_id": company_id,
                "slug": agent["slug"],
                "name": agent["name"],
                "type": agent["type"],
                "status": agent["status"],
                "description": agent["description"],
            },
        ).scalar_one()
        _ensure_active_prompt(session, company_id, agent_id, str(agent["prompt"]))
        _ensure_kpi(session, company_id, agent_id, str(agent["kpi_name"]), float(agent["kpi_value"]))
        seeded_count += 1
    return seeded_count


def _ensure_active_prompt(session: Any, company_id: str, agent_id: str, content: str) -> None:
    existing_prompt_id = session.execute(
        text(
            """
            select id::text
            from agent_prompts
            where company_id=:company_id and agent_id=:agent_id and is_active=true
            limit 1
            """
        ),
        {"company_id": company_id, "agent_id": agent_id},
    ).scalar_one_or_none()
    if existing_prompt_id:
        session.execute(
            text("update agent_prompts set content=:content, updated_at=now() where id=:id"),
            {"id": existing_prompt_id, "content": content},
        )
        return
    session.execute(
        text(
            """
            insert into agent_prompts (id, company_id, agent_id, version, content, is_active)
            values (:id, :company_id, :agent_id, 1, :content, true)
            """
        ),
        {"id": str(uuid4()), "company_id": company_id, "agent_id": agent_id, "content": content},
    )


def _ensure_kpi(session: Any, company_id: str, agent_id: str, metric_name: str, metric_value: float) -> None:
    existing_kpi_id = session.execute(
        text(
            """
            select id::text
            from agent_kpis
            where company_id=:company_id and agent_id=:agent_id and metric_name=:metric_name
            limit 1
            """
        ),
        {"company_id": company_id, "agent_id": agent_id, "metric_name": metric_name},
    ).scalar_one_or_none()
    if existing_kpi_id:
        session.execute(
            text("update agent_kpis set metric_value=:metric_value, measured_at=now(), updated_at=now() where id=:id"),
            {"id": existing_kpi_id, "metric_value": metric_value},
        )
        return
    session.execute(
        text(
            """
            insert into agent_kpis (id, company_id, agent_id, metric_name, metric_value)
            values (:id, :company_id, :agent_id, :metric_name, :metric_value)
            """
        ),
        {
            "id": str(uuid4()),
            "company_id": company_id,
            "agent_id": agent_id,
            "metric_name": metric_name,
            "metric_value": metric_value,
        },
    )


def _ensure_message_bridge(session: Any, company_id: str) -> bool:
    # 这是给真实店铺消息桥接用的虚拟连接，不保存平台令牌，避免把商家密钥暴露给前端。
    for platform in ("taobao", "douyin", "xianyu"):
        session.execute(
            text(
                """
                insert into platform_connections (id, company_id, platform, status, shop_identifier, scopes, authorization_mode, connected_at)
                values (:id, :company_id, cast(:platform as connector_platform), 'connected',
                        'external-message-bridge', array['message_ingest'], 'external_bridge', now())
                on conflict (company_id, platform, shop_identifier) do update set
                  status = 'connected',
                  scopes = array['message_ingest'],
                  authorization_mode = 'external_bridge',
                  connected_at = coalesce(platform_connections.connected_at, now()),
                  updated_at = now()
                """
            ),
            {"id": str(uuid4()), "company_id": company_id, "platform": platform},
        )
    return True


def _ensure_daily_snapshot(session: Any, company_id: str) -> None:
    session.execute(
        text(
            """
            insert into daily_business_snapshots (
              id, company_id, snapshot_date, sales_amount, profit_amount, order_count,
              refund_count, pending_approval_count, inventory_risk_count, ad_spend
            )
            values (:id, :company_id, current_date, 0, 0, 0, 0, 0, 0, 0)
            on conflict (company_id, snapshot_date) do nothing
            """
        ),
        {"id": str(uuid4()), "company_id": company_id},
    )


def main() -> None:
    result = run_production_bootstrap()
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
