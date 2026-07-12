import type {
  AfterSaleCase,
  Agent,
  AgentFeedbackMetric,
  AgentLog,
  ConnectorStatus,
  CustomerInboxItem,
  DashboardSummary,
  CustomerItem,
  OrderItem,
  ProductItem,
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
