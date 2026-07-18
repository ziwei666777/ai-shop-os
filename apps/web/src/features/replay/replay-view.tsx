import Link from "next/link";
import { ArrowRight, CheckCircle2, Clock3, ShieldAlert } from "lucide-react";
import type { ReplayResult, ReplaySummary } from "@/shared/api/types";
import { Badge } from "@/shared/ui/badge";
import { Card } from "@/shared/ui/card";

const decisionLabels: Record<ReplayResult["ai_decision"], string> = {
  approval_required: "必须审批",
  auto_reply: "可自动回复",
  human_review: "人工接管",
  operation_suggestion: "运营建议"
};

const caseTypeLabels: Record<ReplayResult["case_type"], string> = {
  after_sale_case: "售后",
  customer_message: "客服",
  operation_signal: "运营"
};

export function ReplayView({ summary }: { summary: ReplaySummary }) {
  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 border-b border-border pb-5 lg:flex-row lg:items-end">
        <div>
          <p className="text-sm font-medium text-primary">Replay Engine V0.1</p>
          <h1 className="mt-2 text-3xl font-semibold">历史工作回放验证</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            Replay 不是聊天演示，而是拿历史客服、售后、运营样本重新跑一遍 AI，再对比人工结果，判断 AI 是否真的能省人、省钱、降低风险。
          </p>
        </div>
        <Link className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground" href="/commerce-dataset">
          准备更多历史数据
          <ArrowRight aria-hidden className="ml-2 h-4 w-4" />
        </Link>
      </header>

      <section className="grid gap-3 md:grid-cols-5">
        <Metric label="回放样本" value={`${summary.total_cases}`} hint="客服 / 售后 / 运营" />
        <Metric label="判断准确率" value={formatPercent(summary.accuracy)} hint={`${summary.correct_cases}/${summary.total_cases} 条一致`} />
        <Metric label="自动处理率" value={formatPercent(summary.auto_rate)} hint="低风险重复工作" />
        <Metric label="人工接管率" value={formatPercent(summary.manual_rate)} hint="高风险不越权" />
        <Metric label="预估节省" value={`¥${summary.estimated_saving_yuan}`} hint={`${summary.saved_minutes} 分钟`} />
      </section>

      <Card className="p-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-lg font-semibold">老板应该怎么看这张表</h2>
            <p className="mt-1 text-sm leading-6 text-muted-foreground">
              绿色代表 AI 判断和历史人工结果一致；橙色代表 AI 正确要求人工审批。下一阶段接入真实商家数据后，这里会变成是否能替代岗位的核心证据。
            </p>
          </div>
          <Badge tone="amber">当前为 V0 样例回放</Badge>
        </div>
      </Card>

      <section className="grid gap-4">
        {summary.results.map((result) => (
          <ReplayResultCard key={result.id} result={result} />
        ))}
      </section>
    </div>
  );
}

function ReplayResultCard({ result }: { result: ReplayResult }) {
  return (
    <Card className="p-5">
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-start">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone={result.is_correct ? "green" : "amber"}>{result.is_correct ? "判断一致" : "需要训练"}</Badge>
            <Badge tone={result.requires_human ? "amber" : "green"}>{decisionLabels[result.ai_decision]}</Badge>
            <span className="text-xs text-muted-foreground">{caseTypeLabels[result.case_type]}</span>
          </div>
          <h2 className="mt-3 text-lg font-semibold">{result.title}</h2>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">{result.input_text}</p>
        </div>
        <div className="flex min-w-32 items-center gap-2 rounded-md border border-border bg-background px-3 py-2 text-sm">
          <Clock3 aria-hidden className="h-4 w-4 text-primary" />
          省 {result.saved_minutes} 分钟
        </div>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <div className="rounded-md border border-border bg-background p-4">
          <p className="text-xs font-medium text-muted-foreground">历史人工处理</p>
          <p className="mt-2 text-sm leading-6">{result.human_result}</p>
        </div>
        <div className="rounded-md border border-border bg-background p-4">
          <p className="text-xs font-medium text-muted-foreground">AI 重新处理</p>
          <p className="mt-2 text-sm leading-6">{result.ai_result}</p>
        </div>
      </div>

      <div className="mt-4 flex items-start gap-2 rounded-md bg-muted p-3 text-sm text-muted-foreground">
        {result.requires_human ? <ShieldAlert aria-hidden className="mt-0.5 h-4 w-4 text-warning" /> : <CheckCircle2 aria-hidden className="mt-0.5 h-4 w-4 text-primary" />}
        <span>{result.evaluation_note}</span>
      </div>
    </Card>
  );
}

function Metric({ hint, label, value }: { hint: string; label: string; value: string }) {
  return (
    <Card className="p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
      <p className="mt-2 text-xs leading-5 text-muted-foreground">{hint}</p>
    </Card>
  );
}

function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}
