import Link from "next/link";
import { ArrowRight, BarChart3, Boxes, Megaphone, MessageCircle, PackageSearch, RefreshCcw, ShieldCheck, Star } from "lucide-react";
import { Badge } from "@/shared/ui/badge";
import { Card } from "@/shared/ui/card";

const skillGroups = [
  {
    title: "AI 客服知识",
    owner: "AI 客服",
    icon: MessageCircle,
    source: "TikTok Shop Customer Service / Customer Feedback Analysis",
    items: ["响应时间", "客户满意度", "自动回复边界", "买家争议处理", "反馈情绪识别"],
    value: "让客服先处理高频、低风险问题，不确定时升级给老板。"
  },
  {
    title: "AI 售后知识",
    owner: "AI 售后",
    icon: RefreshCcw,
    source: "E-Commerce Returns Management / TikTok Shop Returns",
    items: ["退货原因分析", "逆向物流", "退货成本", "退款风险", "售后挽留"],
    value: "把售后从“凭感觉处理”变成“先分类、再算成本、最后审批”。"
  },
  {
    title: "AI 运营：商品内容",
    owner: "AI 运营",
    icon: PackageSearch,
    source: "Product Title Optimization / Product Description Generator",
    items: ["标题关键词", "卖点结构", "描述优化", "平台字数限制", "A/B 测试候选"],
    value: "让运营先找标题和详情页缺口，再给老板可审批的改写方案。"
  },
  {
    title: "AI 运营：投流预算",
    owner: "AI 运营",
    icon: Megaphone,
    source: "E-Commerce PPC Strategy Planner",
    items: ["盈亏平衡 ROAS", "目标 ROAS", "最大 CPA", "渠道预算分配", "广告素材方向"],
    value: "投流建议必须先算毛利和回本线，禁止只给空泛投放建议。"
  },
  {
    title: "AI 运营：库存预警",
    owner: "AI 运营",
    icon: Boxes,
    source: "Warehouse Optimization / Restock Alert",
    items: ["库存周转", "缺货率", "ABC 分类", "安全库存", "补货点"],
    value: "把低库存、滞销和爆款补货变成每天可检查的运营动作。"
  },
  {
    title: "AI 运营：价格与竞品",
    owner: "AI 运营",
    icon: BarChart3,
    source: "Competitor Price Analysis / Dynamic Pricing",
    items: ["价格带", "竞品分层", "价格空位", "促销频率", "毛利保护"],
    value: "先判断价格有没有空间，再决定是否降价、捆绑或做活动。"
  },
  {
    title: "AI 运营：评价口碑",
    owner: "AI 运营",
    icon: Star,
    source: "Product Review Analysis / Review Monitoring",
    items: ["差评原因", "好评卖点", "功能需求", "投诉聚类", "详情页改进点"],
    value: "把评价和客服反馈沉淀成商品、详情页、售后 SOP 的改进清单。"
  },
  {
    title: "安全边界",
    owner: "AI Boss",
    icon: ShieldCheck,
    source: "AI Commerce OS 内部规则",
    items: ["退款审批", "赔偿审批", "预算审批", "改价审批", "投诉升级"],
    value: "外部技能只提供分析框架，所有高风险动作仍然必须老板确认。"
  }
];

const adoptionSteps = [
  "先把外部技能改写成中文知识，不直接复制英文技能原文。",
  "再把知识绑定到 AI 客服、AI 售后、AI 运营的工作场景。",
  "接真实数据后，用 Replay 验证这些知识是否真的降低人工接管率。",
  "老板确认有效后，再进入 Training Center，沉淀成 Memory、Knowledge 或 Workflow。"
];

export function KnowledgeBaseView() {
  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 border-b border-border pb-5 lg:flex-row lg:items-end">
        <div>
          <p className="text-sm font-medium text-primary">Knowledge Base</p>
          <h1 className="mt-2 text-3xl font-semibold">电商技能知识库</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            已吸收 `eCommerce-Skills` 中适合当前阶段的框架：客服、售后、商品、投流、库存、价格和评价。它们先作为知识和 SOP，不直接变成自动执行权限。
          </p>
        </div>
        <Link className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground" href="/training-center">
          去训练中心
          <ArrowRight aria-hidden className="ml-2 h-4 w-4" />
        </Link>
      </header>

      <section className="grid gap-3 md:grid-cols-4">
        <Metric title="已吸收技能方向" value="8 类" desc="覆盖客服、售后、运营的核心重复工作。" />
        <Metric title="优先服务对象" value="3 个 AI" desc="AI客服、AI售后、AI运营。" />
        <Metric title="当前形态" value="知识 / SOP" desc="先指导 AI 判断，不直接操作店铺。" />
        <Metric title="下一步验证" value="Replay" desc="用真实历史数据验证是否减少人工。" />
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        {skillGroups.map((group) => {
          const Icon = group.icon;
          return (
            <Card className="p-5" key={group.title}>
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
                    <Icon aria-hidden className="h-5 w-5" />
                  </span>
                  <div>
                    <h2 className="text-base font-semibold">{group.title}</h2>
                    <p className="mt-1 text-xs text-muted-foreground">来源：{group.source}</p>
                  </div>
                </div>
                <Badge tone="green">{group.owner}</Badge>
              </div>
              <p className="mt-4 text-sm leading-6 text-muted-foreground">{group.value}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {group.items.map((item) => (
                  <span className="rounded-md border border-border bg-background px-2.5 py-1 text-xs text-muted-foreground" key={item}>
                    {item}
                  </span>
                ))}
              </div>
            </Card>
          );
        })}
      </section>

      <Card className="p-5">
        <h2 className="text-lg font-semibold">吸收原则</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-4">
          {adoptionSteps.map((step, index) => (
            <div className="rounded-md border border-border bg-background p-4" key={step}>
              <p className="text-xs font-medium text-primary">步骤 {index + 1}</p>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">{step}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

function Metric({ desc, title, value }: { desc: string; title: string; value: string }) {
  return (
    <Card className="p-4">
      <p className="text-xs text-muted-foreground">{title}</p>
      <p className="mt-2 text-xl font-semibold">{value}</p>
      <p className="mt-2 text-xs leading-5 text-muted-foreground">{desc}</p>
    </Card>
  );
}
