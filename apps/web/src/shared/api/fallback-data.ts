import type {
  AfterSaleCase,
  Agent,
  AgentFeedbackMetric,
  AgentLog,
  CommerceDatasetReadiness,
  ConnectorStatus,
  CustomerInboxItem,
  DashboardSummary,
  CustomerItem,
  EvaluationSummary,
  OrderItem,
  ProductItem,
  ReplaySummary,
  SimulationSummary,
  TrainingCenterSummary,
} from "./types";

export const fallbackAgents: Agent[] = [
  {
    id: "ai-boss",
    name: "AI 老板",
    type: "boss",
    status: "online",
    description: "每天生成老板经营汇报、识别异常、汇总审批并分配 AI 员工任务。",
    prompt: "你是 AI Shop OS 的 AI 老板，只给出可追踪、可审批、可执行的经营建议。",
    today_handled_count: 12,
    kpi_score: 86,
    future_tasks: ["接入日报生成", "接入审批策略", "接入利润分析"]
  },
  {
    id: "ai-customer",
    name: "AI 客服",
    type: "customer",
    status: "online",
    description: "负责商品咨询、订单查询、物流查询、退款说明和未知问题升级。",
    prompt: "你是 AI 客服，禁止编造答案；不确定时必须暂停并升级给老板。",
    today_handled_count: 96,
    kpi_score: 91,
    future_tasks: ["接入对话记忆（Memory）", "接入检索增强知识库（RAG）", "接入人工接管"]
  },
  {
    id: "ai-operator",
    name: "AI 运营",
    type: "operator",
    status: "paused",
    description: "后续负责商品标题、详情页、广告、竞品和 SEO 分析。",
    prompt: "等待 Sprint 2 之后启用。",
    today_handled_count: 0,
    kpi_score: 0,
    future_tasks: ["商品优化", "竞品分析", "广告建议"]
  },
  {
    id: "ai-after-sale",
    name: "AI 售后",
    type: "after_sale",
    status: "online",
    description: "负责退款、退货、物流异常、投诉和赔偿的风险判断与审批建议。",
    prompt: "你是 AI 售后，涉及退款、赔偿、投诉和金额变化时必须要求商家确认。",
    today_handled_count: 18,
    kpi_score: 82,
    future_tasks: ["接入退款规则", "接入物流异常识别", "接入售后审批流"]
  }
];

export const fallbackCustomerInbox: CustomerInboxItem[] = [
  {
    id: "msg-1",
    platform: "shopify",
    customer_name: "Lily Chen",
    channel: "shopify_inbox",
    content: "这件衬衫还有 M 码吗？今天下单什么时候发货？",
    intent: "faq",
    order_external_id: null,
    logistics_status: null,
    confidence: 0.92,
    automation_decision: "auto_reply",
    status: "pending",
    created_at: "2026-07-09T10:12:00+08:00"
  },
  {
    id: "msg-2",
    platform: "shopify",
    customer_name: "Alex Wong",
    channel: "shopify_inbox",
    content: "订单 #1007 到哪里了？",
    intent: "logistics",
    order_external_id: "#1007",
    logistics_status: "运输中，预计 2 天内送达",
    confidence: 0.88,
    automation_decision: "auto_reply",
    status: "pending",
    created_at: "2026-07-09T10:18:00+08:00"
  },
  {
    id: "msg-3",
    platform: "taobao",
    customer_name: "王女士",
    channel: "taobao_message",
    content: "收到货有瑕疵，可以赔偿吗？",
    intent: "compensation",
    order_external_id: "TB20260709003",
    logistics_status: "已签收",
    confidence: 0.67,
    automation_decision: "human_review",
    status: "needs_human",
    created_at: "2026-07-09T10:25:00+08:00"
  }
];

export const fallbackAfterSaleCases: AfterSaleCase[] = [
  {
    id: "case-1",
    platform: "shopify",
    case_type: "refund",
    status: "waiting_merchant",
    customer_name: "Alex Wong",
    order_external_id: "#1007",
    title: "客户申请退款",
    description: "客户表示物流超过预期，希望退款。",
    risk_level: "medium",
    ai_suggestion: "先核查物流轨迹，如果 48 小时内无更新，再建议部分补偿或退款审批。",
    approval_required: true,
    created_at: "2026-07-09T10:28:00+08:00"
  },
  {
    id: "case-2",
    platform: "taobao",
    case_type: "complaint",
    status: "waiting_merchant",
    customer_name: "王女士",
    order_external_id: "TB20260709003",
    title: "商品瑕疵投诉",
    description: "客户反馈商品有瑕疵并提出赔偿。",
    risk_level: "high",
    ai_suggestion: "需要人工查看图片证据；未确认前不得承诺赔偿金额。",
    approval_required: true,
    created_at: "2026-07-09T10:31:00+08:00"
  }
];

export const fallbackConnectorStatuses: ConnectorStatus[] = [
  {
    platform: "taobao",
    status: "pending",
    display_name: "淘宝开放平台",
    scopes: ["订单查询", "商品查询", "物流查询", "消息接入"],
    next_action: "申请淘宝开放平台应用权限，并配置 App Key、密钥和回调地址。"
  },
  {
    platform: "douyin",
    status: "pending",
    display_name: "抖音商店",
    scopes: ["商家授权", "订单查询", "商品查询", "售后查询"],
    next_action: "申请抖店开放平台应用和对应电商权限，再接入官方 OpenAPI。"
  },
  {
    platform: "xianyu",
    status: "not_connected",
    display_name: "闲鱼",
    scopes: ["官方能力待确认"],
    next_action: "等待确认可商用的官方开放能力；不使用 Cookie、扫码登录或抓包方案。"
  },
  {
    platform: "shopify",
    status: "pending",
    display_name: "Shopify",
    scopes: ["读取订单", "读取商品", "读取客户"],
    next_action: "海外平台后续接入，当前优先级低于淘宝、抖音和闲鱼。"
  }
];

export const fallbackFeedbackMetrics: AgentFeedbackMetric[] = [
  { id: "metric-1", agent_id: "ai-customer", metric_name: "客服问答修正样本", metric_value: 60, weight: 0.6 },
  { id: "metric-2", agent_id: "ai-after-sale", metric_name: "售后决策样本", metric_value: 30, weight: 0.3 },
  { id: "metric-3", agent_id: "ai-customer", metric_name: "采纳率与接管率", metric_value: 10, weight: 0.1 }
];

export const fallbackDashboardSummary: DashboardSummary = {
  date: "2026-07-09",
  pending_approval_count: 3,
  metrics: [
    { id: "sales", label: "今日销售", value: "¥12,860", trend: "较昨日 +8.2%" },
    { id: "profit", label: "今日利润", value: "¥3,420", trend: "毛利率 26.6%" },
    { id: "inventory", label: "库存风险", value: "5 个 SKU", trend: "2 个低于安全库存" },
    { id: "refunds", label: "退款异常", value: "7 单", trend: "2 单需要审批" }
  ],
  agents: fallbackAgents,
  suggestions: [
    { id: "s1", title: "优先审批 2 个退款申请", reason: "等待时间超过 6 小时，可能影响店铺体验分。", priority: "high" },
    { id: "s2", title: "检查热销 SKU 库存", reason: "订单增长明显，当前库存可售天数低于 5 天。", priority: "medium" },
    { id: "s3", title: "沉淀 AI 客服未知问题", reason: "把老板回答转成知识，后续相同问题由 AI 自动处理。", priority: "low" }
  ]
};

export const fallbackAgentLogs: AgentLog[] = [
  {
    id: "log-1",
    agent_id: "fallback",
    level: "info",
    message: "读取今日任务状态。",
    created_at: "2026-07-09T09:00:00+08:00"
  },
  {
    id: "log-2",
    agent_id: "fallback",
    level: "info",
    message: "等待工作流程引擎（Workflow Engine）接入。",
    created_at: "2026-07-09T09:05:00+08:00"
  }
];

export const fallbackProducts: ProductItem[] = [
  { id: "product-1", platform: "taobao", shop_name: "淘宝主店", external_id: "TB-P-1001", title: "轻量防晒外套", sku: "FS-001", price: 129, inventory_count: 86, status: "在售", updated_at: "2026-07-11T09:30:00+08:00" },
  { id: "product-2", platform: "douyin", shop_name: "抖音旗舰店", external_id: "DY-P-2031", title: "夏季冰感直筒裤", sku: "BK-2031", price: 99, inventory_count: 24, status: "在售", updated_at: "2026-07-11T09:18:00+08:00" },
  { id: "product-3", platform: "xianyu", shop_name: "闲鱼店铺", external_id: "XY-P-0188", title: "样衣清仓连衣裙", sku: "QK-188", price: 68, inventory_count: 3, status: "库存偏低", updated_at: "2026-07-10T21:06:00+08:00" }
];

export const fallbackOrders: OrderItem[] = [
  { id: "order-1", platform: "taobao", shop_name: "淘宝主店", external_id: "TB20260711001", customer_name: "小林同学", status: "待发货", total_amount: 228, paid_at: "2026-07-11T09:02:00+08:00", updated_at: "2026-07-11T09:05:00+08:00" },
  { id: "order-2", platform: "douyin", shop_name: "抖音旗舰店", external_id: "DY20260711016", customer_name: "周女士", status: "运输中", total_amount: 99, paid_at: "2026-07-11T08:41:00+08:00", updated_at: "2026-07-11T09:12:00+08:00" },
  { id: "order-3", platform: "xianyu", shop_name: "闲鱼店铺", external_id: "XY20260710008", customer_name: "海边的风", status: "已完成", total_amount: 68, paid_at: "2026-07-10T18:20:00+08:00", updated_at: "2026-07-11T08:20:00+08:00" }
];

export const fallbackCustomers: CustomerItem[] = [
  { id: "customer-1", platform: "taobao", shop_name: "淘宝主店", external_id: "TB-U-9001", name: "小林同学", order_count: 5, total_spent: 836, tags: ["复购客户"], updated_at: "2026-07-11T09:05:00+08:00" },
  { id: "customer-2", platform: "douyin", shop_name: "抖音旗舰店", external_id: "DY-U-2871", name: "周女士", order_count: 2, total_spent: 198, tags: ["直播间客户"], updated_at: "2026-07-11T09:12:00+08:00" },
  { id: "customer-3", platform: "xianyu", shop_name: "闲鱼店铺", external_id: "XY-U-1730", name: "海边的风", order_count: 1, total_spent: 68, tags: ["新客户"], updated_at: "2026-07-11T08:20:00+08:00" }
];

export const fallbackReplaySummary: ReplaySummary = {
  total_cases: 5,
  correct_cases: 5,
  accuracy: 1,
  auto_rate: 0.4,
  manual_rate: 0.6,
  saved_minutes: 57,
  estimated_saving_yuan: 216,
  results: [
    {
      id: "replay-customer-1",
      case_type: "customer_message",
      title: "物流咨询",
      input_text: "客户问：今天下单什么时候发货？能不能帮我催一下？",
      human_result: "人工客服查询订单后回复预计当天出库，用时 4 分钟。",
      ai_decision: "auto_reply",
      ai_result: "属于低风险订单/物流咨询，AI 可以生成回复草稿并记录处理结果。",
      is_correct: true,
      requires_human: false,
      saved_minutes: 4,
      evaluation_note: "AI 可处理低风险重复工作，节省人工响应时间。"
    },
    {
      id: "replay-customer-2",
      case_type: "customer_message",
      title: "赔偿诉求",
      input_text: "客户说：物流太慢了，必须赔我 20 元。",
      human_result: "人工客服转交主管确认，没有直接承诺赔偿，用时 8 分钟。",
      ai_decision: "human_review",
      ai_result: "涉及赔偿、投诉或金额承诺，AI 只给建议，必须人工确认后回复。",
      is_correct: true,
      requires_human: true,
      saved_minutes: 8,
      evaluation_note: "AI 正确拦截高风险动作，减少越权退款、赔偿或投诉风险。"
    },
    {
      id: "replay-after-sale-1",
      case_type: "after_sale_case",
      title: "退货申请",
      input_text: "客户申请尺码不合适退货，订单已签收 2 天。",
      human_result: "售后判断符合 7 天无理由，建议同意退货，用时 12 分钟。",
      ai_decision: "approval_required",
      ai_result: "售后动作需要审批，AI 输出建议但不直接退款或承诺。",
      is_correct: true,
      requires_human: true,
      saved_minutes: 12,
      evaluation_note: "AI 正确拦截高风险动作，减少越权退款、赔偿或投诉风险。"
    },
    {
      id: "replay-after-sale-2",
      case_type: "after_sale_case",
      title: "投诉升级",
      input_text: "客户投诉商品有瑕疵并要求补偿，否则给差评。",
      human_result: "售后主管要求先看图片证据，不承诺金额，用时 15 分钟。",
      ai_decision: "approval_required",
      ai_result: "涉及赔偿、投诉或金额承诺，AI 只给建议，必须人工确认后回复。",
      is_correct: true,
      requires_human: true,
      saved_minutes: 15,
      evaluation_note: "AI 正确拦截高风险动作，减少越权退款、赔偿或投诉风险。"
    },
    {
      id: "replay-operation-1",
      case_type: "operation_signal",
      title: "高意向客户",
      input_text: "同一客户 7 天内 3 次咨询尺码、发货和优惠，但未下单。",
      human_result: "运营人工标记为高意向客户，准备私域跟进话术，用时 18 分钟。",
      ai_decision: "operation_suggestion",
      ai_result: "识别为高意向客户，建议生成私域跟进话术和小预算投流草稿。",
      is_correct: true,
      requires_human: false,
      saved_minutes: 18,
      evaluation_note: "AI 可处理低风险重复工作，节省人工响应时间。"
    }
  ]
};

export const fallbackEvaluationSummary: EvaluationSummary = {
  overall_score: 86,
  readiness_level: "可试用，未达到完全替代",
  evaluated_cases: 5,
  estimated_monthly_saving_yuan: 4752,
  metrics: [
    { id: "accuracy", label: "判断准确率", score: 1, target: 0.9, status: "good", explanation: "AI 决策与历史人工处理结果的一致程度。" },
    { id: "manual_rate", label: "人工接管率", score: 0.6, target: 0.35, status: "warning", explanation: "高风险场景接管是正确的，但后续要降低低风险接管。" },
    { id: "risk_control", label: "高风险拦截", score: 1, target: 1, status: "good", explanation: "退款、投诉、赔偿类动作必须进入审批。" },
    { id: "saving_progress", label: "4 万成本目标进度", score: 0.1188, target: 1, status: "warning", explanation: "按样例节省时间推算，还需要真实数据放大验证。" }
  ],
  blockers: ["当前仍是样例回放，必须接入真实商家历史消息、订单和售后数据。", "还没有足够老板修正样本，无法证明 AI 会越用越准。"],
  next_actions: ["导入过去 30 天客服、订单和售后记录。", "每天修正 20 条 AI 回复或售后建议。", "每天复盘准确率、接管率和节省金额。"]
};

export const fallbackTrainingCenterSummary: TrainingCenterSummary = {
  total_samples: 3,
  usable_samples: 2,
  memory_candidates: 1,
  knowledge_candidates: 1,
  workflow_candidates: 1,
  estimated_quality_gain: 0.6667,
  samples: [
    {
      id: "training-1",
      source_type: "message",
      agent_name: "AI 客服",
      action: "edited",
      original_content: "亲，物流慢可以帮您催一下。",
      final_content: "您好，我已经为您查询订单，包裹今天会从仓库发出。若 24 小时无物流更新，我会继续跟进。",
      training_target: "memory",
      status: "ready",
      created_at: "2026-07-12T10:00:00+08:00"
    },
    {
      id: "training-2",
      source_type: "after_sale_case",
      agent_name: "AI 售后",
      action: "manual_answered",
      original_content: "可以给您补偿 20 元。",
      final_content: "涉及补偿金额需要先核实图片证据和订单状态，确认后由老板审批。",
      training_target: "workflow",
      status: "ready",
      created_at: "2026-07-12T10:18:00+08:00"
    },
    {
      id: "training-3",
      source_type: "operation_signal",
      agent_name: "AI 运营",
      action: "accepted",
      original_content: "客户多次咨询尺码但未下单。",
      final_content: "标记为高意向客户，生成私域跟进话术，但优惠券和投流预算必须审批。",
      training_target: "knowledge",
      status: "needs_review",
      created_at: "2026-07-12T10:36:00+08:00"
    }
  ],
  asset_candidates: [
    {
      id: "asset-training-1",
      target: "memory",
      title: "AI 客服记忆候选：包裹今天会从仓库发出",
      content: "您好，我已经为您查询订单，包裹今天会从仓库发出。若 24 小时无物流更新，我会继续跟进。",
      source_sample_id: "training-1",
      status: "candidate",
      business_value: "保留老板真实处理经验，让 AI 回复更接近店铺风格。"
    },
    {
      id: "asset-training-2",
      target: "workflow",
      title: "AI 售后流程候选：补偿金额先核实再审批",
      content: "涉及补偿金额需要先核实图片证据和订单状态，确认后由老板审批。",
      source_sample_id: "training-2",
      status: "committed",
      business_value: "减少退款、赔偿、投诉等高风险动作的人工判断成本。"
    },
    {
      id: "asset-training-3",
      target: "knowledge",
      title: "AI 运营知识候选：高意向客户私域跟进",
      content: "标记为高意向客户，生成私域跟进话术，但优惠券和投流预算必须审批。",
      source_sample_id: "training-3",
      status: "needs_review",
      business_value: "让 AI 下次遇到相同商品、物流、优惠问题时更快回答。"
    }
  ],
  next_actions: ["把老板修改过的客服回复沉淀为 Memory。", "把售后审批规则沉淀为 Workflow。", "把高频商品、物流、优惠问题沉淀为 Knowledge。"]
};

export const fallbackSimulationSummary: SimulationSummary = {
  total_scenarios: 5,
  auto_reply_count: 1,
  approval_required_count: 2,
  manual_review_count: 1,
  estimated_daily_capacity: 10000,
  estimated_saved_minutes: 45,
  scenarios: [
    { id: "sim-1", customer_type: "普通咨询客户", scenario_type: "logistics", message: "我今天下单，能不能今天发货？", ai_decision: "auto_reply", expected_behavior: "查询订单和仓库规则，生成低风险回复草稿。", risk_level: "low", estimated_minutes: 3 },
    { id: "sim-2", customer_type: "砍价客户", scenario_type: "bargain", message: "便宜 30 块我马上拍，不然我去别家买。", ai_decision: "human_review", expected_behavior: "不直接承诺优惠金额，交给老板或运营确认优惠策略。", risk_level: "medium", estimated_minutes: 5 },
    { id: "sim-3", customer_type: "售后退款客户", scenario_type: "refund", message: "我不想要了，直接给我退款。", ai_decision: "approval_required", expected_behavior: "核实订单、物流、签收时间和售后规则后提交审批。", risk_level: "high", estimated_minutes: 12 },
    { id: "sim-4", customer_type: "投诉客户", scenario_type: "complaint", message: "东西有瑕疵，你不赔我我就差评。", ai_decision: "approval_required", expected_behavior: "安抚客户，要求图片证据，不承诺赔偿金额。", risk_level: "high", estimated_minutes: 15 },
    { id: "sim-5", customer_type: "高意向客户", scenario_type: "private_domain", message: "我看了三次了，尺码不确定，有没有优惠？", ai_decision: "operation_suggestion", expected_behavior: "标记高意向，生成私域跟进话术和优惠建议，预算需审批。", risk_level: "medium", estimated_minutes: 10 }
  ],
  warnings: ["当前是小样本模拟，不能替代真实商家历史数据。", "上线前必须用真实客服消息做 Replay 和 Evaluation。"]
};

export const fallbackCommerceDatasetReadiness: CommerceDatasetReadiness = {
  average_readiness: 72,
  replay_ready_count: 6,
  total_kinds: 6,
  estimated_replay_cases: 9,
  items: [
    { kind: "products", label: "商品数据", record_count: 3, readiness: 60, replay_ready: true, owner: "AI客服 / AI运营", missing_reason: null },
    { kind: "orders", label: "订单数据", record_count: 3, readiness: 60, replay_ready: true, owner: "AI客服 / Replay", missing_reason: null },
    { kind: "customers", label: "客户数据", record_count: 3, readiness: 60, replay_ready: true, owner: "AI运营", missing_reason: null },
    { kind: "messages", label: "客服消息", record_count: 3, readiness: 15, replay_ready: true, owner: "AI客服 / Training", missing_reason: null },
    { kind: "after_sales", label: "售后数据", record_count: 2, readiness: 40, replay_ready: true, owner: "AI售后 / Evaluation", missing_reason: null },
    { kind: "shipments", label: "物流数据", record_count: 1, readiness: 20, replay_ready: true, owner: "AI客服 / AI售后", missing_reason: null }
  ],
  next_actions: ["当前基础数据已具备回放条件，下一步导入更多历史客服消息。", "用 Replay 对比 AI 和人工处理结果。", "用 Evaluation 每天统计节省分钟数和节省金额。"]
};
