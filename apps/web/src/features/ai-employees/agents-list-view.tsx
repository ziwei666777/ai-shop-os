"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Badge } from "@/shared/ui/badge";
import { Card } from "@/shared/ui/card";
import type { Agent } from "@/shared/api/types";
import { getAgentDisplayName } from "@/shared/lib/agent-labels";

export function AgentsListView({ agents }: { agents: Agent[] }) {
  return (
    <div className="space-y-6">
      <header className="border-b border-border pb-5">
        <p className="text-sm font-medium text-primary">AI 员工管理</p>
        <h1 className="mt-2 text-3xl font-semibold">AI 员工</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
          每名 AI 员工都拥有独立的工作指令（Prompt）、记忆（Memory）、知识库、工作流程和工作指标。
        </p>
      </header>

      <section className="grid gap-4 lg:grid-cols-2">
        {agents.map((agent, index) => (
          <motion.div
            animate={{ opacity: 1, y: 0 }}
            initial={{ opacity: 0, y: 10 }}
            key={agent.id}
            transition={{ delay: index * 0.04 }}
          >
            <Link href={`/ai-employees/${agent.id}`}>
              <Card className="h-full p-5 transition hover:border-primary/40">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h2 className="text-lg font-semibold">{getAgentDisplayName(agent.id, agent.name)}</h2>
                    <p className="mt-2 text-sm leading-6 text-muted-foreground">{agent.description}</p>
                  </div>
                  <Badge tone={agent.status === "online" ? "green" : "neutral"}>
                    {agent.status === "online" ? "在线" : "未启用"}
                  </Badge>
                </div>
                <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
                  <div className="rounded-md bg-muted p-3">
                    <div className="text-muted-foreground">今日处理</div>
                    <div className="mt-1 text-lg font-semibold">{agent.today_handled_count}</div>
                  </div>
                  <div className="rounded-md bg-muted p-3">
                    <div className="text-muted-foreground">工作指标（KPI）</div>
                    <div className="mt-1 text-lg font-semibold">{agent.kpi_score}</div>
                  </div>
                </div>
              </Card>
            </Link>
          </motion.div>
        ))}
      </section>
    </div>
  );
}
