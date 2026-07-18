"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { MessageSquare, Search, Send, ShieldAlert, SlidersHorizontal, UserCheck } from "lucide-react";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { DetailDrawer } from "@/shared/ui/detail-drawer";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import { draftCustomerReply, recordLearningEvent, sendCustomerReply, takeoverCustomerMessage } from "@/shared/api/client";
import type { CustomerInboxItem, DraftReply } from "@/shared/api/types";
import { cn } from "@/shared/lib/utils";

type PlatformFilter = "all" | CustomerInboxItem["platform"];
type DecisionFilter = "all" | CustomerInboxItem["automation_decision"];

const decisionLabels = {
  auto_reply: "可自动",
  human_review: "需人工"
} as const;

const intentLabels: Record<string, string> = {
  compensation: "赔偿",
  complaint: "投诉",
  faq: "FAQ",
  logistics: "物流",
  order: "订单",
  refund: "退款",
  unknown: "未知"
};

function buildLocalDraft(message: CustomerInboxItem): string {
  if (message.automation_decision === "human_review") {
    return "这个问题涉及退款、赔偿或投诉，需要商家确认后再回复。";
  }

  if (message.intent === "logistics") {
    return `您好，您的订单 ${message.order_external_id} 当前状态是：${message.logistics_status}。我会继续帮您关注物流更新。`;
  }

  if (message.intent === "order") {
    return `您好，您的订单 ${message.order_external_id} 已查询到，我们会按订单状态继续为您跟进。`;
  }

  return "您好，这款商品当前可以正常咨询和下单。具体尺码库存我会按页面实时库存为您确认。";
}

function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}

export function CustomerWorkbenchView({ inbox, initialSelectedId }: { inbox: CustomerInboxItem[]; initialSelectedId?: string }) {
  const [decisionFilter, setDecisionFilter] = useState<DecisionFilter>("all");
  const [draftOverrides, setDraftOverrides] = useState<Record<string, string>>({});
  const [draftReplies, setDraftReplies] = useState<Record<string, DraftReply>>({});
  const [platformFilter, setPlatformFilter] = useState<PlatformFilter>("all");
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState(initialSelectedId && inbox.some((item) => item.id === initialSelectedId) ? initialSelectedId : inbox[0]?.id ?? "");
  const [statusOverrides, setStatusOverrides] = useState<Record<string, string>>({});
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [pendingAction, setPendingAction] = useState<string | null>(null);
  const [actionFeedback, setActionFeedback] = useState<{ tone: "success" | "error"; message: string } | null>(null);

  const selected = inbox.find((item) => item.id === selectedId) ?? inbox[0];
  const selectedServerDraft = selected ? draftReplies[selected.id] : undefined;
  const selectedBaselineDraft = selected ? selectedServerDraft?.content ?? buildLocalDraft(selected) : "";
  const selectedDraft = selected ? draftOverrides[selected.id] ?? selectedBaselineDraft : "";

  const filteredInbox = useMemo(() => {
    const keyword = query.trim().toLowerCase();

    return inbox.filter((item) => {
      const matchesPlatform = platformFilter === "all" || item.platform === platformFilter;
      const matchesDecision = decisionFilter === "all" || item.automation_decision === decisionFilter;
      const matchesKeyword =
        !keyword ||
        [item.customer_name, item.content, item.intent, item.order_external_id ?? "", item.logistics_status ?? ""]
          .join(" ")
          .toLowerCase()
          .includes(keyword);

      return matchesPlatform && matchesDecision && matchesKeyword;
    });
  }, [decisionFilter, inbox, platformFilter, query]);

  const total = inbox.length;
  const autoReplyCount = inbox.filter((item) => item.automation_decision === "auto_reply").length;
  const humanReviewCount = inbox.filter((item) => item.automation_decision === "human_review").length;
  const averageConfidence = total ? inbox.reduce((sum, item) => sum + item.confidence, 0) / total : 0;

  useEffect(() => {
    let cancelled = false;

    async function loadDraft() {
      if (!selected || draftReplies[selected.id]) {
        return;
      }

      const draft = await draftCustomerReply(selected.id);
      if (!cancelled && draft) {
        setDraftReplies((current) => ({ ...current, [selected.id]: draft }));
      }
    }

    void loadDraft();

    return () => {
      cancelled = true;
    };
  }, [draftReplies, selected]);

  function openDetail(item: CustomerInboxItem) {
    setSelectedId(item.id);
    setActionFeedback(null);
    setDrawerOpen(true);
  }

  function selectMessage(item: CustomerInboxItem) {
    setSelectedId(item.id);
    setActionFeedback(null);
  }

  async function handleSend() {
    if (!selected) {
      return;
    }

    setPendingAction("send");
    setActionFeedback(null);
    const result = await sendCustomerReply(selected.id, selectedDraft.trim());

    if (result.error) {
      setActionFeedback({ tone: "error", message: result.error });
      setPendingAction(null);
      return;
    }

    const baseDraft = draftReplies[selected.id]?.content ?? buildLocalDraft(selected);
    const wasEdited = selectedDraft.trim() !== baseDraft;
    if (wasEdited) {
      const learning = await recordLearningEvent({
        source_type: "message",
        source_id: selected.id,
        agent_id: "ai-customer",
        action: "edited",
        original_content: baseDraft,
        final_content: selectedDraft.trim()
      });

      if (learning.error) {
        setActionFeedback({ tone: "error", message: `回复已发送，但学习样本记录失败：${learning.error}` });
        setStatusOverrides((current) => ({ ...current, [selected.id]: "已发送" }));
        setPendingAction(null);
        return;
      }
    }

    setStatusOverrides((current) => ({ ...current, [selected.id]: "已发送" }));
    setActionFeedback({ tone: "success", message: wasEdited ? "回复已发送，商家修改已记录。" : "回复已发送。" });
    setPendingAction(null);
  }

  async function handleTakeover() {
    if (!selected) {
      return;
    }

    setPendingAction("takeover");
    setActionFeedback(null);
    const result = await takeoverCustomerMessage(selected.id);
    setPendingAction(null);

    if (result.error) {
      setActionFeedback({ tone: "error", message: result.error });
      return;
    }

    setStatusOverrides((current) => ({ ...current, [selected.id]: "人工接管" }));
    setActionFeedback({ tone: "success", message: "已切换为人工接管，AI 将停止自动发送。" });
  }

  async function handleRecordEdit() {
    if (!selected) {
      return;
    }

    const finalContent = selectedDraft.trim();
    const baseDraft = draftReplies[selected.id]?.content ?? buildLocalDraft(selected);
    if (!finalContent || finalContent === baseDraft) {
      setActionFeedback({ tone: "error", message: "请先修改回复内容，再记录学习样本。" });
      return;
    }

    setPendingAction("learn");
    setActionFeedback(null);
    const result = await recordLearningEvent({
      source_type: "message",
      source_id: selected.id,
      agent_id: "ai-customer",
      action: selected.automation_decision === "human_review" ? "manual_answered" : "edited",
      original_content: baseDraft,
      final_content: finalContent
    });
    setPendingAction(null);

    if (result.error) {
      setActionFeedback({ tone: "error", message: result.error });
      return;
    }

    setStatusOverrides((current) => ({ ...current, [selected.id]: "已记录修改" }));
    setActionFeedback({ tone: "success", message: "商家修改已进入学习记录。" });
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 border-b border-border pb-5 md:flex-row md:items-end">
        <div>
          <p className="text-sm font-medium text-primary">AI 客服工作台</p>
          <h1 className="mt-2 text-3xl font-semibold">AI客服商家试用台</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
            平台消息统一进入收件箱，AI 只自动处理 FAQ、订单、物流；退款、赔偿、投诉必须人工确认。
          </p>
        </div>
        <Badge tone="green">客服问答修正 60%</Badge>
      </header>

      <section className="grid gap-3 md:grid-cols-4">
        <MetricCard label="消息总量" value={`${total}`} />
        <MetricCard label="可自动回复" value={`${autoReplyCount}`} />
        <MetricCard label="人工确认" value={`${humanReviewCount}`} />
        <MetricCard label="平均置信度" value={formatPercent(averageConfidence)} />
      </section>

      <Card className="overflow-hidden">
        <div className="flex flex-col gap-3 border-b border-border p-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4 text-primary" />
            <h2 className="text-base font-semibold">平台消息收件箱</h2>
          </div>

          <div className="grid gap-2 sm:grid-cols-[minmax(220px,1fr)_150px_150px]">
            <label className="relative">
              <Search aria-hidden className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                className="h-10 w-full rounded-md border border-border bg-background pl-9 pr-3 text-sm outline-none transition focus:border-primary"
                onChange={(event) => setQuery(event.target.value)}
                placeholder="搜索客户、订单、问题"
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
              onChange={(event) => setDecisionFilter(event.target.value as DecisionFilter)}
              value={decisionFilter}
            >
              <option value="all">全部状态</option>
              <option value="auto_reply">可自动</option>
              <option value="human_review">需人工</option>
            </select>
          </div>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>客户</TableHead>
              <TableHead>消息</TableHead>
              <TableHead>意图</TableHead>
              <TableHead>置信度</TableHead>
              <TableHead>平台</TableHead>
              <TableHead>处理</TableHead>
              <TableHead className="text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredInbox.map((item) => (
              <TableRow
                className={cn(item.id === selectedId && "bg-accent/60")}
                key={item.id}
                onClick={() => selectMessage(item)}
              >
                <TableCell>
                  <div className="font-medium">{item.customer_name}</div>
                  <div className="mt-1 text-xs text-muted-foreground">{item.order_external_id ?? "未绑定订单"}</div>
                </TableCell>
                <TableCell className="max-w-[320px]">
                  <p className="truncate text-sm">{item.content}</p>
                  <p className="mt-1 truncate text-xs text-muted-foreground">{item.channel}</p>
                </TableCell>
                <TableCell>{intentLabels[item.intent] ?? item.intent}</TableCell>
                <TableCell>{formatPercent(item.confidence)}</TableCell>
                <TableCell className="capitalize">{item.platform}</TableCell>
                <TableCell>
                  <Badge tone={item.automation_decision === "auto_reply" ? "green" : "amber"}>
                    {statusOverrides[item.id] ?? decisionLabels[item.automation_decision]}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <Link
                    className="inline-flex h-10 items-center justify-center rounded-md px-4 text-sm font-medium text-muted-foreground transition hover:bg-accent hover:text-foreground"
                    href={`/ai-employees/ai-customer/workbench?message=${encodeURIComponent(item.id)}`}
                    onClick={() => selectMessage(item)}
                  >
                    查看
                  </Link>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        {filteredInbox.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-2 px-6 py-12 text-center text-sm text-muted-foreground">
            <SlidersHorizontal className="h-5 w-5" />
            <p>没有匹配当前筛选条件的消息。</p>
          </div>
        ) : null}
      </Card>

      {selected ? (
        <Card className="p-5">
          <div className="flex flex-col justify-between gap-3 border-b border-border pb-4 md:flex-row md:items-start">
            <div>
              <p className="text-sm font-medium text-primary">当前选中消息</p>
              <h2 className="mt-1 text-xl font-semibold">{selected.customer_name}</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                {selected.platform} / {selected.channel} / {selected.created_at}
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge tone={selected.automation_decision === "auto_reply" ? "green" : "amber"}>
                {decisionLabels[selected.automation_decision]}
              </Badge>
              <Badge>{intentLabels[selected.intent] ?? selected.intent}</Badge>
              <Badge>{formatPercent(selected.confidence)}</Badge>
            </div>
          </div>

          <div className="mt-5 grid gap-5 lg:grid-cols-[1fr_1fr]">
            <section className="rounded-md border border-border bg-background p-4">
              <h3 className="text-sm font-semibold">客户原话</h3>
              <p className="mt-3 text-sm leading-6">{selected.content}</p>
              <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
                <InfoItem label="订单" value={selected.order_external_id ?? "未绑定"} />
                <InfoItem label="物流" value={selected.logistics_status ?? "未查询"} />
              </dl>
            </section>

            <section>
              <label className="text-sm font-semibold" htmlFor="customer-draft-inline">
                AI 回复草稿
              </label>
              <textarea
                className="mt-3 min-h-36 w-full rounded-md border border-border bg-background p-3 text-sm leading-6 outline-none transition focus:border-primary"
                id="customer-draft-inline"
                onChange={(event) => setDraftOverrides((current) => ({ ...current, [selected.id]: event.target.value }))}
                value={selectedDraft}
              />
              <p className="mt-2 text-xs leading-5 text-muted-foreground">看一眼，正确就发；不正确就改，改完让 AI 学习。</p>
            </section>
          </div>

          {selectedServerDraft ? (
            <section className="mt-5 grid gap-3 rounded-md border border-border bg-accent/40 p-4 text-sm sm:grid-cols-2 lg:grid-cols-4">
              <InfoItem label="命中知识" value={selectedServerDraft.knowledge_hit ?? "未命中，等待商家补充"} />
              <InfoItem label="命中记忆" value={selectedServerDraft.memory_hit ?? "未命中，等待沉淀"} />
              <InfoItem label="预计节省时间" value={`${selectedServerDraft.saved_minutes} 分钟`} />
              <InfoItem label="预计节省成本" value={`¥${selectedServerDraft.estimated_saving_yuan}`} />
              <div className="sm:col-span-2 lg:col-span-4">
                <dt className="text-xs text-muted-foreground">AI 判断原因</dt>
                <dd className="mt-1 leading-6">{selectedServerDraft.reason}</dd>
              </div>
            </section>
          ) : (
            <section className="mt-5 rounded-md border border-border bg-accent/40 p-4 text-sm text-muted-foreground">
              正在读取 AI 草稿、知识命中和节省成本估算。
            </section>
          )}

          {actionFeedback ? (
            <div
              className={cn(
                "mt-5 rounded-md border px-4 py-3 text-sm",
                actionFeedback.tone === "success"
                  ? "border-primary/30 bg-primary/10 text-foreground"
                  : "border-destructive/30 bg-destructive/10 text-destructive"
              )}
              role="status"
            >
              {actionFeedback.message}
            </div>
          ) : null}

          {selected.automation_decision === "human_review" ? (
            <div className="mt-5 flex items-start gap-3 rounded-md border border-warning/30 bg-warning/10 p-4 text-sm text-muted-foreground">
              <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-warning" />
              <span>命中高风险规则，AI 不会自动发送，也不会承诺退款、赔偿金额或投诉处理结果。</span>
            </div>
          ) : null}

          <div className="mt-5 flex flex-wrap gap-3">
            <Button disabled={selected.automation_decision !== "auto_reply" || pendingAction !== null} onClick={handleSend} type="button">
              <Send className="mr-2 h-4 w-4" />
              {pendingAction === "send" ? "发送中" : "自动发送"}
            </Button>
            <Button disabled={pendingAction !== null} onClick={handleTakeover} type="button" variant="secondary">
              <UserCheck className="mr-2 h-4 w-4" />
              {pendingAction === "takeover" ? "处理中" : "人工接管"}
            </Button>
            <Button disabled={pendingAction !== null} onClick={handleRecordEdit} type="button" variant="ghost">
              {pendingAction === "learn" ? "记录中" : "记录商家修改"}
            </Button>
          </div>
        </Card>
      ) : null}

      <DetailDrawer
        description={selected ? `${selected.platform} / ${selected.channel} / ${selected.created_at}` : undefined}
        footer={
          selected ? (
            <div className="flex flex-wrap gap-3">
              <Button disabled={selected.automation_decision !== "auto_reply" || pendingAction !== null} onClick={handleSend} type="button">
                <Send className="mr-2 h-4 w-4" />
                {pendingAction === "send" ? "发送中" : "自动发送"}
              </Button>
              <Button disabled={pendingAction !== null} onClick={handleTakeover} type="button" variant="secondary">
                <UserCheck className="mr-2 h-4 w-4" />
                {pendingAction === "takeover" ? "处理中" : "人工接管"}
              </Button>
              <Button disabled={pendingAction !== null} onClick={handleRecordEdit} type="button" variant="ghost">
                {pendingAction === "learn" ? "记录中" : "记录商家修改"}
              </Button>
            </div>
          ) : null
        }
        onClose={() => setDrawerOpen(false)}
        open={drawerOpen && Boolean(selected)}
        title={selected ? selected.customer_name : "消息详情"}
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
                <Badge tone={selected.automation_decision === "auto_reply" ? "green" : "amber"}>
                  {decisionLabels[selected.automation_decision]}
                </Badge>
                <Badge>{intentLabels[selected.intent] ?? selected.intent}</Badge>
                <Badge>{formatPercent(selected.confidence)}</Badge>
              </div>
              <p className="mt-4 text-sm leading-6">{selected.content}</p>
              <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
                <InfoItem label="订单" value={selected.order_external_id ?? "未绑定"} />
                <InfoItem label="物流" value={selected.logistics_status ?? "未查询"} />
              </dl>
            </section>

            <section>
              <label className="text-sm font-medium" htmlFor="customer-draft">
                AI 回复草稿
              </label>
              <textarea
                className="mt-2 min-h-36 w-full rounded-md border border-border bg-background p-3 text-sm leading-6 outline-none transition focus:border-primary"
                id="customer-draft"
                onChange={(event) => setDraftOverrides((current) => ({ ...current, [selected.id]: event.target.value }))}
                value={selectedDraft}
              />
              <p className="mt-2 text-xs leading-5 text-muted-foreground">商家修改会作为学习记录（Learning Event）的采集样本。</p>
            </section>

            {selectedServerDraft ? (
              <section className="grid gap-3 rounded-md border border-border bg-accent/40 p-4 text-sm sm:grid-cols-2">
                <InfoItem label="命中知识" value={selectedServerDraft.knowledge_hit ?? "未命中，等待商家补充"} />
                <InfoItem label="命中记忆" value={selectedServerDraft.memory_hit ?? "未命中，等待沉淀"} />
                <InfoItem label="预计节省时间" value={`${selectedServerDraft.saved_minutes} 分钟`} />
                <InfoItem label="预计节省成本" value={`¥${selectedServerDraft.estimated_saving_yuan}`} />
                <div className="sm:col-span-2">
                  <dt className="text-xs text-muted-foreground">AI 判断原因</dt>
                  <dd className="mt-1 leading-6">{selectedServerDraft.reason}</dd>
                </div>
              </section>
            ) : (
              <section className="rounded-md border border-border bg-accent/40 p-4 text-sm text-muted-foreground">
                正在读取 AI 草稿、知识命中和节省成本估算。
              </section>
            )}

            {selected.automation_decision === "human_review" ? (
              <div className="flex items-start gap-3 rounded-md border border-warning/30 bg-warning/10 p-4 text-sm text-muted-foreground">
                <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-warning" />
                <span>命中高风险规则，AI 不会自动发送，也不会承诺退款、赔偿金额或投诉处理结果。</span>
              </div>
            ) : null}
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
