"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { AlertTriangle, ArrowRight, BadgeCheck, CheckCircle2, ClipboardList, Loader2, PlayCircle, Radio, TrendingUp, WalletCards } from "lucide-react";
import { Badge } from "@/shared/ui/badge";
import { Card } from "@/shared/ui/card";
import { runDailyOperations } from "@/shared/api/client";
import type { CeoDailyReport, DailyOperationsRun, DashboardSummary, LiveOperationSummary, SavingsSummary } from "@/shared/api/types";

const riskLabel = {
  high: "高优先级",
  medium: "中优先级",
  low: "低优先级"
} as const;

const ownerLabel = {
  boss: "老板确认",
  "ai-live-operator": "AI直播运营助理",
  "ai-operator": "AI运营",
  "ai-after-sale": "AI售后",
  "ai-customer": "AI客服"
} as const;

const statusTone = {
  done: "green",
  warning: "amber",
  blocked: "amber",
  pending: "neutral"
} as const;

const statusLabel = {
  done: "已完成",
  warning: "需注意",
  blocked: "已阻塞",
  pending: "待执行"
} as const;

export function DashboardView({
  ceoReport,
  liveOperation,
  savings,
  summary
}: {
  ceoReport: CeoDailyReport;
  liveOperation: LiveOperationSummary;
  savings: SavingsSummary;
  summary: DashboardSummary;
}) {
  const replacementProgress = Math.min(
    Math.round((ceoReport.projected_monthly_saving_yuan / ceoReport.replacement_target_yuan) * 100),
    100
  );
  const topRisk = ceoReport.top_risks[0];
  const firstAction = ceoReport.priority_actions[0];
  const [dailyRun, setDailyRun] = useState<DailyOperationsRun | null>(null);
  const [isRunningDailyWork, setIsRunningDailyWork] = useState(false);
  const [dailyRunError, setDailyRunError] = useState<string | null>(null);

  async function handleRunDailyOperations() {
    setIsRunningDailyWork(true);
    setDailyRunError(null);
    const result = await runDailyOperations();
    setIsRunningDailyWork(false);
    if (result.error || !result.data) {
      setDailyRunError(result.error ?? "今日工作执行失败，请稍后重试。");
      return;
    }
    setDailyRun(result.data);
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 border-b border-border pb-5 lg:flex-row lg:items-end">
        <div>
                    <div className="flex flex-wrap items-center gap-2">
            <p className="text-sm font-medium text-primary">{ceoReport.date}</p>
            <Badge tone={ceoReport.data_status === "real_workflow_logs" ? "green" : "amber"}>{ceoReport.data_status_label}</Badge>
          </div>
          <h1 className="mt-2 text-3xl font-semibold tracking-normal">老板日报</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            这里不是聊天记录，也不是传统后台。老板每天先看结论：今天发生了什么、为什么、先做什么、AI 省了多少钱。
          </p>
          <p className="mt-2 max-w-3xl rounded-md border border-border bg-muted/50 p-3 text-xs leading-5 text-muted-foreground">{ceoReport.data_status_reason}</p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row lg:items-center">
          <button
            className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isRunningDailyWork}
            onClick={handleRunDailyOperations}
            type="button"
          >
            {isRunningDailyWork ? <Loader2 aria-hidden className="mr-2 h-4 w-4 animate-spin" /> : <PlayCircle aria-hidden className="mr-2 h-4 w-4" />}
            {isRunningDailyWork ? "AI 正在工作" : "让 AI 开始今日工作"}
          </button>
          <Link
            className="inline-flex h-10 items-center justify-center rounded-md border border-border bg-background px-4 text-sm font-medium"
            href="/settings/data-import"
          >
            上传真实直播数据
            <ArrowRight aria-hidden className="ml-2 h-4 w-4" />
          </Link>
        </div>
      </header>

      {dailyRun || dailyRunError ? (
        <Card className={`p-5 ${dailyRunError ? "border-destructive/40 bg-destructive/5" : "border-primary/25 bg-primary/5"}`}>
          {dailyRun ? (
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge tone={dailyRun.input_mode === "merchant_payload" ? "green" : "amber"}>
                    {dailyRun.input_mode === "merchant_payload" ? "真实数据执行" : "安全基线巡检"}
                  </Badge>
                  <Badge tone={dailyRun.status === "completed" ? "green" : "amber"}>{dailyRun.status === "completed" ? "已完成" : "需要接真实数据"}</Badge>
                </div>
                <h2 className="mt-3 text-xl font-semibold">{dailyRun.operator_message}</h2>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{dailyRun.next_run_hint}</p>
              </div>
              <div className="grid grid-cols-3 gap-3 text-center lg:min-w-96">
                <MiniMetric label="完成工作" value={`${dailyRun.completed_work_count} 项`} />
                <MiniMetric label="节省时间" value={`${dailyRun.saved_minutes} 分钟`} />
                <MiniMetric label="节省金额" value={`¥${dailyRun.saved_yuan}`} />
              </div>
            </div>
          ) : (
            <div className="flex items-start gap-3">
              <AlertTriangle aria-hidden className="mt-0.5 h-5 w-5 text-warning" />
              <div>
                <h2 className="font-semibold">今日工作没有执行成功</h2>
                <p className="mt-1 text-sm text-muted-foreground">{dailyRunError}</p>
              </div>
            </div>
          )}
        </Card>
      ) : null}

      <section className="grid gap-4 xl:grid-cols-[1.25fr_0.75fr]">
        <Card className="border-primary/25 bg-primary/5 p-6">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <Badge tone={ceoReport.business_health_score >= 80 ? "green" : "amber"}>今天第一眼只看这里</Badge>
              <h2 className="mt-4 max-w-4xl text-3xl font-semibold leading-tight">{ceoReport.headline}</h2>
              <p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground">{ceoReport.boss_message}</p>
            </div>
            <div className="grid min-w-48 grid-cols-2 gap-3 lg:grid-cols-1">
              <MiniMetric label="经营健康分" value={`${ceoReport.business_health_score} 分`} />
              <MiniMetric label="直播状态" value={ceoReport.live_operation_status} />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <Badge tone="green">Savings Engine</Badge>
              <h2 className="mt-4 text-3xl font-semibold">¥{ceoReport.saved_money_today_yuan}</h2>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                今天 AI 员工替代人工工作的预估节省。按当前节奏，月节省约 ¥{ceoReport.projected_monthly_saving_yuan}。
              </p>
            </div>
            <WalletCards aria-hidden className="h-6 w-6 text-primary" />
          </div>
          <div className="mt-5 h-2 overflow-hidden rounded-full bg-muted">
            <div className="h-full rounded-full bg-primary" style={{ width: `${replacementProgress}%` }} />
          </div>
          <p className="mt-2 text-xs text-muted-foreground">替代 20 人团队目标进度：{replacementProgress}% / 月目标 ¥{ceoReport.replacement_target_yuan}</p>
        </Card>
      </section>

      <section className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
        <Card className="p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold">今天最高风险</h2>
              <p className="mt-1 text-sm text-muted-foreground">老板只需要先判断这一件事要不要处理。</p>
            </div>
            <AlertTriangle aria-hidden className="h-5 w-5 text-warning" />
          </div>
          {topRisk ? (
            <article className="mt-5 rounded-md border border-border bg-background p-4">
              <Badge tone={topRisk.level === "high" ? "amber" : "neutral"}>{riskLabel[topRisk.level]}</Badge>
              <h3 className="mt-3 text-lg font-semibold">{topRisk.title}</h3>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">原因：{topRisk.reason}</p>
              <p className="mt-3 text-sm font-medium">建议：{topRisk.suggested_action}</p>
              <p className="mt-2 text-xs leading-5 text-muted-foreground">影响：{topRisk.money_impact}</p>
            </article>
          ) : (
            <p className="mt-5 text-sm text-muted-foreground">今天暂无高风险。</p>
          )}
        </Card>

        <Card className="p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold">今天优先动作</h2>
              <p className="mt-1 text-sm text-muted-foreground">不是让老板分析数据，而是让老板确认 AI 下一步怎么做。</p>
            </div>
            <ClipboardList aria-hidden className="h-5 w-5 text-primary" />
          </div>
          <div className="mt-5 space-y-3">
            {ceoReport.priority_actions.map((action, index) => (
              <motion.article
                animate={{ opacity: 1, y: 0 }}
                className="rounded-md border border-border bg-background p-4"
                initial={{ opacity: 0, y: 8 }}
                key={action.id}
                transition={{ delay: index * 0.04 }}
              >
                <div className="flex flex-wrap items-center gap-2">
                  <Badge tone="neutral">{ownerLabel[action.owner]}</Badge>
                  {action.requires_approval ? <Badge tone="amber">需要老板确认</Badge> : <Badge tone="green">AI 可先执行</Badge>}
                </div>
                <h3 className="mt-3 font-semibold">{action.title}</h3>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{action.expected_result}</p>
              </motion.article>
            ))}
          </div>
        </Card>
      </section>

      <section className="grid gap-4 lg:grid-cols-4">
        {ceoReport.metrics.map((metric) => (
          <Card className="p-4" key={metric.id}>
            <p className="text-sm text-muted-foreground">{metric.label}</p>
            <p className="mt-2 text-2xl font-semibold">{metric.value}</p>
            <p className="mt-2 text-xs leading-5 text-muted-foreground">{metric.explanation}</p>
          </Card>
        ))}
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
        <Card className="p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold">直播运营 Workflow</h2>
              <p className="mt-1 text-sm text-muted-foreground">{liveOperation.session_title}</p>
            </div>
            <Radio aria-hidden className="h-5 w-5 text-primary" />
          </div>
          <div className="mt-5 divide-y divide-border">
            {liveOperation.checklist.map((item, index) => (
              <motion.article
                animate={{ opacity: 1, y: 0 }}
                className="py-4 first:pt-0 last:pb-0"
                initial={{ opacity: 0, y: 8 }}
                key={item.id}
                transition={{ delay: index * 0.04 }}
              >
                <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge tone={statusTone[item.status]}>{statusLabel[item.status]}</Badge>
                      {item.requires_approval ? <Badge tone="amber">需要老板审批</Badge> : null}
                    </div>
                    <h3 className="mt-3 font-semibold">{item.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-muted-foreground">{item.business_value}</p>
                  </div>
                  <MiniMetric label="节省" value={`${item.saved_minutes} 分钟`} />
                </div>
              </motion.article>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold">省钱证据链</h2>
              <p className="mt-1 text-sm text-muted-foreground">老板看到的每一笔节省，都要能追到 Workflow。</p>
            </div>
            <CheckCircle2 aria-hidden className="h-5 w-5 text-primary" />
          </div>
          <div className="mt-5 space-y-3">
            {ceoReport.proof_points.map((proof) => (
              <div className="rounded-md border border-border bg-background p-3 text-sm leading-6 text-muted-foreground" key={proof}>{proof}</div>
            ))}
          </div>
        </Card>
      </section>

      <Card className="p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold">AI 员工绩效</h2>
            <p className="mt-1 text-sm text-muted-foreground">每个 AI 员工必须说明替代哪个岗位、完成多少工作、节省多少钱。</p>
          </div>
          <TrendingUp aria-hidden className="h-5 w-5 text-primary" />
        </div>
        <div className="mt-5 grid gap-4 lg:grid-cols-3">
          {savings.agents.map((agent) => (
            <article className="rounded-md border border-border p-4" key={agent.agent_id}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-semibold">{agent.agent_name}</h3>
                  <p className="mt-1 text-xs text-muted-foreground">替代：{agent.replaced_role}</p>
                </div>
                <Badge tone={agent.performance_score >= 85 ? "green" : "amber"}>{agent.performance_score}分</Badge>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-3">
                <MiniMetric label="完成工作" value={`${agent.completed_work_count} 项`} />
                <MiniMetric label="节省金额" value={`¥${agent.saved_yuan}`} />
              </div>
              <p className="mt-4 text-sm leading-6 text-muted-foreground">{agent.proof}</p>
            </article>
          ))}
        </div>
      </Card>

      <section className="grid gap-4 lg:grid-cols-3">
        <ActionCard
          href="/settings/data-import"
          icon={BadgeCheck}
          title="先接真实数据"
          desc="上传直播商品、优惠券、直播中数据和下播复盘，让老板日报从估算变成真实证据。"
        />
        <ActionCard
          href="/replay"
          icon={TrendingUp}
          title="再跑回放验证"
          desc="用历史数据比较人工和 AI 的处理结果，证明它真的能替代岗位。"
        />
        <ActionCard
          href="/training-center"
          icon={ClipboardList}
          title="最后沉淀经验"
          desc="老板和运营修正过的结果，要沉淀成 Memory、Knowledge 和 Workflow。"
        />
      </section>
    </div>
  );
}

function MiniMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md bg-muted p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-lg font-semibold">{value}</p>
    </div>
  );
}

function ActionCard({
  desc,
  href,
  icon: Icon,
  title
}: {
  desc: string;
  href: string;
  icon: typeof BadgeCheck;
  title: string;
}) {
  return (
    <Link className="block rounded-md border border-border bg-card p-5 transition hover:border-primary/40 hover:bg-accent" href={href}>
      <Icon aria-hidden className="h-5 w-5 text-primary" />
      <h3 className="mt-4 font-semibold">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">{desc}</p>
    </Link>
  );
}




