import Link from "next/link";
import { ArrowRight, CircleAlert, Gauge, ShieldCheck } from "lucide-react";
import type { EvaluationMetric, EvaluationSummary } from "@/shared/api/types";
import { Badge } from "@/shared/ui/badge";
import { Card } from "@/shared/ui/card";

const statusText: Record<EvaluationMetric["status"], string> = {
  blocked: "阻塞",
  good: "达标",
  warning: "需要改进"
};

export function EvaluationView({ summary }: { summary: EvaluationSummary }) {
  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 border-b border-border pb-5 lg:flex-row lg:items-end">
        <div>
          <p className="text-sm font-medium text-primary">Evaluation Engine V0.1</p>
          <h1 className="mt-2 text-3xl font-semibold">AI 团队评分</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            这里告诉老板：AI 今天到底能不能用、能省多少钱、哪里还不能放权。它不是报表，而是是否继续试用的判断依据。
          </p>
        </div>
        <Link className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground" href="/training-center">
          去训练中心
          <ArrowRight aria-hidden className="ml-2 h-4 w-4" />
        </Link>
      </header>

      <section className="grid gap-4 lg:grid-cols-[1.1fr_2fr]">
        <Card className="p-5">
          <div className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-md bg-primary/10 text-primary">
              <Gauge aria-hidden className="h-5 w-5" />
            </span>
            <div>
              <p className="text-xs text-muted-foreground">综合评分</p>
              <p className="text-3xl font-semibold">{summary.overall_score}</p>
            </div>
          </div>
          <p className="mt-4 text-sm leading-6 text-muted-foreground">{summary.readiness_level}</p>
          <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
            <MiniStat label="回放样本" value={`${summary.evaluated_cases}`} />
            <MiniStat label="月节省试算" value={`¥${summary.estimated_monthly_saving_yuan}`} />
          </div>
        </Card>

        <div className="grid gap-3 md:grid-cols-2">
          {summary.metrics.map((metric) => (
            <MetricCard key={metric.id} metric={metric} />
          ))}
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <Card className="p-5">
          <div className="flex items-center gap-2">
            <CircleAlert aria-hidden className="h-4 w-4 text-warning" />
            <h2 className="font-semibold">当前不能直接替代人的原因</h2>
          </div>
          <div className="mt-4 space-y-3">
            {summary.blockers.map((item) => (
              <p key={item} className="rounded-md bg-muted p-3 text-sm leading-6 text-muted-foreground">{item}</p>
            ))}
          </div>
        </Card>
        <Card className="p-5">
          <div className="flex items-center gap-2">
            <ShieldCheck aria-hidden className="h-4 w-4 text-primary" />
            <h2 className="font-semibold">下一步怎么提高评分</h2>
          </div>
          <div className="mt-4 space-y-3">
            {summary.next_actions.map((item) => (
              <p key={item} className="rounded-md bg-muted p-3 text-sm leading-6 text-muted-foreground">{item}</p>
            ))}
          </div>
        </Card>
      </section>
    </div>
  );
}

function MetricCard({ metric }: { metric: EvaluationMetric }) {
  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium">{metric.label}</p>
          <p className="mt-2 text-2xl font-semibold">{formatScore(metric.score)}</p>
        </div>
        <Badge tone={metric.status === "good" ? "green" : "amber"}>{statusText[metric.status]}</Badge>
      </div>
      <p className="mt-3 text-xs leading-5 text-muted-foreground">{metric.explanation}</p>
    </Card>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border bg-background p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 font-semibold">{value}</p>
    </div>
  );
}

function formatScore(value: number) {
  return value <= 1 ? `${Math.round(value * 100)}%` : `${Math.round(value)}`;
}

