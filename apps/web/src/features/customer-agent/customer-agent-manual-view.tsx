import Link from "next/link";
import { ArrowLeft, BookOpen, CheckCircle2, ShieldAlert, Sparkles, UserCheck } from "lucide-react";
import { Badge } from "@/shared/ui/badge";
import { Card } from "@/shared/ui/card";

const dailySteps = [
  "进入 AI客服工作台，先看平台消息收件箱。",
  "优先处理标记为“需人工”的消息。",
  "检查 AI 回复草稿，正确就发送，不正确就修改。",
  "退款、赔偿、投诉、差评、金额相关问题必须人工接管。",
  "每次修改 AI 草稿后，都要记录商家修改，让系统学习。"
];

const autoAllowed = ["商品基础咨询", "订单状态查询", "物流状态查询", "普通 FAQ", "发货时间说明"];

const humanRequired = ["退款", "退货", "赔偿", "投诉", "差评", "价格承诺", "客户情绪激烈", "平台规则风险"];

const learningItems = ["客户原问题", "AI 原草稿", "商家最终回复", "是否人工接管", "最终处理结果"];

export function CustomerAgentManualView() {
  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 border-b border-border pb-5 md:flex-row md:items-end">
        <div>
          <Link className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground" href="/ai-employees/ai-customer/workbench">
            <ArrowLeft className="mr-2 h-4 w-4" />
            返回 AI客服工作台
          </Link>
          <p className="mt-5 text-sm font-medium text-primary">客服培训文档</p>
          <h1 className="mt-2 text-3xl font-semibold">AI客服商家使用说明书</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            这份说明书给老板、客服主管和一线客服使用。当前试用版重点是安全回复、人工接管和收集高质量学习样本。
          </p>
        </div>
        <Badge tone="green">试用版安全边界</Badge>
      </header>

      <section className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
        <Card className="p-5">
          <div className="flex items-center gap-2">
            <BookOpen className="h-4 w-4 text-primary" />
            <h2 className="text-lg font-semibold">AI客服是什么</h2>
          </div>
          <p className="mt-4 text-sm leading-6 text-muted-foreground">
            AI客服不是普通聊天机器人，而是一个可被管理、可被纠正、可学习的数字客服员工。它负责汇总平台消息、生成低风险回复草稿、暂停高风险问题，并记录商家每一次修改。
          </p>
        </Card>

        <Card className="p-5">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-warning" />
            <h2 className="text-lg font-semibold">绝对不能自动处理</h2>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {humanRequired.map((item) => (
              <span className="rounded-md border border-warning/30 bg-warning/10 px-2.5 py-1 text-xs text-muted-foreground" key={item}>
                {item}
              </span>
            ))}
          </div>
        </Card>
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        <InstructionCard icon={<CheckCircle2 className="h-4 w-4 text-primary" />} items={dailySteps} title="每天怎么用" />
        <InstructionCard icon={<Sparkles className="h-4 w-4 text-primary" />} items={autoAllowed} title="可自动回复范围" />
        <InstructionCard icon={<UserCheck className="h-4 w-4 text-primary" />} items={learningItems} title="需要沉淀的数据" />
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <Card className="p-5">
          <h2 className="text-lg font-semibold">处理一条消息的标准流程</h2>
          <div className="mt-4 space-y-3 text-sm leading-6 text-muted-foreground">
            <p>AI 草稿正确：阅读客户原文，确认没有退款、赔偿、价格承诺后发送。</p>
            <p>AI 草稿不准确：直接修改草稿，改成客服真实会说的话，再记录商家修改。</p>
            <p>AI 标记需人工：点击人工接管，按店铺规则处理，再把最终处理结果写回系统。</p>
          </div>
        </Card>

        <Card className="p-5">
          <h2 className="text-lg font-semibold">私域获客和投流边界</h2>
          <p className="mt-4 text-sm leading-6 text-muted-foreground">
            AI客服可以识别高意向客户、生成私域引导话术、建议优惠券和同步线索给 AI运营。自动加微信、自动群发、自动投广告、自动调整预算都必须先进入老板审批。
          </p>
        </Card>
      </section>

      <Card className="p-5">
        <h2 className="text-lg font-semibold">一句话原则</h2>
        <p className="mt-4 rounded-md bg-muted p-4 text-sm leading-6 text-muted-foreground">
          AI能答低风险问题；高风险问题交给人；客服每次修改都要让系统学会。
        </p>
      </Card>
    </div>
  );
}

function InstructionCard({
  icon,
  items,
  title
}: {
  icon: React.ReactNode;
  items: string[];
  title: string;
}) {
  return (
    <Card className="p-5">
      <div className="flex items-center gap-2">
        {icon}
        <h2 className="text-base font-semibold">{title}</h2>
      </div>
      <div className="mt-4 space-y-3">
        {items.map((item) => (
          <div className="rounded-md border border-border bg-background px-3 py-2 text-sm text-muted-foreground" key={item}>
            {item}
          </div>
        ))}
      </div>
    </Card>
  );
}
