"use client";

import Link from "next/link";
import Image from "next/image";
import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  ArrowRight,
  BarChart3,
  Bot,
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  Database,
  FileCheck2,
  Headphones,
  LineChart,
  LockKeyhole,
  RefreshCw,
  ShieldCheck,
  TrendingUp,
  UserCheck,
  WalletCards
} from "lucide-react";
import { Badge } from "@/shared/ui/badge";
import { cn } from "@/shared/lib/utils";

type DemoKey = "customer" | "afterSale" | "operation" | "approval";

const costItems = [
  { label: "客服", detail: "售前咨询、订单查询、物流追踪、催付转化", value: "高频重复" },
  { label: "售后", detail: "退款退货、投诉分级、异常物流、赔偿初筛", value: "风险密集" },
  { label: "运营", detail: "客户线索、私域话术、投流计划、活动复盘", value: "持续消耗" }
];

const agents = [
  {
    icon: Headphones,
    title: "AI客服",
    desc: "处理 FAQ、订单、物流等低风险问题，无法确认时自动暂停并交给人工。",
    can: ["生成回复草稿", "识别购买意图", "记录商家修改"],
    limit: "不承诺退款、赔偿、特殊优惠"
  },
  {
    icon: ShieldCheck,
    title: "AI售后",
    desc: "对退款、退货、投诉和物流异常进行风险分级，输出可审计的审批建议。",
    can: ["售后 case 分类", "风险等级判断", "沉淀售后 SOP"],
    limit: "不越权退款，不自动赔偿"
  },
  {
    icon: TrendingUp,
    title: "AI运营",
    desc: "识别高意向客户，生成私域话术和投流计划草稿，帮助老板看见增长机会。",
    can: ["私域线索识别", "投流草稿", "ROI 复盘"],
    limit: "不自动花广告费，不改预算"
  }
];

const demoPanels: Record<
  DemoKey,
  {
    title: string;
    eyebrow: string;
    summary: string;
    metric: string;
    rows: Array<{ label: string; value: string; tone?: "green" | "amber" | "neutral" }>;
    timeline: string[];
  }
> = {
  customer: {
    eyebrow: "AI Customer",
    title: "客户咨询进入统一收件箱",
    summary: "AI 先判断问题类型，再给出回复草稿。退款、赔偿、投诉类问题自动进入人工接管。",
    metric: "目标：基础问题自动回复率 50%+",
    rows: [
      { label: "客户问题", value: "这件外套今天下单什么时候发？" },
      { label: "AI判断", value: "物流 / 低风险", tone: "green" },
      { label: "AI草稿", value: "您好，当前订单可正常安排发货，预计 24 小时内出库。" },
      { label: "学习动作", value: "客服修改后写入学习记录", tone: "neutral" }
    ],
    timeline: ["识别意图", "生成草稿", "人工抽查", "发送回复", "沉淀学习"]
  },
  afterSale: {
    eyebrow: "AI AfterSale",
    title: "售后 case 自动分级",
    summary: "系统识别退款、退货、投诉和异常物流，把高风险动作统一交给老板或客服主管审批。",
    metric: "目标：高风险售后 100% 拦截",
    rows: [
      { label: "售后类型", value: "客户投诉物流超时并要求赔偿" },
      { label: "风险等级", value: "高风险 / 必须审批", tone: "amber" },
      { label: "AI建议", value: "先核查物流节点，再按店铺规则给出补偿方案。" },
      { label: "权限边界", value: "不自动退款，不自动承诺赔偿", tone: "neutral" }
    ],
    timeline: ["识别售后", "判断责任", "风险分级", "审批建议", "SOP沉淀"]
  },
  operation: {
    eyebrow: "AI Operation",
    title: "把私域获客和投流变成可审批计划",
    summary: "AI运营不直接花钱，而是识别高意向客户、生成话术和投流草稿，让老板基于数据审批。",
    metric: "目标：每天输出可执行运营建议",
    rows: [
      { label: "客户线索", value: "7 天内咨询 3 次尺码和发货，购买意向高" },
      { label: "私域建议", value: "引导领取搭配清单和复购优惠", tone: "green" },
      { label: "投流草稿", value: "围绕爆款外套做素材测试，先小预算验证" },
      { label: "审批要求", value: "预算、优惠、群发必须老板确认", tone: "amber" }
    ],
    timeline: ["客户分层", "线索识别", "话术生成", "投流草稿", "ROI复盘"]
  },
  approval: {
    eyebrow: "Boss Approval",
    title: "老板只处理关键审批",
    summary: "所有预算、退款、赔偿、投诉和客户数据动作统一进入审批，保留完整决策记录。",
    metric: "目标：AI 工作可追踪、可复盘、可控",
    rows: [
      { label: "审批事项", value: "物流投诉补偿 20 元优惠券" },
      { label: "AI依据", value: "客户订单金额高，历史无异常退款" },
      { label: "审批动作", value: "同意 / 修改 / 拒绝 / 要求补充信息", tone: "neutral" },
      { label: "复盘沉淀", value: "写入 Memory、Knowledge、Workflow", tone: "green" }
    ],
    timeline: ["AI建议", "风险说明", "老板审批", "执行记录", "经验沉淀"]
  }
};

const metrics = [
  "客服自动回复率",
  "客服错误率",
  "人工接管率",
  "售后分类准确率",
  "高风险拦截率",
  "私域线索数量",
  "运营建议采纳率",
  "节省人工分钟数"
];

const trialSteps = [
  "导入商品、订单、客户、售后数据",
  "AI客服生成回复草稿，客服修正",
  "AI售后做风险分级和审批建议",
  "AI运营识别私域线索和投流草稿",
  "每周复盘自动化率、错误率和节省工时"
];

const ctas = [
  { href: "/dashboard", label: "查看老板首页" },
  { href: "/ai-employees/ai-customer/workbench", label: "体验AI客服" },
  { href: "/ai-employees/ai-after-sale/workbench", label: "体验AI售后" },
  { href: "/settings/data-import", label: "导入商家数据" }
];

export function PromoSiteView() {
  const [activeDemo, setActiveDemo] = useState<DemoKey>("customer");
  const panel = useMemo(() => demoPanels[activeDemo], [activeDemo]);

  return (
    <main className="min-h-screen bg-background text-foreground">
      <HeroSection />
      <CostSection />
      <ProductSection />
      <AgentSection />
      <DemoSection activeDemo={activeDemo} panel={panel} setActiveDemo={setActiveDemo} />
      <TrialSection />
      <MetricSection />
      <CtaSection />
    </main>
  );
}

function HeroSection() {
  return (
    <section className="relative min-h-[92vh] overflow-hidden bg-slate-950 text-white">
      <Image
        alt="AI Commerce OS 商务运营中枢"
        className="absolute inset-0 h-full w-full object-cover"
        fill
        priority
        src="/marketing/ai-commerce-os-b2b-hero.png"
      />
      <div className="absolute inset-0 bg-slate-950/68" />
      <div className="absolute inset-x-0 bottom-0 h-28 bg-gradient-to-t from-background to-transparent" />
      <div className="relative mx-auto flex min-h-[92vh] max-w-7xl flex-col justify-between px-5 py-6 sm:px-8 lg:px-10">
        <nav className="flex items-center justify-between">
          <Link className="text-sm font-semibold tracking-wide" href="/promo">
            AI Commerce OS
          </Link>
          <div className="hidden items-center gap-6 text-sm text-white/72 md:flex">
            <a href="#product">产品说明</a>
            <a href="#demo">演示界面</a>
            <a href="#trial">试用流程</a>
          </div>
        </nav>

        <motion.div
          animate={{ opacity: 1, y: 0 }}
          className="max-w-3xl pb-16 pt-24"
          initial={{ opacity: 0, y: 18 }}
          transition={{ duration: 0.55 }}
        >
          <Badge className="bg-white/12 text-white" tone="neutral">
            面向电商企业的 AI 员工操作系统
          </Badge>
          <h1 className="mt-6 text-4xl font-semibold leading-tight sm:text-5xl lg:text-6xl">
            让老板拥有一支可审批、可追踪、可学习的 AI 电商团队
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-8 text-white/76 sm:text-lg">
            从 AI客服、AI售后、AI运营三个岗位开始，把重复、标准化、可审批的工作交给 AI，目标逐步替代约 4 万元/月基础人力成本。
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Link
              className="inline-flex h-11 items-center justify-center rounded-md bg-white px-5 text-sm font-semibold text-slate-950 transition hover:bg-white/90"
              href="#demo"
            >
              查看演示界面
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
            <Link
              className="inline-flex h-11 items-center justify-center rounded-md border border-white/20 px-5 text-sm font-semibold text-white transition hover:bg-white/10"
              href="/settings/data-import"
            >
              导入商家数据
            </Link>
          </div>
        </motion.div>

        <div className="grid gap-3 pb-10 sm:grid-cols-3">
          {["低风险自动", "高风险审批", "人工修改学习"].map((item) => (
            <div className="rounded-md border border-white/12 bg-white/8 px-4 py-3 text-sm text-white/80 backdrop-blur" key={item}>
              {item}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CostSection() {
  return (
    <section className="border-b border-border bg-background px-5 py-20 sm:px-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <SectionHeader
          eyebrow="Cost Reduction"
          title="企业真正要买的不是 AI，而是可验证的降本结果"
          desc="AI Commerce OS 优先处理电商团队中重复、标准化、可审批的工作，先省时间，再省人。"
        />
        <div className="mt-10 grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="grid gap-4 md:grid-cols-3">
            {costItems.map((item) => (
              <article className="rounded-md border border-border bg-card p-5 shadow-soft" key={item.label}>
                <p className="text-sm text-primary">{item.value}</p>
                <h3 className="mt-3 text-2xl font-semibold">{item.label}</h3>
                <p className="mt-4 text-sm leading-6 text-muted-foreground">{item.detail}</p>
              </article>
            ))}
          </div>
          <div className="rounded-md border border-border bg-slate-950 p-6 text-white shadow-soft">
            <p className="text-sm text-white/60">目标替代成本</p>
            <p className="mt-4 text-5xl font-semibold">约 4 万/月</p>
            <p className="mt-5 text-sm leading-7 text-white/70">
              当前阶段不承诺一键替代完整团队，而是用真实数据验证 AI 能先替代多少重复工作，并逐步扩大自动化比例。
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

function ProductSection() {
  return (
    <section className="border-b border-border bg-muted/35 px-5 py-20 sm:px-8 lg:px-10" id="product">
      <div className="mx-auto grid max-w-7xl gap-10 lg:grid-cols-[0.85fr_1.15fr] lg:items-start">
        <SectionHeader
          eyebrow="Product"
          title="不是聊天机器人，也不是传统 ERP"
          desc="它是一套 AI 电商员工控制台：AI 负责执行低风险工作，老板负责关键审批，系统负责记录和学习。"
        />
        <div className="grid gap-4">
          {[
            { icon: Bot, title: "AI员工化", desc: "每个 AI 都有职责、权限、工作记录、学习样本和评估指标。" },
            { icon: LockKeyhole, title: "审批优先", desc: "退款、赔偿、预算、投流和客户数据动作必须进入审批。" },
            { icon: Database, title: "数据验证", desc: "通过 Commerce Dataset、Replay 和 Evaluation 验证 AI 是否真的能工作。" }
          ].map((item) => (
            <div className="rounded-md border border-border bg-card p-5 shadow-soft" key={item.title}>
              <div className="flex items-start gap-4">
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-accent">
                  <item.icon className="h-5 w-5 text-primary" />
                </span>
                <div>
                  <h3 className="text-lg font-semibold">{item.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">{item.desc}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function AgentSection() {
  return (
    <section className="border-b border-border bg-background px-5 py-20 sm:px-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <SectionHeader
          eyebrow="AI Employees"
          title="三个 AI 员工，先接管最容易标准化的工作"
          desc="当前聚焦客服、售后、运营，不继续堆更多 Agent。目标是先证明可节省时间和成本。"
        />
        <div className="mt-10 grid gap-5 lg:grid-cols-3">
          {agents.map((agent) => (
            <article className="rounded-md border border-border bg-card p-6 shadow-soft" key={agent.title}>
              <agent.icon className="h-6 w-6 text-primary" />
              <h3 className="mt-5 text-xl font-semibold">{agent.title}</h3>
              <p className="mt-3 text-sm leading-6 text-muted-foreground">{agent.desc}</p>
              <div className="mt-5 space-y-2">
                {agent.can.map((item) => (
                  <div className="flex items-center gap-2 text-sm" key={item}>
                    <CheckCircle2 className="h-4 w-4 text-primary" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
              <div className="mt-5 rounded-md bg-muted p-3 text-xs leading-5 text-muted-foreground">{agent.limit}</div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function DemoSection({
  activeDemo,
  panel,
  setActiveDemo
}: {
  activeDemo: DemoKey;
  panel: (typeof demoPanels)[DemoKey];
  setActiveDemo: (key: DemoKey) => void;
}) {
  const tabs: Array<{ key: DemoKey; label: string }> = [
    { key: "customer", label: "AI客服" },
    { key: "afterSale", label: "AI售后" },
    { key: "operation", label: "AI运营" },
    { key: "approval", label: "老板审批" }
  ];

  return (
    <section className="border-b border-border bg-muted/35 px-5 py-20 sm:px-8 lg:px-10" id="demo">
      <div className="mx-auto max-w-7xl">
        <SectionHeader
          eyebrow="Interactive Demo"
          title="可点击演示：看 AI 如何工作，而不是只看概念"
          desc="演示数据为静态样例，用来说明产品流程。真实上线后会接入商家订单、客户、售后和运营数据。"
        />
        <div className="mt-10 overflow-hidden rounded-md border border-border bg-card shadow-soft">
          <div className="border-b border-border p-3">
            <div className="grid gap-2 sm:grid-cols-4">
              {tabs.map((tab) => (
                <button
                  className={cn(
                    "h-11 rounded-md px-3 text-sm font-medium transition",
                    activeDemo === tab.key ? "bg-slate-950 text-white dark:bg-white dark:text-slate-950" : "bg-muted text-muted-foreground hover:text-foreground"
                  )}
                  key={tab.key}
                  onClick={() => setActiveDemo(tab.key)}
                  type="button"
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
          <div className="grid gap-0 lg:grid-cols-[0.95fr_1.05fr]">
            <div className="border-b border-border p-6 lg:border-b-0 lg:border-r">
              <Badge tone={activeDemo === "afterSale" || activeDemo === "approval" ? "amber" : "green"}>{panel.eyebrow}</Badge>
              <h3 className="mt-4 text-2xl font-semibold">{panel.title}</h3>
              <p className="mt-3 text-sm leading-7 text-muted-foreground">{panel.summary}</p>
              <div className="mt-6 rounded-md bg-slate-950 p-4 text-sm font-medium text-white">{panel.metric}</div>
              <div className="mt-6 flex flex-wrap gap-2">
                {panel.timeline.map((step) => (
                  <span className="rounded-md bg-muted px-3 py-2 text-xs text-muted-foreground" key={step}>
                    {step}
                  </span>
                ))}
              </div>
            </div>
            <div className="p-6">
              <div className="rounded-md border border-border bg-background">
                {panel.rows.map((row) => (
                  <div className="grid gap-2 border-b border-border px-4 py-4 last:border-b-0 sm:grid-cols-[150px_1fr]" key={row.label}>
                    <div className="text-sm text-muted-foreground">{row.label}</div>
                    <div className="flex items-start justify-between gap-3 text-sm font-medium">
                      <span>{row.value}</span>
                      {row.tone ? <Badge tone={row.tone}>状态</Badge> : null}
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-5 grid gap-3 sm:grid-cols-3">
                {[
                  { icon: Clock3, label: "响应更快" },
                  { icon: FileCheck2, label: "过程可审计" },
                  { icon: RefreshCw, label: "修改可学习" }
                ].map((item) => (
                  <div className="rounded-md bg-muted p-3 text-sm" key={item.label}>
                    <item.icon className="mb-3 h-4 w-4 text-primary" />
                    {item.label}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function TrialSection() {
  return (
    <section className="border-b border-border bg-background px-5 py-20 sm:px-8 lg:px-10" id="trial">
      <div className="mx-auto max-w-7xl">
        <SectionHeader
          eyebrow="Pilot"
          title="7 天试用：先让 AI 跑起来，再看数据"
          desc="试用期不追求全自动，先追求可验证：节省多少时间、减少多少人工判断、沉淀多少学习样本。"
        />
        <div className="mt-10 grid gap-3 lg:grid-cols-5">
          {trialSteps.map((step, index) => (
            <article className="rounded-md border border-border bg-card p-5 shadow-soft" key={step}>
              <div className="flex h-9 w-9 items-center justify-center rounded-md bg-accent text-sm font-semibold text-primary">
                {index + 1}
              </div>
              <p className="mt-5 text-sm leading-6 text-muted-foreground">{step}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function MetricSection() {
  return (
    <section className="border-b border-border bg-muted/35 px-5 py-20 sm:px-8 lg:px-10">
      <div className="mx-auto grid max-w-7xl gap-10 lg:grid-cols-[0.8fr_1.2fr]">
        <SectionHeader
          eyebrow="Evaluation"
          title="用指标判断 AI 是否值得继续扩大使用"
          desc="所有演示和试用都要回到同一件事：AI 有没有真正降低人工成本、减少风险、提高响应效率。"
        />
        <div className="grid gap-3 sm:grid-cols-2">
          {metrics.map((metric) => (
            <div className="flex items-center gap-3 rounded-md border border-border bg-card px-4 py-3 text-sm shadow-soft" key={metric}>
              <BarChart3 className="h-4 w-4 text-primary" />
              <span>{metric}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CtaSection() {
  return (
    <section className="bg-slate-950 px-5 py-20 text-white sm:px-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <div className="grid gap-10 lg:grid-cols-[1fr_1.1fr] lg:items-end">
          <div>
            <p className="text-sm font-medium text-teal-300">Next Step</p>
            <h2 className="mt-4 text-3xl font-semibold sm:text-4xl">先用一家真实店铺验证降本</h2>
            <p className="mt-4 max-w-2xl text-sm leading-7 text-white/70">
              导入历史数据，跑 AI客服和 AI售后，收集修改样本，一周后用指标判断是否继续扩大自动化。
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {ctas.map((cta) => (
              <Link
                className="inline-flex min-h-12 items-center justify-between rounded-md border border-white/12 bg-white/8 px-4 text-sm font-medium text-white transition hover:bg-white/14"
                href={cta.href}
                key={cta.href}
              >
                {cta.label}
                <ArrowRight className="h-4 w-4" />
              </Link>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function SectionHeader({ desc, eyebrow, title }: { desc: string; eyebrow: string; title: string }) {
  return (
    <div className="max-w-3xl">
      <p className="text-sm font-medium text-primary">{eyebrow}</p>
      <h2 className="mt-3 text-3xl font-semibold leading-tight sm:text-4xl">{title}</h2>
      <p className="mt-4 text-sm leading-7 text-muted-foreground sm:text-base">{desc}</p>
    </div>
  );
}
