from __future__ import annotations

from apps.api.app.domain.validation import SimulationScenario, SimulationSummary


SIMULATION_SCENARIOS: tuple[SimulationScenario, ...] = (
    SimulationScenario(
        id="sim-1",
        customer_type="普通咨询客户",
        scenario_type="logistics",
        message="我今天下单，能不能今天发货？",
        ai_decision="auto_reply",
        expected_behavior="查询订单和仓库规则，生成低风险回复草稿。",
        risk_level="low",
        estimated_minutes=3,
    ),
    SimulationScenario(
        id="sim-2",
        customer_type="砍价客户",
        scenario_type="bargain",
        message="便宜 30 块我马上拍，不然我去别家买。",
        ai_decision="human_review",
        expected_behavior="不直接承诺优惠金额，交给老板或运营确认优惠策略。",
        risk_level="medium",
        estimated_minutes=5,
    ),
    SimulationScenario(
        id="sim-3",
        customer_type="售后退款客户",
        scenario_type="refund",
        message="我不想要了，直接给我退款。",
        ai_decision="approval_required",
        expected_behavior="核实订单、物流、签收时间和售后规则后提交审批。",
        risk_level="high",
        estimated_minutes=12,
    ),
    SimulationScenario(
        id="sim-4",
        customer_type="投诉客户",
        scenario_type="complaint",
        message="东西有瑕疵，你不赔我我就差评。",
        ai_decision="approval_required",
        expected_behavior="安抚客户，要求图片证据，不承诺赔偿金额。",
        risk_level="high",
        estimated_minutes=15,
    ),
    SimulationScenario(
        id="sim-5",
        customer_type="高意向客户",
        scenario_type="private_domain",
        message="我看了三次了，尺码不确定，有没有优惠？",
        ai_decision="operation_suggestion",
        expected_behavior="标记高意向，生成私域跟进话术和优惠建议，预算需审批。",
        risk_level="medium",
        estimated_minutes=10,
    ),
)


def run_simulation_summary() -> SimulationSummary:
    return SimulationSummary(
        total_scenarios=len(SIMULATION_SCENARIOS),
        auto_reply_count=sum(1 for scenario in SIMULATION_SCENARIOS if scenario.ai_decision == "auto_reply"),
        approval_required_count=sum(1 for scenario in SIMULATION_SCENARIOS if scenario.ai_decision == "approval_required"),
        manual_review_count=sum(1 for scenario in SIMULATION_SCENARIOS if scenario.ai_decision == "human_review"),
        estimated_daily_capacity=10000,
        estimated_saved_minutes=sum(scenario.estimated_minutes for scenario in SIMULATION_SCENARIOS),
        scenarios=SIMULATION_SCENARIOS,
        warnings=(
            "当前是小样本模拟，不能替代真实商家历史数据。",
            "上线前必须用真实客服消息做 Replay 和 Evaluation。",
        ),
    )

