from apps.api.app.infrastructure import production_bootstrap


def test_production_bootstrap_reports_database_blocker_when_no_session(monkeypatch) -> None:
    monkeypatch.setattr(production_bootstrap, "SessionFactory", None)

    result = production_bootstrap.run_production_bootstrap(apply_changes=False)

    assert result.status == "blocked"
    assert result.database is False
    assert result.seeded_agents == 0
    assert "DATABASE_URL" in result.next_actions[0]


def test_production_bootstrap_uses_merchant_company_id(monkeypatch) -> None:
    settings = production_bootstrap.get_settings()
    monkeypatch.setattr(production_bootstrap, "SessionFactory", None)
    monkeypatch.setattr(settings, "merchant_bridge_company_id", "11111111-1111-1111-1111-111111111111")

    result = production_bootstrap.run_production_bootstrap(apply_changes=False)

    assert result.company_id == "11111111-1111-1111-1111-111111111111"


def test_production_bootstrap_reports_evidence_chain_blockers_when_no_session(monkeypatch) -> None:
    monkeypatch.setattr(production_bootstrap, "SessionFactory", None)

    result = production_bootstrap.run_production_bootstrap(apply_changes=False)

    assert result.evidence_chain_ready is False
    assert any("DATABASE_URL" in item for item in result.evidence_chain_blockers)
    assert any("LIVE_WORKFLOW_LOG_STORAGE=postgres" in item for item in result.evidence_chain_blockers)
    assert any("WAREHOUSE_NOTIFICATION_DELIVERY_MODE=http_api" in item for item in result.evidence_chain_blockers)


def test_evidence_chain_readiness_passes_only_with_postgres_and_wms_credentials(monkeypatch) -> None:
    settings = production_bootstrap.get_settings()
    monkeypatch.setattr(settings, "live_workflow_log_storage", "postgres")
    monkeypatch.setattr(settings, "approval_record_storage", "postgres")
    monkeypatch.setattr(settings, "after_sale_decision_storage", "postgres")
    monkeypatch.setattr(settings, "ceo_report_snapshot_storage", "postgres")
    monkeypatch.setattr(settings, "warehouse_notification_delivery_mode", "http_api")
    monkeypatch.setattr(settings, "warehouse_notification_wms_api_url", "https://wms.example.test/notices")
    monkeypatch.setattr(settings, "warehouse_notification_wms_api_key", "secret")

    ready, blockers = production_bootstrap.assess_evidence_chain_readiness(database_ready=True)

    assert ready is True
    assert blockers == ()


def test_evidence_chain_readiness_reports_missing_evidence_tables(monkeypatch) -> None:
    settings = production_bootstrap.get_settings()
    monkeypatch.setattr(settings, "live_workflow_log_storage", "postgres")
    monkeypatch.setattr(settings, "approval_record_storage", "postgres")
    monkeypatch.setattr(settings, "after_sale_decision_storage", "postgres")
    monkeypatch.setattr(settings, "ceo_report_snapshot_storage", "postgres")
    monkeypatch.setattr(settings, "warehouse_notification_delivery_mode", "http_api")
    monkeypatch.setattr(settings, "warehouse_notification_wms_api_url", "https://wms.example.test/notices")
    monkeypatch.setattr(settings, "warehouse_notification_wms_api_key", "secret")

    ready, blockers = production_bootstrap.assess_evidence_chain_readiness(
        database_ready=True,
        missing_evidence_tables=("warehouse_notifications",),
    )

    assert ready is False
    assert "Missing evidence table: warehouse_notifications." in blockers