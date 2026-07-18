import Link from "next/link";
import { ArrowRight, FlaskConical, ShieldAlert } from "lucide-react";
import type { SimulationScenario, SimulationSummary } from "@/shared/api/types";
import { Badge } from "@/shared/ui/badge";
import { Card } from "@/shared/ui/card";

const decisionLabels: Record<SimulationScenario["ai_decision"], string> = {
  approval_required: "必须审批",
  auto_reply: "可自动回复",
  human_review: "人工接管",
  operation_suggestion: "运营建议"
};

export function SimulationView({ summary }: { summary: SimulationSummary }) {
  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 border-b border-border pb-5 lg:flex-row lg:items-end">
        <div>
          <p className="text-sm font-medium text-primary">Simulation Engine V0.1</p>
          <h1 className="mt-2 text-3xl font-semibold">模拟客户压测</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            在真实商家上线前，先用模拟客户测试客服、售后和运营边界。目标不是好看，而是提前发现 AI 会不会乱承诺、乱退款、乱投流。
          </p>
        </div>
        <Link className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground" href="/evaluation">
          回到 AI 评分
          <ArrowRight aria-hidden className="ml-2 h-4 w-4" />
        </Link>
      </header>

      <section className="grid gap-3 md:grid-cols-5">
        <Metric label="模拟场景" value={`${summary.total_scenarios}`} />
        <Metric label="自动回复" value={`${summary.auto_reply_count}`} />
        <Metric label="必须审批" value={`${summary.approval_required_count}`} />
        <Metric label="人工接管" value={`${summary.manual_review_count}`} />
        <Metric label="日压测能力" value={`${summary.estimated_daily_capacity}+`} />
      </section>

      <Card className="p-5">
        <div className="flex items-start gap-3">
          <FlaskConical aria-hidden className="mt-0.5 h-5 w-5 text-primary" />
          <div>
            <h2 className="font-semibold">老板应该怎么看模拟结果</h2>
            <p className="mt-1 text-sm leading-6 text-muted-foreground">
              如果高风险场景全部进入审批，说明 AI 的权限边界安全；如果低风险场景可以自动回复，说明它开始有节省人工的价值。
            </p>
          </div>
        </div>
      </Card>

      <section className="grid gap-4">
        {summary.scenarios.map((scenario) => (
          <ScenarioCard key={scenario.id} scenario={scenario} />
        ))}
      </section>

      <Card className="p-5">
        <div className="flex items-center gap-2">
          <ShieldAlert aria-hidden className="h-4 w-4 text-warning" />
          <h2 className="font-semibold">上线前提醒</h2>
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {summary.warnings.map((warning) => (
            <p key={warning} className="rounded-md bg-muted p-3 text-sm leading-6 text-muted-foreground">{warning}</p>
          ))}
        </div>
      </Card>
    </div>
  );
}

function ScenarioCard({ scenario }: { scenario: SimulationScenario }) {
  return (
    <Card className="p-5">
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-start">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone={scenario.risk_level === "high" ? "amber" : "green"}>{scenario.risk_level === "high" ? "高风险" : "可控风险"}</Badge>
            <Badge tone={scenario.ai_decision === "auto_reply" ? "green" : "amber"}>{decisionLabels[scenario.ai_decision]}</Badge>
            <span className="text-xs text-muted-foreground">{scenario.customer_type}</span>
          </div>
          <p className="mt-3 text-lg font-semibold">{scenario.message}</p>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">{scenario.expected_behavior}</p>
        </div>
        <div className="rounded-md border border-border bg-background px-3 py-2 text-sm">省 {scenario.estimated_minutes} 分钟</div>
      </div>
    </Card>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <Card className="p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </Card>
  );
}

