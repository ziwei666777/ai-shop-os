"use client";

import { useMemo, useState } from "react";
import { CheckCircle2, CircleDollarSign, FilePenLine, Search, ShieldCheck, ShieldQuestion, XCircle } from "lucide-react";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { DetailDrawer } from "@/shared/ui/detail-drawer";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import { decideAfterSaleCase, recordLearningEvent } from "@/shared/api/client";
import type { AfterSaleDecision } from "@/shared/api/types";
import type { AfterSaleCase } from "@/shared/api/types";
import { cn } from "@/shared/lib/utils";

type PlatformFilter = "all" | AfterSaleCase["platform"];
type RiskFilter = "all" | AfterSaleCase["risk_level"];
type ApprovalFilter = "all" | "required" | "optional";

const riskTone = {
  high: "amber",
  medium: "amber",
  low: "green"
} as const;

const riskLabels = {
  high: "高风险",
  medium: "中风险",
  low: "低风险"
} as const;

const caseTypeLabels: Record<string, string> = {
  compensation: "赔偿",
  complaint: "投诉",
  logistics_issue: "物流异常",
  refund: "退款",
  return: "退货"
};

const statusLabels: Record<string, string> = {
  open: "待处理",
  resolved: "已处理",
  waiting_merchant: "待商家确认"
};

export function AfterSaleWorkbenchView({ cases }: { cases: AfterSaleCase[] }) {
  const [approvalFilter, setApprovalFilter] = useState<ApprovalFilter>("all");
  const [decisionOverrides, setDecisionOverrides] = useState<Record<string, string>>({});
  const [merchantNotes, setMerchantNotes] = useState<Record<string, string>>({});
  const [platformFilter, setPlatformFilter] = useState<PlatformFilter>("all");
  const [query, setQuery] = useState("");
  const [riskFilter, setRiskFilter] = useState<RiskFilter>("all");
  const [selectedId, setSelectedId] = useState(cases[0]?.id ?? "");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [pendingAction, setPendingAction] = useState<string | null>(null);
  const [actionFeedback, setActionFeedback] = useState<{ tone: "success" | "error"; message: string } | null>(null);

  const selected = cases.find((item) => item.id === selectedId) ?? cases[0];

  const filteredCases = useMemo(() => {
    const keyword = query.trim().toLowerCase();

    return cases.filter((item) => {
      const matchesPlatform = platformFilter === "all" || item.platform === platformFilter;
      const matchesRisk = riskFilter === "all" || item.risk_level === riskFilter;
      const matchesApproval =
        approvalFilter === "all" ||
        (approvalFilter === "required" && item.approval_required) ||
        (approvalFilter === "optional" && !item.approval_required);
      const matchesKeyword =
        !keyword ||
        [item.title, item.description, item.customer_name, item.order_external_id, item.case_type, item.ai_suggestion]
          .join(" ")
          .toLowerCase()
          .includes(keyword);

      return matchesPlatform && matchesRisk && matchesApproval && matchesKeyword;
    });
  }, [approvalFilter, cases, platformFilter, query, riskFilter]);

  const highRiskCount = cases.filter((item) => item.risk_level === "high").length;
  const approvalCount = cases.filter((item) => item.approval_required).length;
  const waitingCount = cases.filter((item) => item.status === "waiting_merchant").length;

  function openDetail(item: AfterSaleCase) {
    setSelectedId(item.id);
    setActionFeedback(null);
    setDrawerOpen(true);
  }

  async function handleDecision(
    decision: AfterSaleDecision,
    learningAction: "accepted" | "edited" | "rejected",
    statusLabel: string
  ) {
    if (!selected) {
      return;
    }

    const note = (merchantNotes[selected.id] ?? "").trim();
    if (learningAction !== "accepted" && !note) {
      setActionFeedback({ tone: "error", message: "修改或拒绝建议时，请先填写商家处理备注。" });
      return;
    }

    setPendingAction(learningAction);
    setActionFeedback(null);
    const decisionResult = await decideAfterSaleCase(
      selected.id,
      decision,
      note || (learningAction === "accepted" ? "采纳 AI 售后建议" : "商家要求补充信息")
    );

    if (decisionResult.error) {
      setActionFeedback({ tone: "error", message: decisionResult.error });
      setPendingAction(null);
      return;
    }

    const learningResult = await recordLearningEvent({
      source_type: "after_sale_case",
      source_id: selected.id,
      agent_id: "ai-after-sale",
      action: learningAction,
      original_content: selected.ai_suggestion,
      final_content: learningAction === "accepted" ? selected.ai_suggestion : note
    });

    setDecisionOverrides((current) => ({ ...current, [selected.id]: statusLabel }));
    setPendingAction(null);

    if (learningResult.error) {
      setActionFeedback({ tone: "error", message: `售后决定已保存，但学习样本记录失败：${learningResult.error}` });
      return;
    }

    setActionFeedback({ tone: "success", message: "售后决定和商家反馈已保存。" });
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 border-b border-border pb-5 md:flex-row md:items-end">
        <div>
          <p className="text-sm font-medium text-primary">AI 售后工作台</p>
          <h1 className="mt-2 text-3xl font-semibold">AI售后商家试用台</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
            售后任务按风险、审批和平台统一排队；AI 给出判断依据，商家保留最终处理权。
          </p>
        </div>
        <Badge tone="amber">售后决策样本 30%</Badge>
      </header>

      <section className="grid gap-3 md:grid-cols-4">
        <MetricCard label="售后任务" value={`${cases.length}`} />
        <MetricCard label="高风险" value={`${highRiskCount}`} />
        <MetricCard label="必须审批" value={`${approvalCount}`} />
        <MetricCard label="待商家确认" value={`${waitingCount}`} />
      </section>

      <Card className="overflow-hidden">
        <div className="flex flex-col gap-3 border-b border-border p-4 xl:flex-row xl:items-center xl:justify-between">
          <div className="flex items-center gap-2">
            <CircleDollarSign className="h-4 w-4 text-primary" />
            <h2 className="text-base font-semibold">售后任务队列</h2>
          </div>

          <div className="grid gap-2 sm:grid-cols-[minmax(220px,1fr)_140px_140px_140px]">
            <label className="relative">
              <Search aria-hidden className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                className="h-10 w-full rounded-md border border-border bg-background pl-9 pr-3 text-sm outline-none transition focus:border-primary"
                onChange={(event) => setQuery(event.target.value)}
                placeholder="搜索客户、订单、售后问题"
                value={query}
              />
            </label>
            <select
              className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none transition focus:border-primary"
              onChange={(event) => setPlatformFilter(event.target.value as PlatformFilter)}
              value={platformFilter}
            >
              <option value="all">全部平台</option>
              <option value="shopify">Shopify</option>
              <option value="taobao">淘宝</option>
            </select>
            <select
              className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none transition focus:border-primary"
              onChange={(event) => setRiskFilter(event.target.value as RiskFilter)}
              value={riskFilter}
            >
              <option value="all">全部风险</option>
              <option value="high">高风险</option>
              <option value="medium">中风险</option>
              <option value="low">低风险</option>
            </select>
            <select
              className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none transition focus:border-primary"
              onChange={(event) => setApprovalFilter(event.target.value as ApprovalFilter)}
              value={approvalFilter}
            >
              <option value="all">全部审批</option>
              <option value="required">必须审批</option>
              <option value="optional">可自动</option>
            </select>
          </div>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>售后事项</TableHead>
              <TableHead>客户</TableHead>
              <TableHead>订单</TableHead>
              <TableHead>风险</TableHead>
              <TableHead>状态</TableHead>
              <TableHead>审批</TableHead>
              <TableHead className="text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredCases.map((item) => (
              <TableRow
                className={cn(item.id === selectedId && "bg-accent/60")}
                key={item.id}
                onClick={() => openDetail(item)}
              >
                <TableCell className="max-w-[320px]">
                  <div className="font-medium">{item.title}</div>
                  <p className="mt-1 truncate text-xs text-muted-foreground">{caseTypeLabels[item.case_type] ?? item.case_type}</p>
                </TableCell>
                <TableCell>{item.customer_name}</TableCell>
                <TableCell>{item.order_external_id}</TableCell>
                <TableCell>
                  <Badge tone={riskTone[item.risk_level]}>{riskLabels[item.risk_level]}</Badge>
                </TableCell>
                <TableCell>
                  <Badge>{decisionOverrides[item.id] ?? statusLabels[item.status] ?? item.status}</Badge>
                </TableCell>
                <TableCell>
                  <Badge tone={item.approval_required ? "amber" : "green"}>
                    {item.approval_required ? "必须审批" : "可自动"}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <Button onClick={() => openDetail(item)} type="button" variant="ghost">
                    查看
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        {filteredCases.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-2 px-6 py-12 text-center text-sm text-muted-foreground">
            <ShieldQuestion className="h-5 w-5" />
            <p>没有匹配当前筛选条件的售后任务。</p>
          </div>
        ) : null}
      </Card>

      <DetailDrawer
        description={selected ? `${selected.platform} / 订单 ${selected.order_external_id} / ${selected.created_at}` : undefined}
        footer={
          selected ? (
            <div className="grid gap-2 sm:grid-cols-3">
              <Button
                disabled={pendingAction !== null}
                onClick={() => handleDecision("approved", "accepted", "已采纳")}
                type="button"
              >
                <CheckCircle2 className="mr-2 h-4 w-4" />
                {pendingAction === "accepted" ? "保存中" : "采纳建议"}
              </Button>
              <Button
                disabled={pendingAction !== null}
                onClick={() => handleDecision("needs_more_info", "edited", "已修改")}
                type="button"
                variant="secondary"
              >
                <FilePenLine className="mr-2 h-4 w-4" />
                {pendingAction === "edited" ? "保存中" : "修改方案"}
              </Button>
              <Button
                disabled={pendingAction !== null}
                onClick={() => handleDecision("rejected", "rejected", "已拒绝")}
                type="button"
                variant="ghost"
              >
                <XCircle className="mr-2 h-4 w-4" />
                {pendingAction === "rejected" ? "保存中" : "拒绝建议"}
              </Button>
            </div>
          ) : null
        }
        onClose={() => setDrawerOpen(false)}
        open={drawerOpen && Boolean(selected)}
        title={selected ? selected.title : "售后详情"}
      >
        {selected ? (
          <div className="space-y-5">
            {actionFeedback ? (
              <div
                className={cn(
                  "rounded-md border px-4 py-3 text-sm",
                  actionFeedback.tone === "success"
                    ? "border-primary/30 bg-primary/10 text-foreground"
                    : "border-destructive/30 bg-destructive/10 text-destructive"
                )}
                role="status"
              >
                {actionFeedback.message}
              </div>
            ) : null}
            <section className="rounded-md border border-border bg-background p-4">
              <div className="flex flex-wrap items-center gap-2">
                <Badge tone={riskTone[selected.risk_level]}>{riskLabels[selected.risk_level]}</Badge>
                <Badge>{caseTypeLabels[selected.case_type] ?? selected.case_type}</Badge>
                <Badge tone={selected.approval_required ? "amber" : "green"}>
                  {selected.approval_required ? "必须审批" : "可自动"}
                </Badge>
              </div>
              <p className="mt-4 text-sm leading-6">{selected.description}</p>
              <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
                <InfoItem label="客户" value={selected.customer_name} />
                <InfoItem label="平台" value={selected.platform} />
                <InfoItem label="订单" value={selected.order_external_id} />
                <InfoItem label="当前状态" value={decisionOverrides[selected.id] ?? statusLabels[selected.status] ?? selected.status} />
              </dl>
            </section>

            <section className="rounded-md border border-border bg-background p-4">
              <div className="flex items-center gap-2 text-sm font-semibold">
                <ShieldCheck className="h-4 w-4 text-primary" />
                AI 售后建议
              </div>
              <p className="mt-3 text-sm leading-6 text-muted-foreground">{selected.ai_suggestion}</p>
            </section>

            <section>
              <label className="text-sm font-medium" htmlFor="merchant-note">
                商家处理备注
              </label>
              <textarea
                className="mt-2 min-h-32 w-full rounded-md border border-border bg-background p-3 text-sm leading-6 outline-none transition focus:border-primary"
                id="merchant-note"
                onChange={(event) => setMerchantNotes((current) => ({ ...current, [selected.id]: event.target.value }))}
                placeholder="记录商家最终判断、补偿方案或拒绝原因"
                value={merchantNotes[selected.id] ?? ""}
              />
              <p className="mt-2 text-xs leading-5 text-muted-foreground">备注和最终动作会作为售后决策样本，用于后续训练规则和工作流程（Workflow）。</p>
            </section>
          </div>
        ) : null}
      </DetailDrawer>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <Card className="p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </Card>
  );
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className="mt-1 font-medium">{value}</dd>
    </div>
  );
}
