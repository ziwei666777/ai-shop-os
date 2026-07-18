"use client";

import { useState } from "react";
import { AlertCircle, CheckCircle2, FileDown, FileSpreadsheet, PlayCircle, ShieldCheck, UploadCloud } from "lucide-react";
import { previewImportFile, runLiveMetricScan, runPostLiveReview, runPreLiveCheck, submitImportFile } from "@/shared/api/client";
import type { CommercePlatform, ImportDataType, ImportJob, ImportPreview, LivePostReviewReport, LiveWorkflowReport } from "@/shared/api/types";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";

type ImportPlatformOption = CommercePlatform | "pdd";
type LiveRunResult = LiveWorkflowReport | LivePostReviewReport;

const platformLabels: Record<ImportPlatformOption, string> = { taobao: "淘宝", douyin: "抖音商店", pdd: "拼多多", xianyu: "闲鱼" };
const dataTypeLabels: Record<ImportDataType, string> = { products: "商品", orders: "订单", order_items: "订单明细", customers: "客户", shipments: "物流", after_sales: "售后" };
const fieldLabels: Record<string, string> = {
  external_id: "平台编号", title: "名称或标题", sku: "商家编码", price: "价格", inventory_count: "库存",
  customer_name: "客户名称", status: "状态", total_amount: "订单金额", paid_at: "付款时间",
  order_external_id: "关联订单号", quantity: "数量", unit_price: "单价", name: "客户名称", tags: "客户标签",
  carrier_name: "物流公司", tracking_number: "运单号", case_type: "售后类型", reason: "售后原因"
};

const templateLinks: Array<{ title: string; desc: string; href: string }> = [
  { title: "淘宝 / 天猫导入模板", desc: "适合订单、商品、客户、物流、售后先做文件试用。", href: "/templates/taobao-commerce-import-template.csv" },
  { title: "抖音商店 / 抖店导入模板", desc: "适合抖店订单、商品、售后导出后整理上传。", href: "/templates/douyin-commerce-import-template.csv" },
  { title: "拼多多导入模板", desc: "正式 API 未开启前，先用文件样本验证 AI 能力。", href: "/templates/pdd-commerce-import-template.csv" },
  { title: "闲鱼导入模板", desc: "只接受商家自己整理的安全文件，不托管账号。", href: "/templates/xianyu-commerce-import-template.csv" },
  { title: "直播商品检查模板", desc: "用于开播前检查库存、安全库存、日常价和直播价。", href: "/templates/live-products-template.csv" },
  { title: "直播优惠券检查模板", desc: "用于检查优惠券余量和是否过期，避免直播间福利失效。", href: "/templates/live-coupons-template.csv" },
  { title: "直播脚本检查模板", desc: "用于检查直播脚本、赠品准备和商品讲解顺序。", href: "/templates/live-script-template.csv" },
  { title: "直播中数据模板", desc: "用于导入在线人数、成交率、停留率、点击率和异常订单。", href: "/templates/live-metrics-template.csv" },
  { title: "下播复盘模板", desc: "用于生成直播复盘、退款风险和第二天直播建议。", href: "/templates/live-post-review-template.csv" }
];

export function DataImportView({ initialJobs }: { initialJobs: ImportJob[] }) {
  const [platform, setPlatform] = useState<ImportPlatformOption>("xianyu");
  const [dataType, setDataType] = useState<ImportDataType>("orders");
  const [shopName, setShopName] = useState("闲鱼店铺");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<ImportPreview | null>(null);
  const [mapping, setMapping] = useState<Record<string, string>>({});
  const [jobs, setJobs] = useState(initialJobs);
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<{ error: boolean; message: string } | null>(null);
  const [preLiveProductsFile, setPreLiveProductsFile] = useState<File | null>(null);
  const [preLiveCouponsFile, setPreLiveCouponsFile] = useState<File | null>(null);
  const [preLiveScriptFile, setPreLiveScriptFile] = useState<File | null>(null);
  const [liveMetricFile, setLiveMetricFile] = useState<File | null>(null);
  const [postLiveFile, setPostLiveFile] = useState<File | null>(null);
  const [liveBusy, setLiveBusy] = useState(false);
  const [liveFeedback, setLiveFeedback] = useState<{ error: boolean; message: string } | null>(null);
  const [liveReport, setLiveReport] = useState<LiveRunResult | null>(null);

  async function handlePreview() {
    if (!file) { setFeedback({ error: true, message: "请先选择 CSV、.xlsx 或 JSON 文件。" }); return; }
    if (platform === "pdd") { setFeedback({ error: true, message: "拼多多正式导入需要先确认数据库和后端平台枚举。本页已提供模板，接真实数据前再开启入库。" }); return; }
    setBusy(true); setFeedback(null);
    const result = await previewImportFile(file, platform, dataType);
    setBusy(false);
    if (result.error || !result.data) { setFeedback({ error: true, message: result.error ?? "文件预览失败。" }); return; }
    setPreview(result.data); setMapping(result.data.suggested_mapping);
    setFeedback({ error: false, message: "文件读取成功，请检查字段对应关系。" });
  }

  async function handleSubmit() {
    if (!file || !preview) { setFeedback({ error: true, message: "请先完成文件预览。" }); return; }
    if (platform === "pdd") { setFeedback({ error: true, message: "拼多多当前只开放模板和接入说明，暂不提交入库，避免真实数据平台字段不一致。" }); return; }
    const missing = preview.required_fields.filter((field) => !mapping[field]);
    if (missing.length) { setFeedback({ error: true, message: `请先匹配必填字段：${missing.map((field) => fieldLabels[field] ?? field).join("、")}` }); return; }
    setBusy(true); setFeedback(null);
    const result = await submitImportFile(file, platform, dataType, shopName.trim(), mapping);
    setBusy(false);
    if (result.error || !result.data) { setFeedback({ error: true, message: result.error ?? "提交失败。" }); return; }
    setJobs((current) => [result.data!, ...current]);
    setFeedback({ error: false, message: "导入任务已提交，系统正在后台处理。" });
  }

  async function handlePreLiveRun() {
    if (!preLiveProductsFile || !preLiveScriptFile) {
      setLiveFeedback({ error: true, message: "请至少上传直播商品检查模板和直播脚本检查模板。" });
      return;
    }
    setLiveBusy(true); setLiveFeedback(null); setLiveReport(null);
    try {
      const productRows = await parseCsvFile(preLiveProductsFile);
      const couponRows = preLiveCouponsFile ? await parseCsvFile(preLiveCouponsFile) : [];
      const scriptRows = await parseCsvFile(preLiveScriptFile);
      const script = scriptRows[0] ?? {};
      const result = await runPreLiveCheck({
        products: productRows.map((row) => ({
          title: textValue(row.title),
          inventory_count: numberValue(row.inventory_count),
          safe_stock: numberValue(row.safe_stock, 20),
          regular_price: numberValue(row.regular_price),
          live_price: numberValue(row.live_price)
        })).filter((item) => item.title),
        coupons: couponRows.map((row) => ({
          name: textValue(row.name),
          remaining_count: numberValue(row.remaining_count),
          expired: booleanValue(row.expired)
        })).filter((item) => item.name),
        script_text: textValue(script.script_text),
        gift_ready: booleanValue(script.gift_ready),
        product_order_ready: booleanValue(script.product_order_ready)
      });
      handleLiveResult(result, "开播前检查已完成。AI 已生成准备报告和风险提醒。");
    } catch (error) {
      setLiveFeedback({ error: true, message: error instanceof Error ? error.message : "直播模板读取失败。" });
    } finally {
      setLiveBusy(false);
    }
  }

  async function handleLiveMetricRun() {
    if (!liveMetricFile) { setLiveFeedback({ error: true, message: "请先上传直播中数据模板。" }); return; }
    setLiveBusy(true); setLiveFeedback(null); setLiveReport(null);
    try {
      const row = (await parseCsvFile(liveMetricFile))[0];
      if (!row) { throw new Error("直播中数据模板没有可读取的数据行。"); }
      const result = await runLiveMetricScan({
        online_users: numberValue(row.online_users),
        conversion_rate: numberValue(row.conversion_rate),
        retention_rate: numberValue(row.retention_rate),
        comment_count: numberValue(row.comment_count),
        like_count: numberValue(row.like_count),
        product_click_rate: numberValue(row.product_click_rate),
        inventory_delta: numberValue(row.inventory_delta),
        abnormal_order_count: numberValue(row.abnormal_order_count)
      });
      handleLiveResult(result, "直播中扫描已完成。AI 已生成主播提醒和异常处理建议。");
    } catch (error) {
      setLiveFeedback({ error: true, message: error instanceof Error ? error.message : "直播中模板读取失败。" });
    } finally {
      setLiveBusy(false);
    }
  }

  async function handlePostLiveRun() {
    if (!postLiveFile) { setLiveFeedback({ error: true, message: "请先上传下播复盘模板。" }); return; }
    setLiveBusy(true); setLiveFeedback(null); setLiveReport(null);
    try {
      const row = (await parseCsvFile(postLiveFile))[0];
      if (!row) { throw new Error("下播复盘模板没有可读取的数据行。"); }
      const result = await runPostLiveReview({
        sales_amount_yuan: numberValue(row.sales_amount_yuan),
        order_count: numberValue(row.order_count),
        viewer_count: numberValue(row.viewer_count),
        refund_count: numberValue(row.refund_count),
        top_product_title: textValue(row.top_product_title),
        negative_comment_count: numberValue(row.negative_comment_count),
        host_script_score: numberValue(row.host_script_score)
      });
      handleLiveResult(result, "下播复盘已完成。AI 已生成成交分析、退款风险和第二天建议。");
    } catch (error) {
      setLiveFeedback({ error: true, message: error instanceof Error ? error.message : "下播复盘模板读取失败。" });
    } finally {
      setLiveBusy(false);
    }
  }

  function handleLiveResult(result: { data: LiveRunResult | null; error: string | null }, successMessage: string) {
    if (result.error || !result.data) { setLiveFeedback({ error: true, message: result.error ?? "AI 执行失败。" }); return; }
    setLiveReport(result.data);
    setLiveFeedback({ error: false, message: successMessage });
  }

  function resetPreview() { setPreview(null); setMapping({}); setFeedback(null); }

  return (
    <div className="space-y-6">
      <header className="border-b border-border pb-5">
        <p className="text-sm font-medium text-primary">系统设置</p>
        <h1 className="mt-2 text-3xl font-semibold">平台数据导入</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">商家先用模板上传真实数据，AI 直接跑 Workflow，生成检查、提醒、复盘和节省金额。所有操作只读，不会退款、改价、上下架或发货。</p>
      </header>

      <div className="grid gap-3 sm:grid-cols-4">{["选择数据", "上传文件", "匹配字段", "生成结果"].map((label, index) => <div className="flex items-center gap-3 rounded-md border border-border bg-card p-3" key={label}><span className="flex h-7 w-7 items-center justify-center rounded-full bg-muted text-xs font-semibold">{index + 1}</span><span className="text-sm font-medium">{label}</span></div>)}</div>

      <Card className="p-5">
        <div className="flex items-start gap-3">
          <ShieldCheck className="mt-1 h-5 w-5 shrink-0 text-primary" />
          <div>
            <h2 className="text-base font-semibold">第一步：下载模板，填入商家真实数据</h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">先不要急着接官方 API。让商家把直播、订单、商品、客户、物流和售后按模板整理好，系统先跑 Workflow、Replay、Evaluation 和省钱测算。</p>
          </div>
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {templateLinks.map((template) => (
            <a className="rounded-md border border-border bg-background p-4 transition hover:border-primary/40 hover:bg-accent" href={template.href} key={template.href}>
              <FileDown aria-hidden className="h-5 w-5 text-primary" />
              <h3 className="mt-3 text-sm font-semibold">{template.title}</h3>
              <p className="mt-2 text-xs leading-5 text-muted-foreground">{template.desc}</p>
            </a>
          ))}
        </div>
      </Card>

      <Card className="p-5">
        <div className="flex items-start gap-3">
          <PlayCircle className="mt-1 h-5 w-5 shrink-0 text-primary" />
          <div>
            <h2 className="text-base font-semibold">直播运营助理：上传模板后直接让 AI 干活</h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">这里已经不是模拟展示。上传直播模板后，系统会调用后端 Workflow，记录工作日志，并让 Savings Engine 计算节省时间和金额。</p>
          </div>
        </div>
        <div className="mt-5 grid gap-4 lg:grid-cols-3">
          <div className="rounded-md border border-border bg-background p-4">
            <h3 className="text-sm font-semibold">开播前检查</h3>
            <p className="mt-2 text-xs leading-5 text-muted-foreground">检查库存、优惠券、价格、脚本、赠品和商品顺序。</p>
            <FileInput label="商品模板" file={preLiveProductsFile} onChange={setPreLiveProductsFile} />
            <FileInput label="优惠券模板（可选）" file={preLiveCouponsFile} onChange={setPreLiveCouponsFile} />
            <FileInput label="脚本模板" file={preLiveScriptFile} onChange={setPreLiveScriptFile} />
            <Button className="mt-4 w-full" disabled={liveBusy} onClick={handlePreLiveRun} type="button">{liveBusy ? "AI 检查中" : "生成开播准备报告"}</Button>
          </div>
          <div className="rounded-md border border-border bg-background p-4">
            <h3 className="text-sm font-semibold">直播中扫描</h3>
            <p className="mt-2 text-xs leading-5 text-muted-foreground">检查在线人数、成交率、停留率、点击率、库存变化和异常订单。</p>
            <FileInput label="直播中数据模板" file={liveMetricFile} onChange={setLiveMetricFile} />
            <Button className="mt-4 w-full" disabled={liveBusy} onClick={handleLiveMetricRun} type="button">{liveBusy ? "AI 扫描中" : "生成直播提醒"}</Button>
          </div>
          <div className="rounded-md border border-border bg-background p-4">
            <h3 className="text-sm font-semibold">下播复盘</h3>
            <p className="mt-2 text-xs leading-5 text-muted-foreground">生成成交分析、退款风险、主播表现和第二天直播建议。</p>
            <FileInput label="下播复盘模板" file={postLiveFile} onChange={setPostLiveFile} />
            <Button className="mt-4 w-full" disabled={liveBusy} onClick={handlePostLiveRun} type="button">{liveBusy ? "AI 复盘中" : "生成下播复盘"}</Button>
          </div>
        </div>
        {liveFeedback ? <div className={`mt-4 flex items-start gap-2 rounded-md border p-3 text-sm ${liveFeedback.error ? "border-red-500/30 bg-red-500/10" : "border-primary/30 bg-primary/10"}`}>{liveFeedback.error ? <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-500" /> : <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />}<span>{liveFeedback.message}</span></div> : null}
        {liveReport ? <LiveReportCard report={liveReport} /> : null}
      </Card>

      <Card className="p-4">
        <h2 className="text-sm font-semibold">普通经营数据导入</h2>
        <p className="mt-2 text-xs leading-5 text-muted-foreground">订单、商品、客户、物流和售后数据仍然走原来的预览、字段匹配和导入任务，用于 Replay 和 Evaluation。</p>
      </Card>

      <Card className="p-5">
        <div className="grid gap-4 md:grid-cols-3">
          <label className="text-sm font-medium">平台<select className="mt-2 h-10 w-full rounded-md border border-border bg-background px-3 font-normal" onChange={(event) => { setPlatform(event.target.value as ImportPlatformOption); setShopName(`${platformLabels[event.target.value as ImportPlatformOption]}店铺`); resetPreview(); }} value={platform}><option value="taobao">淘宝</option><option value="douyin">抖音商店</option><option value="pdd">拼多多（先用模板）</option><option value="xianyu">闲鱼</option></select></label>
          <label className="text-sm font-medium">数据类型<select className="mt-2 h-10 w-full rounded-md border border-border bg-background px-3 font-normal" onChange={(event) => { setDataType(event.target.value as ImportDataType); resetPreview(); }} value={dataType}>{Object.entries(dataTypeLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
          <label className="text-sm font-medium">店铺名称<input className="mt-2 h-10 w-full rounded-md border border-border bg-background px-3 font-normal outline-none focus:border-primary" onChange={(event) => setShopName(event.target.value)} value={shopName} /></label>
        </div>
        <label className="mt-5 flex min-h-32 cursor-pointer flex-col items-center justify-center rounded-md border border-dashed border-border bg-background p-5 text-center"><UploadCloud className="h-6 w-6 text-primary" /><span className="mt-2 text-sm font-medium">{file?.name ?? "选择 CSV、.xlsx 或 JSON 文件"}</span><span className="mt-1 text-xs text-muted-foreground">最大 20MB；CSV 支持 UTF-8、UTF-8 BOM、GB18030；JSON 支持数组或 rows/items/data</span><input accept=".csv,.xlsx,.json,application/json" className="sr-only" onChange={(event) => { setFile(event.target.files?.[0] ?? null); resetPreview(); }} type="file" /></label>
        <div className="mt-4 flex flex-wrap gap-3"><Button disabled={busy || !file} onClick={handlePreview} type="button" variant="secondary"><FileSpreadsheet className="mr-2 h-4 w-4" />{busy ? "读取中" : "预览文件"}</Button>{preview ? <Button disabled={busy || !shopName.trim()} onClick={handleSubmit} type="button">{busy ? "提交中" : "确认并开始导入"}</Button> : null}</div>
        {platform === "pdd" ? <p className="mt-3 rounded-md bg-muted p-3 text-xs leading-5 text-muted-foreground">拼多多当前是“接入准备模式”：可以下载模板、整理样本、给商家说明流程；等你确认数据库平台枚举后，再开启正式预览和导入。</p> : null}
        {feedback ? <div className={`mt-4 flex items-start gap-2 rounded-md border p-3 text-sm ${feedback.error ? "border-red-500/30 bg-red-500/10" : "border-primary/30 bg-primary/10"}`}>{feedback.error ? <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-500" /> : <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />}<span>{feedback.message}</span></div> : null}
      </Card>

      {preview ? <Card className="overflow-hidden"><div className="border-b border-border p-4"><h2 className="font-semibold">字段对应关系</h2><p className="mt-1 text-xs text-muted-foreground">左侧是系统字段，右侧选择文件中的列。带“必填”的字段必须匹配。</p></div><div className="grid gap-3 p-4 md:grid-cols-2">{Object.keys(fieldLabels).filter((field) => preview.required_fields.includes(field) || mapping[field]).map((field) => <label className="grid grid-cols-[minmax(110px,1fr)_minmax(150px,1.5fr)] items-center gap-3 text-sm" key={field}><span>{fieldLabels[field] ?? field}{preview.required_fields.includes(field) ? <strong className="ml-1 text-red-500">必填</strong> : null}</span><select className="h-10 rounded-md border border-border bg-background px-3" onChange={(event) => setMapping((current) => ({ ...current, [field]: event.target.value }))} value={mapping[field] ?? ""}><option value="">不导入</option>{preview.headers.map((header) => <option key={header} value={header}>{header}</option>)}</select></label>)}</div><div className="border-t border-border p-4"><p className="mb-3 text-sm font-medium">数据样例</p><Table><TableHeader><TableRow>{preview.headers.slice(0, 6).map((header) => <TableHead key={header}>{header}</TableHead>)}</TableRow></TableHeader><TableBody>{preview.sample_rows.map((row, index) => <TableRow key={index}>{preview.headers.slice(0, 6).map((header) => <TableCell key={header}>{row[header]}</TableCell>)}</TableRow>)}</TableBody></Table></div></Card> : null}
      <Card className="overflow-hidden"><div className="border-b border-border p-4"><h2 className="font-semibold">最近导入任务</h2></div>{jobs.length ? <Table><TableHeader><TableRow><TableHead>平台</TableHead><TableHead>数据</TableHead><TableHead>状态</TableHead><TableHead>进度</TableHead><TableHead>成功 / 失败</TableHead><TableHead>错误摘要</TableHead></TableRow></TableHeader><TableBody>{jobs.map((job) => <TableRow key={job.id}><TableCell>{platformLabels[job.platform]}</TableCell><TableCell>{dataTypeLabels[job.data_type]}</TableCell><TableCell><Badge tone={job.status === "succeeded" ? "green" : "amber"}>{jobStatusLabel(job.status)}</Badge></TableCell><TableCell>{job.progress}%</TableCell><TableCell>{job.success_count} / {job.failure_count}</TableCell><TableCell className="max-w-xs truncate">{job.error_summary ?? "无"}</TableCell></TableRow>)}</TableBody></Table> : <div className="p-8 text-center text-sm text-muted-foreground">还没有导入任务。完成一次预览并确认后，任务会出现在这里。</div>}</Card>
    </div>
  );
}

function FileInput({ label, file, onChange }: { label: string; file: File | null; onChange: (file: File | null) => void }) {
  return <label className="mt-3 block text-xs font-medium"><span>{label}</span><input accept=".csv" className="mt-2 block w-full rounded-md border border-border bg-muted/30 px-3 py-2 text-xs" onChange={(event) => onChange(event.target.files?.[0] ?? null)} type="file" /><span className="mt-1 block truncate text-muted-foreground">{file?.name ?? "未选择文件"}</span></label>;
}

function LiveReportCard({ report }: { report: LiveRunResult }) {
  const isPostReview = "next_day_actions" in report;
  const actions = isPostReview ? report.next_day_actions : report.next_actions;
  return <div className="mt-4 rounded-md border border-border bg-background p-4"><div className="flex flex-wrap items-center gap-3"><Badge tone={report.status === "done" ? "green" : report.status === "blocked" ? "amber" : "amber"}>{statusLabel(report.status)}</Badge><span className="text-sm font-semibold">AI 评分：{report.score}</span><span className="text-sm text-muted-foreground">节省 {report.saved_minutes} 分钟，约 {report.estimated_saving_yuan} 元</span></div>{isPostReview ? <div className="mt-4 grid gap-3 text-sm md:grid-cols-3"><p className="rounded-md bg-muted p-3">销售额：{report.sales_amount_yuan} 元</p><p className="rounded-md bg-muted p-3">成交率：{(report.conversion_rate * 100).toFixed(2)}%</p><p className="rounded-md bg-muted p-3">最高成交商品：{report.top_product_title}</p><p className="rounded-md bg-muted p-3 md:col-span-3">{report.refund_risk_note}</p><p className="rounded-md bg-muted p-3 md:col-span-3">{report.host_performance_note}</p></div> : <div className="mt-4 grid gap-3 md:grid-cols-2">{report.alerts.map((alert) => <div className="rounded-md border border-border p-3" key={alert.id}><p className="text-sm font-semibold">{alert.title}</p><p className="mt-1 text-xs text-muted-foreground">触发原因：{alert.trigger}</p><p className="mt-1 text-xs text-muted-foreground">建议动作：{alert.suggested_action}</p></div>)}</div>}<div className="mt-4"><p className="text-sm font-semibold">下一步动作</p><ul className="mt-2 space-y-1 text-sm text-muted-foreground">{actions.map((action) => <li key={action}>- {action}</li>)}</ul></div></div>;
}

async function parseCsvFile(file: File): Promise<Record<string, string>[]> {
  const buffer = await file.arrayBuffer();
  let text = "";
  try {
    text = new TextDecoder("utf-8", { fatal: true }).decode(buffer);
  } catch {
    text = new TextDecoder("gb18030").decode(buffer);
  }
  const rows = parseCsv(text.replace(/^\uFEFF/, "")).filter((row) => row.some((cell) => cell.trim()));
  const headers = rows[0]?.map((header) => header.trim()) ?? [];
  if (!headers.length) { throw new Error(`${file.name} 没有表头。`); }
  return rows.slice(1).map((row) => Object.fromEntries(headers.map((header, index) => [header, row[index]?.trim() ?? ""])));
}

function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let cell = "";
  let quoted = false;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const next = text[index + 1];
    if (char === '"' && quoted && next === '"') { cell += '"'; index += 1; continue; }
    if (char === '"') { quoted = !quoted; continue; }
    if (char === "," && !quoted) { row.push(cell); cell = ""; continue; }
    if ((char === "\n" || char === "\r") && !quoted) {
      if (char === "\r" && next === "\n") { index += 1; }
      row.push(cell); rows.push(row); row = []; cell = ""; continue;
    }
    cell += char;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  return rows;
}

function textValue(value: string | undefined): string { return (value ?? "").trim(); }
function numberValue(value: string | undefined, fallback = 0): number { const parsed = Number((value ?? "").trim()); return Number.isFinite(parsed) ? parsed : fallback; }
function booleanValue(value: string | undefined): boolean { return ["true", "1", "yes", "是", "已准备", "准备好"].includes((value ?? "").trim().toLowerCase()); }
function jobStatusLabel(status: ImportJob["status"]) { return { queued: "等待中", running: "执行中", partial_success: "部分成功", succeeded: "成功", failed: "失败" }[status]; }
function statusLabel(status: LiveRunResult["status"]) { return { done: "已完成", warning: "有风险", blocked: "需人工处理", pending: "等待中" }[status]; }
