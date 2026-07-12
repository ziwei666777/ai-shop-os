"use client";

import Link from "next/link";
import { Cable, KeyRound } from "lucide-react";
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

export function IntegrationsView({ connectors }: { connectors: ConnectorStatus[] }) {
  const [pendingPlatform, setPendingPlatform] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<Record<string, string>>({});

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
        <h1 className="mt-2 text-3xl font-semibold">平台集成</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
          淘宝、抖音只通过官方接口（API）和授权登录（OAuth）接入；闲鱼仅使用平台导出的文件，不采集 Cookie、不扫码托管账号、不抓包。
        </p>
      </header>

      <section className="grid gap-4 lg:grid-cols-2">
        {connectors.map((connector) => (
          <Card className="p-5" key={connector.platform}>
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <Cable className="h-4 w-4 text-primary" />
                  <h2 className="text-lg font-semibold">{connector.display_name}</h2>
                </div>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{connector.next_action}</p>
              </div>
              <Badge tone={connector.status === "connected" ? "green" : "amber"}>
                {connector.status === "connected" ? "已连接" : connector.status === "not_connected" ? "等待官方能力" : "待配置"}
              </Badge>
            </div>
            <div className="mt-5 flex flex-wrap gap-2">
              {connector.scopes.map((scope) => (
                <span className="rounded-md bg-muted px-2.5 py-1 text-xs text-muted-foreground" key={scope}>
                  {scopeLabels[scope] ?? scope}
                </span>
              ))}
            </div>
            {feedback[connector.platform] ? <p className="mt-4 text-xs leading-5 text-warning">{feedback[connector.platform]}</p> : null}
            {connector.platform === "xianyu" ? (
              <Link className="mt-5 inline-flex h-10 items-center justify-center rounded-md border border-border bg-card px-4 text-sm font-medium hover:bg-accent" href="/settings/data-import"><KeyRound className="mr-2 h-4 w-4" />使用文件导入</Link>
            ) : connector.platform === "taobao" || connector.platform === "douyin" ? (
              <Button className="mt-5" disabled={pendingPlatform !== null} onClick={() => handleAuthorize(connector.platform as "taobao" | "douyin")} type="button" variant="secondary"><KeyRound className="mr-2 h-4 w-4" />{pendingPlatform === connector.platform ? "正在准备授权" : "开始官方授权"}</Button>
            ) : (
              <Button className="mt-5" disabled type="button" variant="secondary"><KeyRound className="mr-2 h-4 w-4" />后续接入</Button>
            )}
          </Card>
        ))}
      </section>
    </div>
  );
}
