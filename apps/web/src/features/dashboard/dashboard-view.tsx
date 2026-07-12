"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Badge } from "@/shared/ui/badge";
import { Card } from "@/shared/ui/card";
import type { DashboardSummary } from "@/shared/api/types";
import { getAgentDisplayName } from "@/shared/lib/agent-labels";

const priorityTone = {
  high: "amber",
  medium: "green",
  low: "neutral"
} as const;

export function DashboardView({ summary }: { summary: DashboardSummary }) {
  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 border-b border-border pb-5 md:flex-row md:items-end">
        <div>
          <p className="text-sm font-medium text-primary">{summary.date}</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-normal">老板首页</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
            AI 老板已把经营数据、异常风险和审批事项整理成今日汇报。
          </p>
        </div>
        <Link
          className="inline-flex h-10 items-center justify-center rounded-md border border-border bg-card px-4 text-sm font-medium transition hover:bg-accent"
          href="/ai-employees/ai-boss"
        >
          查看 AI 老板
        </Link>
      </header>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {summary.metrics.map((metric, index) => (
          <motion.div
            animate={{ opacity: 1, y: 0 }}
            initial={{ opacity: 0, y: 10 }}
            key={metric.id}
            transition={{ delay: index * 0.04 }}
          >
            <Card className="p-5">
              <p className="text-sm text-muted-foreground">{metric.label}</p>
              <div className="mt-3 text-2xl font-semibold">{metric.value}</div>
              <p className="mt-3 text-sm text-primary">{metric.trend}</p>
            </Card>
          </motion.div>
        ))}
      </section>

      <div className="grid gap-5 xl:grid-cols-[1fr_0.82fr]">
        <Card className="p-5">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold">AI 员工状态</h2>
              <p className="mt-1 text-sm text-muted-foreground">所有 AI 员工独立运行，通过工作流程（Workflow）协作。</p>
            </div>
            <Badge tone="green">运行中</Badge>
          </div>
          <div className="mt-5 divide-y divide-border">
            {summary.agents.map((agent) => (
              <Link
                className="block py-4 transition first:pt-0 last:pb-0 hover:text-primary"
                href={`/ai-employees/${agent.id}`}
                key={agent.id}
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h3 className="font-semibold">{getAgentDisplayName(agent.id, agent.name)}</h3>
                    <p className="mt-1 max-w-2xl text-sm leading-6 text-muted-foreground">{agent.description}</p>
                  </div>
                  <Badge tone={agent.status === "online" ? "green" : "neutral"}>
                    {agent.status === "online" ? "在线" : "未启用"}
                  </Badge>
                </div>
                <p className="mt-3 text-sm text-muted-foreground">今日处理：{agent.today_handled_count} 项</p>
              </Link>
            ))}
          </div>
        </Card>

        <Card className="p-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold">今日建议</h2>
              <p className="mt-1 text-sm text-muted-foreground">AI 先分析，老板只审批关键动作。</p>
            </div>
            <div className="min-w-[4rem] rounded-md border border-warning/30 bg-warning/10 px-3 py-2 text-center">
              <div className="text-xl font-semibold text-warning">{summary.pending_approval_count}</div>
              <div className="text-xs text-muted-foreground">待审批</div>
            </div>
          </div>

          <div className="mt-5 space-y-4">
            {summary.suggestions.map((suggestion) => (
              <article className="rounded-md border border-border p-4" key={suggestion.id}>
                <div className="flex items-start justify-between gap-3">
                  <h3 className="font-semibold">{suggestion.title}</h3>
                  <Badge tone={priorityTone[suggestion.priority]}>
                    {suggestion.priority === "high" ? "高优先级" : suggestion.priority === "medium" ? "中优先级" : "低优先级"}
                  </Badge>
                </div>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{suggestion.reason}</p>
              </article>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
