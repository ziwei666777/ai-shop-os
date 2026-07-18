from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from apps.api.app.infrastructure.after_sale_decision_workflow import configure_after_sale_decision_outcome_repository_from_settings
from apps.api.app.infrastructure.config import get_settings
from apps.api.app.infrastructure.database import SessionFactory
from apps.api.app.infrastructure.approval_records import configure_approval_record_repository_from_settings
from apps.api.app.infrastructure.ceo_report_snapshot_store import configure_ceo_daily_report_snapshot_repository_from_settings
from apps.api.app.infrastructure.live_workflow_log_store import configure_live_workflow_repository_from_settings
from apps.api.app.infrastructure.live_metric_snapshots import configure_live_metric_snapshot_repository_from_settings
from apps.api.app.infrastructure.production_bootstrap import assess_evidence_chain_readiness, find_missing_evidence_tables
from apps.api.app.interfaces.http.routes import router
from apps.api.app.interfaces.http.commerce_routes import router as commerce_router


def create_app() -> FastAPI:
    """Create the FastAPI app and configure runtime repositories."""
    settings = get_settings()
    if SessionFactory is not None:
        configure_live_workflow_repository_from_settings(lambda: SessionFactory())
        configure_approval_record_repository_from_settings(lambda: SessionFactory())
        configure_after_sale_decision_outcome_repository_from_settings(lambda: SessionFactory())
        configure_ceo_daily_report_snapshot_repository_from_settings(lambda: SessionFactory())
        configure_live_metric_snapshot_repository_from_settings(lambda: SessionFactory())
    else:
        configure_live_workflow_repository_from_settings()
        configure_approval_record_repository_from_settings()
        configure_after_sale_decision_outcome_repository_from_settings()
        configure_ceo_daily_report_snapshot_repository_from_settings()
        configure_live_metric_snapshot_repository_from_settings()
    app = FastAPI(title="AI Shop OS API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    app.include_router(commerce_router)
    return app


app = create_app()


@app.get("/health/ready")
async def readiness() -> dict[str, object]:
    """Production readiness check for database and merchant bridge configuration."""
    settings = get_settings()
    database_ok = False
    missing_evidence_tables: tuple[str, ...] = ()
    if SessionFactory is not None:
        try:
            with SessionFactory() as session:
                session.execute(text("select 1")).scalar_one()
                missing_evidence_tables = find_missing_evidence_tables(session)
            database_ok = True
        except Exception:
            database_ok = False
    evidence_ready, evidence_blockers = assess_evidence_chain_readiness(database_ok, missing_evidence_tables)
    ready = database_ok and bool(settings.merchant_bridge_api_key) and evidence_ready
    return {
        "status": "ready" if ready else "blocked",
        "database": database_ok,
        "bridge_key": bool(settings.merchant_bridge_api_key),
        "supabase_url": bool(settings.supabase_url),
        "auth_required": settings.auth_required,
        "evidence_chain_ready": evidence_ready,
        "evidence_chain_blockers": evidence_blockers,
    }
