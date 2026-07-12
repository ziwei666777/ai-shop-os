from __future__ import annotations

import base64
import json
import shutil
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "sites-vinext-promo"
ARCHIVE = ROOT / "dist" / "sites-vinext-promo.tar.gz"
IMAGE = ROOT / "apps" / "promo-deploy" / "public" / "marketing" / "ai-commerce-os-b2b-hero.png"


def html_document(image_data_url: str) -> str:
    # 线上宣传站使用单文件 HTML，避免部署平台读取 monorepo workspace 依赖。
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI Commerce OS | AI 电商员工操作系统</title>
  <meta name="description" content="面向电商企业的 AI 员工操作系统，从客服、售后、运营开始验证真实降本。" />
  <style>
    :root {{ --bg:#f8fafc; --fg:#111827; --muted:#64748b; --line:#e5e7eb; --card:#fff; --ink:#0f172a; --primary:#0f766e; --soft:#eef6f6; }}
    * {{ box-sizing:border-box; }}
    html {{ scroll-behavior:smooth; }}
    body {{ margin:0; background:var(--bg); color:var(--fg); font-family:"Microsoft YaHei","PingFang SC",Arial,sans-serif; }}
    a {{ color:inherit; text-decoration:none; }}
    .hero {{ position:relative; min-height:92vh; overflow:hidden; background:#020617; color:#fff; }}
    .hero::before {{ content:""; position:absolute; inset:0; background-image:url('{image_data_url}'); background-size:cover; background-position:center; }}
    .hero::after {{ content:""; position:absolute; inset:0; background:linear-gradient(90deg,rgb(2 6 23 / .88),rgb(2 6 23 / .66),rgb(2 6 23 / .28)); }}
    .nav {{ position:relative; z-index:1; display:flex; justify-content:space-between; gap:24px; max-width:1180px; margin:0 auto; padding:28px 24px; }}
    .nav div {{ display:flex; gap:24px; color:rgb(255 255 255 / .72); font-size:14px; }}
    .heroContent {{ position:relative; z-index:1; max-width:1180px; margin:0 auto; padding:120px 24px 90px; }}
    .eyebrow,.sectionHeader span {{ color:var(--primary); font-size:14px; font-weight:700; }}
    .hero .eyebrow {{ color:#99f6e4; }}
    h1,h2,h3,p {{ margin:0; }}
    h1 {{ max-width:760px; margin-top:24px; font-size:clamp(42px,6vw,72px); line-height:1.08; letter-spacing:0; }}
    .heroContent p {{ max-width:650px; margin-top:26px; color:rgb(255 255 255 / .76); font-size:18px; line-height:1.85; }}
    .heroActions {{ display:flex; flex-wrap:wrap; gap:12px; margin-top:34px; }}
    .heroActions a,.cta a {{ display:inline-flex; min-height:46px; align-items:center; justify-content:center; border-radius:8px; padding:0 20px; background:#fff; color:#0f172a; font-size:14px; font-weight:700; }}
    .heroActions a + a {{ border:1px solid rgb(255 255 255 / .22); background:rgb(255 255 255 / .08); color:#fff; }}
    .section {{ padding:86px 24px; border-bottom:1px solid var(--line); }}
    .muted {{ background:#f1f5f9; }}
    .section > *,.split {{ max-width:1180px; margin-left:auto; margin-right:auto; }}
    .sectionHeader {{ max-width:780px; }}
    .sectionHeader h2 {{ margin-top:14px; font-size:clamp(30px,4vw,46px); line-height:1.18; letter-spacing:0; }}
    .sectionHeader p {{ margin-top:18px; color:var(--muted); font-size:16px; line-height:1.8; }}
    .costGrid,.agentGrid,.steps {{ display:grid; gap:18px; margin-top:42px; }}
    .costGrid {{ grid-template-columns:repeat(4,minmax(0,1fr)); }}
    .agentGrid {{ grid-template-columns:repeat(3,minmax(0,1fr)); }}
    .card,.feature,.demoBoard,.step,.metric {{ border:1px solid var(--line); border-radius:10px; background:var(--card); box-shadow:0 18px 60px rgb(15 23 42 / .08); }}
    .card {{ min-height:220px; padding:26px; }}
    .card small {{ color:var(--primary); font-weight:700; }}
    .card h3 {{ margin-top:18px; font-size:28px; }}
    .card p {{ margin-top:18px; color:var(--muted); line-height:1.75; }}
    .darkCard {{ background:var(--ink); color:#fff; }}
    .darkCard small,.darkCard p {{ color:rgb(255 255 255 / .7); }}
    .darkCard strong {{ display:block; margin-top:18px; font-size:42px; }}
    .split {{ display:grid; grid-template-columns:.85fr 1.15fr; gap:50px; align-items:start; }}
    .featureList,.metricGrid {{ display:grid; gap:14px; }}
    .feature {{ padding:24px; color:#334155; line-height:1.7; }}
    .agentIcon {{ width:42px; height:42px; border-radius:12px; background:linear-gradient(135deg,#0f766e,#2563eb); }}
    .demoBoard {{ max-width:1180px; margin:42px auto 0; overflow:hidden; }}
    .demoRow {{ display:grid; grid-template-columns:170px 1fr 1.25fr; gap:20px; padding:22px 26px; border-bottom:1px solid var(--line); }}
    .demoRow:last-child {{ border-bottom:0; }}
    .demoRow span {{ color:#334155; }}
    .demoRow p {{ color:var(--muted); }}
    .steps {{ grid-template-columns:repeat(5,minmax(0,1fr)); }}
    .step {{ padding:22px; }}
    .step b {{ display:inline-flex; width:38px; height:38px; align-items:center; justify-content:center; border-radius:10px; background:var(--soft); color:var(--primary); }}
    .step p {{ margin-top:22px; color:var(--muted); line-height:1.7; }}
    .metricGrid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
    .metric {{ padding:18px 20px; color:#334155; }}
    .cta {{ padding:92px 24px; background:#020617; color:#fff; text-align:center; }}
    .cta h2 {{ font-size:clamp(32px,4vw,52px); }}
    .cta p {{ max-width:760px; margin:22px auto 32px; color:rgb(255 255 255 / .72); line-height:1.8; }}
    @media (max-width:980px) {{ .nav div {{ display:none; }} .costGrid,.agentGrid,.steps,.split,.metricGrid {{ grid-template-columns:1fr; }} .demoRow {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <nav class="nav"><strong>AI Commerce OS</strong><div><a href="#product">产品说明</a><a href="#demo">演示界面</a><a href="#trial">试用流程</a></div></nav>
      <div class="heroContent">
        <span class="eyebrow">面向电商企业的 AI 员工操作系统</span>
        <h1>让老板拥有一支可审批、可追踪、可学习的 AI 电商团队</h1>
        <p>从 AI客服、AI售后、AI运营三个岗位开始，把重复、标准化、可审批的工作交给 AI，目标逐步替代约 4 万元/月基础人力成本。</p>
        <div class="heroActions"><a href="#demo">查看演示界面</a><a href="#trial">了解 7 天试用</a></div>
      </div>
    </section>
    <section class="section"><div class="sectionHeader"><span>Cost Reduction</span><h2>企业真正要买的不是 AI，而是可验证的降本结果</h2><p>AI Commerce OS 优先处理电商团队中重复、标准化、可审批的工作，先省时间，再省人。</p></div><div class="costGrid">
      <article class="card"><small>高频重复工作</small><h3>客服</h3><p>售前咨询、订单查询、物流追踪、催付转化</p></article>
      <article class="card"><small>风险密集工作</small><h3>售后</h3><p>退款退货、投诉分级、异常物流、赔偿初筛</p></article>
      <article class="card"><small>持续消耗工作</small><h3>运营</h3><p>客户线索、私域话术、投流计划、活动复盘</p></article>
      <article class="card darkCard"><small>目标替代成本</small><strong>约 4 万/月</strong><p>用真实数据验证 AI 能先替代多少重复工作，再逐步扩大自动化比例。</p></article>
    </div></section>
    <section class="section muted" id="product"><div class="split"><div class="sectionHeader"><span>Product</span><h2>不是聊天机器人，也不是传统 ERP</h2><p>它是一套 AI 电商员工控制台：AI 负责执行低风险工作，老板负责关键审批，系统负责记录和学习。</p></div><div class="featureList"><div class="feature">AI员工化：每个 AI 都有职责、权限、工作记录和评估指标。</div><div class="feature">审批优先：退款、赔偿、预算、投流和客户数据动作必须进入审批。</div><div class="feature">数据验证：通过 Dataset、Replay 和 Evaluation 验证 AI 是否真的能工作。</div></div></div></section>
    <section class="section"><div class="sectionHeader"><span>AI Employees</span><h2>三个 AI 员工，先接管最容易标准化的工作</h2><p>当前聚焦客服、售后、运营，不继续堆更多 Agent。目标是先证明可节省时间和成本。</p></div><div class="agentGrid"><article class="card"><div class="agentIcon"></div><h3>AI客服</h3><p>自动处理 FAQ、订单、物流等低风险问题；不会的问题交给人工，并记录修改。</p></article><article class="card"><div class="agentIcon"></div><h3>AI售后</h3><p>识别退款、退货、投诉和异常物流，输出风险等级和审批建议。</p></article><article class="card"><div class="agentIcon"></div><h3>AI运营</h3><p>识别高意向客户，生成私域话术和投流计划草稿，预算动作必须审批。</p></article></div></section>
    <section class="section muted" id="demo"><div class="sectionHeader"><span>Demo</span><h2>演示界面：看 AI 如何工作，而不是只看概念</h2><p>演示数据为静态样例，用来说明产品流程。真实上线后会接入商家订单、客户、售后和运营数据。</p></div><div class="demoBoard"><div class="demoRow"><strong>客户咨询</strong><span>这件外套今天下单什么时候发？</span><p>AI 判断为物流低风险，生成回复草稿</p></div><div class="demoRow"><strong>售后投诉</strong><span>物流超时要求赔偿</span><p>AI 标记高风险，必须老板审批</p></div><div class="demoRow"><strong>运营线索</strong><span>7 天内多次咨询尺码和发货</span><p>AI 生成私域引导话术和投流草稿</p></div><div class="demoRow"><strong>老板审批</strong><span>退款、赔偿、预算、群发</span><p>统一进入审批，记录决策依据</p></div></div></section>
    <section class="section" id="trial"><div class="sectionHeader"><span>Pilot</span><h2>7 天试用：先让 AI 跑起来，再看数据</h2><p>试用期不追求全自动，先追求可验证：节省多少时间、减少多少人工判断、沉淀多少学习样本。</p></div><div class="steps"><div class="step"><b>1</b><p>导入商品、订单、客户、售后数据</p></div><div class="step"><b>2</b><p>AI客服生成回复草稿，客服修正</p></div><div class="step"><b>3</b><p>AI售后做风险分级和审批建议</p></div><div class="step"><b>4</b><p>AI运营识别私域线索和投流草稿</p></div><div class="step"><b>5</b><p>每周复盘自动化率、错误率和节省工时</p></div></div></section>
    <section class="section muted"><div class="split"><div class="sectionHeader"><span>Evaluation</span><h2>用指标判断 AI 是否值得继续扩大使用</h2><p>所有演示和试用都要回到同一件事：AI 有没有真正降低人工成本、减少风险、提高响应效率。</p></div><div class="metricGrid"><div class="metric">客服自动回复率</div><div class="metric">客服错误率</div><div class="metric">人工接管率</div><div class="metric">售后分类准确率</div><div class="metric">高风险拦截率</div><div class="metric">私域线索数量</div><div class="metric">运营建议采纳率</div><div class="metric">节省人工分钟数</div></div></div></section>
    <section class="cta"><h2>先用一家真实店铺验证降本</h2><p>导入历史数据，跑 AI客服和 AI售后，收集修改样本，一周后用指标判断是否继续扩大自动化。</p><a href="#demo">查看演示流程</a></section>
  </main>
</body>
</html>"""


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    if ARCHIVE.exists():
        ARCHIVE.unlink()
    (OUT / ".openai").mkdir(parents=True, exist_ok=True)
    image_data = "data:image/png;base64," + base64.b64encode(IMAGE.read_bytes()).decode("ascii")
    worker = f"""const HTML = {json.dumps(html_document(image_data), ensure_ascii=False)};

export default {{
  async fetch() {{
    return new Response(HTML, {{
      headers: {{
        "content-type": "text/html; charset=utf-8",
        "cache-control": "public, max-age=300"
      }}
    }});
  }}
}};
"""
    (OUT / "index.js").write_text(worker, encoding="utf-8")
    (OUT / ".openai" / "hosting.json").write_text(
        json.dumps({"project_id": "appgprj_6a5307e4aec0819197ad99d8de2b358b"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    with tarfile.open(ARCHIVE, "w:gz") as tar:
        tar.add(OUT, arcname=".")
    print(ARCHIVE)


if __name__ == "__main__":
    main()
