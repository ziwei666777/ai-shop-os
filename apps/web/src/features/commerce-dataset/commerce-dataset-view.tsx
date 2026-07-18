import Link from "next/link";
import { ArrowRight, CheckCircle2, Database, FileJson, RotateCcw, ShieldCheck } from "lucide-react";
import type { CommerceDatasetReadiness, DatasetReadinessItem } from "@/shared/api/types";
import { Badge } from "@/shared/ui/badge";
import { Card } from "@/shared/ui/card";

const datasetDetails: Record<DatasetReadinessItem["kind"], { purpose: string; fields: string[] }> = {
  after_sales: {
    purpose: "让 AI 售后学习退款、退货、投诉和赔偿决策。",
    fields: ["external_id", "order_external_id", "status", "case_type", "reason", "proofPics"]
  },
  customers: {
    purpose: "让 AI 识别高价值客户、复购客户和私域跟进对象。",
    fields: ["external_id", "name", "tags", "order_count", "total_spent"]
  },
  messages: {
    purpose: "让 Replay 对比人工回复和 AI 回复，训练客服话术。",
    fields: ["external_id", "customer_id", "content", "reply", "created_at"]
  },
  orders: {
    purpose: "让 AI 客服查询订单，让 Replay 复盘历史人工处理。",
    fields: ["external_id", "status", "total_amount", "customer_name", "paid_at", "payAmount", "orderSn"]
  },
  products: {
    purpose: "让 AI 客服回答商品问题，让 AI 运营发现详情页缺口。",
    fields: ["external_id", "title", "price", "sku", "inventory_count", "productName", "productSkuCode"]
  },
  shipments: {
    purpose: "让 AI 客服和售后判断物流异常、催发货和签收状态。",
    fields: ["external_id", "order_external_id", "carrier_name", "tracking_number", "status"]
  }
};

export function CommerceDatasetView({ summary }: { summary: CommerceDatasetReadiness }) {
  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 border-b border-border pb-5 lg:flex-row lg:items-end">
        <div>
          <p className="text-sm font-medium text-primary">Commerce Dataset</p>
          <h1 className="mt-2 text-3xl font-semibold">标准电商数据集</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            这里不是订单系统，也不是 ERP。这里负责把淘宝、抖音、闲鱼等平台的历史数据整理成 AI 可以 Replay、Evaluation 和 Training 的统一输入。
          </p>
        </div>
        <Link className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground" href="/settings/data-import">
          导入数据
          <ArrowRight aria-hidden className="ml-2 h-4 w-4" />
        </Link>
      </header>

      <section className="grid gap-3 md:grid-cols-4">
        <GateCard desc="至少要覆盖订单、消息、售后，才能验证 AI 是否能替人。" title="数据类型覆盖率" value={`${summary.replay_ready_count} / ${summary.total_kinds}`} />
        <GateCard desc="根据当前订单、消息、售后和物流数据估算。" title="预计可回放" value={`${summary.estimated_replay_cases} 条`} />
        <GateCard desc="低于 80% 时，不建议承诺替代完整岗位。" title="平均准备度" value={`${summary.average_readiness}%`} />
        <GateCard desc="导入后进入 Replay、Evaluation 和 Training。" title="支持格式" value="CSV / Excel / JSON" />
      </section>

      <Card className="p-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-lg font-semibold">当前数据可用性</h2>
            <p className="mt-1 text-sm text-muted-foreground">真实商家能不能连续使用 30 天，先看数据能不能支撑 AI 接管工作。</p>
          </div>
          <Badge tone={summary.average_readiness >= 80 ? "green" : "amber"}>平均准备度 {summary.average_readiness}%</Badge>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-3">
          <DatasetPrinciple icon={Database} title="统一输入" desc="所有 Agent 共用同一套标准数据，不各自维护孤岛数据。" />
          <DatasetPrinciple icon={RotateCcw} title="可 Replay" desc="每条历史消息、订单和售后都要能重新跑 AI 决策。" />
          <DatasetPrinciple icon={ShieldCheck} title="可 Evaluation" desc="每次导入都要能计算字段完整率、错误率和可回放记录数。" />
        </div>
      </Card>

      <section className="grid gap-4 xl:grid-cols-2">
        {summary.items.map((dataset) => (
          <Card className="p-5" key={dataset.kind}>
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="text-base font-semibold">{dataset.label}</h3>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{datasetDetails[dataset.kind].purpose}</p>
              </div>
              <Badge tone={dataset.readiness >= 70 ? "green" : dataset.readiness >= 40 ? "amber" : "neutral"}>{dataset.readiness}%</Badge>
            </div>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <Info label="服务对象" value={dataset.owner} />
              <Info label="当前记录数" value={`${dataset.record_count} 条`} />
            </div>
            {dataset.missing_reason ? <p className="mt-3 rounded-md bg-muted p-3 text-xs leading-5 text-muted-foreground">{dataset.missing_reason}</p> : null}
            <div className="mt-4 flex flex-wrap gap-2">
              {datasetDetails[dataset.kind].fields.map((field) => (
                <span className="rounded-md border border-border bg-background px-2.5 py-1 text-xs text-muted-foreground" key={field}>
                  {field}
                </span>
              ))}
            </div>
          </Card>
        ))}
      </section>

      <Card className="p-5">
        <h2 className="font-semibold">下一步导入建议</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          {summary.next_actions.map((action, index) => (
            <div className="rounded-md bg-muted p-3 text-sm leading-6 text-muted-foreground" key={action}>
              <span className="mb-2 block text-xs font-medium text-foreground">步骤 {index + 1}</span>
              {action}
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-5">
        <h2 className="font-semibold">已吸收成熟商城字段</h2>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">
          参考成熟商城项目的订单、商品、退货申请模型后，导入预览已能自动识别常见字段，例如 orderSn、payAmount、productName、productSkuCode、deliverySn、proofPics。
          这些字段不会改变数据库结构，只作为 Commerce Dataset、Replay 和 AI售后的映射参考。
        </p>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          <DatasetPrinciple icon={Database} title="订单字段" desc="识别 orderSn、memberUsername、payAmount、paymentTime，用于客服查单和 Replay。" />
          <DatasetPrinciple icon={ShieldCheck} title="售后字段" desc="识别 reason、description、proofPics，用于售后风险判断和证据完整度检查。" />
          <DatasetPrinciple icon={RotateCcw} title="商品字段" desc="识别 productName、productSkuCode、productPrice，让 AI客服回答商品问题更稳。" />
        </div>
      </Card>

      <Card className="p-5">
        <div className="flex items-start gap-3">
          <FileJson aria-hidden className="mt-1 h-5 w-5 text-primary" />
          <div>
            <h2 className="font-semibold">JSON 导入规则</h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              JSON 只接受顶层数组，或包含 items、rows、data 数组的对象。数组里的每一项必须是对象。复杂字段会转成 JSON 字符串进入预览，不执行脚本，不保存非必要敏感数据。
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}

function GateCard({ desc, title, value }: { desc: string; title: string; value: string }) {
  return (
    <Card className="p-4">
      <p className="text-xs text-muted-foreground">{title}</p>
      <p className="mt-2 text-xl font-semibold">{value}</p>
      <p className="mt-2 text-xs leading-5 text-muted-foreground">{desc}</p>
    </Card>
  );
}

function DatasetPrinciple({ desc, icon: Icon, title }: { desc: string; icon: typeof CheckCircle2; title: string }) {
  return (
    <div className="rounded-md border border-border bg-background p-4">
      <Icon aria-hidden className="h-5 w-5 text-primary" />
      <h3 className="mt-3 font-semibold">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">{desc}</p>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-medium text-muted-foreground">{label}</p>
      <p className="mt-1 text-sm">{value}</p>
    </div>
  );
}
