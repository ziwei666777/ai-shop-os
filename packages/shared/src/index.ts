export const PRIMARY_NAVIGATION_ITEMS = [
  { label: "老板首页", href: "/dashboard" },
  { label: "AI 员工", href: "/ai-employees" },
  { label: "订单", href: "/orders" },
  { label: "商品", href: "/products" },
  { label: "客户", href: "/customers" },
  { label: "数据集", href: "/commerce-dataset" },
  { label: "回放验证", href: "/replay" },
  { label: "AI 评分", href: "/evaluation" },
  { label: "训练中心", href: "/training-center" },
  { label: "模拟压测", href: "/simulation" },
  { label: "知识库", href: "/knowledge-base" },
  { label: "工作流程", href: "/workflow" },
  { label: "经营分析", href: "/analytics" },
  { label: "设置", href: "/settings" }
] as const;

export type AgentType =
  | "boss"
  | "customer"
  | "operator"
  | "after_sale"
  | "purchase"
  | "logistics"
  | "finance"
  | "analyst";

export type AgentStatus = "online" | "paused" | "offline";

export type MemoryType = "conversation" | "customer" | "business" | "company";
