import Image from "next/image";

const costs = [
  ["客服", "售前咨询、订单查询、物流追踪、催付转化"],
  ["售后", "退款退货、投诉分级、异常物流、赔偿初筛"],
  ["运营", "客户线索、私域话术、投流计划、活动复盘"]
];

const agents = [
  ["AI客服", "自动处理 FAQ、订单、物流等低风险问题；不会的问题交给人工，并记录修改。"],
  ["AI售后", "识别退款、退货、投诉和异常物流，输出风险等级和审批建议。"],
  ["AI运营", "识别高意向客户，生成私域话术和投流计划草稿，预算动作必须审批。"]
];

const demoRows = [
  ["客户咨询", "这件外套今天下单什么时候发？", "AI 判断为物流低风险，生成回复草稿"],
  ["售后投诉", "物流超时要求赔偿", "AI 标记高风险，必须老板审批"],
  ["运营线索", "7 天内多次咨询尺码和发货", "AI 生成私域引导话术和投流草稿"],
  ["老板审批", "退款、赔偿、预算、群发", "统一进入审批，记录决策依据"]
];

const metrics = [
  "客服自动回复率",
  "客服错误率",
  "人工接管率",
  "售后分类准确率",
  "高风险拦截率",
  "私域线索数量",
  "运营建议采纳率",
  "节省人工分钟数"
];

export default function Page() {
  return (
    <main>
      <section className="hero">
        <Image
          alt="AI Commerce OS 商务运营中枢"
          className="heroImage"
          fill
          priority
          src="/marketing/ai-commerce-os-b2b-hero.png"
        />
        <div className="heroOverlay" />
        <nav className="nav">
          <strong>AI Commerce OS</strong>
          <div>
            <a href="#product">产品说明</a>
            <a href="#demo">演示界面</a>
            <a href="#trial">试用流程</a>
          </div>
        </nav>
        <div className="heroContent">
          <span className="eyebrow">面向电商企业的 AI 员工操作系统</span>
          <h1>让老板拥有一支可审批、可追踪、可学习的 AI 电商团队</h1>
          <p>
            从 AI客服、AI售后、AI运营三个岗位开始，把重复、标准化、可审批的工作交给 AI，目标逐步替代约 4 万元/月基础人力成本。
          </p>
          <div className="heroActions">
            <a href="#demo">查看演示界面</a>
            <a href="#trial">了解 7 天试用</a>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="sectionHeader">
          <span>Cost Reduction</span>
          <h2>企业真正要买的不是 AI，而是可验证的降本结果</h2>
          <p>AI Commerce OS 优先处理电商团队中重复、标准化、可审批的工作，先省时间，再省人。</p>
        </div>
        <div className="costGrid">
          {costs.map(([title, desc]) => (
            <article className="card" key={title}>
              <small>高频重复工作</small>
              <h3>{title}</h3>
              <p>{desc}</p>
            </article>
          ))}
          <article className="card darkCard">
            <small>目标替代成本</small>
            <strong>约 4 万/月</strong>
            <p>用真实数据验证 AI 能先替代多少重复工作，再逐步扩大自动化比例。</p>
          </article>
        </div>
      </section>

      <section className="section muted" id="product">
        <div className="split">
          <div className="sectionHeader">
            <span>Product</span>
            <h2>不是聊天机器人，也不是传统 ERP</h2>
            <p>它是一套 AI 电商员工控制台：AI 负责执行低风险工作，老板负责关键审批，系统负责记录和学习。</p>
          </div>
          <div className="featureList">
            {["AI员工化：每个 AI 都有职责、权限、工作记录和评估指标。", "审批优先：退款、赔偿、预算、投流和客户数据动作必须进入审批。", "数据验证：通过 Dataset、Replay 和 Evaluation 验证 AI 是否真的能工作。"].map((item) => (
              <div className="feature" key={item}>{item}</div>
            ))}
          </div>
        </div>
      </section>

      <section className="section">
        <div className="sectionHeader">
          <span>AI Employees</span>
          <h2>三个 AI 员工，先接管最容易标准化的工作</h2>
          <p>当前聚焦客服、售后、运营，不继续堆更多 Agent。目标是先证明可节省时间和成本。</p>
        </div>
        <div className="agentGrid">
          {agents.map(([title, desc]) => (
            <article className="card agent" key={title}>
              <div className="agentIcon" />
              <h3>{title}</h3>
              <p>{desc}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section muted" id="demo">
        <div className="sectionHeader">
          <span>Demo</span>
          <h2>演示界面：看 AI 如何工作，而不是只看概念</h2>
          <p>演示数据为静态样例，用来说明产品流程。真实上线后会接入商家订单、客户、售后和运营数据。</p>
        </div>
        <div className="demoBoard">
          {demoRows.map(([title, input, output]) => (
            <div className="demoRow" key={title}>
              <strong>{title}</strong>
              <span>{input}</span>
              <p>{output}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section" id="trial">
        <div className="sectionHeader">
          <span>Pilot</span>
          <h2>7 天试用：先让 AI 跑起来，再看数据</h2>
          <p>试用期不追求全自动，先追求可验证：节省多少时间、减少多少人工判断、沉淀多少学习样本。</p>
        </div>
        <div className="steps">
          {["导入商品、订单、客户、售后数据", "AI客服生成回复草稿，客服修正", "AI售后做风险分级和审批建议", "AI运营识别私域线索和投流草稿", "每周复盘自动化率、错误率和节省工时"].map((step, index) => (
            <div className="step" key={step}>
              <b>{index + 1}</b>
              <p>{step}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section muted">
        <div className="split">
          <div className="sectionHeader">
            <span>Evaluation</span>
            <h2>用指标判断 AI 是否值得继续扩大使用</h2>
            <p>所有演示和试用都要回到同一件事：AI 有没有真正降低人工成本、减少风险、提高响应效率。</p>
          </div>
          <div className="metricGrid">
            {metrics.map((metric) => <div className="metric" key={metric}>{metric}</div>)}
          </div>
        </div>
      </section>

      <section className="cta">
        <h2>先用一家真实店铺验证降本</h2>
        <p>导入历史数据，跑 AI客服和 AI售后，收集修改样本，一周后用指标判断是否继续扩大自动化。</p>
        <a href="#demo">查看演示流程</a>
      </section>
    </main>
  );
}
