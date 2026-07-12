import Link from "next/link";
import { Badge } from "@/shared/ui/badge";
import { Card } from "@/shared/ui/card";
import type { Agent, AgentLog } from "@/shared/api/types";
import { getAgentDisplayName } from "@/shared/lib/agent-labels";

const capabilitySections = [
  "状态",
  "工作指令（Prompt）",
  "知识库（Knowledge）",
  "记忆（Memory）",
  "工作流程（Workflow）",
  "可调用工具（Tools）",
  "工作记录（Logs）",
  "学习记录（Learning）",
  "工作指标（KPI）",
  "后续任务"
];

export function AgentDetailView({ agent, logs }: { agent: Agent; logs: AgentLog[] }) {
  const workbenchHref =
    agent.id === "ai-customer"
      ? "/ai-employees/ai-customer/workbench"
      : agent.id === "ai-after-sale"
        ? "/ai-employees/ai-after-sale/workbench"
        : null;
  const manualHref = agent.id === "ai-customer" ? "/ai-employees/ai-customer/manual" : null;

  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 border-b border-border pb-5 md:flex-row md:items-end">
        <div>
          <p className="text-sm font-medium text-primary">AI 员工详情</p>
          <h1 className="mt-2 text-3xl font-semibold">{getAgentDisplayName(agent.id, agent.name)}</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">{agent.description}</p>
        </div>
        <Badge tone={agent.status === "online" ? "green" : "neutral"}>
          {agent.status === "online" ? "在线" : "未启用"}
        </Badge>
        <div className="flex flex-wrap gap-3">
          {manualHref ? (
            <Link
              className="inline-flex h-10 items-center justify-center rounded-md border border-border bg-card px-4 text-sm font-medium transition hover:bg-accent"
              href={manualHref}
            >
              查看使用说明
            </Link>
          ) : null}
          {workbenchHref ? (
            <Link
              className="inline-flex h-10 items-center justify-center rounded-md border border-border bg-card px-4 text-sm font-medium transition hover:bg-accent"
              href={workbenchHref}
            >
              进入工作台
            </Link>
          ) : null}
        </div>
      </header>

      <section className="grid gap-4 lg:grid-cols-[0.95fr_1.05fr]">
        <Card className="p-5">
          <h2 className="text-lg font-semibold">系统工作指令（Prompt）</h2>
          <p className="mt-4 rounded-md bg-muted p-4 text-sm leading-6 text-muted-foreground">{agent.prompt}</p>
        </Card>
        <Card className="p-5">
          <h2 className="text-lg font-semibold">能力入口</h2>
          <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3">
            {capabilitySections.map((section) => (
              <div className="rounded-md border border-border bg-background px-3 py-3 text-sm font-medium" key={section}>
                {section}
              </div>
            ))}
          </div>
        </Card>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <Card className="p-5">
          <h2 className="text-lg font-semibold">后续任务</h2>
          <div className="mt-4 space-y-3">
            {agent.future_tasks.map((task) => (
              <div className="rounded-md border border-border px-3 py-3 text-sm text-muted-foreground" key={task}>
                {task}
              </div>
            ))}
          </div>
        </Card>
        <Card className="p-5">
          <h2 className="text-lg font-semibold">工作记录（Logs）</h2>
          <div className="mt-4 space-y-3">
            {logs.map((log) => (
              <div className="rounded-md bg-muted px-3 py-3 text-sm" key={log.id}>
                <div className="font-medium">{log.message}</div>
                <div className="mt-1 text-xs text-muted-foreground">{log.created_at}</div>
              </div>
            ))}
          </div>
        </Card>
      </section>
    </div>
  );
}
