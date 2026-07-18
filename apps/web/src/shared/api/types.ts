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
  knowledge_hit: string | null;
  memory_hit: string | null;
  saved_minutes: number;
  estimated_saving_yuan: number;
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

export interface ReplayResult {
  id: string;
  case_type: "customer_message" | "after_sale_case" | "operation_signal";
  title: string;
  input_text: string;
  human_result: string;
  ai_decision: "auto_reply" | "human_review" | "approval_required" | "operation_suggestion";
  ai_result: string;
  is_correct: boolean;
  requires_human: boolean;
  saved_minutes: number;
  evaluation_note: string;
}

export interface ReplaySummary {
  total_cases: number;
  correct_cases: number;
  accuracy: number;
  auto_rate: number;
  manual_rate: number;
  saved_minutes: number;
  estimated_saving_yuan: number;
  results: ReplayResult[];
}

export interface EvaluationMetric {
  id: string;
  label: string;
  score: number;
  target: number;
  status: "good" | "warning" | "blocked";
  explanation: string;
}

export interface EvaluationSummary {
  overall_score: number;
  readiness_level: string;
  evaluated_cases: number;
  estimated_monthly_saving_yuan: number;
  metrics: EvaluationMetric[];
  blockers: string[];
  next_actions: string[];
}

export interface TrainingSample {
  id: string;
  source_type: "message" | "after_sale_case" | "operation_signal";
  agent_name: string;
  action: "accepted" | "edited" | "rejected" | "manual_answered";
  original_content: string;
  final_content: string;
  training_target: "memory" | "knowledge" | "workflow";
  status: "ready" | "needs_review";
  created_at: string;
}

export interface TrainingAssetCandidate {
  id: string;
  target: "memory" | "knowledge" | "workflow";
  title: string;
  content: string;
  source_sample_id: string;
  status: "candidate" | "needs_review" | "committed";
  business_value: string;
}

export interface TrainingCenterSummary {
  total_samples: number;
  usable_samples: number;
  memory_candidates: number;
  knowledge_candidates: number;
  workflow_candidates: number;
  estimated_quality_gain: number;
  samples: TrainingSample[];
  asset_candidates: TrainingAssetCandidate[];
  next_actions: string[];
}

export interface SimulationScenario {
  id: string;
  customer_type: string;
  scenario_type: "faq" | "bargain" | "refund" | "complaint" | "logistics" | "private_domain";
  message: string;
  ai_decision: "auto_reply" | "human_review" | "approval_required" | "operation_suggestion";
  expected_behavior: string;
  risk_level: "low" | "medium" | "high";
  estimated_minutes: number;
}

export interface SimulationSummary {
  total_scenarios: number;
  auto_reply_count: number;
  approval_required_count: number;
  manual_review_count: number;
  estimated_daily_capacity: number;
  estimated_saved_minutes: number;
  scenarios: SimulationScenario[];
  warnings: string[];
}

export interface DatasetReadinessItem {
  kind: "products" | "orders" | "customers" | "messages" | "after_sales" | "shipments";
  label: string;
  record_count: number;
  readiness: number;
  replay_ready: boolean;
  owner: string;
  missing_reason: string | null;
}

export interface CommerceDatasetReadiness {
  average_readiness: number;
  replay_ready_count: number;
  total_kinds: number;
  estimated_replay_cases: number;
  items: DatasetReadinessItem[];
  next_actions: string[];
}

export interface LiveOperationCheckItem {
  id: string;
  stage: "pre_live" | "during_live" | "post_live";
  title: string;
  status: "done" | "warning" | "blocked" | "pending";
  owner_agent: string;
  business_value: string;
  saved_minutes: number;
  requires_approval: boolean;
}

export interface LiveOperationAlert {
  id: string;
  priority: "high" | "medium" | "low";
  title: string;
  trigger: string;
  suggested_action: string;
  expected_impact: string;
}

export interface LiveOperationSummary {
  date: string;
  replacement_role: string;
  target_monthly_salary_yuan: number;
  session_title: string;
  pre_live_ready_score: number;
  during_live_risk_score: number;
  post_live_review_status: string;
  checklist: LiveOperationCheckItem[];
  alerts: LiveOperationAlert[];
  next_actions: string[];
}

export interface AgentSavingsWork {
  agent_id: string;
  agent_name: string;
  replaced_role: string;
  completed_work_count: number;
  saved_minutes: number;
  saved_yuan: number;
  performance_score: number;
  proof: string;
}

export interface SavingsSummary {
  date: string;
  target_monthly_replacement_yuan: number;
  today_saved_minutes: number;
  today_saved_yuan: number;
  projected_monthly_saving_yuan: number;
  ai_monthly_cost_yuan: number;
  annual_saving_yuan: number;
  annual_roi_percent: number;
  agents: AgentSavingsWork[];
  next_actions: string[];
}

export interface LiveProductInput {
  title: string;
  inventory_count: number;
  safe_stock: number;
  regular_price: number;
  live_price: number;
}

export interface LiveCouponInput {
  name: string;
  remaining_count: number;
  expired: boolean;
}

export interface PreLiveCheckInput {
  products: LiveProductInput[];
  coupons: LiveCouponInput[];
  script_text: string;
  gift_ready: boolean;
  product_order_ready: boolean;
}

export interface LiveMetricScanInput {
  online_users: number;
  conversion_rate: number;
  retention_rate: number;
  comment_count: number;
  like_count: number;
  product_click_rate: number;
  inventory_delta: number;
  abnormal_order_count: number;
}

export interface PostLiveReviewInput {
  sales_amount_yuan: number;
  order_count: number;
  viewer_count: number;
  refund_count: number;
  top_product_title: string;
  negative_comment_count: number;
  host_script_score: number;
}

export interface LiveWorkflowReport {
  stage: "pre_live" | "during_live" | "post_live";
  status: "done" | "warning" | "blocked" | "pending";
  score: number;
  saved_minutes: number;
  estimated_saving_yuan: number;
  checks: LiveOperationCheckItem[];
  alerts: LiveOperationAlert[];
  next_actions: string[];
}

export interface LivePostReviewReport {
  stage: "pre_live" | "during_live" | "post_live";
  status: "done" | "warning" | "blocked" | "pending";
  score: number;
  saved_minutes: number;
  estimated_saving_yuan: number;
  sales_amount_yuan: number;
  conversion_rate: number;
  top_product_title: string;
  refund_risk_note: string;
  host_performance_note: string;
  next_day_actions: string[];
}

export interface LiveWorkflowRun {
  id: string;
  workflow_name: string;
  stage: "pre_live" | "during_live" | "post_live";
  status: "done" | "warning" | "blocked" | "pending";
  score: number;
  saved_minutes: number;
  estimated_saving_yuan: number;
  alert_count: number;
  approval_required: boolean;
  proof: string;
  created_at: string;
}

export interface DailyOperationsRun {
  id: string;
  date: string;
  trigger: "manual" | "scheduled" | "webhook";
  input_mode: "merchant_payload" | "safe_baseline";
  status: "completed" | "needs_real_data";
  replacement_role: string;
  operator_message: string;
  completed_work_count: number;
  saved_minutes: number;
  saved_yuan: number;
  workflow_runs: LiveWorkflowRun[];
  ceo_report: CeoDailyReport;
  savings_summary: SavingsSummary;
  next_run_hint: string;
}
export interface CeoReportMetric {
  id: string;
  label: string;
  value: string;
  explanation: string;
}

export interface CeoReportRisk {
  id: string;
  level: "high" | "medium" | "low";
  title: string;
  reason: string;
  suggested_action: string;
  money_impact: string;
}

export interface CeoReportAction {
  id: string;
  owner: "boss" | "ai-live-operator" | "ai-operator" | "ai-after-sale" | "ai-customer";
  title: string;
  expected_result: string;
  requires_approval: boolean;
}

export interface CeoDailyReport {
  date: string;
  headline: string;
  business_health_score: number;
  boss_message: string;
  saved_money_today_yuan: number;
  projected_monthly_saving_yuan: number;
  annual_roi_percent: number;
  replacement_target_yuan: number;
  live_operation_status: string;
  data_status: "demo_estimate" | "real_workflow_logs";
  data_status_label: string;
  data_status_reason: string;
  metrics: CeoReportMetric[];
  top_risks: CeoReportRisk[];
  priority_actions: CeoReportAction[];
  ai_employee_notes: string[];
  proof_points: string[];
}
