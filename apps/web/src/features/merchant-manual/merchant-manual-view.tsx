import Link from "next/link";
import {
  BarChart3,
  Bot,
  Brain,
  CheckCircle2,
  Database,
  Dumbbell,
  Gauge,
  Home,
  MessageSquareText,
  PackageSearch,
  RotateCcw,
  Settings,
  ShieldAlert,
  ShoppingBag,
  UploadCloud,
  Users,
  Workflow
} from "lucide-react";
import { Badge } from "@/shared/ui/badge";
import { Card } from "@/shared/ui/card";

const leftMenuItems = [
  { icon: Home, name: "老板首页", use: "每天先点这里。看今天要处理什么、AI 省了多少钱、哪里有风险。", href: "/dashboard" },
  { icon: Bot, name: "AI 员工", use: "看 AI客服、AI售后、AI运营、AI老板。想进入某个 AI 的工作台，就从这里点。", href: "/ai-employees" },
  { icon: ShoppingBag, name: "订单", use: "看订单号、客户、金额、状态。AI客服查订单会用这里的数据。", href: "/orders" },
  { icon: PackageSearch, name: "商品", use: "看商品名称、价格、库存、SKU。AI客服回答商品问题会用这里的数据。", href: "/products" },
  { icon: Users, name: "客户", use: "看客户资料。以后 AI 会用它判断老客户、高意向客户。", href: "/customers" },
  { icon: Database, name: "数据集", use: "看数据够不够。低于 80%，不要承诺 AI 能完全替人。", href: "/commerce-dataset" },
  { icon: RotateCcw, name: "回放验证", use: "让 AI 重新做一遍历史工作，看它和人工结果像不像。", href: "/replay" },
  { icon: Gauge, name: "AI 评分", use: "看 AI 靠不靠谱、能省多少钱、哪里还不能放权。", href: "/evaluation" },
  { icon: Dumbbell, name: "训练中心", use: "老板或客服改过的回复，会在这里变成记忆、知识和流程。", href: "/training-center" },
  { icon: Brain, name: "知识库", use: "放店铺规则，比如发货时间、售后规则、商品尺码。", href: "/knowledge-base" },
  { icon: Workflow, name: "工作流程", use: "放标准步骤，比如退款先查订单，再查物流，最后老板审批。", href: "/workflow" },
  { icon: BarChart3, name: "经营分析", use: "看经营数据。当前是预留入口，后续给 AI运营使用。", href: "/analytics" },
  { icon: Settings, name: "设置", use: "连接平台、导入数据、配置系统。新商家第一天主要用这里。", href: "/settings" }
];

const topRules = [
  "看到“可自动”：AI 可以先写草稿，客服看一眼，没问题再发。",
  "看到“需人工”：不要自动发，必须人工接管。",
  "看到“审批”：说明涉及钱、投诉、赔偿、预算，老板确认后再做。",
  "看到“记录商家修改”：说明这句话要让 AI 学会，下次少问人。"
];

const dailyFlow = [
  { title: "第 1 步：打开老板首页", desc: "只看“今天要处理什么”和“省钱进度”。不要先乱点左侧菜单。", href: "/dashboard" },
  { title: "第 2 步：处理客户消息", desc: "进入 AI客服。可自动就发送；退款、赔偿、投诉就人工接管。", href: "/ai-employees/ai-customer/workbench" },
  { title: "第 3 步：处理售后", desc: "进入 AI售后。只要是高风险、退款、赔偿、投诉，都要老板确认。", href: "/ai-employees/ai-after-sale/workbench" },
  { title: "第 4 步：看 AI 靠不靠谱", desc: "进入 AI评分。看准确率、人工接管率、节省金额。", href: "/evaluation" },
  { title: "第 5 步：让 AI 学习", desc: "进入训练中心。把修改过的好回复沉淀下来。", href: "/training-center" }
];

const platformSteps = [
  {
    title: "淘宝怎么接",
    desc: "去“设置 → 平台集成 → 淘宝”，优先走官方授权。没有开放平台权限时，先用文件导入订单、商品、物流和售后。"
  },
  {
    title: "抖店怎么接",
    desc: "去“设置 → 平台集成 → 抖音商店”，准备抖店开放平台应用。正式接入前，先导出文件做试用。"
  },
  {
    title: "拼多多怎么接",
    desc: "当前先做接入窗口和说明，不假装已连通。需要拼多多开放平台或服务商权限后再接真实授权。"
  },
  {
    title: "闲鱼怎么接",
    desc: "闲鱼只走安全文件导入。不扫码托管账号，不拿 Cookie，不抓包。先导出订单、商品、售后文件。"
  }
];

export function MerchantManualView() {
  return (
    <div className="space-y-6">
      <header className="border-b border-border pb-5">
        <p className="text-sm font-medium text-primary">商家使用说明</p>
        <h1 className="mt-2 text-3xl font-semibold">不会电脑也能照着用</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
          这份说明给第一次使用的老板和客服看。不要理解技术词，只按页面提示点。遇到退款、赔偿、投诉、预算，一律交给人确认。
        </p>
      </header>

      <section className="grid gap-4 lg:grid-cols-[1fr_0.8fr]">
        <Card className="border-primary/20 bg-primary/5 p-5">
          <Badge tone="green">每天只记一句话</Badge>
          <h2 className="mt-3 text-2xl font-semibold">先看老板首页，再处理客服和售后，最后看省了多少钱。</h2>
          <p className="mt-3 text-sm leading-6 text-muted-foreground">
            这个系统不是让你研究报表。它是让 AI 先干活，人只检查高风险事情。
          </p>
        </Card>
        <Card className="p-5">
          <h2 className="text-lg font-semibold">红线</h2>
          <p className="mt-3 text-sm leading-6 text-muted-foreground">
            AI 不能自己退款、赔偿、投广告、加预算、改价格、承诺优惠金额。看到这些事，必须人工确认。
          </p>
        </Card>
      </section>

      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        {dailyFlow.map((item) => (
          <Link className="rounded-md border border-border bg-card p-4 transition hover:border-primary/40 hover:bg-accent" href={item.href} key={item.title}>
            <h2 className="text-sm font-semibold">{item.title}</h2>
            <p className="mt-2 text-xs leading-5 text-muted-foreground">{item.desc}</p>
          </Link>
        ))}
      </section>

      <Card className="p-5">
        <h2 className="text-lg font-semibold">左边每个图标是什么意思</h2>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {leftMenuItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link className="rounded-md border border-border bg-background p-4 transition hover:border-primary/40 hover:bg-accent" href={item.href} key={item.name}>
                <div className="flex items-center gap-3">
                  <span className="flex h-9 w-9 items-center justify-center rounded-md bg-primary/10 text-primary">
                    <Icon aria-hidden className="h-4 w-4" />
                  </span>
                  <h3 className="font-semibold">{item.name}</h3>
                </div>
                <p className="mt-3 text-xs leading-5 text-muted-foreground">{item.use}</p>
              </Link>
            );
          })}
        </div>
      </Card>

      <section className="grid gap-4 lg:grid-cols-2">
        <Card className="p-5">
          <h2 className="text-lg font-semibold">页面上常见按钮怎么用</h2>
          <div className="mt-4 space-y-3">
            {topRules.map((rule) => (
              <div className="rounded-md border border-border bg-background p-3 text-sm leading-6 text-muted-foreground" key={rule}>
                {rule}
              </div>
            ))}
          </div>
        </Card>
        <Card className="p-5">
          <h2 className="text-lg font-semibold">四个平台怎么接</h2>
          <div className="mt-4 space-y-3">
            {platformSteps.map((step) => (
              <div className="rounded-md border border-border bg-background p-3" key={step.title}>
                <h3 className="text-sm font-semibold">{step.title}</h3>
                <p className="mt-1 text-xs leading-5 text-muted-foreground">{step.desc}</p>
              </div>
            ))}
          </div>
          <Link className="mt-5 inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground" href="/settings/integrations">
            去平台集成窗口
          </Link>
        </Card>
      </section>

      <Card className="p-5">
        <div className="flex items-start gap-3">
          <ShieldAlert className="mt-1 h-5 w-5 shrink-0 text-warning" />
          <div>
            <h2 className="text-lg font-semibold">如果不知道该点哪里</h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              回到老板首页。只点“导入店铺数据”“处理客户消息”“处理售后审批”“看省了多少钱”这四个入口。其它页面先不用管。
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
