from __future__ import annotations

import json
import shutil
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "dist" / "sites-internal-app"
ARCHIVE_PATH = ROOT / "dist" / "sites-internal-app.tar.gz"
PROJECT_ID = "appgprj_6a532caf36408191b5b95e2f99f1f567"


def build_html() -> str:
    # 内部试用版只保存浏览器本地状态，不写入真实客户数据，避免试用阶段泄露商家隐私。
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI Commerce OS 内部控制台</title>
  <meta name="description" content="AI Commerce OS 内部试用控制台，包含登录、AI客服、AI售后、AI运营和老板审批。" />
  <style>
    :root { --bg:#f6f8fb; --fg:#0f172a; --muted:#667085; --line:#e5e7eb; --card:#fff; --primary:#0f766e; --blue:#1d4ed8; --warn:#b45309; --danger:#b91c1c; }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--fg); font-family:"Microsoft YaHei","PingFang SC",Arial,sans-serif; }
    button,input,textarea,select { font:inherit; }
    .hidden { display:none !important; }
    .login { min-height:100vh; display:grid; grid-template-columns:1.05fr .95fr; }
    .loginHero { padding:72px; background:#06111f; color:#fff; display:flex; flex-direction:column; justify-content:center; }
    .loginHero h1 { margin:18px 0 0; max-width:760px; font-size:56px; line-height:1.08; letter-spacing:0; }
    .loginHero p { max-width:620px; margin-top:24px; color:rgb(255 255 255 / .72); line-height:1.9; }
    .loginPanel { display:flex; align-items:center; justify-content:center; padding:32px; }
    .box { width:min(440px,100%); border:1px solid var(--line); border-radius:14px; background:#fff; box-shadow:0 24px 80px rgb(15 23 42 / .08); padding:28px; }
    label { display:block; margin-top:18px; color:#344054; font-size:14px; font-weight:700; }
    input,textarea,select { width:100%; border:1px solid var(--line); border-radius:10px; background:#fff; padding:12px 13px; color:var(--fg); outline:none; }
    textarea { min-height:120px; resize:vertical; }
    .btn { border:0; border-radius:10px; background:#0f172a; color:#fff; padding:12px 16px; cursor:pointer; font-weight:700; }
    .btn.secondary { border:1px solid var(--line); background:#fff; color:#0f172a; }
    .btn.green { background:var(--primary); }
    .btn.warn { background:var(--warn); }
    .btn.danger { background:var(--danger); }
    .app { min-height:100vh; display:grid; grid-template-columns:260px 1fr; }
    aside { border-right:1px solid var(--line); background:#fff; padding:22px; position:sticky; top:0; height:100vh; }
    .brand { font-size:18px; font-weight:800; }
    .nav { display:grid; gap:8px; margin-top:28px; }
    .nav button { border:0; border-radius:10px; background:transparent; padding:12px; text-align:left; color:#475467; cursor:pointer; }
    .nav button.active { background:#eef7f6; color:#0f766e; font-weight:800; }
    main { padding:28px; }
    header.top { display:flex; justify-content:space-between; align-items:center; gap:16px; margin-bottom:22px; }
    h2 { margin:0; font-size:30px; letter-spacing:0; }
    p { margin:0; }
    .muted { color:var(--muted); }
    .grid { display:grid; gap:16px; }
    .metrics { grid-template-columns:repeat(4,minmax(0,1fr)); }
    .two { grid-template-columns:1.15fr .85fr; }
    .three { grid-template-columns:repeat(3,minmax(0,1fr)); }
    .card { border:1px solid var(--line); border-radius:14px; background:var(--card); box-shadow:0 14px 40px rgb(15 23 42 / .05); padding:20px; }
    .metric strong { display:block; margin-top:10px; font-size:30px; }
    .badge { display:inline-flex; align-items:center; border-radius:999px; background:#ecfdf5; color:#047857; padding:6px 10px; font-size:12px; font-weight:800; white-space:nowrap; }
    .badge.warn { background:#fffbeb; color:#b45309; }
    .badge.gray { background:#f2f4f7; color:#475467; }
    .toolbar { display:flex; flex-wrap:wrap; gap:10px; margin:16px 0; }
    table { width:100%; border-collapse:collapse; }
    th,td { border-bottom:1px solid var(--line); padding:13px 10px; text-align:left; vertical-align:top; font-size:14px; }
    th { color:#667085; font-weight:800; }
    tr { cursor:pointer; }
    tr:hover { background:#f8fafc; }
    .drawer { position:fixed; inset:0; display:none; background:rgb(15 23 42 / .32); z-index:20; }
    .drawer.open { display:block; }
    .drawerPanel { width:min(560px,92vw); height:100%; margin-left:auto; background:#fff; padding:24px; overflow:auto; box-shadow:-20px 0 80px rgb(15 23 42 / .18); }
    .row { display:flex; gap:10px; flex-wrap:wrap; align-items:center; }
    .list { display:grid; gap:12px; }
    .item { border:1px solid var(--line); border-radius:12px; padding:14px; }
    .notice { border:1px solid #bfdbfe; border-radius:12px; background:#eff6ff; color:#1e3a8a; padding:14px; line-height:1.7; }
    @media (max-width:960px) { .login,.app,.metrics,.two,.three { grid-template-columns:1fr; } aside { position:relative; height:auto; } .loginHero { padding:42px 24px; } .loginHero h1 { font-size:40px; } main { padding:18px; } }
  </style>
</head>
<body>
  <section class="login" id="loginView">
    <div class="loginHero">
      <span class="badge">内部试用版</span>
      <h1>AI Commerce OS 商家控制台</h1>
      <p>登录后进入老板首页，直接试用 AI客服、AI售后、AI运营和审批流。当前版本用于内部演示和商家试用，不接入真实交易动作。</p>
    </div>
    <div class="loginPanel">
      <form class="box" id="loginForm">
        <h2>登录系统</h2>
        <p class="muted" style="margin-top:10px">演示账号：boss@aicos.local / aicos2026</p>
        <label>邮箱</label>
        <input id="email" type="email" value="boss@aicos.local" autocomplete="username" />
        <label>密码</label>
        <input id="password" type="password" value="aicos2026" autocomplete="current-password" />
        <button class="btn green" style="width:100%;margin-top:22px" type="submit">进入内部控制台</button>
        <p class="muted" id="loginMessage" style="margin-top:14px;font-size:13px">这是试用登录门槛，不存储真实密码。生产版将接 Supabase Auth。</p>
      </form>
    </div>
  </section>

  <section class="app hidden" id="appView">
    <aside>
      <div class="brand">AI Commerce OS</div>
      <p class="muted" style="margin-top:8px;font-size:13px">内部试用控制台</p>
      <div class="nav" id="nav"></div>
      <button class="btn secondary" id="logoutBtn" style="width:100%;margin-top:28px">退出登录</button>
    </aside>
    <main>
      <header class="top">
        <div>
          <h2 id="pageTitle">老板首页</h2>
          <p class="muted" id="pageDesc">AI 先整理经营状态，老板只处理关键审批。</p>
        </div>
        <span class="badge">试用数据 / 不执行真实动作</span>
      </header>
      <div id="content"></div>
    </main>
  </section>

  <div class="drawer" id="drawer"><div class="drawerPanel" id="drawerPanel"></div></div>

  <script>
    const LOGIN_EMAIL = "boss@aicos.local";
    const LOGIN_PASSWORD = "aicos2026";
    const pages = [
      ["dashboard", "老板首页", "AI 汇总销售、售后、运营和审批事项。"],
      ["customer", "AI客服", "处理客户咨询、回复草稿、人工接管和学习记录。"],
      ["aftersale", "AI售后", "处理退款、退货、物流异常、投诉和赔偿建议。"],
      ["operation", "AI运营", "生成私域获客、投流计划和转化动作草稿。"],
      ["approvals", "老板审批", "所有高风险动作必须经过老板确认。"],
      ["import", "数据导入", "导入商品、订单、客户、售后和物流数据。"]
    ];
    const state = {
      customer: [
        { id:"m1", platform:"淘宝", customer:"王女士", intent:"物流", risk:"低风险", message:"今天下单什么时候发货？", draft:"您好，今天18点前付款预计当天出库，揽收后我会继续跟进。", status:"待确认" },
        { id:"m2", platform:"抖音小店", customer:"陈先生", intent:"优惠", risk:"低风险", message:"两件有没有优惠？", draft:"您好，两件可领取店铺满减券，我可以帮您确认当前可用优惠。", status:"待确认" },
        { id:"m3", platform:"闲鱼", customer:"李同学", intent:"赔偿", risk:"高风险", message:"物流太慢了，赔我20元。", draft:"该问题涉及赔偿，AI 暂停自动回复，建议人工确认后处理。", status:"人工接管" }
      ],
      cases: [
        { id:"s1", type:"物流异常", customer:"李同学", risk:"高风险", ask:"要求赔偿20元", suggestion:"先核实物流轨迹，不自动承诺赔偿。", status:"待审批" },
        { id:"s2", type:"退货", customer:"赵女士", risk:"中风险", ask:"尺码不合适申请退货", suggestion:"符合7天无理由，建议同意退货但不承担非质量运费。", status:"待处理" },
        { id:"s3", type:"投诉", customer:"何先生", risk:"高风险", ask:"差评威胁", suggestion:"升级人工，统一口径安抚，不私下承诺。", status:"待审批" }
      ],
      approvals: [
        { id:"a1", title:"物流投诉补偿20元", owner:"AI售后", risk:"高风险", action:"等待老板审批" },
        { id:"a2", title:"私域群发优惠券", owner:"AI运营", risk:"中风险", action:"等待老板审批" },
        { id:"a3", title:"客户导出名单", owner:"AI客服", risk:"高风险", action:"禁止自动执行" }
      ]
    };

    function saveSession() { localStorage.setItem("aicos_internal_login", "1"); }
    function clearSession() { localStorage.removeItem("aicos_internal_login"); }
    function isLoggedIn() { return localStorage.getItem("aicos_internal_login") === "1"; }
    function setView(loggedIn) {
      document.getElementById("loginView").classList.toggle("hidden", loggedIn);
      document.getElementById("appView").classList.toggle("hidden", !loggedIn);
      if (loggedIn) renderPage("dashboard");
    }
    document.getElementById("loginForm").addEventListener("submit", (event) => {
      event.preventDefault();
      const email = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value;
      if (email === LOGIN_EMAIL && password === LOGIN_PASSWORD) { saveSession(); setView(true); return; }
      document.getElementById("loginMessage").textContent = "账号或密码不正确。请使用演示账号登录。";
    });
    document.getElementById("logoutBtn").addEventListener("click", () => { clearSession(); setView(false); });

    function renderNav(active) {
      const nav = document.getElementById("nav");
      nav.innerHTML = pages.map(([key, label]) => `<button class="${active === key ? "active" : ""}" data-page="${key}">${label}</button>`).join("");
      nav.querySelectorAll("button").forEach((button) => button.onclick = () => renderPage(button.dataset.page));
    }
    function renderPage(key) {
      const page = pages.find((item) => item[0] === key) || pages[0];
      document.getElementById("pageTitle").textContent = page[1];
      document.getElementById("pageDesc").textContent = page[2];
      renderNav(key);
      const views = { dashboard, customer, aftersale, operation, approvals, import: dataImport };
      document.getElementById("content").innerHTML = views[key]();
      bindActions(key);
    }
    function dashboard() {
      return `<section class="grid metrics">
        ${metric("今日咨询", "128", "+23%")}
        ${metric("AI可处理", "74%", "低风险优先")}
        ${metric("待审批", "6", "退款/补偿/群发")}
        ${metric("预估节省", "11.6小时", "按人工处理时长估算")}
      </section>
      <section class="grid two" style="margin-top:16px">
        <div class="card"><h3>今天 AI 已整理</h3><div class="list" style="margin-top:14px">
          ${item("AI客服", "订单与物流类问题占 61%，其中 3 条赔偿诉求已拦截。")}
          ${item("AI售后", "高风险售后 2 单，需要老板审批后才能回复。")}
          ${item("AI运营", "发现 18 个高意向客户，可进入私域跟进。")}
        </div></div>
        <div class="card"><h3>老板今天只需要处理</h3><div class="list" style="margin-top:14px">${state.approvals.map(a => item(a.owner, a.title + " / " + a.action)).join("")}</div></div>
      </section>`;
    }
    function customer() {
      return `<div class="toolbar"><button class="btn green" data-action="auto-customer">生成AI回复草稿</button><button class="btn secondary" data-action="customer-learning">记录商家修正</button></div>
      <div class="card"><table><thead><tr><th>平台</th><th>客户</th><th>意图</th><th>风险</th><th>消息</th><th>状态</th></tr></thead><tbody>
        ${state.customer.map(row => `<tr data-open="customer:${row.id}"><td>${row.platform}</td><td>${row.customer}</td><td>${row.intent}</td><td>${badge(row.risk)}</td><td>${row.message}</td><td>${row.status}</td></tr>`).join("")}
      </tbody></table></div>`;
    }
    function aftersale() {
      return `<div class="toolbar"><button class="btn warn" data-action="risk-check">重新风险分级</button><button class="btn secondary" data-action="sop">沉淀售后SOP</button></div>
      <div class="card"><table><thead><tr><th>类型</th><th>客户</th><th>诉求</th><th>风险</th><th>AI建议</th><th>状态</th></tr></thead><tbody>
        ${state.cases.map(row => `<tr data-open="case:${row.id}"><td>${row.type}</td><td>${row.customer}</td><td>${row.ask}</td><td>${badge(row.risk)}</td><td>${row.suggestion}</td><td>${row.status}</td></tr>`).join("")}
      </tbody></table></div>`;
    }
    function operation() {
      return `<section class="grid three">
        <div class="card"><span class="badge">私域获客</span><h3>高意向客户 18 人</h3><p class="muted">反复咨询尺码、发货和优惠，建议进入企业微信跟进。</p><button class="btn secondary" data-action="copy-script">生成话术</button></div>
        <div class="card"><span class="badge warn">投流草稿</span><h3>预算 300 元测试</h3><p class="muted">素材主题：快速发货 + 尺码顾问。预算动作必须审批。</p><button class="btn secondary" data-action="ad-plan">查看计划</button></div>
        <div class="card"><span class="badge">复盘</span><h3>转化建议</h3><p class="muted">把“发货时间”和“尺码建议”放到详情页首屏。</p><button class="btn secondary" data-action="ops-log">记录建议</button></div>
      </section>`;
    }
    function approvals() {
      return `<div class="notice">AI 永远没有无限权限。退款、赔偿、预算、群发、客户数据导出必须审批。</div>
      <div class="grid" style="margin-top:16px">${state.approvals.map(row => `<div class="card row" style="justify-content:space-between"><div><strong>${row.title}</strong><p class="muted">${row.owner} / ${row.risk}</p></div><div class="row"><button class="btn green" data-action="approve">同意</button><button class="btn secondary" data-action="edit">修改</button><button class="btn danger" data-action="reject">拒绝</button></div></div>`).join("")}</div>`;
    }
    function dataImport() {
      return `<div class="card"><h3>导入商家历史数据</h3><p class="muted" style="margin-top:8px">支持商品、订单、客户、物流、售后 CSV / Excel / JSON。当前内部版只做前端预览，不上传真实文件。</p>
      <label>平台</label><select><option>淘宝</option><option>抖音小店</option><option>闲鱼</option></select>
      <label>数据类型</label><select><option>订单</option><option>商品</option><option>客户</option><option>售后</option><option>物流</option></select>
      <label>文件</label><input type="file" />
      <button class="btn green" data-action="preview-import" style="margin-top:18px">预览导入结果</button></div>`;
    }
    function metric(label, value, hint) { return `<div class="card metric"><span class="muted">${label}</span><strong>${value}</strong><p class="muted">${hint}</p></div>`; }
    function item(title, desc) { return `<div class="item"><strong>${title}</strong><p class="muted" style="margin-top:6px">${desc}</p></div>`; }
    function badge(text) { return `<span class="badge ${text.includes("高") || text.includes("中") ? "warn" : ""}">${text}</span>`; }
    function bindActions(key) {
      document.querySelectorAll("[data-open]").forEach(row => row.onclick = () => openDrawer(row.dataset.open));
      document.querySelectorAll("[data-action]").forEach(btn => btn.onclick = () => toastAction(btn.dataset.action));
    }
    function openDrawer(token) {
      const [type, id] = token.split(":");
      const data = type === "customer" ? state.customer.find(x => x.id === id) : state.cases.find(x => x.id === id);
      document.getElementById("drawerPanel").innerHTML = `<button class="btn secondary" onclick="closeDrawer()">关闭</button><h2 style="margin-top:18px">${type === "customer" ? "客服详情" : "售后详情"}</h2><pre style="white-space:pre-wrap;line-height:1.8;background:#f8fafc;border:1px solid #e5e7eb;border-radius:12px;padding:16px">${JSON.stringify(data, null, 2)}</pre><label>商家修正/处理备注</label><textarea placeholder="把老板或客服最终处理结果写在这里，后续会进入学习中心。"></textarea><button class="btn green" style="margin-top:14px" onclick="toastAction('save-learning')">保存学习记录</button>`;
      document.getElementById("drawer").classList.add("open");
    }
    function closeDrawer() { document.getElementById("drawer").classList.remove("open"); }
    window.closeDrawer = closeDrawer;
    function toastAction(action) { alert("已模拟执行：" + action + "\\n生产版会写入 API、Memory、Knowledge 和审计日志。"); }
    setView(isLoggedIn());
  </script>
</body>
</html>"""


def main() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    if ARCHIVE_PATH.exists():
        ARCHIVE_PATH.unlink()

    (OUT_DIR / ".openai").mkdir(parents=True, exist_ok=True)
    worker = f"""const HTML = {json.dumps(build_html(), ensure_ascii=False)};

export default {{
  async fetch() {{
    return new Response(HTML, {{
      headers: {{
        "content-type": "text/html; charset=utf-8",
        "cache-control": "public, max-age=60"
      }}
    }});
  }}
}};
"""
    (OUT_DIR / "index.js").write_text(worker, encoding="utf-8")
    (OUT_DIR / ".openai" / "hosting.json").write_text(
        json.dumps({"project_id": PROJECT_ID}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    with tarfile.open(ARCHIVE_PATH, "w:gz") as archive:
        archive.add(OUT_DIR, arcname=".")
    print(ARCHIVE_PATH)


if __name__ == "__main__":
    main()
