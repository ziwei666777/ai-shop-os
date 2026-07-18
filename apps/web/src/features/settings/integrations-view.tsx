"use client";

import Link from "next/link";
import { Cable, FileSpreadsheet, KeyRound, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import type { ConnectorStatus } from "@/shared/api/types";
import { startConnectorOAuth } from "@/shared/api/client";

const scopeLabels: Record<string, string> = {
  read_orders: "读取订单",
  read_products: "读取商品",
  read_customers: "读取客户"
};

type MerchantPlatform = "taobao" | "douyin" | "pdd" | "xianyu";

const platformGuides: Array<{
  platform: MerchantPlatform;
  displayName: string;
  statusLabel: string;
  statusTone: "green" | "amber" | "neutral";
  safeMode: string;
  need: string[];
  steps: string[];
  buttonLabel: string;
  href?: string;
}> = [
  {
    platform: "taobao",
    displayName: "淘宝 / 天猫",
    statusLabel: "官方授权优先",
    statusTone: "amber",
    safeMode: "只用淘宝开放平台或服务商授权；没有权限时先用文件导入。",
    need: ["店铺管理员账号", "淘宝开放平台应用或服务商权限", "订单、商品、物流、售后读取权限"],
    steps: ["点“开始官方授权”。", "跳到淘宝官方页面后，由店铺管理员确认授权。", "授权成功后，系统只读同步数据，不会自动退款、改价、发货。"],
    buttonLabel: "开始官方授权"
  },
  {
    platform: "douyin",
    displayName: "抖音商店 / 抖店",
    statusLabel: "官方授权优先",
    statusTone: "amber",
    safeMode: "只用抖店开放平台；正式授权前可以先导出文件试用。",
    need: ["抖店管理员账号", "抖店开放平台应用", "订单、商品、物流、售后读取权限"],
    steps: ["点“开始官方授权”。", "进入抖店官方授权页。", "授权成功后，先同步最近 30 天订单和售后，再进入 AI评分。"],
    buttonLabel: "开始官方授权"
  },
  {
    platform: "pdd",
    displayName: "拼多多",
    statusLabel: "接入窗口已预留",
    statusTone: "neutral",
    safeMode: "当前不伪装已接通；需要拼多多开放平台或服务商权限后再启用真实授权。",
    need: ["拼多多店铺管理员账号", "拼多多开放平台或服务商应用", "订单、商品、售后、物流读取权限"],
    steps: ["先准备开放平台权限。", "权限没准备好时，先导出订单、商品、售后文件。", "用“数据导入”先让 AI 试跑 Replay 和 Evaluation。"],
    buttonLabel: "先用文件导入",
    href: "/settings/data-import"
  },
  {
    platform: "xianyu",
    displayName: "闲鱼",
    statusLabel: "文件导入模式",
    statusTone: "neutral",
    safeMode: "只接受文件导入；不扫码托管账号、不拿 Cookie、不抓包。",
    need: ["闲鱼后台或商家自己导出的订单文件", "商品文件", "售后或聊天整理文件"],
    steps: ["从闲鱼导出或整理 CSV / Excel / JSON 文件。", "进入“数据导入”。", "一次只导入一种数据：订单、商品、客户、物流或售后。"],
    buttonLabel: "使用文件导入",
    href: "/settings/data-import"
  }
];

export function IntegrationsView({ connectors }: { connectors: ConnectorStatus[] }) {
  const [pendingPlatform, setPendingPlatform] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<Record<string, string>>({});
  const connectorByPlatform = new Map<string, ConnectorStatus>(connectors.map((connector) => [connector.platform, connector]));

  async function handleAuthorize(platform: "taobao" | "douyin") {
    setPendingPlatform(platform);
    const result = await startConnectorOAuth(platform);
    setPendingPlatform(null);
    if (result.error || !result.data) {
      setFeedback((current) => ({ ...current, [platform]: result.error ?? "授权入口暂时不可用。" }));
      return;
    }
    window.location.assign(result.data.authorization_url);
  }

  return (
    <div className="space-y-6">
      <header className="border-b border-border pb-5">
        <p className="text-sm font-medium text-primary">系统设置</p>
        <h1 className="mt-2 text-3xl font-semibold">平台接入窗口</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
          商家只需要看自己用哪个平台。淘宝、抖店优先官方授权；拼多多先预留接入窗口；闲鱼只做安全文件导入。
        </p>
      </header>

      <section className="grid gap-4 lg:grid-cols-2">
        {platformGuides.map((guide) => {
          const connector = connectorByPlatform.get(guide.platform);
          const connected = connector?.status === "connected";

          return (
            <Card className="p-5" key={guide.platform}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <Cable className="h-4 w-4 text-primary" />
                    <h2 className="text-lg font-semibold">{guide.displayName}</h2>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">{guide.safeMode}</p>
                </div>
                <Badge tone={connected ? "green" : guide.statusTone}>{connected ? "已连接" : guide.statusLabel}</Badge>
              </div>

              <div className="mt-5 grid gap-4 md:grid-cols-2">
                <section className="rounded-md border border-border bg-background p-4">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="h-4 w-4 text-primary" />
                    <h3 className="text-sm font-semibold">商家要准备</h3>
                  </div>
                  <div className="mt-3 space-y-2">
                    {guide.need.map((item) => (
                      <p className="text-xs leading-5 text-muted-foreground" key={item}>• {item}</p>
                    ))}
                  </div>
                </section>
                <section className="rounded-md border border-border bg-background p-4">
                  <div className="flex items-center gap-2">
                    <FileSpreadsheet className="h-4 w-4 text-primary" />
                    <h3 className="text-sm font-semibold">怎么操作</h3>
                  </div>
                  <div className="mt-3 space-y-2">
                    {guide.steps.map((item, index) => (
                      <p className="text-xs leading-5 text-muted-foreground" key={item}>{index + 1}. {item}</p>
                    ))}
                  </div>
                </section>
              </div>

              {connector ? (
                <div className="mt-5 flex flex-wrap gap-2">
                  {connector.scopes.map((scope) => (
                    <span className="rounded-md bg-muted px-2.5 py-1 text-xs text-muted-foreground" key={scope}>
                      {scopeLabels[scope] ?? scope}
                    </span>
                  ))}
                </div>
              ) : null}

              {feedback[guide.platform] ? <p className="mt-4 text-xs leading-5 text-warning">{feedback[guide.platform]}</p> : null}

              {guide.href ? (
                <Link className="mt-5 inline-flex h-10 items-center justify-center rounded-md border border-border bg-card px-4 text-sm font-medium hover:bg-accent" href={guide.href}>
                  <KeyRound className="mr-2 h-4 w-4" />
                  {guide.buttonLabel}
                </Link>
              ) : guide.platform === "taobao" || guide.platform === "douyin" ? (
              <Button className="mt-5" disabled={pendingPlatform !== null} onClick={() => handleAuthorize(guide.platform as "taobao" | "douyin")} type="button" variant="secondary">
                  <KeyRound className="mr-2 h-4 w-4" />
                  {pendingPlatform === guide.platform ? "正在准备授权" : guide.buttonLabel}
                </Button>
              ) : (
                <Button className="mt-5" disabled type="button" variant="secondary">
                  <KeyRound className="mr-2 h-4 w-4" />
                  后续接入
                </Button>
              )}
            </Card>
          );
        })}
      </section>

      <Card className="p-5">
        <h2 className="text-lg font-semibold">给客服看的简单说明</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-4">
          <div className="rounded-md bg-muted p-3 text-xs leading-5 text-muted-foreground">淘宝：优先官方授权；没有权限就导文件。</div>
          <div className="rounded-md bg-muted p-3 text-xs leading-5 text-muted-foreground">抖店：优先官方授权；先同步最近 30 天。</div>
          <div className="rounded-md bg-muted p-3 text-xs leading-5 text-muted-foreground">拼多多：先准备开放平台权限；现在先文件导入。</div>
          <div className="rounded-md bg-muted p-3 text-xs leading-5 text-muted-foreground">闲鱼：只导文件，不托管账号，不扫码，不抓包。</div>
        </div>
      </Card>
    </div>
  );
}
