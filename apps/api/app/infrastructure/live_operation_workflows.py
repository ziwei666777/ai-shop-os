from __future__ import annotations

from collections.abc import Sequence

from apps.api.app.domain.live_operations import (
    LiveOperationAlert,
    LiveOperationCheckItem,
    LivePostReviewReport,
    LiveWorkflowReport,
)
from apps.api.app.infrastructure.live_operation_engine import HOURLY_LABOR_COST_YUAN


PROHIBITED_WORDS = ("最便宜", "全网第一", "永久有效", "绝对有效", "包治", "稳赚", "国家级")


def run_pre_live_check(
    products: Sequence[dict[str, object]],
    coupons: Sequence[dict[str, object]],
    script_text: str,
    gift_ready: bool,
    product_order_ready: bool,
) -> LiveWorkflowReport:
    """开播前检查工作流：替代直播运营助理逐项翻商品、券、脚本和赠品。"""
    checks: list[LiveOperationCheckItem] = []
    alerts: list[LiveOperationAlert] = []

    low_stock_products = [
        product for product in products if int(product.get("inventory_count", 0) or 0) <= int(product.get("safe_stock", 20) or 20)
    ]
    checks.append(
        _check(
            "pre-inventory",
            "库存安全检查",
            "warning" if low_stock_products else "done",
            25,
            "发现低库存主推款，避免直播中卖断货。",
            requires_approval=False,
        )
    )
    if low_stock_products:
        title = str(low_stock_products[0].get("title") or "未知商品")
        alerts.append(
            LiveOperationAlert(
                id="pre-alert-low-stock",
                priority="high",
                title="主推商品库存不足",
                trigger=f"{title} 库存低于安全线。",
                suggested_action="开播前调整商品排序，低库存商品不要作为第一主推。",
                expected_impact="减少缺货退款和主播空讲时间。",
            )
        )

    invalid_coupons = [coupon for coupon in coupons if int(coupon.get("remaining_count", 0) or 0) <= 0 or bool(coupon.get("expired", False))]
    checks.append(
        _check(
            "pre-coupon",
            "优惠券有效性检查",
            "blocked" if invalid_coupons else "done",
            18,
            "提前发现优惠券过期或库存为 0，避免直播间承诺无法兑现。",
            requires_approval=bool(invalid_coupons),
        )
    )
    if invalid_coupons:
        alerts.append(
            LiveOperationAlert(
                id="pre-alert-coupon",
                priority="high",
                title="优惠券不可用",
                trigger="存在已过期或剩余数量为 0 的优惠券。",
                suggested_action="开播前更换优惠券，或删除脚本中的对应福利口播。",
                expected_impact="减少客诉、退款和主播临场解释成本。",
            )
        )

    price_conflicts = [
        product
        for product in products
        if float(product.get("live_price", 0) or 0) > 0
        and float(product.get("regular_price", 0) or 0) > 0
        and float(product.get("live_price", 0) or 0) > float(product.get("regular_price", 0) or 0)
    ]
    checks.append(
        _check(
            "pre-price",
            "直播价检查",
            "warning" if price_conflicts else "done",
            15,
            "检查直播价是否高于日常价，避免价格解释和差评。",
            requires_approval=bool(price_conflicts),
        )
    )

    prohibited_hits = tuple(word for word in PROHIBITED_WORDS if word in script_text)
    checks.append(
        _check(
            "pre-script",
            "脚本违禁词检查",
            "blocked" if prohibited_hits else "done",
            35,
            "提前检查主播口播风险，减少平台违规。",
            requires_approval=bool(prohibited_hits),
        )
    )
    if prohibited_hits:
        alerts.append(
            LiveOperationAlert(
                id="pre-alert-script",
                priority="high",
                title="直播脚本存在高风险词",
                trigger=f"命中：{'、'.join(prohibited_hits)}。",
                suggested_action="开播前替换为更稳妥的表述，再交给主播使用。",
                expected_impact="减少违规扣分和直播中断风险。",
            )
        )

    checks.append(
        _check(
            "pre-gift",
            "赠品准备检查",
            "done" if gift_ready else "warning",
            10,
            "确认赠品库存和发放规则，避免售后争议。",
            requires_approval=not gift_ready,
        )
    )
    checks.append(
        _check(
            "pre-product-order",
            "商品排序检查",
            "done" if product_order_ready else "warning",
            12,
            "确认直播间商品排序与脚本一致，减少主播临场找品。",
            requires_approval=False,
        )
    )
    return _workflow_report("pre_live", checks, alerts, _pre_live_next_actions(checks, alerts))


def run_live_metric_scan(
    online_users: int,
    conversion_rate: float,
    retention_rate: float,
    comment_count: int,
    like_count: int,
    product_click_rate: float,
    inventory_delta: int,
    abnormal_order_count: int,
) -> LiveWorkflowReport:
    """直播中盯盘工作流：把运营助理盯屏动作变成规则化预警。"""
    checks: list[LiveOperationCheckItem] = []
    alerts: list[LiveOperationAlert] = []

    checks.append(_check("live-online", "在线人数监控", "done" if online_users >= 100 else "warning", 12, "判断直播间流量是否低于基本盘。"))
    checks.append(_check("live-conversion", "成交率监控", "done" if conversion_rate >= 0.025 else "warning", 18, "成交率偏低时提醒主播切商品或加强利益点。"))
    checks.append(_check("live-retention", "停留率监控", "done" if retention_rate >= 0.35 else "warning", 20, "停留率下降时提醒互动或讲福利。"))
    checks.append(_check("live-comments", "评论热度监控", "done" if comment_count >= 30 else "warning", 10, "评论少时提醒主播提问和点名互动。"))
    checks.append(_check("live-click", "商品点击率监控", "done" if product_click_rate >= 0.08 else "warning", 15, "点击率低时提醒重讲卖点或换品。"))
    checks.append(_check("live-orders", "异常订单监控", "done" if abnormal_order_count == 0 else "blocked", 12, "异常订单需要及时标记，避免售后成本扩大。", abnormal_order_count > 0))

    if retention_rate < 0.35:
        alerts.append(
            LiveOperationAlert(
                id="live-alert-retention",
                priority="high",
                title="停留率下降",
                trigger=f"当前停留率 {retention_rate:.1%}，低于 35% 观察线。",
                suggested_action="主播立刻做福利倒计时或评论区互动，再切到高点击商品。",
                expected_impact="减少流量流失，提高成交机会。",
            )
        )
    if product_click_rate < 0.08:
        alerts.append(
            LiveOperationAlert(
                id="live-alert-click",
                priority="medium",
                title="商品点击率偏低",
                trigger=f"当前商品点击率 {product_click_rate:.1%}。",
                suggested_action="重讲价格锚点、尺码场景和赠品，再观察 3 分钟。",
                expected_impact="提高商品页进入量。",
            )
        )
    if inventory_delta <= -50:
        alerts.append(
            LiveOperationAlert(
                id="live-alert-inventory",
                priority="high",
                title="库存消耗过快",
                trigger=f"本轮库存变化 {inventory_delta}。",
                suggested_action="提醒主播限量口播，并准备替代商品。",
                expected_impact="降低卖断货和退款风险。",
            )
        )
    if abnormal_order_count > 0:
        alerts.append(
            LiveOperationAlert(
                id="live-alert-order",
                priority="high",
                title="存在异常订单",
                trigger=f"发现 {abnormal_order_count} 个异常订单。",
                suggested_action="先交给售后 Agent 标记，不要直播间直接承诺赔偿。",
                expected_impact="减少高风险售后成本。",
            )
        )
    del like_count
    return _workflow_report("during_live", checks, alerts, _during_live_next_actions(alerts))


def run_post_live_review(
    sales_amount_yuan: float,
    order_count: int,
    viewer_count: int,
    refund_count: int,
    top_product_title: str,
    negative_comment_count: int,
    host_script_score: int,
) -> LivePostReviewReport:
    """下播复盘工作流：替代运营助理整理成交、商品、主播和退款风险。"""
    conversion_rate = order_count / viewer_count if viewer_count else 0
    refund_rate = refund_count / order_count if order_count else 0
    risk_note = "退款风险正常。"
    if refund_rate >= 0.08:
        risk_note = "退款风险偏高，明天开播前要检查商品质量、尺码说明和主播承诺。"
    if negative_comment_count >= 20:
        risk_note = f"{risk_note} 负面评论较多，建议运营复盘评论关键词。"

    score = 100
    if conversion_rate < 0.025:
        score -= 20
    if refund_rate >= 0.08:
        score -= 20
    if host_script_score < 80:
        score -= 15
    if negative_comment_count >= 20:
        score -= 10
    score = max(score, 0)

    saved_minutes = 60
    status = "warning" if score < 80 else "done"
    return LivePostReviewReport(
        stage="post_live",
        status=status,
        score=score,
        saved_minutes=saved_minutes,
        estimated_saving_yuan=_minutes_to_yuan(saved_minutes),
        sales_amount_yuan=sales_amount_yuan,
        conversion_rate=round(conversion_rate, 4),
        top_product_title=top_product_title,
        refund_risk_note=risk_note,
        host_performance_note="主播脚本稳定。" if host_script_score >= 80 else "主播脚本分偏低，明天需要减少临场发挥，增加标准话术。",
        next_day_actions=(
            f"明天继续把 {top_product_title} 放入重点讲解位。",
            "开播前复查库存、优惠券、价格和赠品。",
            "把高频负面评论沉淀为脚本修正点。",
        ),
    )


def _check(
    item_id: str,
    title: str,
    status: str,
    saved_minutes: int,
    business_value: str,
    requires_approval: bool = False,
) -> LiveOperationCheckItem:
    return LiveOperationCheckItem(
        id=item_id,
        stage="pre_live" if item_id.startswith("pre-") else "during_live",
        title=title,
        status=status,  # type: ignore[arg-type]
        owner_agent="AI直播运营助理",
        business_value=business_value,
        saved_minutes=saved_minutes,
        requires_approval=requires_approval,
    )


def _workflow_report(
    stage: str,
    checks: Sequence[LiveOperationCheckItem],
    alerts: Sequence[LiveOperationAlert],
    next_actions: Sequence[str],
) -> LiveWorkflowReport:
    blocked_count = sum(1 for check in checks if check.status == "blocked")
    warning_count = sum(1 for check in checks if check.status == "warning")
    score = max(0, 100 - blocked_count * 28 - warning_count * 12)
    status = "blocked" if blocked_count else "warning" if warning_count or alerts else "done"
    saved_minutes = sum(check.saved_minutes for check in checks)
    return LiveWorkflowReport(
        stage=stage,  # type: ignore[arg-type]
        status=status,  # type: ignore[arg-type]
        score=score,
        saved_minutes=saved_minutes,
        estimated_saving_yuan=_minutes_to_yuan(saved_minutes),
        checks=tuple(checks),
        alerts=tuple(alerts),
        next_actions=tuple(next_actions),
    )


def _pre_live_next_actions(checks: Sequence[LiveOperationCheckItem], alerts: Sequence[LiveOperationAlert]) -> tuple[str, ...]:
    if any(check.status == "blocked" for check in checks):
        return ("先处理阻塞项，再允许进入直播准备完成状态。", "把需要审批的优惠券、价格或脚本修改交给老板确认。")
    if alerts:
        return ("直播前 30 分钟复查预警项。", "把库存和互动提醒同步给主播。")
    return ("开播准备通过，可以进入直播中监控。",)


def _during_live_next_actions(alerts: Sequence[LiveOperationAlert]) -> tuple[str, ...]:
    if not alerts:
        return ("继续监控在线人数、成交率、停留率和库存变化。",)
    return tuple(alert.suggested_action for alert in alerts[:3])


def _minutes_to_yuan(minutes: int) -> int:
    return round(minutes / 60 * HOURLY_LABOR_COST_YUAN)
