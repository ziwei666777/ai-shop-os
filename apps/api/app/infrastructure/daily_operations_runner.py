from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from apps.api.app.domain.daily_operations import DailyOperationsRun, DailyOperationTrigger
from apps.api.app.infrastructure.ceo_report_engine import get_ceo_daily_report
from apps.api.app.infrastructure.ceo_report_snapshot_store import record_ceo_daily_report_snapshot
from apps.api.app.infrastructure.live_operation_engine import get_savings_summary
from apps.api.app.infrastructure.live_operation_workflows import run_live_metric_scan, run_post_live_review, run_pre_live_check
from apps.api.app.infrastructure.live_workflow_log_store import (
    list_live_workflow_runs,
    record_live_workflow_report,
    record_post_live_review,
)


# 每日主动工作编排器：未来可以被定时任务、平台 Webhook 或老板手动按钮调用。
def run_daily_operations(
    *,
    trigger: DailyOperationTrigger = "manual",
    pre_live: dict | None = None,
    live_metrics: dict | None = None,
    post_live: dict | None = None,
) -> DailyOperationsRun:
    before_ids = {run.id for run in list_live_workflow_runs(limit=500)}
    input_mode = "merchant_payload" if any((pre_live, live_metrics, post_live)) else "safe_baseline"

    pre_live_data = pre_live or _baseline_pre_live_payload()
    pre_report = run_pre_live_check(
        products=tuple(pre_live_data["products"]),
        coupons=tuple(pre_live_data.get("coupons", ())),
        script_text=str(pre_live_data.get("script_text", "")),
        gift_ready=bool(pre_live_data.get("gift_ready", False)),
        product_order_ready=bool(pre_live_data.get("product_order_ready", False)),
    )
    record_live_workflow_report("每日开播前自动巡检", pre_report, input_snapshot=pre_live_data)

    if live_metrics is not None:
        live_report = run_live_metric_scan(
            online_users=int(live_metrics["online_users"]),
            conversion_rate=float(live_metrics["conversion_rate"]),
            retention_rate=float(live_metrics["retention_rate"]),
            comment_count=int(live_metrics["comment_count"]),
            like_count=int(live_metrics["like_count"]),
            product_click_rate=float(live_metrics["product_click_rate"]),
            inventory_delta=int(live_metrics["inventory_delta"]),
            abnormal_order_count=int(live_metrics["abnormal_order_count"]),
        )
        record_live_workflow_report("每日直播中自动扫描", live_report, input_snapshot=live_metrics)

    if post_live is not None:
        post_report = run_post_live_review(
            sales_amount_yuan=float(post_live["sales_amount_yuan"]),
            order_count=int(post_live["order_count"]),
            viewer_count=int(post_live["viewer_count"]),
            refund_count=int(post_live["refund_count"]),
            top_product_title=str(post_live["top_product_title"]),
            negative_comment_count=int(post_live["negative_comment_count"]),
            host_script_score=int(post_live["host_script_score"]),
        )
        record_post_live_review("每日下播后自动复盘", post_report, input_snapshot=post_live)

    runs = tuple(run for run in list_live_workflow_runs(limit=50) if run.id not in before_ids)
    savings = get_savings_summary()
    ceo_report = get_ceo_daily_report()
    record_ceo_daily_report_snapshot(ceo_report)
    saved_minutes = sum(run.saved_minutes for run in runs)
    saved_yuan = sum(run.estimated_saving_yuan for run in runs)
    status = "completed" if input_mode == "merchant_payload" else "needs_real_data"

    return DailyOperationsRun(
        id=f"daily-ops-{uuid4()}",
        date=datetime.now(timezone.utc).date().isoformat(),
        trigger=trigger,
        input_mode=input_mode,  # type: ignore[arg-type]
        status=status,  # type: ignore[arg-type]
        replacement_role="直播运营助理",
        operator_message=_operator_message(input_mode, len(runs), saved_minutes, saved_yuan),
        completed_work_count=len(runs),
        saved_minutes=saved_minutes,
        saved_yuan=saved_yuan,
        workflow_runs=runs,
        ceo_report=ceo_report,
        savings_summary=savings,
        next_run_hint="接入真实抖店/淘宝直播数据后，可由定时任务每天自动调用本接口。",
    )


def _baseline_pre_live_payload() -> dict:
    return {
        "products": (
            {
                "title": "待接入真实店铺的主推商品",
                "inventory_count": 30,
                "safe_stock": 20,
                "regular_price": 129,
                "live_price": 99,
            },
        ),
        "coupons": (
            {"name": "待确认直播间优惠券", "remaining_count": 50, "expired": False},
        ),
        "script_text": "今晚福利讲清楚，不承诺绝对效果，不使用极限词。",
        "gift_ready": False,
        "product_order_ready": False,
    }


def _operator_message(input_mode: str, count: int, minutes: int, yuan: int) -> str:
    if input_mode == "merchant_payload":
        return f"AI 已按商家数据完成 {count} 项每日运营工作，节省约 {minutes} 分钟，折合约 {yuan} 元。"
    return (
        f"AI 已完成 {count} 项安全基线巡检，节省约 {minutes} 分钟，折合约 {yuan} 元；"
        "当前还不是店铺真实数据结论，请尽快接入平台数据。"
    )
