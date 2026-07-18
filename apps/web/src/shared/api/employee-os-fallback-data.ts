import type { CeoDailyReport, LiveOperationSummary, SavingsSummary } from "./types";

export const fallbackCeoDailyReport: CeoDailyReport = {
  date: "2026-07-15",
  headline: "今天经营状态稳定，AI 已节省约 540 元，可以继续扩大直播运营自动化。",
  business_health_score: 86,
  boss_message: "今天先看一件事：主推款库存低于安全线。如果确认无误，就先调整直播商品顺序。",
  saved_money_today_yuan: 540,
  projected_monthly_saving_yuan: 14040,
  annual_roi_percent: 602,
  replacement_target_yuan: 70000,
  live_operation_status: "需要老板关注",
  data_status: "demo_estimate",
  data_status_label: "演示估算数据",
  data_status_reason: "当前还没有持久化直播 Workflow 运行记录，页面用于试用演示和接入前校准。",
  metrics: [
    { id: "saved_today", label: "今日节省", value: "540 元", explanation: "AI 员工今天替代人工完成工作的估算金额。" },
    { id: "monthly_projection", label: "预计月节省", value: "14040 元", explanation: "按当前工作日节奏推算的月度节省。" },
    { id: "roi", label: "年度 ROI", value: "602%", explanation: "用年度节省减去 AI 成本后计算。" },
    { id: "live_status", label: "直播状态", value: "需要老板关注", explanation: "来自直播准备分、直播中风险和风险提醒。" }
  ],
  top_risks: [
    {
      id: "ceo-alert-stock",
      level: "high",
      title: "主推款库存低于安全线",
      reason: "主推 SKU 可售库存只够 1.8 场直播。",
      suggested_action: "直播前调整商品顺序，把库存更健康的同价位商品放到第二位。",
      money_impact: "减少缺货导致的退款和流量浪费。"
    },
    {
      id: "ceo-alert-retention",
      level: "medium",
      title: "第 20 分钟停留率预计下滑",
      reason: "历史同类直播在第 18-25 分钟出现停留率下滑。",
      suggested_action: "准备 30 秒福利口播和评论区互动问题。",
      money_impact: "提高停留时间，给成交转化争取更多曝光。"
    }
  ],
  priority_actions: [
    {
      id: "live-action-1",
      owner: "ai-live-operator",
      title: "先接入抖店商品、库存、优惠券和直播间基础指标。",
      expected_result: "减少直播运营助理人工检查时间，并降低直播间临场错误。",
      requires_approval: false
    },
    {
      id: "boss-action-upload-live-data",
      owner: "boss",
      title: "今天先上传至少一场真实直播数据，让日报从估算变成真实证据。",
      expected_result: "让节省金额、风险提醒和复盘建议可以被 Replay 和 Evaluation 验证。",
      requires_approval: true
    }
  ],
  ai_employee_notes: [
    "AI直播运营助理：完成 5 项工作，节省 168 分钟，约 126 元，绩效 82 分。",
    "AI售后：完成 18 项工作，节省 216 分钟，约 162 元，绩效 84 分。",
    "AI客服：完成 96 项工作，节省 336 分钟，约 252 元，绩效 88 分。"
  ],
  proof_points: [
    "Savings Engine 今日记录节省 720 分钟，约 540 元。",
    "按当前节奏，预计月节省 14040 元，年度 ROI 602%。",
    "直播 Workflow 尚未写入生产数据库；当前 fallback 为演示数据。"
  ]
};

export const fallbackLiveOperationSummary: LiveOperationSummary = {
  date: "2026-07-15",
  replacement_role: "直播运营助理",
  target_monthly_salary_yuan: 12000,
  session_title: "今晚 20:00 抖店服饰专场",
  pre_live_ready_score: 78,
  during_live_risk_score: 64,
  post_live_review_status: "等待直播结束后自动生成",
  checklist: [
    {
      id: "pre-inventory",
      stage: "pre_live",
      title: "直播前库存检查",
      status: "warning",
      owner_agent: "AI直播运营助理",
      business_value: "避免主播推爆款时突然缺货，减少空讲和售后退款。",
      saved_minutes: 25,
      requires_approval: false
    },
    {
      id: "pre-coupon",
      stage: "pre_live",
      title: "优惠券与价格检查",
      status: "done",
      owner_agent: "AI直播运营助理",
      business_value: "提前发现优惠券过期、价格不一致、赠品规则冲突。",
      saved_minutes: 18,
      requires_approval: true
    },
    {
      id: "live-retention",
      stage: "during_live",
      title: "直播中停留率预警",
      status: "warning",
      owner_agent: "AI直播运营助理",
      business_value: "停留率下降时主动提醒切商品、讲福利或做互动。",
      saved_minutes: 30,
      requires_approval: false
    },
    {
      id: "post-review",
      stage: "post_live",
      title: "直播后复盘报告",
      status: "pending",
      owner_agent: "AI老板",
      business_value: "把成交、商品、评论、退款风险整理成第二天动作。",
      saved_minutes: 55,
      requires_approval: false
    }
  ],
  alerts: [
    {
      id: "alert-stock",
      priority: "high",
      title: "主推款库存低于安全线",
      trigger: "主推 SKU 可售库存只够 1.8 场直播。",
      suggested_action: "直播前调整商品顺序，把库存更健康的同价位商品放到第二位。",
      expected_impact: "减少缺货导致的退款和流量浪费。"
    },
    {
      id: "alert-retention",
      priority: "medium",
      title: "第 20 分钟停留率预计下滑",
      trigger: "历史同类直播在第 18-25 分钟出现停留率下滑。",
      suggested_action: "准备 30 秒福利口播和评论区互动问题。",
      expected_impact: "提高停留时间，给成交转化争取更多曝光。"
    }
  ],
  next_actions: [
    "接入抖店商品、库存、优惠券和直播间基础指标。",
    "把直播中预警接到主播助理提示面板。",
    "直播结束后自动生成第二天直播建议。"
  ]
};

export const fallbackSavingsSummary: SavingsSummary = {
  date: "2026-07-15",
  target_monthly_replacement_yuan: 70000,
  today_saved_minutes: 720,
  today_saved_yuan: 540,
  projected_monthly_saving_yuan: 14040,
  ai_monthly_cost_yuan: 2000,
  annual_saving_yuan: 168480,
  annual_roi_percent: 602,
  agents: [
    {
      agent_id: "ai-live-operator",
      agent_name: "AI直播运营助理",
      replaced_role: "直播运营助理",
      completed_work_count: 5,
      saved_minutes: 168,
      saved_yuan: 126,
      performance_score: 82,
      proof: "完成库存、优惠券、脚本、停留率和复盘准备 5 项直播运营工作。"
    },
    {
      agent_id: "ai-after-sale",
      agent_name: "AI售后",
      replaced_role: "售后专员",
      completed_work_count: 18,
      saved_minutes: 216,
      saved_yuan: 162,
      performance_score: 84,
      proof: "识别退款、投诉、赔偿等高风险售后，并给出审批建议。"
    },
    {
      agent_id: "ai-customer",
      agent_name: "AI客服",
      replaced_role: "客服专员",
      completed_work_count: 96,
      saved_minutes: 336,
      saved_yuan: 252,
      performance_score: 88,
      proof: "处理低风险订单、物流、FAQ 草稿，高风险问题转人工。"
    }
  ],
  next_actions: [
    "接真实直播数据后，把节省时间从估算改成按任务日志计算。",
    "老板首页第一屏只保留节省金额、异常风险和今日审批。",
    "节省金额稳定超过 AI 成本 5 倍后，再扩大自动化权限。"
  ]
};