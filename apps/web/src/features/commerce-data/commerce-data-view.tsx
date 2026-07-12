"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { FileUp, Search, SlidersHorizontal } from "lucide-react";
import { Badge } from "@/shared/ui/badge";
import { Card } from "@/shared/ui/card";
import { DetailDrawer } from "@/shared/ui/detail-drawer";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import type { CommercePlatform } from "@/shared/api/types";

export interface CommerceRow {
  id: string;
  platform: CommercePlatform;
  shopName: string;
  primary: string;
  secondary: string;
  status: string;
  value: string;
  updatedAt: string;
  details: { label: string; value: string }[];
}

const platformLabels: Record<CommercePlatform, string> = { taobao: "淘宝", douyin: "抖音商店", xianyu: "闲鱼" };

export function CommerceDataView({ eyebrow, title, description, primaryLabel, secondaryLabel, valueLabel, rows }: {
  eyebrow: string; title: string; description: string; primaryLabel: string; secondaryLabel: string; valueLabel: string; rows: CommerceRow[];
}) {
  const [platform, setPlatform] = useState<"all" | CommercePlatform>("all");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<CommerceRow | null>(null);
  const filteredRows = useMemo(() => {
    const keyword = query.trim().toLowerCase();
    return rows.filter((row) => (platform === "all" || row.platform === platform) && (!keyword || [row.primary, row.secondary, row.shopName, row.status].join(" ").toLowerCase().includes(keyword)));
  }, [platform, query, rows]);

  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 border-b border-border pb-5 md:flex-row md:items-end">
        <div><p className="text-sm font-medium text-primary">{eyebrow}</p><h1 className="mt-2 text-3xl font-semibold">{title}</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">{description}</p></div>
        <Link className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground" href="/settings/data-import"><FileUp className="mr-2 h-4 w-4" />导入平台数据</Link>
      </header>
      <section className="grid gap-3 sm:grid-cols-3"><Metric label="当前记录" value={`${rows.length}`} /><Metric label="已覆盖平台" value={`${new Set(rows.map((row) => row.platform)).size}`} /><Metric label="当前筛选结果" value={`${filteredRows.length}`} /></section>
      <Card className="overflow-hidden">
        <div className="grid gap-2 border-b border-border p-4 sm:grid-cols-[minmax(220px,1fr)_180px]">
          <label className="relative"><Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><input className="h-10 w-full rounded-md border border-border bg-background pl-9 pr-3 text-sm outline-none focus:border-primary" onChange={(event) => setQuery(event.target.value)} placeholder="搜索编号、名称、店铺或状态" value={query} /></label>
          <select className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary" onChange={(event) => setPlatform(event.target.value as "all" | CommercePlatform)} value={platform}><option value="all">全部平台</option><option value="taobao">淘宝</option><option value="douyin">抖音商店</option><option value="xianyu">闲鱼</option></select>
        </div>
        <Table><TableHeader><TableRow><TableHead>{primaryLabel}</TableHead><TableHead>{secondaryLabel}</TableHead><TableHead>平台与店铺</TableHead><TableHead>状态</TableHead><TableHead>{valueLabel}</TableHead><TableHead>最近更新</TableHead></TableRow></TableHeader><TableBody>{filteredRows.map((row) => <TableRow className="cursor-pointer" key={row.id} onClick={() => setSelected(row)}><TableCell className="font-medium">{row.primary}</TableCell><TableCell>{row.secondary}</TableCell><TableCell><div>{platformLabels[row.platform]}</div><div className="mt-1 text-xs text-muted-foreground">{row.shopName}</div></TableCell><TableCell><Badge tone={row.status.includes("完成") || row.status === "在售" ? "green" : "amber"}>{row.status}</Badge></TableCell><TableCell>{row.value}</TableCell><TableCell className="text-muted-foreground">{formatDate(row.updatedAt)}</TableCell></TableRow>)}</TableBody></Table>
        {filteredRows.length === 0 ? <div className="flex flex-col items-center gap-2 px-6 py-12 text-sm text-muted-foreground"><SlidersHorizontal className="h-5 w-5" /><span>没有符合当前条件的数据。</span></div> : null}
      </Card>
      <DetailDrawer description={selected ? `${platformLabels[selected.platform]} / ${selected.shopName}` : undefined} onClose={() => setSelected(null)} open={Boolean(selected)} title={selected?.primary ?? "详情"}>{selected ? <dl className="grid gap-4 sm:grid-cols-2">{selected.details.map((detail) => <div className="rounded-md border border-border bg-background p-4" key={detail.label}><dt className="text-xs text-muted-foreground">{detail.label}</dt><dd className="mt-2 break-words text-sm font-medium">{detail.value || "未提供"}</dd></div>)}</dl> : null}</DetailDrawer>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) { return <Card className="p-4"><p className="text-xs text-muted-foreground">{label}</p><p className="mt-2 text-2xl font-semibold">{value}</p></Card>; }
function formatDate(value: string) { const date = new Date(value); return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat("zh-CN", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" }).format(date); }
