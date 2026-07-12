import { BarChart3 } from "lucide-react";
import { Card } from "@/shared/ui/card";
import type { AgentFeedbackMetric } from "@/shared/api/types";

export function DataCollectionView({ metrics }: { metrics: AgentFeedbackMetric[] }) {
  return (
    <div className="space-y-6">
      <header className="border-b border-border pb-5">
        <p className="text-sm font-medium text-primary">系统设置</p>
        <h1 className="mt-2 text-3xl font-semibold">数据采集目标</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
          商家试用阶段优先收集真实问题、AI 回复、商家修正、售后决策和工作指标（KPI）反馈。
        </p>
      </header>

      <section className="grid gap-4 lg:grid-cols-3">
        {metrics.map((metric) => (
          <Card className="p-5" key={metric.id}>
            <div className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-primary" />
              <h2 className="text-base font-semibold">{metric.metric_name}</h2>
            </div>
            <div className="mt-5 text-3xl font-semibold">{metric.metric_value}%</div>
            <p className="mt-2 text-sm text-muted-foreground">
              权重 {(metric.weight * 100).toFixed(0)}%，用于衡量试用数据价值。
            </p>
          </Card>
        ))}
      </section>
    </div>
  );
}
