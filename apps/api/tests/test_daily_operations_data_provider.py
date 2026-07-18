from apps.api.app.infrastructure.daily_operations_data_provider import load_daily_operations_source_data


class _FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def mappings(self):
        return self

    def all(self):
        return list(self._rows)

    def one(self):
        return self._rows[0]


class _FakeSession:
    def __init__(self, products, orders, after_sales):
        self.products = products
        self.orders = orders
        self.after_sales = after_sales

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, statement, params=None):
        query = str(statement)
        if "from products" in query:
            return _FakeResult(self.products)
        if "from orders" in query:
            return _FakeResult([self.orders])
        if "from after_sale_cases" in query:
            return _FakeResult([self.after_sales])
        raise AssertionError(f"unexpected query: {query}")


def test_daily_operations_source_builds_real_workflow_payloads_from_database_rows() -> None:
    session = _FakeSession(
        products=({"title": "真实主推商品", "price": 199, "inventory_count": 80},),
        orders={"order_count": 12, "sales_amount": 2388},
        after_sales={"after_sale_count": 3, "refund_count": 2, "complaint_count": 1},
    )

    source = load_daily_operations_source_data(lambda: session, "company-1")

    assert source.source_mode == "database"
    assert source.product_count == 1
    assert source.order_count == 12
    assert source.after_sale_count == 3
    assert source.pre_live is not None
    assert source.pre_live["products"][0]["title"] == "真实主推商品"
    assert source.pre_live["products"][0]["live_price"] == 179.1
    assert source.post_live is not None
    assert source.post_live["sales_amount_yuan"] == 2388
    assert source.post_live["refund_count"] == 2
    assert source.post_live["negative_comment_count"] == 1


def test_daily_operations_source_marks_empty_database_without_fake_payload() -> None:
    session = _FakeSession(
        products=(),
        orders={"order_count": 0, "sales_amount": 0},
        after_sales={"after_sale_count": 0, "refund_count": 0, "complaint_count": 0},
    )

    source = load_daily_operations_source_data(lambda: session, "company-1")

    assert source.source_mode == "empty"
    assert source.pre_live is None
    assert source.post_live is None
    assert source.warnings


def test_daily_operations_source_reads_latest_live_metric_snapshot() -> None:
    from datetime import datetime, timezone

    from apps.api.app.infrastructure.live_metric_snapshots import (
        InMemoryLiveMetricSnapshotRepository,
        configure_live_metric_snapshot_repository,
        record_live_metric_snapshot,
    )

    configure_live_metric_snapshot_repository(InMemoryLiveMetricSnapshotRepository())
    record_live_metric_snapshot(
        "company-1",
        {
            "platform": "taobao",
            "stream_external_id": "taobao-live-1",
            "observed_at": datetime(2026, 7, 18, 8, 0, tzinfo=timezone.utc),
            "online_users": 560,
            "conversion_rate": 0.1,
            "retention_rate": 0.4,
            "comment_count": 20,
            "like_count": 200,
            "product_click_rate": 0.15,
            "inventory_delta": -8,
            "abnormal_order_count": 1,
            "source_reference": "taobao-live-api",
        },
    )
    session = _FakeSession(
        products=({"title": "真实主推商品", "price": 199, "inventory_count": 80},),
        orders={"order_count": 12, "sales_amount": 2388},
        after_sales={"after_sale_count": 3, "refund_count": 2, "complaint_count": 1},
    )

    source = load_daily_operations_source_data(lambda: session, "company-1")

    assert source.live_metrics is not None
    assert source.live_metrics["online_users"] == 560
    assert source.live_metrics["abnormal_order_count"] == 1