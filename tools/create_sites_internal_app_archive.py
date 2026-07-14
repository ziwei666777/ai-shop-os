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
    # 商家可用版采用 localStorage 保存业务数据，确保没有后端时也能跑通客服和售后工作流。
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI Commerce OS 商家控制台</title>
  <meta name="description" content="AI Commerce OS 商家控制台，打开即可使用 AI 客服、AI 售后和 AI 运营基础流程。" />
  <style>
    :root { --bg:#f6f8fb; --fg:#101828; --muted:#667085; --line:#e4e7ec; --card:#fff; --primary:#0f766e; --primary2:#115e59; --blue:#1d4ed8; --amber:#b45309; --red:#b42318; --green:#047857; }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--fg); font-family:"Microsoft YaHei","PingFang SC",Arial,sans-serif; }
    button,input,textarea,select { font:inherit; }
    button { cursor:pointer; }
    .hidden { display:none !important; }
    .login { min-height:100vh; display:grid; grid-template-columns:1.05fr .95fr; }
    .loginHero { padding:72px; background:#07131f; color:#fff; display:flex; flex-direction:column; justify-content:center; }
    .loginHero h1 { max-width:760px; margin:18px 0 0; font-size:54px; line-height:1.08; letter-spacing:0; }
    .loginHero p { max-width:660px; margin-top:22px; color:rgb(255 255 255 / .74); line-height:1.9; }
    .loginPanel { display:flex; align-items:center; justify-content:center; padding:28px; }
    .box,.card { border:1px solid var(--line); border-radius:14px; background:var(--card); box-shadow:0 16px 48px rgb(15 23 42 / .06); }
    .box { width:min(460px,100%); padding:28px; }
    label { display:block; margin-top:16px; color:#344054; font-size:14px; font-weight:700; }
    input,textarea,select { width:100%; border:1px solid var(--line); border-radius:10px; background:#fff; padding:11px 12px; color:var(--fg); outline:none; }
    textarea { min-height:112px; resize:vertical; line-height:1.7; }
    .btn { border:0; border-radius:10px; background:#0f172a; color:#fff; padding:11px 15px; font-weight:800; }
    .btn.green { background:var(--primary); }
    .btn.red { background:var(--red); }
    .btn.amber { background:var(--amber); }
    .btn.secondary { border:1px solid var(--line); background:#fff; color:#101828; }
    .btn:disabled { opacity:.5; cursor:not-allowed; }
    .app { min-height:100vh; display:grid; grid-template-columns:270px 1fr; }
    aside { border-right:1px solid var(--line); background:#fff; padding:22px; position:sticky; top:0; height:100vh; }
    .brand { font-size:18px; font-weight:900; }
    .nav { display:grid; gap:8px; margin-top:24px; }
    .nav button { border:0; border-radius:10px; background:transparent; padding:12px; text-align:left; color:#475467; }
    .nav button.active { background:#eaf7f5; color:#0f766e; font-weight:900; }
    main { padding:28px; }
    header.top { display:flex; align-items:flex-start; justify-content:space-between; gap:16px; margin-bottom:18px; }
    h1,h2,h3,p { margin:0; }
    h2 { font-size:30px; letter-spacing:0; }
    h3 { font-size:16px; }
    .muted { color:var(--muted); }
    .grid { display:grid; gap:16px; }
    .metrics { grid-template-columns:repeat(4,minmax(0,1fr)); }
    .two { grid-template-columns:1.15fr .85fr; }
    .three { grid-template-columns:repeat(3,minmax(0,1fr)); }
    .card { padding:18px; }
    .metric strong { display:block; margin-top:8px; font-size:30px; }
    .badge { display:inline-flex; align-items:center; border-radius:999px; background:#ecfdf5; color:#047857; padding:6px 10px; font-size:12px; font-weight:900; white-space:nowrap; }
    .badge.gray { background:#f2f4f7; color:#475467; }
    .badge.amber { background:#fffbeb; color:#b45309; }
    .badge.red { background:#fef3f2; color:#b42318; }
    .toolbar { display:flex; flex-wrap:wrap; gap:10px; margin:14px 0; }
    .notice { border:1px solid #bfdbfe; border-radius:12px; background:#eff6ff; color:#1e3a8a; padding:14px; line-height:1.75; }
    .success { border:1px solid #a7f3d0; background:#ecfdf5; color:#064e3b; }
    .danger { border:1px solid #fecaca; background:#fff1f2; color:#991b1b; }
    table { width:100%; border-collapse:collapse; }
    th,td { border-bottom:1px solid var(--line); padding:12px 10px; text-align:left; vertical-align:top; font-size:14px; }
    th { color:#667085; font-weight:900; }
    tr:hover { background:#f8fafc; }
    .item { border:1px solid var(--line); border-radius:12px; padding:14px; background:#fff; }
    .row { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
    .between { justify-content:space-between; }
    .drawer { position:fixed; inset:0; z-index:20; display:none; background:rgb(15 23 42 / .34); }
    .drawer.open { display:block; }
    .drawerPanel { width:min(620px,94vw); height:100%; margin-left:auto; background:#fff; padding:24px; overflow:auto; box-shadow:-20px 0 80px rgb(15 23 42 / .18); }
    .mini { font-size:12px; line-height:1.7; }
    .pill { border-radius:999px; background:#f2f4f7; padding:5px 9px; font-size:12px; color:#475467; }
    @media (max-width:980px) { .login,.app,.metrics,.two,.three { grid-template-columns:1fr; } aside { position:relative; height:auto; } .loginHero { padding:40px 24px; } .loginHero h1 { font-size:38px; } main { padding:18px; } }
  </style>
</head>
<body>
  <section class="login" id="loginView">
    <div class="loginHero">
      <span class="badge">商家可用控制台</span>
      <h1>今天有商家来，就让他直接开始用</h1>
      <p>这不是宣传页。商家登录后可以导入数据、录入真实客户消息、生成 AI 客服回复草稿、处理售后审批、查看节省人工时间。当前数据保存在本浏览器，适合当天试用和现场交付。</p>
    </div>
    <div class="loginPanel">
      <form class="box" id="loginForm">
        <h2>进入商家控制台</h2>
        <p class="muted" style="margin-top:10px;line-height:1.7">输入店铺名即可创建一个本地工作台。正式上线后这里会接 Supabase 登录和多商家权限。</p>
        <label>店铺名称</label>
        <input id="shopName" value="深圳女装淘宝店" />
        <label>负责人手机号</label>
        <input id="ownerPhone" value="13800000000" />
        <button class="btn green" style="width:100%;margin-top:22px" type="submit">进入控制台</button>
      </form>
    </div>
  </section>

  <section class="app hidden" id="appView">
    <aside>
      <div class="brand">AI Commerce OS</div>
      <p class="muted mini" id="shopBadge" style="margin-top:8px"></p>
      <div class="nav" id="nav"></div>
      <button class="btn secondary" id="logoutBtn" style="width:100%;margin-top:22px">切换商家</button>
    </aside>
    <main>
      <header class="top">
        <div>
          <h2 id="pageTitle">老板首页</h2>
          <p class="muted" id="pageDesc" style="margin-top:8px">AI 把今天该处理的事放到老板眼前。</p>
        </div>
        <span class="badge">本地可用 / 可接真实后端</span>
      </header>
      <div id="toast"></div>
      <div id="content"></div>
    </main>
  </section>

  <div class="drawer" id="drawer"><div class="drawerPanel" id="drawerPanel"></div></div>

  <script>
    const HOURLY_COST = 40000 / 22 / 8;
    const pages = [
      ["dashboard", "老板首页", "先看 AI 今天帮你处理了什么，还剩什么要你拍板。"],
      ["connect", "接入店铺", "淘宝、天猫、抖店、拼多多、闲鱼先用文件和消息桥接跑起来。"],
      ["import", "导入数据", "上传订单、商品、客户、售后 CSV，立刻形成 AI 可用数据。"],
      ["customer", "AI客服", "真实客户消息进来后，AI 生成草稿，风险高就转人工。"],
      ["aftersale", "AI售后", "退款、退货、投诉、物流异常统一审批处理。"],
      ["operation", "AI运营", "根据咨询和订单生成私域跟进与投流草稿。"],
      ["saving", "省钱统计", "记录 AI 替代了多少人工分钟和预计节省金额。"],
      ["settings", "系统设置", "配置后端 API、桥接密钥和安全边界。"]
    ];

    function defaultState() {
      return {
        shopName: "深圳女装淘宝店",
        ownerPhone: "13800000000",
        importedRows: [],
        messages: [
          { id:"msg-1", platform:"淘宝", customer:"王女士", content:"这件还有 M 码吗？今天下单什么时候发货？", intent:"faq", risk:"低", status:"待处理", draft:"您好，这款可以先按页面库存确认。今天 16:00 前付款会优先当天发出。", saved:5 },
          { id:"msg-2", platform:"抖音商店", customer:"陈先生", content:"订单到哪里了？", intent:"logistics", risk:"低", status:"待处理", draft:"您好，我先帮您查询订单物流状态，如果 24 小时没有更新会转人工继续跟进。", saved:5 },
          { id:"msg-3", platform:"闲鱼", customer:"李同学", content:"物流太慢了，赔我 20 元。", intent:"compensation", risk:"高", status:"人工确认", draft:"该问题涉及赔偿金额，AI 不会自动承诺，建议人工核实物流后回复。", saved:0 }
        ],
        cases: [
          { id:"case-1", platform:"淘宝", customer:"王女士", title:"商品瑕疵投诉", desc:"客户反馈收到商品有瑕疵，要求赔偿。", risk:"高", suggestion:"先要求图片证据，不承诺赔偿金额，老板确认后再回复。", status:"待审批" },
          { id:"case-2", platform:"抖音商店", customer:"赵女士", title:"尺码不合适退货", desc:"客户申请 7 天无理由退货。", risk:"中", suggestion:"符合规则可同意退货，但运费承担按店铺规则执行。", status:"待处理" }
        ],
        approvals: [],
        logs: [],
        savedMinutes: 10,
        savedYuan: Math.round(10 / 60 * HOURLY_COST),
        apiBase: "",
        bridgeKey: ""
      };
    }

    function loadState() {
      const raw = localStorage.getItem("aicos_merchant_console");
      if (!raw) return defaultState();
      try { return { ...defaultState(), ...JSON.parse(raw) }; } catch { return defaultState(); }
    }
    let state = loadState();
    function saveState() { localStorage.setItem("aicos_merchant_console", JSON.stringify(state)); }
    function isLoggedIn() { return localStorage.getItem("aicos_merchant_logged_in") === "1"; }
    function showToast(text, type="success") {
      document.getElementById("toast").innerHTML = `<div class="notice ${type}" style="margin-bottom:16px">${text}</div>`;
    }
    function metric(label, value, hint) { return `<div class="card metric"><span class="muted">${label}</span><strong>${value}</strong><p class="muted">${hint}</p></div>`; }
    function badge(text) { const cls = text.includes("高") || text.includes("待") ? "amber" : text.includes("人工") || text.includes("拒绝") ? "red" : text.includes("已") || text.includes("低") ? "" : "gray"; return `<span class="badge ${cls}">${text}</span>`; }
    function platformBadge(name) { return `<span class="pill">${name}</span>`; }

    document.getElementById("loginForm").addEventListener("submit", (event) => {
      event.preventDefault();
      state.shopName = document.getElementById("shopName").value.trim() || "未命名店铺";
      state.ownerPhone = document.getElementById("ownerPhone").value.trim();
      saveState();
      localStorage.setItem("aicos_merchant_logged_in", "1");
      setView(true);
    });
    document.getElementById("logoutBtn").addEventListener("click", () => { localStorage.removeItem("aicos_merchant_logged_in"); setView(false); });

    function setView(loggedIn) {
      document.getElementById("loginView").classList.toggle("hidden", loggedIn);
      document.getElementById("appView").classList.toggle("hidden", !loggedIn);
      if (loggedIn) {
        document.getElementById("shopBadge").textContent = state.shopName + " / 今日可用";
        renderPage("dashboard");
      }
    }
    function renderNav(active) {
      const nav = document.getElementById("nav");
      nav.innerHTML = pages.map(([key,label]) => `<button class="${active === key ? "active" : ""}" data-page="${key}">${label}</button>`).join("");
      nav.querySelectorAll("button").forEach((button) => button.onclick = () => renderPage(button.dataset.page));
    }
    function renderPage(key) {
      const page = pages.find((item) => item[0] === key) || pages[0];
      document.getElementById("pageTitle").textContent = page[1];
      document.getElementById("pageDesc").textContent = page[2];
      document.getElementById("toast").innerHTML = "";
      renderNav(key);
      const views = { dashboard, connect, import: dataImport, customer, aftersale, operation, saving, settings };
      document.getElementById("content").innerHTML = views[key]();
      bindActions();
    }

    function dashboard() {
      const pending = state.messages.filter(m => m.status === "待处理" || m.status === "人工确认").length + state.cases.filter(c => c.status !== "已处理").length;
      return `<section class="grid metrics">
        ${metric("待处理消息", state.messages.length, "AI客服收件箱")}
        ${metric("待处理售后", state.cases.length, "退款/投诉/物流异常")}
        ${metric("需要老板确认", pending, "高风险不会自动处理")}
        ${metric("预计已省", "¥" + state.savedYuan, state.savedMinutes + " 分钟人工")}
      </section>
      <section class="grid two" style="margin-top:16px">
        <div class="card">
          <h3>今天商家第一步做什么</h3>
          <div class="grid" style="margin-top:14px">
            <div class="item"><strong>1. 接入店铺</strong><p class="muted mini">先选择淘宝、天猫、抖店、拼多多或闲鱼的接入方式。</p></div>
            <div class="item"><strong>2. 导入真实数据</strong><p class="muted mini">上传订单、商品、客户、售后 CSV，AI 才知道店铺实际情况。</p></div>
            <div class="item"><strong>3. 处理 AI 客服</strong><p class="muted mini">低风险消息点“采用”，高风险消息点“人工接管”。</p></div>
          </div>
        </div>
        <div class="card">
          <h3>今天必须老板看的事</h3>
          <div class="grid" style="margin-top:14px">
            ${state.messages.filter(m => m.risk === "高").slice(0,3).map(m => `<div class="item">${badge("高风险")} <strong>${m.customer}</strong><p class="muted mini">${m.content}</p></div>`).join("") || `<p class="muted">暂无高风险客服消息。</p>`}
          </div>
        </div>
      </section>`;
    }

    function connect() {
      const platforms = [
        ["淘宝 / 天猫", "官方授权或客服桥接", "可先用导出文件 + 消息桥接跑起来。"],
        ["抖音商店 / 抖店", "官方授权或客服桥接", "先同步订单售后，消息进入 AI客服。"],
        ["拼多多", "文件优先", "先导出订单、商品、售后文件做试用。"],
        ["闲鱼", "安全文件模式", "不托管账号，不抓包，不拿 Cookie。"]
      ];
      return `<div class="notice success">目标很简单：今天先让商家能用。官方授权没下来，就用文件导入和消息桥接；官方权限下来后，再换成自动同步。</div>
      <section class="grid two" style="margin-top:16px">
        ${platforms.map(p => `<div class="card"><div class="row between"><h3>${p[0]}</h3>${badge(p[1])}</div><p class="muted" style="margin-top:10px;line-height:1.7">${p[2]}</p><div class="toolbar"><button class="btn green" data-page-jump="import">去导入数据</button><button class="btn secondary" data-page-jump="customer">去 AI客服</button></div></div>`).join("")}
      </section>
      <div class="card" style="margin-top:16px"><h3>真实消息桥接地址</h3><p class="muted mini" style="margin-top:8px">后端部署后，平台中转程序调用：POST /v1/customer-agent/external-messages，Header 带 X-AICOS-Bridge-Key。这个控制台已经按同一套字段设计。</p></div>`;
    }

    function dataImport() {
      return `<div class="card">
        <h3>导入真实数据</h3>
        <p class="muted mini" style="margin-top:8px">上传 CSV。第一行必须是表头。常见表头：订单号、客户、客户问题、商品、金额、状态、售后原因。</p>
        <label>数据类型</label><select id="importType"><option value="messages">客服消息</option><option value="orders">订单</option><option value="after_sales">售后</option><option value="products">商品</option></select>
        <label>平台</label><select id="importPlatform"><option>淘宝</option><option>天猫</option><option>抖音商店</option><option>拼多多</option><option>闲鱼</option></select>
        <label>选择 CSV 文件</label><input id="csvFile" type="file" accept=".csv,text/csv" />
        <div class="toolbar"><button class="btn green" data-action="parse-csv">读取并导入</button><button class="btn secondary" data-action="load-sample">没有文件，先生成 5 条真实试用数据</button></div>
      </div>
      <div class="card" style="margin-top:16px"><h3>已导入数据</h3><p class="muted mini" style="margin-top:8px">当前共 ${state.importedRows.length} 条导入记录。</p><div style="overflow:auto;margin-top:12px">${renderImportedRows()}</div></div>`;
    }

    function customer() {
      return `<div class="toolbar"><button class="btn green" data-action="new-message">录入一条真实客户消息</button><button class="btn secondary" data-action="send-pending-api">把待处理消息发送到后端 API</button></div>
      <div class="card" style="overflow:auto"><table><thead><tr><th>平台</th><th>客户</th><th>消息</th><th>风险</th><th>AI草稿</th><th>状态</th><th>操作</th></tr></thead><tbody>
      ${state.messages.map(m => `<tr><td>${platformBadge(m.platform)}</td><td>${m.customer}</td><td>${m.content}</td><td>${badge(m.risk + "风险")}</td><td>${m.draft}</td><td>${badge(m.status)}</td><td><div class="row"><button class="btn green" data-approve-msg="${m.id}">采用</button><button class="btn secondary" data-edit-msg="${m.id}">修改</button><button class="btn amber" data-takeover-msg="${m.id}">人工接管</button></div></td></tr>`).join("")}
      </tbody></table></div>`;
    }

    function aftersale() {
      return `<div class="toolbar"><button class="btn green" data-action="new-case">新增售后任务</button></div>
      <div class="card" style="overflow:auto"><table><thead><tr><th>平台</th><th>客户</th><th>售后问题</th><th>风险</th><th>AI建议</th><th>状态</th><th>操作</th></tr></thead><tbody>
      ${state.cases.map(c => `<tr><td>${platformBadge(c.platform)}</td><td>${c.customer}</td><td><strong>${c.title}</strong><p class="muted mini">${c.desc}</p></td><td>${badge(c.risk + "风险")}</td><td>${c.suggestion}</td><td>${badge(c.status)}</td><td><button class="btn green" data-close-case="${c.id}">标记已处理</button></td></tr>`).join("")}
      </tbody></table></div>`;
    }

    function operation() {
      const highIntent = state.messages.filter(m => /尺码|下单|优惠|还有|库存|发货/.test(m.content)).length;
      return `<section class="grid three">
        <div class="card"><span class="badge">私域获客</span><h3 style="margin-top:10px">高意向客户 ${highIntent} 人</h3><p class="muted mini" style="margin-top:8px">建议客服把反复问尺码、库存、发货的客户拉进企微或社群。</p><button class="btn secondary" data-action="ops-script">生成私域话术</button></div>
        <div class="card"><span class="badge amber">投流草稿</span><h3 style="margin-top:10px">先不自动花钱</h3><p class="muted mini" style="margin-top:8px">AI 只能生成投流建议，预算必须老板审批。</p><button class="btn secondary" data-action="ops-ad">生成测试计划</button></div>
        <div class="card"><span class="badge">详情页优化</span><h3 style="margin-top:10px">减少重复咨询</h3><p class="muted mini" style="margin-top:8px">如果客户老问同一问题，AI 会建议写到详情页。</p><button class="btn secondary" data-action="ops-detail">生成优化建议</button></div>
      </section><div class="card" id="opsOutput" style="margin-top:16px"><p class="muted">点击上方按钮生成运营动作。</p></div>`;
    }

    function saving() {
      const handled = state.messages.filter(m => m.status === "已采用").length;
      return `<section class="grid metrics">
        ${metric("已采用 AI 回复", handled, "客服可替代动作")}
        ${metric("节省分钟", state.savedMinutes, "按每条 4-5 分钟")}
        ${metric("预估节省", "¥" + state.savedYuan, "深圳客服/售后/运营约 4 万/月")}
        ${metric("当前替代率", replacementRate() + "%", "按低风险任务估算")}
      </section>
      <div class="card" style="margin-top:16px"><h3>怎么把替代率做到 60%-70%</h3><div class="grid" style="margin-top:12px">
        <div class="item">1. 导入最近 30 天真实订单、商品、售后、客服问题。</div>
        <div class="item">2. 先让 AI 只处理低风险 FAQ、订单、物流。</div>
        <div class="item">3. 每天让客服修改 50 条 AI 草稿，形成学习样本。</div>
        <div class="item">4. 当错误率低于 3%，再开启低风险自动回复。</div>
      </div></div>`;
    }

    function settings() {
      return `<div class="card">
        <h3>后端 API 设置</h3>
        <p class="muted mini" style="margin-top:8px">如果 FastAPI 后端已经部署，填入地址和桥接密钥后，可把真实消息同步到后端数据库。</p>
        <label>后端 API 地址</label><input id="apiBase" value="${state.apiBase || ""}" placeholder="https://api.your-domain.com" />
        <label>桥接密钥（生产必填，本地测试可空）</label><input id="bridgeKey" value="${state.bridgeKey || ""}" placeholder="X-AICOS-Bridge-Key" />
        <div class="toolbar"><button class="btn green" data-action="save-settings">保存设置</button><button class="btn secondary" data-action="test-api">测试后端连接</button><button class="btn red" data-action="reset-data">清空本店本地数据</button></div>
      </div>
      <div class="notice" style="margin-top:16px">安全边界：AI 不自动退款、不自动赔偿、不自动改价、不自动投流花钱。涉及钱和投诉必须老板确认。</div>`;
    }

    function renderImportedRows() {
      if (!state.importedRows.length) return `<p class="muted">还没有导入数据。</p>`;
      const rows = state.importedRows.slice(-8);
      const headers = Object.keys(rows[0] || {}).slice(0,6);
      return `<table><thead><tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr></thead><tbody>${rows.map(row => `<tr>${headers.map(h => `<td>${row[h] || ""}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
    }

    function bindActions() {
      document.querySelectorAll("[data-page-jump]").forEach(b => b.onclick = () => renderPage(b.dataset.pageJump));
      document.querySelectorAll("[data-action]").forEach(b => b.onclick = () => handleAction(b.dataset.action));
      document.querySelectorAll("[data-approve-msg]").forEach(b => b.onclick = () => approveMessage(b.dataset.approveMsg));
      document.querySelectorAll("[data-edit-msg]").forEach(b => b.onclick = () => editMessage(b.dataset.editMsg));
      document.querySelectorAll("[data-takeover-msg]").forEach(b => b.onclick = () => takeoverMessage(b.dataset.takeoverMsg));
      document.querySelectorAll("[data-close-case]").forEach(b => b.onclick = () => closeCase(b.dataset.closeCase));
    }

    function classifyMessage(content) {
      if (/退款|退货|赔|补偿|投诉|差评|金额|便宜/.test(content)) return ["compensation","高",0,"该问题涉及退款、赔偿、投诉或金额承诺，AI 不会自动回复，必须人工确认。"];
      if (/物流|快递|发货|到哪|单号/.test(content)) return ["logistics","低",5,"您好，我先帮您确认订单和物流状态。如果 24 小时没有更新，会转人工继续跟进。"];
      if (/订单|下单|付款|拍下/.test(content)) return ["order","低",5,"您好，您的订单我已经收到，会按订单状态继续为您跟进。"];
      if (/尺码|颜色|库存|有没有|适合/.test(content)) return ["faq","低",4,"您好，这个问题我先按店铺商品知识为您确认；如涉及金额或售后会转人工。"];
      return ["unknown","高",0,"这个问题 AI 还不确定，需要人工确认后再回复，避免乱说。"];
    }

    function handleAction(action) {
      if (action === "load-sample") {
        const samples = [
          { "客户":"刘女士", "客户问题":"今天下单什么时候发货？", "平台":"淘宝" },
          { "客户":"张先生", "客户问题":"这件衣服有 L 码吗？", "平台":"抖音商店" },
          { "客户":"小林", "客户问题":"物流三天没动了，能赔偿吗？", "平台":"闲鱼" },
          { "客户":"陈女士", "客户问题":"订单到哪里了？", "平台":"拼多多" },
          { "客户":"何先生", "客户问题":"商品破损我要投诉。", "平台":"天猫" }
        ];
        state.importedRows.push(...samples);
        samples.forEach(addMessageFromRow);
        saveState(); renderPage("customer"); showToast("已生成 5 条可处理的真实试用消息。");
      }
      if (action === "parse-csv") parseCsvFile();
      if (action === "new-message") openNewMessageDrawer();
      if (action === "new-case") openNewCaseDrawer();
      if (action === "save-settings") { state.apiBase = document.getElementById("apiBase").value.trim(); state.bridgeKey = document.getElementById("bridgeKey").value.trim(); saveState(); showToast("设置已保存。"); }
      if (action === "test-api") testApiConnection();
      if (action === "reset-data") { state = defaultState(); saveState(); renderPage("dashboard"); showToast("已清空并恢复初始数据。", "danger"); }
      if (action === "send-pending-api") sendPendingToApi();
      if (action === "ops-script") document.getElementById("opsOutput").innerHTML = `<h3>私域话术</h3><p class="muted" style="margin-top:8px;line-height:1.8">您好，我看到您刚才咨询了尺码和发货。我们可以帮您优先确认库存，并给您保留当前优惠，有需要可以继续发身高体重，我帮您推荐。</p>`;
      if (action === "ops-ad") document.getElementById("opsOutput").innerHTML = `<h3>投流计划草稿</h3><p class="muted" style="margin-top:8px;line-height:1.8">建议先用 300 元测试“当天发货 + 尺码顾问”素材，不自动投放，老板确认后再执行。</p>`;
      if (action === "ops-detail") document.getElementById("opsOutput").innerHTML = `<h3>详情页优化建议</h3><p class="muted" style="margin-top:8px;line-height:1.8">把发货时间、尺码建议、退换规则放到详情页前 3 屏，减少客服重复回答。</p>`;
    }

    function addMessageFromRow(row) {
      const content = row["客户问题"] || row["问题"] || row["买家留言"] || row["message"] || "";
      if (!content) return;
      const platform = row["平台"] || document.getElementById("importPlatform")?.value || "淘宝";
      const customer = row["客户"] || row["买家昵称"] || row["customer"] || "平台客户";
      const [intent,risk,saved,draft] = classifyMessage(content);
      state.messages.unshift({ id:"msg-" + Date.now() + "-" + Math.random().toString(16).slice(2), platform, customer, content, intent, risk, status:risk === "高" ? "人工确认" : "待处理", draft, saved });
    }

    function parseCsvFile() {
      const input = document.getElementById("csvFile");
      const file = input.files && input.files[0];
      if (!file) { showToast("请先选择 CSV 文件。", "danger"); return; }
      const reader = new FileReader();
      reader.onload = () => {
        const text = String(reader.result || "");
        const rows = csvToRows(text);
        if (!rows.length) { showToast("文件没有读到有效数据。", "danger"); return; }
        state.importedRows.push(...rows);
        if (document.getElementById("importType").value === "messages") rows.forEach(addMessageFromRow);
        saveState(); renderPage(document.getElementById("importType").value === "messages" ? "customer" : "import");
        showToast("已导入 " + rows.length + " 条数据。");
      };
      reader.readAsText(file, "utf-8");
    }

    function csvToRows(text) {
      const lines = text.replace(/^\\ufeff/, "").split(/\\r?\\n/).filter(Boolean);
      if (lines.length < 2) return [];
      const headers = splitCsvLine(lines[0]);
      return lines.slice(1).map(line => {
        const values = splitCsvLine(line);
        const row = {};
        headers.forEach((h,i) => row[h.trim()] = (values[i] || "").trim());
        return row;
      });
    }
    function splitCsvLine(line) {
      const out = []; let cur = ""; let quote = false;
      for (let i=0; i<line.length; i++) {
        const ch = line[i];
        if (ch === '"') { quote = !quote; continue; }
        if (ch === "," && !quote) { out.push(cur); cur = ""; continue; }
        cur += ch;
      }
      out.push(cur); return out;
    }

    function approveMessage(id) {
      const msg = state.messages.find(m => m.id === id);
      if (!msg) return;
      if (msg.risk === "高") { showToast("高风险消息不能直接采用，必须人工确认。", "danger"); return; }
      msg.status = "已采用";
      state.savedMinutes += msg.saved || 4;
      state.savedYuan = Math.round(state.savedMinutes / 60 * HOURLY_COST);
      saveState(); renderPage("customer"); showToast("已采用 AI 回复，并计入省钱统计。");
    }
    function takeoverMessage(id) { const msg = state.messages.find(m => m.id === id); if (msg) { msg.status = "人工接管"; saveState(); renderPage("customer"); showToast("已转人工接管，AI 不会自动发送。"); } }
    function editMessage(id) {
      const msg = state.messages.find(m => m.id === id); if (!msg) return;
      openDrawer(`<button class="btn secondary" onclick="closeDrawer()">关闭</button><h2 style="margin-top:18px">修改 AI 回复</h2><p class="muted" style="margin-top:8px">${msg.content}</p><label>最终回复</label><textarea id="editedReply">${msg.draft}</textarea><button class="btn green" style="margin-top:14px" onclick="saveEditedReply('${id}')">保存并学习</button>`);
    }
    function saveEditedReply(id) { const msg = state.messages.find(m => m.id === id); if (msg) { msg.draft = document.getElementById("editedReply").value; msg.status = "已修改"; state.savedMinutes += 3; state.savedYuan = Math.round(state.savedMinutes / 60 * HOURLY_COST); saveState(); closeDrawer(); renderPage("customer"); showToast("已保存商家修改，后续可进入训练中心。"); } }

    function openNewMessageDrawer() {
      openDrawer(`<button class="btn secondary" onclick="closeDrawer()">关闭</button><h2 style="margin-top:18px">录入真实客户消息</h2><label>平台</label><select id="newPlatform"><option>淘宝</option><option>天猫</option><option>抖音商店</option><option>拼多多</option><option>闲鱼</option></select><label>客户名</label><input id="newCustomer" value="新客户" /><label>客户消息</label><textarea id="newContent">今天下单什么时候发货？</textarea><button class="btn green" style="margin-top:14px" onclick="saveNewMessage()">让 AI 处理</button>`);
    }
    function saveNewMessage() {
      addMessageFromRow({ "平台":document.getElementById("newPlatform").value, "客户":document.getElementById("newCustomer").value, "客户问题":document.getElementById("newContent").value });
      saveState(); closeDrawer(); renderPage("customer"); showToast("真实客户消息已进入 AI 客服。");
    }
    function openNewCaseDrawer() {
      openDrawer(`<button class="btn secondary" onclick="closeDrawer()">关闭</button><h2 style="margin-top:18px">新增售后任务</h2><label>平台</label><select id="casePlatform"><option>淘宝</option><option>抖音商店</option><option>拼多多</option><option>闲鱼</option></select><label>客户名</label><input id="caseCustomer" value="售后客户" /><label>售后问题</label><textarea id="caseDesc">客户要求退款并投诉物流太慢。</textarea><button class="btn green" style="margin-top:14px" onclick="saveNewCase()">生成售后建议</button>`);
    }
    function saveNewCase() {
      const desc = document.getElementById("caseDesc").value;
      const high = /投诉|赔|退款|差评/.test(desc);
      state.cases.unshift({ id:"case-" + Date.now(), platform:document.getElementById("casePlatform").value, customer:document.getElementById("caseCustomer").value, title:high ? "高风险售后" : "普通售后", desc, risk:high ? "高" : "中", suggestion:high ? "必须人工确认，先核实证据，不承诺金额。" : "按店铺规则处理，保留沟通记录。", status:"待审批" });
      saveState(); closeDrawer(); renderPage("aftersale"); showToast("售后任务已生成。");
    }
    function closeCase(id) { const item = state.cases.find(c => c.id === id); if (item) { item.status = "已处理"; state.savedMinutes += 8; state.savedYuan = Math.round(state.savedMinutes / 60 * HOURLY_COST); saveState(); renderPage("aftersale"); showToast("售后任务已处理，并计入省钱统计。"); } }

    async function sendPendingToApi() {
      if (!state.apiBase) { showToast("请先在系统设置里填写后端 API 地址。", "danger"); return; }
      const pending = state.messages.filter(m => m.status === "待处理" || m.status === "人工确认").slice(0, 10);
      let ok = 0;
      for (const msg of pending) {
        try {
          const headers = { "content-type":"application/json" };
          if (state.bridgeKey) headers["X-AICOS-Bridge-Key"] = state.bridgeKey;
          const res = await fetch(state.apiBase.replace(/\\/$/, "") + "/v1/customer-agent/external-messages", {
            method:"POST",
            headers,
            body:JSON.stringify({ platform: platformCode(msg.platform), platform_message_id: msg.id, customer_name: msg.customer, content: msg.content, channel:"merchant_console" })
          });
          if (res.ok) ok++;
        } catch {}
      }
      showToast("已尝试发送 " + pending.length + " 条消息到后端，成功 " + ok + " 条。");
    }
    async function testApiConnection() {
      const apiBase = (document.getElementById("apiBase")?.value || state.apiBase || "").trim();
      if (!apiBase) { showToast("请先填写后端 API 地址。", "danger"); return; }
      try {
        const response = await fetch(apiBase.replace(/\\/$/, "") + "/health/ready", { headers:{ accept:"application/json" } });
        const payload = await response.json();
        if (payload.status === "ready") {
          showToast("后端已就绪：数据库和桥接密钥都已配置，可以接真实商家消息。");
          return;
        }
        showToast("后端还没完全就绪：数据库=" + (payload.database ? "已连接" : "未连接") + "，桥接密钥=" + (payload.bridge_key ? "已配置" : "未配置") + "。", "danger");
      } catch {
        showToast("无法连接后端 API。请确认 FastAPI 已部署，并允许当前控制台域名跨域访问。", "danger");
      }
    }
    function platformCode(name) { if (name.includes("抖")) return "douyin"; if (name.includes("闲")) return "xianyu"; if (name.includes("Shopify")) return "shopify"; return "taobao"; }
    function replacementRate() { const total = Math.max(1, state.messages.length + state.cases.length); const done = state.messages.filter(m => m.status === "已采用" || m.status === "已修改").length + state.cases.filter(c => c.status === "已处理").length; return Math.min(70, Math.round(done / total * 100)); }
    function openDrawer(html) { document.getElementById("drawerPanel").innerHTML = html; document.getElementById("drawer").classList.add("open"); }
    function closeDrawer() { document.getElementById("drawer").classList.remove("open"); }
    window.closeDrawer = closeDrawer; window.saveNewMessage = saveNewMessage; window.saveEditedReply = saveEditedReply; window.saveNewCase = saveNewCase;
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
