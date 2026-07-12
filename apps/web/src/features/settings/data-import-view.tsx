"use client";

import { useState } from "react";
import { AlertCircle, CheckCircle2, FileSpreadsheet, UploadCloud } from "lucide-react";
import { previewImportFile, submitImportFile } from "@/shared/api/client";
import type { CommercePlatform, ImportDataType, ImportJob, ImportPreview } from "@/shared/api/types";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";

const platformLabels: Record<CommercePlatform, string> = { taobao: "淘宝", douyin: "抖音商店", xianyu: "闲鱼" };
const dataTypeLabels: Record<ImportDataType, string> = { products: "商品", orders: "订单", order_items: "订单明细", customers: "客户", shipments: "物流", after_sales: "售后" };
const fieldLabels: Record<string, string> = {
  external_id: "平台编号", title: "名称或标题", sku: "商家编码", price: "价格", inventory_count: "库存",
  customer_name: "客户名称", status: "状态", total_amount: "订单金额", paid_at: "付款时间",
  order_external_id: "关联订单号", quantity: "数量", unit_price: "单价", name: "客户名称", tags: "客户标签",
  carrier_name: "物流公司", tracking_number: "运单号", case_type: "售后类型", reason: "售后原因"
};

export function DataImportView({ initialJobs }: { initialJobs: ImportJob[] }) {
  const [platform, setPlatform] = useState<CommercePlatform>("xianyu");
  const [dataType, setDataType] = useState<ImportDataType>("orders");
  const [shopName, setShopName] = useState("闲鱼店铺");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<ImportPreview | null>(null);
  const [mapping, setMapping] = useState<Record<string, string>>({});
  const [jobs, setJobs] = useState(initialJobs);
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<{ error: boolean; message: string } | null>(null);

  async function handlePreview() {
    if (!file) { setFeedback({ error: true, message: "请先选择 CSV 或 .xlsx 文件。" }); return; }
    setBusy(true); setFeedback(null);
    const result = await previewImportFile(file, platform, dataType);
    setBusy(false);
    if (result.error || !result.data) { setFeedback({ error: true, message: result.error ?? "文件预览失败。" }); return; }
    setPreview(result.data); setMapping(result.data.suggested_mapping);
    setFeedback({ error: false, message: "文件读取成功，请检查字段对应关系。" });
  }

  async function handleSubmit() {
    if (!file || !preview) { setFeedback({ error: true, message: "请先完成文件预览。" }); return; }
    const missing = preview.required_fields.filter((field) => !mapping[field]);
    if (missing.length) { setFeedback({ error: true, message: `请先匹配必填字段：${missing.map((field) => fieldLabels[field] ?? field).join("、")}` }); return; }
    setBusy(true); setFeedback(null);
    const result = await submitImportFile(file, platform, dataType, shopName.trim(), mapping);
    setBusy(false);
    if (result.error || !result.data) { setFeedback({ error: true, message: result.error ?? "提交失败。" }); return; }
    setJobs((current) => [result.data!, ...current]);
    setFeedback({ error: false, message: "导入任务已提交，系统正在后台处理。" });
  }

  function resetPreview() { setPreview(null); setMapping({}); setFeedback(null); }

  return (
    <div className="space-y-6">
      <header className="border-b border-border pb-5"><p className="text-sm font-medium text-primary">系统设置</p><h1 className="mt-2 text-3xl font-semibold">平台数据导入</h1><p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">淘宝和抖音支持官方授权与文件导入；闲鱼只接受平台导出的 CSV/Excel。所有操作只读，不会退款、改价、上下架或发货。</p></header>
      <div className="grid gap-3 sm:grid-cols-4">{["选择数据", "上传文件", "匹配字段", "确认结果"].map((label, index) => <div className="flex items-center gap-3 rounded-md border border-border bg-card p-3" key={label}><span className="flex h-7 w-7 items-center justify-center rounded-full bg-muted text-xs font-semibold">{index + 1}</span><span className="text-sm font-medium">{label}</span></div>)}</div>
      <Card className="p-5">
        <div className="grid gap-4 md:grid-cols-3">
          <label className="text-sm font-medium">平台<select className="mt-2 h-10 w-full rounded-md border border-border bg-background px-3 font-normal" onChange={(event) => { setPlatform(event.target.value as CommercePlatform); setShopName(`${platformLabels[event.target.value as CommercePlatform]}店铺`); resetPreview(); }} value={platform}><option value="taobao">淘宝</option><option value="douyin">抖音商店</option><option value="xianyu">闲鱼</option></select></label>
          <label className="text-sm font-medium">数据类型<select className="mt-2 h-10 w-full rounded-md border border-border bg-background px-3 font-normal" onChange={(event) => { setDataType(event.target.value as ImportDataType); resetPreview(); }} value={dataType}>{Object.entries(dataTypeLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
          <label className="text-sm font-medium">店铺名称<input className="mt-2 h-10 w-full rounded-md border border-border bg-background px-3 font-normal outline-none focus:border-primary" onChange={(event) => setShopName(event.target.value)} value={shopName} /></label>
        </div>
        <label className="mt-5 flex min-h-32 cursor-pointer flex-col items-center justify-center rounded-md border border-dashed border-border bg-background p-5 text-center"><UploadCloud className="h-6 w-6 text-primary" /><span className="mt-2 text-sm font-medium">{file?.name ?? "选择 CSV 或 .xlsx 文件"}</span><span className="mt-1 text-xs text-muted-foreground">最大 20MB；CSV 支持 UTF-8、UTF-8 BOM、GB18030</span><input accept=".csv,.xlsx" className="sr-only" onChange={(event) => { setFile(event.target.files?.[0] ?? null); resetPreview(); }} type="file" /></label>
        <div className="mt-4 flex flex-wrap gap-3"><Button disabled={busy || !file} onClick={handlePreview} type="button" variant="secondary"><FileSpreadsheet className="mr-2 h-4 w-4" />{busy ? "读取中" : "预览文件"}</Button>{preview ? <Button disabled={busy || !shopName.trim()} onClick={handleSubmit} type="button">{busy ? "提交中" : "确认并开始导入"}</Button> : null}</div>
        {feedback ? <div className={`mt-4 flex items-start gap-2 rounded-md border p-3 text-sm ${feedback.error ? "border-red-500/30 bg-red-500/10" : "border-primary/30 bg-primary/10"}`}>{feedback.error ? <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-500" /> : <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />}<span>{feedback.message}</span></div> : null}
      </Card>
      {preview ? <Card className="overflow-hidden"><div className="border-b border-border p-4"><h2 className="font-semibold">字段对应关系</h2><p className="mt-1 text-xs text-muted-foreground">左侧是系统字段，右侧选择文件中的列。带“必填”的字段必须匹配。</p></div><div className="grid gap-3 p-4 md:grid-cols-2">{Object.keys(fieldLabels).filter((field) => preview.required_fields.includes(field) || mapping[field]).map((field) => <label className="grid grid-cols-[minmax(110px,1fr)_minmax(150px,1.5fr)] items-center gap-3 text-sm" key={field}><span>{fieldLabels[field] ?? field}{preview.required_fields.includes(field) ? <strong className="ml-1 text-red-500">必填</strong> : null}</span><select className="h-10 rounded-md border border-border bg-background px-3" onChange={(event) => setMapping((current) => ({ ...current, [field]: event.target.value }))} value={mapping[field] ?? ""}><option value="">不导入</option>{preview.headers.map((header) => <option key={header} value={header}>{header}</option>)}</select></label>)}</div><div className="border-t border-border p-4"><p className="mb-3 text-sm font-medium">数据样例</p><Table><TableHeader><TableRow>{preview.headers.slice(0, 6).map((header) => <TableHead key={header}>{header}</TableHead>)}</TableRow></TableHeader><TableBody>{preview.sample_rows.map((row, index) => <TableRow key={index}>{preview.headers.slice(0, 6).map((header) => <TableCell key={header}>{row[header]}</TableCell>)}</TableRow>)}</TableBody></Table></div></Card> : null}
      <Card className="overflow-hidden"><div className="border-b border-border p-4"><h2 className="font-semibold">最近导入任务</h2></div>{jobs.length ? <Table><TableHeader><TableRow><TableHead>平台</TableHead><TableHead>数据</TableHead><TableHead>状态</TableHead><TableHead>进度</TableHead><TableHead>成功 / 失败</TableHead><TableHead>错误摘要</TableHead></TableRow></TableHeader><TableBody>{jobs.map((job) => <TableRow key={job.id}><TableCell>{platformLabels[job.platform]}</TableCell><TableCell>{dataTypeLabels[job.data_type]}</TableCell><TableCell><Badge tone={job.status === "succeeded" ? "green" : "amber"}>{jobStatusLabel(job.status)}</Badge></TableCell><TableCell>{job.progress}%</TableCell><TableCell>{job.success_count} / {job.failure_count}</TableCell><TableCell className="max-w-xs truncate">{job.error_summary ?? "无"}</TableCell></TableRow>)}</TableBody></Table> : <div className="p-8 text-center text-sm text-muted-foreground">还没有导入任务。完成一次预览并确认后，任务会出现在这里。</div>}</Card>
    </div>
  );
}

function jobStatusLabel(status: ImportJob["status"]) { return { queued: "等待中", running: "执行中", partial_success: "部分成功", succeeded: "成功", failed: "失败" }[status]; }
