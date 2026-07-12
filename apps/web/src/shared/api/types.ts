import type { AgentStatus, AgentType } from "@ai-shop-os/shared";

export interface DashboardMetric {
  id: string;
  label: string;
  value: string;
  trend: string;
}

export interface DashboardSuggestion {
  id: string;
  title: string;
  reason: string;
  priority: "high" | "medium" | "low";
}

export interface Agent {
  id: string;
  name: string;
  type: AgentType;
  status: AgentStatus;
  description: string;
  prompt: string;
  today_handled_count: number;
  kpi_score: number;
  future_tasks: string[];
}

export interface AgentLog {
  id: string;
  agent_id: string;
  level: string;
  message: string;
  created_at: string;
}

export interface CustomerInboxItem {
  id: string;
  platform: "shopify" | "taobao";
  customer_name: string;
  channel: string;
  content: string;
  intent: string;
  order_external_id: string | null;
  logistics_status: string | null;
  confidence: number;
  automation_decision: "auto_reply" | "human_review";
  status: string;
  created_at: string;
}

export interface DraftReply {
  message_id: string;
  content: string;
  confidence: number;
  automation_decision: "auto_reply" | "human_review";
  reason: string;
  required_human_review: boolean;
}

export interface LearningEvent {
  id: string;
  source_type: "message" | "after_sale_case";
  source_id: string;
  agent_id: string;
  action: "accepted" | "edited" | "rejected" | "manual_answered";
  original_content: string;
  final_content: string;
  created_at: string;
}

export interface LearningEventInput {
  source_type: LearningEvent["source_type"];
  source_id: string;
  agent_id: string;
  action: LearningEvent["action"];
  original_content: string;
  final_content: string;
}

export type AfterSaleDecision = "approved" | "rejected" | "needs_more_info";

export interface AfterSaleCase {
  id: string;
  platform: "shopify" | "taobao";
  case_type: string;
  status: string;
  customer_name: string;
  order_external_id: string;
  title: string;
  description: string;
  risk_level: "high" | "medium" | "low";
  ai_suggestion: string;
  approval_required: boolean;
  created_at: string;
}

export interface ConnectorStatus {
  platform: "taobao" | "douyin" | "xianyu" | "shopify";
  status: "connected" | "pending" | "not_connected";
  display_name: string;
  scopes: string[];
  next_action: string;
}

export interface AgentFeedbackMetric {
  id: string;
  agent_id: string;
  metric_name: string;
  metric_value: number;
  weight: number;
}

export interface DashboardSummary {
  date: string;
  metrics: DashboardMetric[];
  agents: Agent[];
  suggestions: DashboardSuggestion[];
  pending_approval_count: number;
}

export type CommercePlatform = "taobao" | "douyin" | "xianyu";
export type ImportDataType = "products" | "orders" | "order_items" | "customers" | "shipments" | "after_sales";

export interface ProductItem {
  id: string;
  platform: CommercePlatform;
  shop_name: string;
  external_id: string;
  title: string;
  sku: string;
  price: number;
  inventory_count: number;
  status: string;
  updated_at: string;
}

export interface OrderItem {
  id: string;
  platform: CommercePlatform;
  shop_name: string;
  external_id: string;
  customer_name: string;
  status: string;
  total_amount: number;
  paid_at: string | null;
  updated_at: string;
}

export interface CustomerItem {
  id: string;
  platform: CommercePlatform;
  shop_name: string;
  external_id: string;
  name: string;
  order_count: number;
  total_spent: number;
  tags: string[];
  updated_at: string;
}

export interface CatalogPage<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface ImportPreview {
  file_name: string;
  encoding: string;
  headers: string[];
  sample_rows: Record<string, string>[];
  suggested_mapping: Record<string, string>;
  required_fields: string[];
  warnings: string[];
}

export interface ImportJob {
  id: string;
  platform: CommercePlatform;
  import_mode: "api_sync" | "file";
  data_type: ImportDataType;
  status: "queued" | "running" | "partial_success" | "succeeded" | "failed";
  progress: number;
  total_count: number;
  success_count: number;
  failure_count: number;
  file_name: string | null;
  error_summary: string | null;
  created_at: string;
}
