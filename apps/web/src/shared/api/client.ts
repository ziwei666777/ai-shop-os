import {
  fallbackAfterSaleCases,
  fallbackAgentLogs,
  fallbackAgents,
  fallbackConnectorStatuses,
  fallbackCustomerInbox,
  fallbackDashboardSummary,
  fallbackFeedbackMetrics,
  fallbackCustomers,
  fallbackOrders,
  fallbackProducts,
} from "./fallback-data";
import { fallbackCeoDailyReport, fallbackLiveOperationSummary, fallbackSavingsSummary } from "./employee-os-fallback-data";
import type {
  AfterSaleCase,
  Agent,
  AgentFeedbackMetric,
  AgentLog,
  ConnectorStatus,
  CustomerInboxItem,
  DashboardSummary,
  DraftReply,
  LearningEvent,
  LearningEventInput,
  TrainingAssetCandidate,
  AfterSaleDecision,
  CatalogPage,
  CeoDailyReport,
  CommercePlatform,
  CustomerItem,
  DailyOperationsRun,
  ImportDataType,
  ImportJob,
  ImportPreview,
  LiveOperationSummary,
  LivePostReviewReport,
  LiveWorkflowReport,
  LiveMetricScanInput,
  OrderItem,
  ProductItem,
  PostLiveReviewInput,
  PreLiveCheckInput,
  SavingsSummary,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function getAuthHeaders(): Promise<Record<string, string>> {
  const companyId = process.env.NEXT_PUBLIC_DEFAULT_COMPANY_ID ?? "00000000-0000-0000-0000-000000000001";
  try {
    if (typeof window === "undefined") {
      return { "X-Company-ID": companyId };
    }
    const { createBrowserSupabaseClient } = await import("./supabase-client");
    const { data } = await createBrowserSupabaseClient().auth.getSession();
    return { "X-Company-ID": companyId, ...(data.session ? { Authorization: `Bearer ${data.session.access_token}` } : {}) };
  } catch {
    return { "X-Company-ID": companyId };
  }
}

async function request<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      cache: "no-store",
      headers: {
        accept: "application/json",
        ...(await getAuthHeaders())
      }
    });

    if (!response.ok) {
      return fallback;
    }

    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export interface ApiMutationResult<T> {
  data: T | null;
  error: string | null;
}

async function mutate<T>(path: string, body?: unknown): Promise<ApiMutationResult<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: {
        accept: "application/json",
        ...(await getAuthHeaders()),
        ...(body === undefined ? {} : { "content-type": "application/json" })
      },
      body: body === undefined ? undefined : JSON.stringify(body)
    });

    if (!response.ok) {
      const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
      return { data: null, error: payload?.detail ?? `操作失败（HTTP ${response.status}）` };
    }

    return { data: (await response.json()) as T, error: null };
  } catch {
    return { data: null, error: "无法连接后端服务，请确认 API 已启动后重试。" };
  }
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  return request<DashboardSummary>("/v1/dashboard/summary", fallbackDashboardSummary);
}

export async function getCeoDailyReport(): Promise<CeoDailyReport> {
  return request<CeoDailyReport>("/v1/ceo/daily-report", fallbackCeoDailyReport);
}

export async function getLiveOperationSummary(): Promise<LiveOperationSummary> {
  return request<LiveOperationSummary>("/v1/live-operations/summary", fallbackLiveOperationSummary);
}

export async function getSavingsSummary(): Promise<SavingsSummary> {
  return request<SavingsSummary>("/v1/savings/summary", fallbackSavingsSummary);
}

export async function runDailyOperations(): Promise<ApiMutationResult<DailyOperationsRun>> {
  return mutate<DailyOperationsRun>("/v1/daily-operations/run", { trigger: "manual" });
}
export async function runPreLiveCheck(input: PreLiveCheckInput): Promise<ApiMutationResult<LiveWorkflowReport>> {
  return mutate<LiveWorkflowReport>("/v1/live-operations/pre-live-check", input);
}

export async function runLiveMetricScan(input: LiveMetricScanInput): Promise<ApiMutationResult<LiveWorkflowReport>> {
  return mutate<LiveWorkflowReport>("/v1/live-operations/live-metric-scan", input);
}

export async function runPostLiveReview(input: PostLiveReviewInput): Promise<ApiMutationResult<LivePostReviewReport>> {
  return mutate<LivePostReviewReport>("/v1/live-operations/post-live-review", input);
}


export async function listAgents(): Promise<Agent[]> {
  return request<Agent[]>("/v1/agents", fallbackAgents);
}

export async function getAgent(agentId: string): Promise<Agent | null> {
  const fallbackAgent = fallbackAgents.find((agent) => agent.id === agentId) ?? null;
  return request<Agent | null>(`/v1/agents/${agentId}`, fallbackAgent);
}

export async function listAgentLogs(agentId: string): Promise<AgentLog[]> {
  return request<AgentLog[]>(`/v1/agents/${agentId}/logs`, fallbackAgentLogs);
}

export async function listCustomerInbox(): Promise<CustomerInboxItem[]> {
  return request<CustomerInboxItem[]>("/v1/customer-agent/inbox", fallbackCustomerInbox);
}

export async function draftCustomerReply(messageId: string): Promise<DraftReply | null> {
  return request<DraftReply | null>(`/v1/customer-agent/messages/${messageId}/draft-reply`, null);
}

export async function sendCustomerReply(messageId: string, content: string): Promise<ApiMutationResult<CustomerInboxItem>> {
  return mutate<CustomerInboxItem>(`/v1/customer-agent/messages/${messageId}/send`, { content });
}

export async function takeoverCustomerMessage(messageId: string): Promise<ApiMutationResult<CustomerInboxItem>> {
  return mutate<CustomerInboxItem>(`/v1/customer-agent/messages/${messageId}/takeover`);
}

export async function listAfterSaleCases(): Promise<AfterSaleCase[]> {
  return request<AfterSaleCase[]>("/v1/after-sale/cases", fallbackAfterSaleCases);
}

export async function getAfterSaleCase(caseId: string): Promise<AfterSaleCase | null> {
  const fallbackCase = fallbackAfterSaleCases.find((item) => item.id === caseId) ?? null;
  return request<AfterSaleCase | null>(`/v1/after-sale/cases/${caseId}`, fallbackCase);
}

export async function decideAfterSaleCase(
  caseId: string,
  decision: AfterSaleDecision,
  note: string
): Promise<ApiMutationResult<AfterSaleCase>> {
  return mutate<AfterSaleCase>(`/v1/after-sale/cases/${caseId}/decision`, { decision, note });
}

export async function recordLearningEvent(input: LearningEventInput): Promise<ApiMutationResult<LearningEvent>> {
  return mutate<LearningEvent>("/v1/learning-events", input);
}

export async function commitTrainingAsset(candidateId: string): Promise<ApiMutationResult<TrainingAssetCandidate>> {
  return mutate<TrainingAssetCandidate>(`/v1/training-center/assets/${candidateId}/commit`);
}

export async function listConnectorStatuses(): Promise<ConnectorStatus[]> {
  return request<ConnectorStatus[]>("/v1/connectors/status", fallbackConnectorStatuses);
}

export async function listFeedbackMetrics(): Promise<AgentFeedbackMetric[]> {
  return request<AgentFeedbackMetric[]>("/v1/feedback-metrics", fallbackFeedbackMetrics);
}

export async function listProducts(): Promise<ProductItem[]> {
  const fallback = { items: fallbackProducts, total: fallbackProducts.length, page: 1, page_size: 20 };
  return (await request<CatalogPage<ProductItem>>("/v1/products", fallback)).items;
}

export async function listOrders(): Promise<OrderItem[]> {
  const fallback = { items: fallbackOrders, total: fallbackOrders.length, page: 1, page_size: 20 };
  return (await request<CatalogPage<OrderItem>>("/v1/orders", fallback)).items;
}

export async function listCustomers(): Promise<CustomerItem[]> {
  const fallback = { items: fallbackCustomers, total: fallbackCustomers.length, page: 1, page_size: 20 };
  return (await request<CatalogPage<CustomerItem>>("/v1/customers", fallback)).items;
}

export async function listImportJobs(): Promise<ImportJob[]> {
  return request<ImportJob[]>("/v1/imports", []);
}

export async function previewImportFile(
  file: File,
  platform: CommercePlatform,
  dataType: ImportDataType
): Promise<ApiMutationResult<ImportPreview>> {
  return sendFile<ImportPreview>("/v1/imports/preview", file, { platform, data_type: dataType });
}

export async function submitImportFile(
  file: File,
  platform: CommercePlatform,
  dataType: ImportDataType,
  shopName: string,
  mapping: Record<string, string>
): Promise<ApiMutationResult<ImportJob>> {
  return sendFile<ImportJob>("/v1/imports/files", file, { platform, data_type: dataType, shop_name: shopName }, mapping);
}

export async function startConnectorOAuth(platform: "taobao" | "douyin"): Promise<ApiMutationResult<{ authorization_url: string }>> {
  return mutate<{ authorization_url: string }>(`/v1/connectors/${platform}/oauth/start`);
}

async function sendFile<T>(
  path: string,
  file: File,
  parameters: Record<string, string>,
  mapping?: Record<string, string>
): Promise<ApiMutationResult<T>> {
  try {
    const query = new URLSearchParams({ file_name: file.name, ...parameters });
    const response = await fetch(`${API_BASE_URL}${path}?${query.toString()}`, {
      method: "POST",
      headers: {
        accept: "application/json",
        "content-type": "application/octet-stream",
        ...(mapping ? { "X-Field-Mapping": encodeURIComponent(JSON.stringify(mapping)) } : {}),
        ...(await getAuthHeaders())
      },
      body: await file.arrayBuffer()
    });
    if (!response.ok) {
      const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
      return { data: null, error: payload?.detail ?? `操作失败（HTTP ${response.status}）` };
    }
    return { data: (await response.json()) as T, error: null };
  } catch {
    return { data: null, error: "无法连接后端服务，请确认 API 已启动后重试。" };
  }
}


