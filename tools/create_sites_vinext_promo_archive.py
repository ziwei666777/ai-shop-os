from __future__ import annotations

import base64
import json
import shutil
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "dist" / "sites-vinext-promo"
ARCHIVE_PATH = ROOT / "dist" / "sites-vinext-promo.tar.gz"
HERO_IMAGE = ROOT / "apps" / "promo-deploy" / "public" / "marketing" / "ai-commerce-os-b2b-hero.png"
PROJECT_ID = "appgprj_6a5307e4aec0819197ad99d8de2b358b"


def build_html(hero_data_url: str) -> str:
    # 线上宣传站使用单文件 HTML，避免 Sites 读取 monorepo workspace 依赖后构建失败。
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI Commerce OS | AI 电商员工操作系统</title>
  <meta name="description" content="面向电商企业的 AI 员工操作系统，从 AI 客服、AI 售后、AI 运营开始验证真实降本。" />
  <style>
    :root {{
      --bg: #f8fafc;
      --fg: #101827;
      --muted: #64748b;
      --line: #e5e7eb;
      --card: #ffffff;
      --ink: #08111f;
      --primary: #0f766e;
      --blue: #1d4ed8;
      --soft: #eef7f6;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--fg);
      font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
      letter-spacing: 0;
    }}
    a {{ color: inherit; text-decoration: none; }}
    h1, h2, h3, p {{ margin: 0; }}
    .hero {{
      position: relative;
      min-height: 92vh;
      overflow: hidden;
      background: #020617;
      color: white;
    }}
    .hero::before {{
      content: "";
      position: absolute;
      inset: 0;
      background-image: url("{hero_data_url}");
      background-size: cover;
      background-position: center;
      opacity: .82;
    }}
    .hero::after {{
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(90deg, rgb(2 6 23 / .9), rgb(2 6 23 / .66), rgb(2 6 23 / .24));
    }}
    .nav, .hero-inner, .section-inner {{
      position: relative;
      z-index: 1;
      max-width: 1180px;
      margin: 0 auto;
      padding-left: 24px;
      padding-right: 24px;
    }}
    .nav {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
      padding-top: 28px;
      padding-bottom: 28px;
    }}
    .nav-links {{ display: flex; gap: 22px; color: rgb(255 255 255 / .72); font-size: 14px; }}
    .hero-inner {{ padding-top: 112px; padding-bottom: 88px; }}
    .eyebrow {{ color: #99f6e4; font-size: 14px; font-weight: 700; }}
    h1 {{ max-width: 820px; margin-top: 24px; font-size: clamp(42px, 6vw, 72px); line-height: 1.08; }}
    .hero p {{ max-width: 680px; margin-top: 26px; color: rgb(255 255 255 / .76); font-size: 18px; line-height: 1.85; }}
    .actions {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 34px; }}
    .button {{
      display: inline-flex;
      min-height: 46px;
      align-items: center;
      justify-content: center;
      border-radius: 8px;
      padding: 0 20px;
      background: white;
      color: #0f172a;
      font-size: 14px;
      font-weight: 700;
    }}
    .button.secondary {{ border: 1px solid rgb(255 255 255 / .24); background: rgb(255 255 255 / .08); color: white; }}
    .section {{ padding: 86px 0; border-bottom: 1px solid var(--line); }}
    .muted {{ background: #f1f5f9; }}
    .section-title {{ max-width: 820px; }}
    .section-title span {{ color: var(--primary); font-size: 14px; font-weight: 700; }}
    .section-title h2 {{ margin-top: 14px; font-size: clamp(30px, 4vw, 46px); line-height: 1.18; }}
    .section-title p {{ margin-top: 18px; color: var(--muted); font-size: 16px; line-height: 1.8; }}
    .grid {{ display: grid; gap: 18px; margin-top: 42px; }}
    .cost-grid {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
    .agent-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    .steps {{ grid-template-columns: repeat(5, minmax(0, 1fr)); }}
    .card, .panel, .step, .metric {{
      border: 1px solid var(--line);
      border-radius: 10px;
      background: var(--card);
      box-shadow: 0 18px 60px rgb(15 23 42 / .08);
    }}
    .card {{ min-height: 220px; padding: 26px; }}
    .card small {{ color: var(--primary); font-weight: 700; }}
    .card h3 {{ margin-top: 18px; font-size: 28px; }}
    .card p {{ margin-top: 18px; color: var(--muted); line-height: 1.75; }}
    .dark-card {{ background: var(--ink); color: white; }}
    .dark-card small, .dark-card p {{ color: rgb(255 255 255 / .72); }}
    .dark-card strong {{ display: block; margin-top: 18px; font-size: 42px; }}
    .split {{ display: grid; grid-template-columns: .85fr 1.15fr; gap: 50px; align-items: start; }}
    .feature-list, .metric-grid {{ display: grid; gap: 14px; }}
    .panel {{ padding: 24px; color: #334155; line-height: 1.75; }}
    .agent-dot {{ width: 42px; height: 42px; border-radius: 12px; background: linear-gradient(135deg, var(--primary), var(--blue)); }}
    .demo-shell {{
      display: grid;
      grid-template-columns: 220px 1fr;
      gap: 18px;
      margin-top: 42px;
    }}
    .demo-tabs {{ display: grid; gap: 10px; align-content: start; }}
    .demo-tab {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: white;
      padding: 16px 18px;
      color: #334155;
      font: inherit;
      text-align: left;
      cursor: pointer;
    }}
    .demo-tab.active {{
      border-color: #0f172a;
      background: #0f172a;
      color: white;
      box-shadow: 0 18px 40px rgb(15 23 42 / .16);
    }}
    .demo-panel {{ display: none; padding: 28px; }}
    .demo-panel.active {{ display: block; }}
    .demo-panel header {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 18px; }}
    .demo-panel h3 {{ font-size: 30px; line-height: 1.2; }}
    .demo-panel header p {{ max-width: 680px; margin-top: 14px; color: var(--muted); line-height: 1.75; }}
    .badge {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      background: #ecfdf5;
      color: #047857;
      padding: 8px 12px;
      font-size: 13px;
      font-weight: 700;
      white-space: nowrap;
    }}
    .badge.warn {{ background: #fffbeb; color: #b45309; }}
    .demo-cards {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 28px; }}
    .demo-card {{ border: 1px solid var(--line); border-radius: 10px; background: #f8fafc; padding: 18px; }}
    .demo-card small {{ color: var(--muted); font-weight: 700; }}
    .demo-card p {{ margin-top: 12px; color: #172033; line-height: 1.65; }}
    .demo-flow {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 24px; }}
    .demo-flow span {{ border: 1px solid var(--line); border-radius: 999px; background: white; padding: 10px 12px; color: #475569; font-size: 13px; }}
    .step {{ padding: 22px; }}
    .step b {{ display: inline-flex; width: 38px; height: 38px; align-items: center; justify-content: center; border-radius: 10px; background: var(--soft); color: var(--primary); }}
    .step p {{ margin-top: 22px; color: var(--muted); line-height: 1.7; }}
    .metric-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .metric {{ padding: 18px 20px; color: #334155; }}
    .sandbox {{
      margin-top: 42px;
      display: grid;
      grid-template-columns: .9fr 1.1fr;
      gap: 18px;
      align-items: stretch;
    }}
    .sandbox-card {{
      border: 1px solid var(--line);
      border-radius: 14px;
      background: white;
      padding: 24px;
      box-shadow: 0 18px 60px rgb(15 23 42 / .08);
    }}
    .sandbox-card h3 {{ font-size: 24px; }}
    .sandbox-card p {{ margin-top: 12px; color: var(--muted); line-height: 1.75; }}
    .sandbox textarea {{
      width: 100%;
      min-height: 150px;
      margin-top: 18px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 14px;
      color: #0f172a;
      font: inherit;
      line-height: 1.65;
      outline: none;
    }}
    .sandbox textarea:focus {{ border-color: var(--primary); box-shadow: 0 0 0 4px rgb(15 118 110 / .1); }}
    .sandbox-actions {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }}
    .sandbox-actions button {{
      min-height: 42px;
      border: 0;
      border-radius: 8px;
      padding: 0 16px;
      background: #0f172a;
      color: white;
      font: inherit;
      font-size: 14px;
      font-weight: 800;
      cursor: pointer;
    }}
    .sandbox-actions button.secondary {{ border: 1px solid var(--line); background: white; color: #0f172a; }}
    .sandbox-output {{
      min-height: 100%;
      border: 1px solid #bfdbfe;
      border-radius: 14px;
      background: #eff6ff;
      padding: 24px;
    }}
    .sandbox-output small {{ color: #1d4ed8; font-weight: 800; }}
    .sandbox-output h3 {{ margin-top: 12px; font-size: 26px; }}
    .sandbox-result {{
      margin-top: 18px;
      border-radius: 10px;
      background: white;
      padding: 18px;
      color: #172033;
      line-height: 1.8;
      white-space: pre-wrap;
    }}
    .sandbox-kpis {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin-top: 18px;
    }}
    .sandbox-kpis span {{
      border-radius: 10px;
      background: rgb(255 255 255 / .78);
      padding: 12px;
      color: #334155;
      font-size: 13px;
      line-height: 1.5;
    }}
    .experience-wrap {{
      margin-top: 42px;
      border: 1px solid var(--line);
      border-radius: 16px;
      overflow: hidden;
      background: #0f172a;
      box-shadow: 0 24px 80px rgb(15 23 42 / .14);
    }}
    .experience-bar {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px 20px;
      color: white;
      border-bottom: 1px solid rgb(255 255 255 / .12);
    }}
    .experience-bar p {{ color: rgb(255 255 255 / .68); font-size: 14px; line-height: 1.6; }}
    .experience-bar a {{
      display: inline-flex;
      min-height: 38px;
      align-items: center;
      justify-content: center;
      border-radius: 8px;
      background: white;
      color: #0f172a;
      padding: 0 14px;
      font-size: 13px;
      font-weight: 800;
    }}
    .experience-frame {{
      width: 100%;
      height: 760px;
      border: 0;
      display: block;
      background: #f8fafc;
    }}
    .credential-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
      margin-top: 18px;
    }}
    .credential {{
      border: 1px solid var(--line);
      border-radius: 10px;
      background: white;
      padding: 16px;
      color: #334155;
    }}
    .credential strong {{ display: block; margin-top: 8px; color: #0f172a; word-break: break-all; }}
    .cta {{ padding: 92px 24px; background: #020617; color: white; text-align: center; }}
    .cta h2 {{ font-size: clamp(32px, 4vw, 52px); }}
    .cta p {{ max-width: 760px; margin: 22px auto 32px; color: rgb(255 255 255 / .72); line-height: 1.8; }}
    @media (max-width: 980px) {{
      .nav-links {{ display: none; }}
      .cost-grid, .agent-grid, .steps, .split, .metric-grid, .sandbox, .sandbox-kpis {{ grid-template-columns: 1fr; }}
      .demo-shell {{ grid-template-columns: 1fr; }}
      .demo-tabs {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .demo-cards {{ grid-template-columns: 1fr; }}
      .demo-panel header {{ display: block; }}
      .badge {{ margin-top: 16px; }}
      .credential-grid {{ grid-template-columns: 1fr; }}
      .experience-frame {{ height: 700px; }}
      .hero-inner {{ padding-top: 82px; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <nav class="nav">
        <strong>AI Commerce OS</strong>
        <div class="nav-links">
          <a href="#product">产品说明</a>
          <a href="#demo">演示界面</a>
          <a href="#sandbox">现场试用</a>
          <a href="#experience">产品体验</a>
          <a href="#trial">试用流程</a>
        </div>
      </nav>
      <div class="hero-inner">
        <span class="eyebrow">面向电商企业的 AI 员工操作系统</span>
        <h1>让老板拥有一支可审批、可追踪、可学习的 AI 电商团队</h1>
        <p>从 AI 客服、AI 售后、AI 运营三个岗位开始，把重复、标准化、可审批的工作交给 AI，目标逐步替代约 4 万元/月基础人力成本。</p>
        <div class="actions">
          <a class="button" href="#demo">查看演示界面</a>
          <a class="button secondary" href="#experience">直接体验产品</a>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="section-inner">
        <div class="section-title">
          <span>Cost Reduction</span>
          <h2>企业真正要买的不是 AI，而是可验证的降本结果</h2>
          <p>AI Commerce OS 优先处理电商团队中重复、标准化、可审批的工作，先节省时间，再逐步减少对基础岗位人力的依赖。</p>
        </div>
        <div class="grid cost-grid">
          <article class="card"><small>高频重复工作</small><h3>客服</h3><p>售前咨询、订单查询、物流追踪、催付转化、FAQ 回复。</p></article>
          <article class="card"><small>风险密集工作</small><h3>售后</h3><p>退款退货、投诉分级、异常物流、赔偿初筛、审批建议。</p></article>
          <article class="card"><small>持续消耗工作</small><h3>运营</h3><p>客户线索、私域话术、投流计划、活动复盘、转化建议。</p></article>
          <article class="card dark-card"><small>目标替代成本</small><strong>约 4 万/月</strong><p>用真实数据验证 AI 能先替代多少重复工作，再逐步扩大自动化比例。</p></article>
        </div>
      </div>
    </section>

    <section class="section muted" id="product">
      <div class="section-inner split">
        <div class="section-title">
          <span>Product</span>
          <h2>不是聊天机器人，也不是传统 ERP</h2>
          <p>这是 AI 电商员工控制台：AI 负责执行低风险工作，老板负责关键审批，系统负责记录、评估和学习。</p>
        </div>
        <div class="feature-list">
          <div class="panel">AI 员工化：每个 AI 都有职责、权限、工作记录、评估指标和学习记录。</div>
          <div class="panel">审批优先：退款、赔偿、预算、投流和客户数据动作必须进入老板审批。</div>
          <div class="panel">数据验证：通过 Dataset、Replay 和 Evaluation 验证 AI 是否真的能工作。</div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="section-inner">
        <div class="section-title">
          <span>AI Employees</span>
          <h2>三个 AI 员工，先接管最容易标准化的工作</h2>
          <p>当前聚焦客服、售后、运营，不继续堆更多 Agent。目标是先证明可以节省时间和成本。</p>
        </div>
        <div class="grid agent-grid">
          <article class="card"><div class="agent-dot"></div><h3>AI 客服</h3><p>自动处理 FAQ、订单、物流等低风险问题；不会的问题交给人工，并记录商家修正。</p></article>
          <article class="card"><div class="agent-dot"></div><h3>AI 售后</h3><p>识别退款、退货、投诉和异常物流，输出风险等级和审批建议。</p></article>
          <article class="card"><div class="agent-dot"></div><h3>AI 运营</h3><p>识别高意向客户，生成私域话术和投流计划草稿，预算动作必须审批。</p></article>
        </div>
      </div>
    </section>

    <section class="section muted" id="demo">
      <div class="section-inner">
        <div class="section-title">
          <span>Demo</span>
          <h2>演示界面：看 AI 如何工作，而不是只看概念</h2>
          <p>演示数据为静态样例，用来说明产品流程。真实上线后会接入商家订单、客户、售后和运营数据。</p>
        </div>
        <div class="demo-shell">
          <div class="demo-tabs" aria-label="演示模块切换">
            <button class="demo-tab active" type="button" data-demo-tab="customer">AI 客服</button>
            <button class="demo-tab" type="button" data-demo-tab="after-sale">AI 售后</button>
            <button class="demo-tab" type="button" data-demo-tab="operation">AI 运营</button>
            <button class="demo-tab" type="button" data-demo-tab="approval">老板审批</button>
          </div>

          <div class="panel demo-panel active" data-demo-panel="customer">
            <header>
              <div>
                <h3>AI 客服工作台</h3>
                <p>客户消息进入收件箱后，AI 先判断问题类型和风险等级。FAQ、订单、物流类低风险问题可以生成回复草稿；不会的问题必须暂停并交给人工。</p>
              </div>
              <span class="badge">低风险可自动</span>
            </header>
            <div class="demo-cards">
              <div class="demo-card"><small>客户消息</small><p>这件外套今天下单什么时候发？能不能帮我催一下？</p></div>
              <div class="demo-card"><small>AI 草稿</small><p>您好，这款商品当前正常发货。今天 18:00 前付款预计当天出库，物流揽收后我会继续跟进。</p></div>
              <div class="demo-card"><small>学习动作</small><p>客服修改话术后，系统记录为学习事件，后续相同问题优先复用。</p></div>
            </div>
            <div class="demo-flow"><span>消息进入</span><span>风险判断</span><span>生成草稿</span><span>人工确认</span><span>写入学习</span></div>
          </div>

          <div class="panel demo-panel" data-demo-panel="after-sale">
            <header>
              <div>
                <h3>AI 售后风险分级</h3>
                <p>系统把退款、退货、物流异常、投诉、赔偿统一变成售后 case。AI 只给判断和建议，高风险动作必须由老板或客服主管审批。</p>
              </div>
              <span class="badge warn">高风险必须审批</span>
            </header>
            <div class="demo-cards">
              <div class="demo-card"><small>售后类型</small><p>客户投诉物流超时，并要求赔偿 20 元优惠券。</p></div>
              <div class="demo-card"><small>AI 判断</small><p>物流责任待核实，涉及赔偿金额，标记为高风险，不允许自动承诺。</p></div>
              <div class="demo-card"><small>处理建议</small><p>先查询物流轨迹，再给老板审批：同意补偿、拒绝补偿或补充证据。</p></div>
            </div>
            <div class="demo-flow"><span>识别售后</span><span>判断责任</span><span>风险分级</span><span>审批建议</span><span>SOP 沉淀</span></div>
          </div>

          <div class="panel demo-panel" data-demo-panel="operation">
            <header>
              <div>
                <h3>AI 运营计划草稿</h3>
                <p>AI 运营不直接花钱，而是从客户咨询、订单和售后数据中找机会，生成私域获客话术、活动建议和投流计划草稿。</p>
              </div>
              <span class="badge">预算动作需审批</span>
            </header>
            <div class="demo-cards">
              <div class="demo-card"><small>发现机会</small><p>近 7 天多名客户反复咨询尺码、发货速度和搭配建议。</p></div>
              <div class="demo-card"><small>运营建议</small><p>生成“尺码顾问 + 快速发货”私域话术，并推荐小预算测试短视频素材。</p></div>
              <div class="demo-card"><small>老板边界</small><p>优惠、群发、投流预算必须审批，AI 只提交计划和理由。</p></div>
            </div>
            <div class="demo-flow"><span>识别线索</span><span>生成话术</span><span>形成投流草稿</span><span>老板审批</span><span>复盘效果</span></div>
          </div>

          <div class="panel demo-panel" data-demo-panel="approval">
            <header>
              <div>
                <h3>老板统一审批中心</h3>
                <p>所有退款、赔偿、预算、群发、客户数据导出等动作统一进入审批。老板看到的是 AI 给出的原因、风险和建议动作。</p>
              </div>
              <span class="badge warn">老板最终决定</span>
            </header>
            <div class="demo-cards">
              <div class="demo-card"><small>审批事项</small><p>物流投诉补偿 20 元优惠券，AI 建议先核实轨迹后再处理。</p></div>
              <div class="demo-card"><small>决策选项</small><p>同意、修改、拒绝、要求补充信息。</p></div>
              <div class="demo-card"><small>长期学习</small><p>老板最终处理结果写入 Memory 和 SOP，下次相似场景直接参考。</p></div>
            </div>
            <div class="demo-flow"><span>AI 建议</span><span>风险说明</span><span>老板审批</span><span>执行记录</span><span>经验沉淀</span></div>
          </div>
        </div>
      </div>
    </section>

    <section class="section" id="sandbox">
      <div class="section-inner">
        <div class="section-title">
          <span>Try It Now</span>
          <h2>商家不用登录，也能现场试一下 AI 客服和 AI 售后</h2>
          <p>这是展示页内置的试用沙盒。它不会连接真实店铺，也不会真的发送消息；它用安全规则演示 AI 如何生成客服回复、识别售后风险、判断是否需要老板审批。</p>
        </div>
        <div class="sandbox">
          <div class="sandbox-card">
            <h3>输入一条真实客户问题</h3>
            <p>可以直接复制商家客服聊天里的问题，例如“什么时候发货”“订单到哪了”“能不能退款”“物流超时要赔偿”。</p>
            <textarea id="sandbox-input">这件外套今天下单什么时候发？我明天要穿，能不能帮我催一下？</textarea>
            <div class="sandbox-actions">
              <button type="button" data-sandbox-action="customer">生成 AI 客服回复</button>
              <button class="secondary" type="button" data-sandbox-action="after-sale">判断售后风险</button>
              <button class="secondary" type="button" data-sandbox-action="sample">换一个高风险样例</button>
            </div>
          </div>
          <div class="sandbox-output">
            <small id="sandbox-mode">AI 客服试用结果</small>
            <h3 id="sandbox-title">低风险，可生成回复草稿</h3>
            <div class="sandbox-result" id="sandbox-result">您好，这款商品正常情况下今天 18:00 前付款会优先当天出库。您下单后我会继续帮您关注物流揽收情况。如果物流 24 小时没有更新，我会帮您转人工继续跟进。</div>
            <div class="sandbox-kpis">
              <span id="sandbox-kpi-1">风险等级：低</span>
              <span id="sandbox-kpi-2">建议动作：可自动草稿</span>
              <span id="sandbox-kpi-3">预计节省：4 分钟</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section" id="experience">
      <div class="section-inner">
        <div class="section-title">
          <span>Live Product</span>
          <h2>直接体验 AI Commerce OS 的完整操作过程</h2>
          <p>下面嵌入的是可操作的产品控制台。客户可以在宣传页里直接登录体验老板首页、AI客服、AI售后、AI运营、老板审批和数据导入，看到系统不是只停留在概念图。</p>
        </div>
        <div class="credential-grid">
          <div class="credential">体验账号<strong>boss@aicos.local</strong></div>
          <div class="credential">体验密码<strong>aicos2026</strong></div>
          <div class="credential">安全说明<strong>演示数据，不执行真实退款、投流或导出动作</strong></div>
        </div>
        <div class="experience-wrap">
          <div class="experience-bar">
            <div>
              <strong>AI Commerce OS 商家控制台</strong>
              <p>如果嵌入窗口显示较小，可以点击右侧按钮打开完整窗口。</p>
            </div>
            <a href="https://ai-commerce-os-internal.ybqes.chatgpt.site" target="_blank" rel="noreferrer">打开完整控制台</a>
          </div>
          <iframe
            class="experience-frame"
            loading="lazy"
            referrerpolicy="no-referrer"
            src="https://ai-commerce-os-internal.ybqes.chatgpt.site"
            title="AI Commerce OS 内部试用控制台"
          ></iframe>
        </div>
      </div>
    </section>

    <section class="section" id="trial">
      <div class="section-inner">
        <div class="section-title">
          <span>Pilot</span>
          <h2>7 天试用：先让 AI 跑起来，再看数据</h2>
          <p>试用期不追求全自动，先追求可验证：节省多少时间、减少多少人工判断、沉淀多少学习样本。</p>
        </div>
        <div class="grid steps">
          <div class="step"><b>1</b><p>导入商品、订单、客户、售后数据。</p></div>
          <div class="step"><b>2</b><p>AI 客服生成回复草稿，客服修正。</p></div>
          <div class="step"><b>3</b><p>AI 售后做风险分级和审批建议。</p></div>
          <div class="step"><b>4</b><p>AI 运营识别私域线索和投流草稿。</p></div>
          <div class="step"><b>5</b><p>每周复盘自动化率、错误率和节省工时。</p></div>
        </div>
      </div>
    </section>

    <section class="section muted">
      <div class="section-inner split">
        <div class="section-title">
          <span>Evaluation</span>
          <h2>用指标判断 AI 是否值得继续扩大使用</h2>
          <p>所有演示和试用都要回到同一件事：AI 有没有真正降低人工成本、减少风险、提高响应效率。</p>
        </div>
        <div class="metric-grid">
          <div class="metric">客服自动回复率</div>
          <div class="metric">客服错误率</div>
          <div class="metric">人工接管率</div>
          <div class="metric">售后分类准确率</div>
          <div class="metric">高风险拦截率</div>
          <div class="metric">私域线索数量</div>
          <div class="metric">运营建议采纳率</div>
          <div class="metric">节省人工分钟数</div>
        </div>
      </div>
    </section>

    <section class="cta">
      <h2>先用一家真实店铺验证降本</h2>
      <p>导入历史数据，跑 AI 客服和 AI 售后，收集修正样本，一周后用指标判断是否继续扩大自动化。</p>
      <a class="button" href="#experience">进入产品体验</a>
    </section>
  </main>
  <script>
    document.querySelectorAll("[data-demo-tab]").forEach((button) => {{
      button.addEventListener("click", () => {{
        const target = button.getAttribute("data-demo-tab");
        document.querySelectorAll("[data-demo-tab]").forEach((tab) => tab.classList.toggle("active", tab === button));
        document.querySelectorAll("[data-demo-panel]").forEach((panel) => panel.classList.toggle("active", panel.getAttribute("data-demo-panel") === target));
      }});
    }});

    const sandboxInput = document.getElementById("sandbox-input");
    const sandboxMode = document.getElementById("sandbox-mode");
    const sandboxTitle = document.getElementById("sandbox-title");
    const sandboxResult = document.getElementById("sandbox-result");
    const sandboxKpi1 = document.getElementById("sandbox-kpi-1");
    const sandboxKpi2 = document.getElementById("sandbox-kpi-2");
    const sandboxKpi3 = document.getElementById("sandbox-kpi-3");

    function hasAny(text, words) {{
      return words.some((word) => text.includes(word));
    }}

    function renderSandbox(mode, title, result, k1, k2, k3) {{
      sandboxMode.textContent = mode;
      sandboxTitle.textContent = title;
      sandboxResult.textContent = result;
      sandboxKpi1.textContent = k1;
      sandboxKpi2.textContent = k2;
      sandboxKpi3.textContent = k3;
    }}

    function customerReply() {{
      const text = sandboxInput.value.trim();
      if (!text) {{
        renderSandbox("AI 客服试用结果", "请输入客户问题", "请先在左侧输入客户咨询内容。", "风险等级：未知", "建议动作：等待输入", "预计节省：0 分钟");
        return;
      }}
      if (hasAny(text, ["退款", "退货", "赔", "补偿", "投诉", "差评", "仅退款", "威胁"])) {{
        renderSandbox(
          "AI 客服试用结果",
          "高风险，必须人工接管",
          "这个问题涉及退款、赔偿、投诉或差评风险，AI 不能自动承诺金额或处理结果。建议回复：您好，我已经看到您的问题，这类情况需要商家确认后处理。我会先为您登记并转人工核实订单、物流和商品情况，确认后给您明确处理方案。",
          "风险等级：高",
          "建议动作：人工确认",
          "预计节省：避免错误承诺"
        );
        return;
      }}
      if (hasAny(text, ["发货", "物流", "到哪", "快递", "催"])) {{
        renderSandbox(
          "AI 客服试用结果",
          "低风险，可生成回复草稿",
          "您好，正常情况下当天 18:00 前付款会优先当天出库。您下单后我会继续帮您关注物流揽收情况。如果物流 24 小时没有更新，我会帮您转人工继续跟进。",
          "风险等级：低",
          "建议动作：可自动草稿",
          "预计节省：4 分钟"
        );
        return;
      }}
      if (hasAny(text, ["尺码", "大小", "身高", "体重", "合适"])) {{
        renderSandbox(
          "AI 客服试用结果",
          "低风险，可生成尺码建议",
          "您好，尺码建议优先参考商品详情页尺码表。如果您方便提供身高、体重和喜欢宽松还是合身，我可以帮您进一步建议；如介于两个尺码之间，建议优先选择大一码。",
          "风险等级：低",
          "建议动作：可自动草稿",
          "预计节省：3 分钟"
        );
        return;
      }}
      renderSandbox(
        "AI 客服试用结果",
        "中风险，建议人工确认后学习",
        "这个问题没有命中明确知识。建议先由客服确认标准答案，确认后的回复会进入学习记录，下次类似问题可自动生成草稿。",
        "风险等级：中",
        "建议动作：人工确认并学习",
        "预计节省：下次生效"
      );
    }}

    function afterSaleCheck() {{
      const text = sandboxInput.value.trim();
      if (!text) {{
        renderSandbox("AI 售后试用结果", "请输入售后问题", "请先在左侧输入退款、退货、投诉或物流异常内容。", "风险等级：未知", "建议动作：等待输入", "预计节省：0 分钟");
        return;
      }}
      if (hasAny(text, ["赔", "补偿", "投诉", "差评", "平台介入", "威胁"])) {{
        renderSandbox(
          "AI 售后试用结果",
          "高风险售后，必须老板审批",
          "判断：涉及赔偿、投诉或平台风险，AI 只能给处理建议，不能自动承诺。建议流程：1. 查询订单和物流；2. 收集图片或凭证；3. 给出补偿/拒绝/补证三个选项；4. 老板确认后再回复客户。",
          "风险等级：高",
          "建议动作：老板审批",
          "预计节省：12 分钟"
        );
        return;
      }}
      if (hasAny(text, ["退款", "退货", "不想要", "七天"])) {{
        renderSandbox(
          "AI 售后试用结果",
          "中风险售后，需要人工确认",
          "判断：这是退款/退货类问题，AI 可以先说明流程，但不能自动同意退款。建议回复客户先提交申请并保留商品状态，客服核实订单后处理。",
          "风险等级：中",
          "建议动作：人工确认",
          "预计节省：8 分钟"
        );
        return;
      }}
      renderSandbox(
        "AI 售后试用结果",
        "低风险说明，可生成流程回复",
        "判断：当前更像普通流程咨询。AI 可以回复售后流程说明，但如后续涉及金额、退款、赔偿，需要转人工审批。",
        "风险等级：低",
        "建议动作：流程说明",
        "预计节省：5 分钟"
      );
    }}

    document.querySelectorAll("[data-sandbox-action]").forEach((button) => {{
      button.addEventListener("click", () => {{
        const action = button.getAttribute("data-sandbox-action");
        if (action === "sample") {{
          sandboxInput.value = "物流已经超时两天了，我要投诉，还要你们赔偿，不然我就给差评。";
          afterSaleCheck();
          return;
        }}
        if (action === "after-sale") {{
          afterSaleCheck();
          return;
        }}
        customerReply();
      }});
    }});
  </script>
</body>
</html>"""


def main() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    if ARCHIVE_PATH.exists():
        ARCHIVE_PATH.unlink()

    (OUT_DIR / ".openai").mkdir(parents=True, exist_ok=True)
    image_data_url = "data:image/png;base64," + base64.b64encode(HERO_IMAGE.read_bytes()).decode("ascii")

    # Sites 支持 vinext 风格入口，这里直接返回静态 HTML，避免线上安装任何前端依赖。
    worker = f"""const HTML = {json.dumps(build_html(image_data_url), ensure_ascii=False)};

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
