import { useEffect, useRef } from "react";
import * as THREE from "three";
import {
  ArrowUpRight,
  Bot,
  BrainCircuit,
  Brush,
  Cpu,
  ExternalLink,
  Layers3,
  Mail,
  MapPin,
  MessageCircleHeart,
  MousePointer2,
  Phone,
  Sparkles,
  Workflow,
  Zap
} from "lucide-react";
import { LiquidChrome } from "./LiquidChrome";
import { BorderGlow } from "./BorderGlow";
import { MagicRings } from "./MagicRings";
import { FluidGlass } from "./FluidGlass";

const phoneNumber = "19571023940";
const emailAddress = "2984952331@qq.com";

const stats = [
  { value: "AI", label: "应用创作主线" },
  { value: "18", label: "岁 / 武汉" },
  { value: "MVP", label: "快速原型实践" },
  { value: "Web", label: "页面搭建与设计" }
];

const featuredProjects = [
  {
    title: "情绪翻译器",
    tag: "AI 应用 / 情绪理解 / 交互设计",
    description: "把模糊情绪翻译成可表达、可沟通、可行动的语言，面向个人表达与关系沟通场景。",
    metrics: ["情绪识别", "表达重写", "AI 交互"],
    visual: "emotion",
    images: ["emotion-mark-transparent.png", "emotion-app.png"],
    url: "http://175.24.197.102/",
    readOnly: true
  },
  {
    title: "AI Commerce OS",
    tag: "AI 应用 / 电商运营系统",
    description: "围绕商家运营、客服协作、数据导入和 AI 员工工作台搭建的完整产品表达。",
    metrics: ["多模块", "工作台", "AI 员工"],
    visual: "commerce",
    image: "ai-commerce-os.png",
    url: "https://ai-commerce-os-demo.ybqes.chatgpt.site"
  },
  {
    title: "B2B Marketing Deck",
    tag: "商业表达 / 视觉叙事",
    description: "把产品能力转译成面向客户的销售材料、路演结构和品牌化首屏视觉。",
    metrics: ["路演", "提案", "销售素材"],
    visual: "deck"
  }
];

const hiddenProjects = [
  {
    title: "AI + 实体落地探索",
    tag: "原型 / 硬件辅助 / 场景实验",
    description: "关注 AI 辅助硬件、线下设备与真实空间结合，让智能能力进入具体流程。",
    metrics: ["实体场景", "Demo", "验证"],
    visual: "hardware"
  },
  {
    title: "网页搭建设计实验",
    tag: "Web Design / 交互原型",
    description: "围绕暗色科技感、首屏叙事、产品卡片和动效体验做快速页面搭建。",
    metrics: ["React", "Vite", "视觉系统"],
    visual: "web"
  }
];

const strengths = [
  {
    icon: Bot,
    title: "AI 应用构建",
    text: "围绕任务拆解、工具调用、知识整理和自动化流程，把 AI 能力做成可操作的产品。"
  },
  {
    icon: Brush,
    title: "视觉与页面设计",
    text: "美术生背景带来的审美判断，能把界面、演示材料和品牌感控制在同一个气质里。"
  },
  {
    icon: Workflow,
    title: "从想法到原型",
    text: "擅长用低成本方式快速做出 MVP、Demo 和可演示页面，帮助想法进入验证阶段。"
  },
  {
    icon: Cpu,
    title: "AI + 硬件场景",
    text: "持续关注 AI 辅助硬件、实体空间和真实业务流程的结合，而不只停留在屏幕演示。"
  }
];

const experience = [
  "18 岁，来自湖北武汉，美术生背景，同时长期实践 AI 应用开发与创业项目。",
  "身份定位是 AI 应用创作者、AI 设计师、网页搭建设计师。",
  "关注 AI 辅助硬件、实体场景落地、黑客松协作和年轻创业项目实践。",
  "擅长把一个模糊想法快速推进到可展示、可体验、可继续迭代的原型。"
];

const emotionReadOnlyUrl = "http://175.24.197.102/";

const creatorMarqueeItems = [
  {
    title: "我做的电商产品项目",
    subtitle: "产品介绍图 / 点击查看",
    cover: "nature",
    url: emotionReadOnlyUrl,
    readOnly: true
  },
  {
    title: "情绪翻译器",
    subtitle: "AI 交互应用",
    src: "emotion-mark-transparent.png",
    url: emotionReadOnlyUrl,
    readOnly: true
  },
  {
    title: "AI Commerce OS",
    subtitle: "电商运营系统",
    src: "ai-commerce-os.png",
    url: "https://ai-commerce-os-demo.ybqes.chatgpt.site"
  },
  {
    title: "只读体验入口",
    subtitle: "访客可看不可改",
    src: "ai-commerce-console.png",
    url: emotionReadOnlyUrl,
    readOnly: true
  },
  {
    title: "网页搭建设计",
    subtitle: "React / Vite / 视觉系统",
    src: "orven-cover.png",
    url: "#strengths"
  }
];

const creatorServices = [
  {
    number: "01",
    icon: Bot,
    title: "AI 应用构建",
    text: "把任务拆解、工具调用、知识整理和自动化流程组合成可真实使用的 AI 产品。"
  },
  {
    number: "02",
    icon: Sparkles,
    title: "视觉系统与页面设计",
    text: "用更克制的版式、材质、动效和品牌秩序，让界面、演示材料与产品气质保持一致。"
  },
  {
    number: "03",
    icon: Workflow,
    title: "从想法到原型",
    text: "用低成本方式快速做出 MVP、Demo 和可演示页面，让想法尽快进入验证。"
  },
  {
    number: "04",
    icon: Cpu,
    title: "AI + 实体场景",
    text: "关注 AI 辅助硬件、线下设备和真实业务流程的结合，而不是只停留在屏幕演示。"
  },
  {
    number: "05",
    icon: Layers3,
    title: "商业展示与叙事",
    text: "把产品能力翻译成客户能理解的首页、路演材料、案例页面和销售表达。"
  }
];

const creatorProjects = [
  {
    number: "01",
    title: "情绪翻译器",
    category: "AI 应用 / 交互设计",
    summary: "把模糊情绪翻译成可表达、可沟通、可行动的语言，面向个人表达与关系沟通场景。",
    images: ["emotion-mark-transparent.png", "emotion-app.png"],
    url: emotionReadOnlyUrl,
    readOnly: true
  },
  {
    number: "02",
    title: "AI Commerce OS",
    category: "AI 应用 / 电商运营系统",
    summary: "从 AI 客服、AI 售后、AI 运营三个岗位切入，把重复、标准化、可审批的工作交给 AI。",
    compactImage: "ai-commerce-console.png",
    visual: "pilot",
    url: "https://ai-commerce-os-demo.ybqes.chatgpt.site"
  },
  {
    number: "03",
    title: "节约电商 4w+",
    category: "AI 电商提效 / 商业验证",
    summary: "面向中小电商企业，把 AI 客服、AI 售后、AI 运营等重复岗位工作拆成可审批、可追踪、可学习的自动化流程。",
    compactImage: "ai-commerce-os.png",
    visual: "saving",
    url: "#contact"
  }
];

const teamProfiles = [
  {
    badge: "Founder / Main Field",
    name: "闵怡强",
    role: "AI 创业者 / AI Agent 产品负责人",
    location: "湖北武汉 / AI 电商 Agent / 工业 AI",
    intro:
      "专注 AI Agent 在真实企业中的落地，正在推进面向中小电商企业的 AI 自动化运营系统，把客服、售后、运营、知识库和 SOP 流程做成可验证的 AI 工作流。",
    focus: ["AI 电商 Agent", "Workflow Automation", "企业知识库", "Multi-Agent", "真实商家调研"],
    stats: [
      { value: "Founder", label: "AI 电商 Agent 发起人" },
      { value: "4w+", label: "目标替代月度基础人力成本" },
      { value: "0-1", label: "产品架构 / Demo / 试点推进" },
      { value: "AI", label: "客服 / 售后 / 运营多 Agent 协同" }
    ],
    highlights: [
      "自主设计并推进 AI 电商 Agent 系统，覆盖 AI 客服、AI 售后、工单管理、商品知识库、企业知识库和 SOP 自动执行。",
      "长期研究 AI Agent、Workflow Automation、LLM 应用、工业 AI 和 Physical AI，关注 AI 如何进入真实企业生产流程。",
      "具备从产品规划、需求分析、Prompt Engineering、Agent 流程设计到 MVP 验证和用户访谈的完整推进能力。",
      "持续与实体企业、电商企业和产业资源交流，验证真实需求、付费意愿、交付难度和 AI SaaS 商业化路径。"
    ]
  },
  {
    badge: "Product / Business",
    name: "李俊杰",
    role: "AI 产品实习生方向 / 产品运营与商业运营",
    location: "江苏海洋大学 / 国际经济与贸易本科在读",
    intro:
      "具备 AI 产品从需求识别、功能设计、原型开发、服务器部署到用户内测和迭代优化的完整实践经验，擅长把模糊想法转化为可上线、可测试、可复盘的产品。",
    focus: ["弦外 AI 情绪产品", "OCR + DeepSeek", "用户内测", "商业场景观察", "客户触达"],
    stats: [
      { value: "0-1", label: "独立完成弦外设计开发上线" },
      { value: "OCR", label: "聊天截图识别与情绪分析" },
      { value: "PM2", label: "Ubuntu / Nginx / PM2 部署" },
      { value: "商业", label: "电商服务 / 家庭教育 / 社区商业研究" }
    ],
    highlights: [
      "独立完成 AI 情绪与关系分析产品「弦外」，覆盖产品定位、场景拆解、提示词设计、前后端开发和用户内测。",
      "围绕 OCR 识别、隐私安全、表达质量、上下文理解和产品定价收集真实用户反馈，并设计后续迭代方案。",
      "研究企业 AI 服务与电商视觉提效，设计免费试做、客户筛选、批量触达和低成本试点验证路径。",
      "接触家庭教育高客单转化、电商企业服务、物业社区商业等真实场景，对需求、信任和销售决策有持续观察。"
    ]
  },
  {
    badge: "AI Builder / Research",
    name: "胡卓涵",
    role: "AI 产品与创业项目成员",
    location: "南京 / AI 原型 / 数据与自动化",
    intro:
      "战略管理硕士背景，长期做数据分析、AI 产品原型和自动化工具，把业务需求拆成可上线、可验证、可复用的系统。",
    focus: ["AI Agent 审核", "OCR + LLM", "创业型全栈", "数据爬虫", "商业分析"],
    stats: [
      { value: "95%+", label: "AI 审核准确率目标" },
      { value: "5 min", label: "单文件审核提效" },
      { value: "98%+", label: "OCR 识别准确率" },
      { value: "1000+", label: "酒店竞品数据覆盖" }
    ],
    highlights: [
      "核心开发 AI 知识产权智能审核系统，覆盖文档解析、风险检测、合规评估与审核结果输出。",
      "负责法律文件智能识别工具，整合 OCR、LLM 文本处理和模板生成，面向律师及企业法务场景。",
      "独立开发小六壬智能排盘系统，完成 Flask 后端、前端交互、云服务器部署与算法逻辑。",
      "搭建酒店竞品爬虫与分析系统，将采集、清洗、维度分析和经营报告串成数据闭环。"
    ]
  }
];

export function App() {
  return (
    <main className="creatorPage">
      <GlobalMouseGlass />
      <CreatorHero />
      <CreatorMarquee />
      <CreatorAbout />
      <CreatorTeam />
      <CreatorServices />
      <CreatorProjects />
      <CreatorContact />
    </main>
  );
}

function CreatorContactButton({ href = "#contact", label = "Contact Me" }: { href?: string; label?: string }) {
  return (
    <a className="creatorContactButton" href={href}>
      <span>{label}</span>
      <ArrowUpRight size={18} />
    </a>
  );
}

function GlobalMouseGlass() {
  const lensRef = useRef<HTMLDivElement>(null);
  const cloneHostRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const lens = lensRef.current;
    const cloneHost = cloneHostRef.current;
    const source = document.querySelector(".creatorPage");
    if (!lens || !cloneHost || !source) return undefined;

    const sourceClone = source.cloneNode(true) as HTMLElement;
    sourceClone.querySelector(".globalMouseGlassLens")?.remove();
    sourceClone.classList.add("globalMouseGlassPageClone");
    sourceClone.setAttribute("aria-hidden", "true");
    cloneHost.replaceChildren(sourceClone);

    const scale = 1.18;
    let targetX = window.innerWidth * 0.5;
    let targetY = window.innerHeight * 0.48;
    let currentX = targetX;
    let currentY = targetY;
    let rafId = 0;

    const render = () => {
      currentX += (targetX - currentX) * 0.22;
      currentY += (targetY - currentY) * 0.22;

      const rect = lens.getBoundingClientRect();
      const lensWidth = rect.width || 240;
      const lensHeight = rect.height || 160;
      const pageX = currentX + window.scrollX;
      const pageY = currentY + window.scrollY;

      lens.style.left = `${currentX}px`;
      lens.style.top = `${currentY}px`;
      sourceClone.style.width = `${Math.max(document.documentElement.scrollWidth, window.innerWidth)}px`;
      sourceClone.style.transform = `translate3d(${lensWidth / 2 - pageX * scale}px, ${lensHeight / 2 - pageY * scale}px, 0) scale(${scale})`;

      rafId = window.requestAnimationFrame(render);
    };

    const handlePointerMove = (event: PointerEvent) => {
      targetX = event.clientX;
      targetY = event.clientY;
      lens.classList.add("is-active");
    };

    const handlePointerLeave = () => {
      lens.classList.remove("is-active");
    };

    window.addEventListener("pointermove", handlePointerMove, { passive: true });
    window.addEventListener("pointerleave", handlePointerLeave);
    rafId = window.requestAnimationFrame(render);

    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerleave", handlePointerLeave);
      window.cancelAnimationFrame(rafId);
    };
  }, []);

  return (
    <div className="globalMouseGlassLens" ref={lensRef} aria-hidden="true">
      <div className="globalMouseGlassCloneHost" ref={cloneHostRef} />
      <span className="globalMouseGlassEdge" />
      <span className="globalMouseGlassCaustic" />
    </div>
  );
}
function CreatorHero() {
  return (
    <section className="creatorHero" id="top">
      <GeneratedVideoBackground />
      <div className="creatorHeroChrome">
        <LiquidChrome
          amplitude={0.38}
          baseColor={[0.125, 0.216, 0.839]}
          frequencyX={2.2}
          frequencyY={1.6}
          interactive
          speed={0.28}
        />
      </div>
      <nav className="creatorNav" aria-label="主导航">
        <a href="#profile">关于</a>
        <a href="#team">团队</a>
        <a href="#strengths">能力</a>
        <a href="#projects">项目</a>
        <a href="#contact">联系</a>
        <FluidGlass variant="nav" />
      </nav>

      <div className="creatorHeroTitle" aria-label="首页标题">
        <span>MIN</span>
        <span>PROJECTS</span>
      </div>


      <div className="creatorHeroObject">
        <ScrollEarth />
      </div>

      <div className="creatorHeroBottom">
        <p>这里展示我做过的 AI 与电商产品项目，包括产品介绍图、交互原型、网页搭建和商业化展示表达。</p>
        <CreatorContactButton href="#projects" label="查看项目" />
      </div>
    </section>
  );
}

function CreatorMarquee() {
  const firstRow = [...creatorMarqueeItems, ...creatorMarqueeItems];
  const secondRow = [...creatorMarqueeItems].reverse().concat([...creatorMarqueeItems].reverse());

  return (
    <section className="creatorMarquee" aria-label="作品动态带">
      <div className="marqueeTrack moveRight">
        {firstRow.map((item, index) => (
          <CreatorMarqueeTile item={item} key={`${item.title}-a-${index}`} />
        ))}
      </div>
      <div className="marqueeTrack moveLeft">
        {secondRow.map((item, index) => (
          <CreatorMarqueeTile item={item} key={`${item.title}-b-${index}`} />
        ))}
      </div>
    </section>
  );
}

function CreatorMarqueeTile({ item }: { item: (typeof creatorMarqueeItems)[number] }) {
  const href = "url" in item && item.url ? item.url : "#projects";
  const target = href.startsWith("http") ? "_blank" : undefined;

  return (
    <a className="marqueeTile" href={href} rel="noreferrer" target={target}>
      {"src" in item && item.src ? (
        <img alt="" src={item.src} />
      ) : "cover" in item && item.cover ? (
        <PremiumProductCover mode={String(item.cover)} />
      ) : (
        <div className={`marqueeMock ${"visual" in item ? item.visual : "web"}`}>
          <Layers3 size={44} />
        </div>
      )}
      <FluidGlass />
      <span>{item.title}</span>
      {"subtitle" in item && item.subtitle ? <small>{item.subtitle}</small> : null}
    </a>
  );
}

function PremiumProductCover({ mode = "showcase" }: { mode?: string }) {
  if (mode === "nature") {
    return (
      <div className="natureProductCover" aria-hidden="true">
        <div className="natureCopy">
          <strong>The Power of</strong>
          <strong>Nature in Every</strong>
          <strong>Capsule</strong>
        </div>
        <div className="natureBottle">
          <span>HerraFit</span>
          <i />
          <i />
          <i />
        </div>
        <div className="natureFern fernOne" />
        <div className="natureFern fernTwo" />
        <div className="naturePanel">
          <b>电商产品网页图</b>
          <small>产品介绍页 / 点击查看</small>
        </div>
        <div className="natureMetric">
          <b>+14K</b>
          <small>optimized wellness</small>
        </div>
      </div>
    );
  }

  return (
    <div className={`premiumProductCover ${mode}`} aria-hidden="true">
      <div className="coverRings">
        <MagicRings
          attenuation={8}
          baseRadius={0.2}
          color="#2037d6"
          colorTwo="#5f7cff"
          lineThickness={1.6}
          opacity={0.88}
          radiusStep={0.085}
          ringCount={7}
          rotation={-18}
          speed={0.58}
        />
      </div>
      <div className="coverTopline">
        <i />
        <i />
        <i />
      </div>
      <div className="coverBadge">{mode === "readonly" ? "READ ONLY" : "MY PROJECT"}</div>
      <div className="coverDevice">
        <div className="coverScreen">
          <span />
          <span />
          <span />
        </div>
        <div className="coverAction">
          <MessageCircleHeart size={22} />
          <b>{mode === "readonly" ? "只读体验" : "电商产品项目"}</b>
        </div>
      </div>
      <div className="coverGlowOrb" />
    </div>
  );
}

function CreatorAbout() {
  return (
    <section className="creatorAbout" id="profile">
      <div className="floatObject moon">AI</div>
      <div className="floatObject cube">UX</div>
      <div className="floatObject chip">WEB</div>
      <div className="floatObject orb">MVP</div>
      <div className="creatorSectionCenter">
        <p className="creatorKicker">About me</p>
        <h2>我做的项目</h2>
        <p className="creatorRevealText">
          这里集中展示我做过的 AI 与电商产品项目。我的目标不是只做一张漂亮页面，而是把一个模糊想法推进到可展示、可体验、可继续迭代的真实产品状态。
        </p>
        <CreatorContactButton href="#contact" label="直接联系" />
      </div>
    </section>
  );
}

function CreatorTeam() {
  return (
    <section className="creatorTeam" id="team">
      <div className="creatorWide">
        <div className="teamHeader">
          <p className="creatorKicker">Team</p>
          <h2>AI 创业团队能力</h2>
          <p>
            这里不是传统简历陈列，而是把成员经历转译成项目协作时真正有用的能力：AI 产品判断、全栈落地、数据抓取、业务分析和创业执行。
          </p>
        </div>

        <div className="teamDeck">
          {teamProfiles.map((member, index) => (
            <article className={`teamProfileCard${index === 0 ? " primary" : ""}`} key={member.name}>
              <div className="teamIdentity">
                <div className="teamAvatar" aria-hidden="true">
                  <BrainCircuit size={42} />
                </div>
                <div>
                  <span>{member.badge}</span>
                  <h3>{member.name}</h3>
                  <p>{member.role}</p>
                </div>
              </div>

              <p className="teamIntro">{member.intro}</p>

              <div className="teamFocus">
                {member.focus.map((item) => (
                  <span key={item}>{item}</span>
                ))}
              </div>

              <div className="teamStats">
                {member.stats.map((item) => (
                  <div key={item.label}>
                    <strong>{item.value}</strong>
                    <span>{item.label}</span>
                  </div>
                ))}
              </div>

              <div className="teamLocation">
                <MapPin size={17} />
                <span>{member.location}</span>
              </div>
              <FluidGlass variant="soft" />
            </article>
          ))}

          <div className="teamOptionGrid">
            {teamProfiles[0].highlights.map((item, index) => (
              <div className="teamOptionCard" key={item}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <p>{item}</p>
                <FluidGlass variant="soft" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function CreatorServices() {
  return (
    <section className="creatorServices" id="strengths">
      <div className="creatorWide">
        <h2>Services</h2>
        <div className="serviceList">
          {creatorServices.map((item) => {
            const Icon = item.icon;
            return (
              <article className="serviceItem" key={item.title}>
                <strong>{item.number}</strong>
                <div className="serviceIcon">
                  <Icon size={26} />
                </div>
                <div>
                  <h3>{item.title}</h3>
                  <p>{item.text}</p>
                </div>
                <FluidGlass variant="soft" />
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function CreatorProjects() {
  return (
    <section className="creatorProjects" id="projects">
      <div className="creatorWide">
        <h2>Project</h2>
        <div className="stackedProjects">
          {creatorProjects.map((project, index) => (
            <CreatorProjectCard index={index} key={project.title} project={project} />
          ))}
        </div>
      </div>
    </section>
  );
}

function CreatorProjectCard({
  index,
  project
}: {
  index: number;
  project: (typeof creatorProjects)[number];
}) {
  return (
    <article className="stackProjectShell" style={{ top: `${112 + index * 28}px` }}>
      <div className="stackProjectCard" style={{ transform: `scale(${1 - (creatorProjects.length - index - 1) * 0.025})` }}>
        <div className="stackProjectMeta">
          <strong>{project.number}</strong>
          <span>{project.category}</span>
          <h3>{project.title}</h3>
          <a href={project.url} rel="noreferrer" target={project.url.startsWith("http") ? "_blank" : undefined}>
            {"readOnly" in project && project.readOnly ? "只读体验" : "Live Project"}
            <ArrowUpRight size={17} />
          </a>
        </div>
        <div className="stackProjectVisuals">
          <div className="projectColumn">
            <CreatorProjectPreview compact project={project} />
            <p>{project.summary}</p>
          </div>
          <CreatorProjectPreview project={project} />
        </div>
        <FluidGlass />
      </div>
    </article>
  );
}

function CreatorProjectPreview({
  compact = false,
  project
}: {
  compact?: boolean;
  project: (typeof creatorProjects)[number];
}) {
  if (compact && "compactImage" in project && project.compactImage) {
    const compactSrc = String(project.compactImage);

    return (
      <div className="projectPreview compact">
        <img alt="" src={compactSrc} />
      </div>
    );
  }

  if ("visual" in project && project.visual === "pilot") {
    const steps = [
      "导入商品、订单、客户、售后数据。",
      "AI 客服生成回复草稿，客服修正。",
      "AI 售后做风险分级和审批建议。",
      "AI 运营识别私域线索和投诉草稿。",
      "每周复盘自动化率、错误率和节省工时。"
    ];

    return (
      <div className={compact ? "projectPreview compact pilotTrial" : "projectPreview tall pilotTrial"}>
        <div className="pilotCanvas">
          <span>Pilot</span>
          <h4>7 天试用：先让 AI 跑起来，再看数据</h4>
          <p>试用期不追求全自动，先追求可验证：节省多少时间、减少多少人工判断、沉淀多少学习样本。</p>
          <div className="pilotStepGrid">
            {steps.map((step, index) => (
              <div className="pilotStep" key={step}>
                <strong>{index + 1}</strong>
                <p>{step}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if ("visual" in project && project.visual === "saving") {
    return (
      <div className={compact ? "projectPreview compact savingArt" : "projectPreview tall savingArt"}>
        <span>节约</span>
        <strong>4w+</strong>
        <small>电商月度基础人力成本</small>
      </div>
    );
  }

  if ("images" in project && project.images) {
    if (compact) {
      const src = project.images[0];
      return (
        <div className="projectPreview compact">
          <img alt="" src={src} />
        </div>
      );
    }

    const src = project.images[1];
    return (
      <div className={compact ? "projectPreview compact" : "projectPreview tall"}>
        <img alt="" src={src} />
      </div>
    );
  }

  if ("image" in project && project.image) {
    const imageSrc = String(project.image);

    return (
      <div className={compact ? "projectPreview compact" : "projectPreview tall"}>
        <img alt="" src={imageSrc} />
      </div>
    );
  }

  return (
    <div className={compact ? "projectPreview compact mock" : "projectPreview tall mock"}>
      <div className="mockOrb">
        <Layers3 size={42} />
      </div>
      <div className="mockLines">
        <span />
        <span />
        <span />
      </div>
    </div>
  );
}

function CreatorContact() {
  return (
    <section className="creatorContact" id="contact">
      <div className="creatorWide contactStack">
        <div>
          <p className="creatorKicker">Contact</p>
          <h2>让下一个 AI 项目进入真实场景</h2>
          <p>适合聊 AI 应用、AI 辅助硬件、网页搭建、黑客松、创意技术、项目合作和第一版产品原型。</p>
          <div className="contactActions">
            <a className="creatorContactButton" href={`tel:${phoneNumber}`}>
              <span>联系</span>
            </a>
            <a className="creatorGhostButton" href="#top">Back to top</a>
          </div>
        </div>
        <div className="creatorContactCard">
          <div className="contactCardHeader">
            <span>MIN / 闵怡强</span>
            <ExternalLink size={18} />
          </div>
          <dl>
            <div>
              <dt>姓名</dt>
              <dd>闵怡强</dd>
            </div>
            <div>
              <dt>电话 / 飞书手机号</dt>
              <dd>{phoneNumber}</dd>
            </div>
            <div>
              <dt>邮箱</dt>
              <dd>{emailAddress}</dd>
            </div>
            <div>
              <dt>地点</dt>
              <dd>湖北武汉</dd>
            </div>
            <div>
              <dt>身份</dt>
              <dd>AI 应用创作者 / AI 设计师 / 网页搭建设计师</dd>
            </div>
          </dl>
          <img src="wechat.jpg" alt="微信二维码" />
        </div>
      </div>
    </section>
  );
}

function Hero() {
  return (
    <section className="hero posterHero" id="top">
      <div className="liquidHeroLayer">
        <LiquidChrome
          amplitude={0.48}
          baseColor={[0.125, 0.216, 0.839]}
          frequencyX={2.5}
          frequencyY={1.7}
          interactive
          speed={0.42}
        />
      </div>
      <GeneratedVideoBackground />
      <div className="heroOverlay" />
      <nav className="nav shell" aria-label="主导航">
        <a className="brand" href="#top" aria-label="MIN 作品集首页">
          <span>MIN</span>
          <span>AI Portfolio</span>
        </a>
        <div className="navLinks">
          <a href="#profile">经历</a>
          <a href="#projects">项目</a>
          <a href="#strengths">优势</a>
          <a href="#contact">联系</a>
        </div>
        <a className="navButton" href={`tel:${phoneNumber}`}>
          <Phone size={16} />
          联系我
        </a>
      </nav>

      <div className="posterStage shell">
        <div className="posterTitleBlock" aria-label="首页主标题">
          <span>Make AI</span>
          <span>Works Real</span>
        </div>

        <ScrollEarth />

        <div className="posterManifest">
          <strong>MIN AI Manifest</strong>
          <span>AI 应用创作者 / AI 设计师 / 网页搭建设计师</span>
        </div>

        <div className="posterIntro">
          <p>
            我把视觉表达、AI 应用开发和网页搭建组合在一起，快速完成从概念、原型、页面到商业展示的第一版落地。
          </p>
          <div className="heroActions">
            <a className="primaryButton" href="#projects">
              查看精选项目
              <ArrowUpRight size={18} />
            </a>
            <a className="secondaryButton" href="#contact">
              获取联系方式
            </a>
          </div>
        </div>
      </div>

      <div className="heroBottom shell" aria-label="个人数据">
        {stats.map((item) => (
          <div className="stat" key={item.label}>
            <strong>{item.value}</strong>
            <span>{item.label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function GeneratedVideoBackground() {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const canvas = document.createElement("canvas");
    canvas.width = 1600;
    canvas.height = 900;
    const ctx = canvas.getContext("2d");

    if (!ctx || !videoRef.current || !canvas.captureStream) {
      return undefined;
    }

    const stream = canvas.captureStream(30);
    videoRef.current.srcObject = stream;
    void videoRef.current.play();

    let frame = 0;
    let animationId = 0;
    const nodes = Array.from({ length: 58 }, (_, index) => ({
      x: (index * 271) % canvas.width,
      y: (index * 149) % canvas.height,
      speed: 0.22 + (index % 7) * 0.035,
      size: 1 + (index % 4) * 0.45
    }));

    const render = () => {
      frame += 1;
      ctx.fillStyle = "#030614";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const leftBeam = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
      leftBeam.addColorStop(0, "rgba(32, 55, 214, 0.36)");
      leftBeam.addColorStop(0.46, "rgba(95, 124, 255, 0.16)");
      leftBeam.addColorStop(1, "rgba(255, 255, 255, 0)");
      ctx.fillStyle = leftBeam;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.strokeStyle = "rgba(255,255,255,0.045)";
      ctx.lineWidth = 1;
      for (let x = 80; x < canvas.width; x += 160) {
        ctx.beginPath();
        ctx.moveTo(x + Math.sin(frame * 0.01 + x) * 16, 0);
        ctx.lineTo(x - 180, canvas.height);
        ctx.stroke();
      }

      for (const node of nodes) {
        node.y += node.speed;
        node.x += Math.sin((frame + node.y) * 0.01) * 0.22;
        if (node.y > canvas.height + 20) {
          node.y = -20;
        }

        ctx.fillStyle = "rgba(175, 194, 255, 0.46)";
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.size, 0, Math.PI * 2);
        ctx.fill();
      }

      const scanY = (frame * 2.4) % canvas.height;
      const scan = ctx.createLinearGradient(0, scanY - 80, 0, scanY + 80);
      scan.addColorStop(0, "rgba(255,255,255,0)");
      scan.addColorStop(0.5, "rgba(95, 124, 255, 0.18)");
      scan.addColorStop(1, "rgba(255,255,255,0)");
      ctx.fillStyle = scan;
      ctx.fillRect(0, scanY - 90, canvas.width, 180);

      ctx.fillStyle = "rgba(0,0,0,0.2)";
      for (let y = 0; y < canvas.height; y += 4) {
        ctx.fillRect(0, y, canvas.width, 1);
      }

      animationId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationId);
      stream.getTracks().forEach((track) => track.stop());
    };
  }, []);

  return <video ref={videoRef} className="heroVideo" muted playsInline autoPlay aria-hidden="true" />;
}

function createEarthMapTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 2048;
  canvas.height = 1024;
  const ctx = canvas.getContext("2d");

  if (!ctx) {
    return new THREE.CanvasTexture(canvas);
  }

  const ocean = ctx.createLinearGradient(0, 0, 0, canvas.height);
  ocean.addColorStop(0, "#183fdc");
  ocean.addColorStop(0.38, "#0c2b9e");
  ocean.addColorStop(0.68, "#06175e");
  ocean.addColorStop(1, "#03091f");
  ctx.fillStyle = ocean;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (let index = 0; index < 5200; index += 1) {
    const x = Math.random() * canvas.width;
    const y = Math.random() * canvas.height;
    const alpha = 0.025 + Math.random() * 0.055;
    ctx.fillStyle = `rgba(145, 194, 255, ${alpha})`;
    ctx.fillRect(x, y, 1.2, 1.2);
  }

  const mapPoint = (lon: number, lat: number) => ({
    x: ((lon + 180) / 360) * canvas.width,
    y: ((90 - lat) / 180) * canvas.height
  });

  const drawLand = (points: Array<[number, number]>, color = "#62d6a6") => {
    if (points.length < 3) return;

    const first = mapPoint(points[0][0], points[0][1]);
    ctx.beginPath();
    ctx.moveTo(first.x, first.y);

    points.slice(1).forEach(([lon, lat]) => {
      const point = mapPoint(lon, lat);
      ctx.lineTo(point.x, point.y);
    });

    ctx.closePath();
    ctx.fillStyle = color;
    ctx.shadowColor = "rgba(120, 210, 255, 0.34)";
    ctx.shadowBlur = 18;
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.strokeStyle = "rgba(225, 255, 235, 0.2)";
    ctx.lineWidth = 3;
    ctx.stroke();
  };

  drawLand(
    [
      [-167, 63],
      [-145, 70],
      [-120, 62],
      [-93, 52],
      [-68, 48],
      [-57, 32],
      [-78, 22],
      [-94, 16],
      [-112, 23],
      [-125, 40],
      [-150, 52]
    ],
    "#69e2ad"
  );
  drawLand(
    [
      [-82, 13],
      [-64, 9],
      [-48, -8],
      [-41, -24],
      [-55, -55],
      [-72, -48],
      [-80, -22],
      [-89, 1]
    ],
    "#4bc789"
  );
  drawLand(
    [
      [-18, 35],
      [9, 37],
      [31, 31],
      [47, 11],
      [43, -24],
      [30, -35],
      [17, -33],
      [4, -17],
      [-9, 5],
      [-17, 23]
    ],
    "#58d999"
  );
  drawLand(
    [
      [-11, 58],
      [16, 66],
      [42, 55],
      [32, 43],
      [9, 44],
      [-4, 50]
    ],
    "#81eeb7"
  );
  drawLand(
    [
      [29, 55],
      [63, 66],
      [111, 58],
      [151, 49],
      [164, 30],
      [139, 13],
      [113, 18],
      [87, 8],
      [70, 25],
      [43, 30],
      [30, 42]
    ],
    "#72e7af"
  );
  drawLand(
    [
      [43, 30],
      [74, 24],
      [96, 8],
      [104, -7],
      [92, -13],
      [73, 7],
      [51, 12]
    ],
    "#4acb8f"
  );
  drawLand(
    [
      [113, -11],
      [137, -10],
      [154, -25],
      [144, -43],
      [118, -39],
      [108, -25]
    ],
    "#5dd69c"
  );

  const ice = ctx.createLinearGradient(0, 0, 0, canvas.height);
  ice.addColorStop(0, "rgba(240, 250, 255, 0.58)");
  ice.addColorStop(0.16, "rgba(240, 250, 255, 0)");
  ice.addColorStop(0.84, "rgba(240, 250, 255, 0)");
  ice.addColorStop(1, "rgba(240, 250, 255, 0.5)");
  ctx.fillStyle = ice;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.ClampToEdgeWrapping;
  texture.anisotropy = 8;
  texture.needsUpdate = true;
  return texture;
}

function createEarthBumpTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 1024;
  canvas.height = 512;
  const ctx = canvas.getContext("2d");

  if (!ctx) {
    return new THREE.CanvasTexture(canvas);
  }

  ctx.fillStyle = "#1f2b46";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (let index = 0; index < 9000; index += 1) {
    const x = Math.random() * canvas.width;
    const y = Math.random() * canvas.height;
    const value = 42 + Math.floor(Math.random() * 92);
    ctx.fillStyle = `rgb(${value}, ${value}, ${value})`;
    ctx.fillRect(x, y, 1, 1);
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.ClampToEdgeWrapping;
  texture.needsUpdate = true;
  return texture;
}

function createCloudTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 2048;
  canvas.height = 1024;
  const ctx = canvas.getContext("2d");

  if (!ctx) {
    return new THREE.CanvasTexture(canvas);
  }

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  for (let band = 0; band < 18; band += 1) {
    const y = 120 + band * 46 + Math.sin(band * 1.7) * 32;
    const height = 24 + (band % 4) * 10;
    const gradient = ctx.createLinearGradient(0, y - height, canvas.width, y + height);
    gradient.addColorStop(0, "rgba(255, 255, 255, 0)");
    gradient.addColorStop(0.18, "rgba(255, 255, 255, 0.12)");
    gradient.addColorStop(0.5, "rgba(255, 255, 255, 0.24)");
    gradient.addColorStop(0.82, "rgba(255, 255, 255, 0.1)");
    gradient.addColorStop(1, "rgba(255, 255, 255, 0)");
    ctx.fillStyle = gradient;

    ctx.beginPath();
    for (let x = -80; x <= canvas.width + 80; x += 80) {
      const waveY = y + Math.sin(x * 0.015 + band) * height;
      if (x === -80) {
        ctx.moveTo(x, waveY);
      } else {
        ctx.lineTo(x, waveY);
      }
    }
    ctx.lineWidth = height;
    ctx.strokeStyle = gradient;
    ctx.stroke();
  }

  for (let index = 0; index < 240; index += 1) {
    const x = Math.random() * canvas.width;
    const y = Math.random() * canvas.height;
    const radius = 9 + Math.random() * 42;
    const glow = ctx.createRadialGradient(x, y, 0, x, y, radius);
    glow.addColorStop(0, "rgba(255, 255, 255, 0.18)");
    glow.addColorStop(1, "rgba(255, 255, 255, 0)");
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.ClampToEdgeWrapping;
  texture.needsUpdate = true;
  return texture;
}

function ScrollEarth() {
  const mountRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const mount = mountRef.current;
    const canvas = canvasRef.current;

    if (!mount || !canvas) {
      return undefined;
    }

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 100);
    camera.position.set(0, 0, 7.1);

    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      canvas,
      powerPreference: "high-performance"
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2.5));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.08;

    const earthGroup = new THREE.Group();
    scene.add(earthGroup);

    const texture = createEarthMapTexture();
    const bumpTexture = createEarthBumpTexture();
    const cloudTexture = createCloudTexture();

    const earth = new THREE.Mesh(
      new THREE.SphereGeometry(2.36, 128, 128),
      new THREE.MeshStandardMaterial({
        map: texture,
        bumpMap: bumpTexture,
        bumpScale: 0.045,
        metalness: 0.02,
        roughness: 0.58,
        emissive: new THREE.Color("#06175e"),
        emissiveIntensity: 0.12
      })
    );
    earthGroup.rotation.set(-0.16, -0.78, 0.08);
    earthGroup.add(earth);

    const clouds = new THREE.Mesh(
      new THREE.SphereGeometry(2.395, 128, 128),
      new THREE.MeshStandardMaterial({
        alphaMap: cloudTexture,
        color: "#f4fbff",
        depthWrite: false,
        opacity: 0.42,
        roughness: 0.8,
        transparent: true
      })
    );
    earthGroup.add(clouds);

    const atmosphere = new THREE.Mesh(
      new THREE.SphereGeometry(2.46, 128, 128),
      new THREE.MeshBasicMaterial({
        blending: THREE.AdditiveBlending,
        color: "#77a8ff",
        opacity: 0.18,
        side: THREE.BackSide,
        transparent: true
      })
    );
    scene.add(atmosphere);

    const rim = new THREE.Mesh(
      new THREE.SphereGeometry(2.5, 96, 96),
      new THREE.MeshBasicMaterial({
        color: "#2037d6",
        blending: THREE.AdditiveBlending,
        opacity: 0.1,
        side: THREE.BackSide,
        transparent: true
      })
    );
    scene.add(rim);

    const cityGeometry = new THREE.BufferGeometry();
    const cityPoints = [
      [-74, 40],
      [-118, 34],
      [-46, -23],
      [-0.1, 51.5],
      [2.3, 48.8],
      [31.2, 30],
      [77.2, 28.6],
      [103.8, 1.3],
      [116.4, 39.9],
      [121.5, 31.2],
      [139.7, 35.6],
      [151.2, -33.8]
    ];
    const cityPositions = cityPoints.map(([lon, lat]) => {
      const phi = (90 - lat) * (Math.PI / 180);
      const theta = (lon + 180) * (Math.PI / 180);
      const radius = 2.382;
      return [
        -(radius * Math.sin(phi) * Math.cos(theta)),
        radius * Math.cos(phi),
        radius * Math.sin(phi) * Math.sin(theta)
      ];
    });
    cityGeometry.setAttribute("position", new THREE.Float32BufferAttribute(cityPositions.flat(), 3));
    const cityLights = new THREE.Points(
      cityGeometry,
      new THREE.PointsMaterial({
        blending: THREE.AdditiveBlending,
        color: "#c7f3ff",
        depthWrite: false,
        opacity: 0.78,
        size: 0.045,
        transparent: true
      })
    );
    earthGroup.add(cityLights);

    scene.add(new THREE.AmbientLight("#b7caff", 1.25));

    const keyLight = new THREE.DirectionalLight("#ffffff", 3.1);
    keyLight.position.set(-2.8, 3.8, 5);
    scene.add(keyLight);

    const blueLight = new THREE.PointLight("#2037d6", 8.5, 12);
    blueLight.position.set(3.8, -1.5, 3.5);
    scene.add(blueLight);

    let targetRotation = earthGroup.rotation.y;
    let frameId = 0;

    const resize = () => {
      const bounds = mount.getBoundingClientRect();
      const size = Math.max(320, Math.round(Math.min(bounds.width, bounds.height || bounds.width)));
      renderer.setSize(size, size, false);
      camera.aspect = 1;
      camera.updateProjectionMatrix();
    };

    const onScroll = () => {
      targetRotation = -0.7 + window.scrollY * 0.0042;
    };

    const animate = () => {
      earthGroup.rotation.y += (targetRotation - earthGroup.rotation.y) * 0.08 + 0.0028;
      earthGroup.rotation.x = -0.16 + Math.sin(earthGroup.rotation.y * 0.65) * 0.035;
      clouds.rotation.y += 0.0038;
      clouds.rotation.x = earthGroup.rotation.x + 0.02;
      atmosphere.rotation.copy(earthGroup.rotation);
      atmosphere.rotation.y += 0.12;
      rim.rotation.copy(earthGroup.rotation);
      renderer.render(scene, camera);
      frameId = window.requestAnimationFrame(animate);
    };

    const observer = new ResizeObserver(resize);
    observer.observe(mount);
    resize();
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    animate();

    return () => {
      window.cancelAnimationFrame(frameId);
      window.removeEventListener("scroll", onScroll);
      observer.disconnect();
      texture.dispose();
      bumpTexture.dispose();
      cloudTexture.dispose();
      earth.geometry.dispose();
      clouds.geometry.dispose();
      atmosphere.geometry.dispose();
      rim.geometry.dispose();
      cityGeometry.dispose();
      renderer.dispose();
      if (earth.material instanceof THREE.Material) earth.material.dispose();
      if (clouds.material instanceof THREE.Material) clouds.material.dispose();
      if (atmosphere.material instanceof THREE.Material) atmosphere.material.dispose();
      if (rim.material instanceof THREE.Material) rim.material.dispose();
      if (cityLights.material instanceof THREE.Material) cityLights.material.dispose();
    };
  }, []);

  return (
    <div className="posterVisual earthVisual" ref={mountRef} aria-label="随滚动旋转的 3D 地球视觉">
      <canvas className="earthCanvas" ref={canvasRef} />
    </div>
  );
}

function ProfileSection() {
  return (
    <section className="section profileSection" id="profile">
      <div className="shell profileGrid">
        <div className="portraitPanel" aria-label="人物视觉">
          <div className="portraitFrame">
            <div className="animeAvatar" aria-hidden="true">
              <div className="avatarHalo" />
              <div className="avatarHair" />
              <div className="avatarFace">
                <span />
                <span />
              </div>
              <div className="avatarCollar" />
              <div className="avatarBody" />
              <div className="avatarChip">AI</div>
            </div>
            <div className="portraitInterface">
              <span>MIN</span>
              <span>AI DESIGNER</span>
            </div>
          </div>
        </div>

        <div className="profileCopy">
          <p className="sectionKicker">Experience</p>
          <h2>个人经历与创作方向</h2>
          <p className="sectionLead">
            我目前围绕 AI 应用、AI 辅助硬件、实体场景落地和网页搭建设计持续做项目，把技术能力转化成能被看见、被理解、被使用的作品。
          </p>
          <div className="experienceList">
            {experience.map((item) => (
              <p key={item}>{item}</p>
            ))}
          </div>

          <div className="contactStrip">
            <a href={`tel:${phoneNumber}`}>
              <Phone size={18} />
              195 7102 3940
            </a>
            <span>
              <MapPin size={18} />
              湖北武汉
            </span>
            <span>
              <Mail size={18} />
              {emailAddress}
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}

function ProjectsSection() {
  return (
    <section className="section projectsSection" id="projects">
      <div className="projectChromeLayer">
        <LiquidChrome
          amplitude={0.18}
          baseColor={[0.06, 0.12, 0.42]}
          frequencyX={1.7}
          frequencyY={2.2}
          interactive={false}
          speed={0.16}
        />
      </div>
      <div className="shell">
        <div className="sectionHeader">
          <div>
            <p className="sectionKicker">Selected Work</p>
            <h2>精选项目</h2>
          </div>
          <p>用更产品化、更克制的视觉呈现项目，不再使用低质感照片素材。</p>
        </div>

        <div className="projectGrid">
          {featuredProjects.map((project, index) => (
            <ProjectCard featured={index === 0} key={project.title} project={project} />
          ))}
        </div>

        <details className="moreProjects">
          <summary>
            <span>其他项目</span>
            <small>默认隐藏，展开查看</small>
          </summary>
          <div className="hiddenProjectGrid">
            {hiddenProjects.map((project) => (
              <ProjectCard key={project.title} project={project} />
            ))}
          </div>
        </details>
      </div>
    </section>
  );
}

function ProjectCard({
  featured = false,
  project
}: {
  featured?: boolean;
  project: (typeof featuredProjects)[number] | (typeof hiddenProjects)[number];
}) {
  return (
    <BorderGlow
      animated={featured}
      backgroundColor="#071026"
      borderRadius={8}
      className={featured ? "projectCard featured" : "projectCard"}
      colors={["#2037d6", "#5f7cff", "#f3f7ff"]}
      edgeSensitivity={24}
      glowColor="225 86 66"
      glowIntensity={1.15}
      glowRadius={42}
    >
      <ProjectVisual project={project} />
      <div className="projectBody">
        <p>{project.tag}</p>
        <h3>{project.title}</h3>
        <span>{project.description}</span>
        <div className="metricRow">
          {project.metrics.map((metric) => (
            <strong key={metric}>{metric}</strong>
          ))}
        </div>
        {"url" in project && project.url ? (
          <a className="projectLink" href={project.url} rel="noreferrer" target="_blank">
            {"readOnly" in project && project.readOnly ? "只读体验" : "查看项目"}
            <ExternalLink size={16} />
          </a>
        ) : null}
      </div>
    </BorderGlow>
  );
}

function ProjectVisual({
  project
}: {
  project: (typeof featuredProjects)[number] | (typeof hiddenProjects)[number];
}) {
  const { type, images, image } = {
    type: project.visual,
    images: "images" in project ? project.images : undefined,
    image: "image" in project ? project.image : undefined
  };
  const Icon = type === "emotion" ? MessageCircleHeart : type === "deck" ? Layers3 : type === "hardware" ? Cpu : Bot;

  if (type === "emotion" && images?.length) {
    return (
      <div className="projectImageShowcase emotionShowcase" aria-hidden="true">
        <div className="emotionMarkCard">
          <img alt="" src={images[0]} />
        </div>
        <div className="emotionAppCard">
          <img alt="" src={images[1]} />
        </div>
      </div>
    );
  }

  if (image) {
    return (
      <div className={`projectImageShowcase realProjectShowcase ${type}`} aria-hidden="true">
        <img alt="" className="projectRealImage" src={image} />
      </div>
    );
  }

  return (
    <div className={`projectVisualSurface ${type}`} aria-hidden="true">
      <div className="visualHeader">
        <span />
        <span />
        <span />
      </div>
      <div className="visualOrb">
        <Icon size={42} />
      </div>
      <div className="visualGridLines" />
      <div className="visualPanel left">
        <i />
        <i />
        <i />
      </div>
      <div className="visualPanel right">
        <b />
        <b />
        <b />
        <b />
      </div>
      <div className="visualWave" />
    </div>
  );
}

function StrengthsSection() {
  return (
    <section className="section strengthsSection" id="strengths">
      <div className="shell">
        <div className="sectionHeader">
          <div>
            <p className="sectionKicker">Strengths</p>
            <h2>个人优势</h2>
          </div>
          <p>这个版本先突出你的复合能力：AI、设计、网页搭建、实体落地和快速原型。</p>
        </div>

        <div className="strengthGrid">
          {strengths.map((item) => {
            const Icon = item.icon;

            return (
              <BorderGlow
                backgroundColor="#071026"
                borderRadius={8}
                className="strengthCard"
                colors={["#2037d6", "#5f7cff", "#f3f7ff"]}
                edgeSensitivity={30}
                glowColor="225 86 66"
                glowIntensity={0.8}
                glowRadius={30}
                key={item.title}
              >
                <div className="iconBox">
                  <Icon size={24} />
                </div>
                <h3>{item.title}</h3>
                <p>{item.text}</p>
              </BorderGlow>
            );
          })}
        </div>

        <div className="processBand" aria-label="工作方式">
          <div>
            <MousePointer2 size={20} />
            <span>发现问题</span>
          </div>
          <div>
            <BrainCircuit size={20} />
            <span>AI 工作流</span>
          </div>
          <div>
            <Layers3 size={20} />
            <span>界面原型</span>
          </div>
          <div>
            <Zap size={20} />
            <span>演示验证</span>
          </div>
        </div>
      </div>
    </section>
  );
}

function ContactSection() {
  return (
    <section className="contactPage" id="contact">
      <div className="shell contactGrid">
        <div>
          <p className="sectionKicker">Contact</p>
          <h2>让下一个 AI 作品进入真实场景</h2>
          <p>适合聊 AI 应用、AI 辅助硬件、网页搭建、黑客松、创意技术、项目合作和第一版产品原型。</p>
          <div className="contactActions">
            <a className="primaryButton" href={`tel:${phoneNumber}`}>
              <Phone size={18} />
              直接联系
            </a>
            <a className="secondaryButton" href="#top">
              回到首页
            </a>
          </div>
        </div>

        <BorderGlow
          backgroundColor="#071026"
          borderRadius={8}
          className="contactCard"
          colors={["#2037d6", "#5f7cff", "#f3f7ff"]}
          edgeSensitivity={28}
          glowColor="225 86 66"
          glowIntensity={0.9}
          glowRadius={34}
        >
          <div className="contactCardHeader">
            <span>MIN</span>
            <ExternalLink size={18} />
          </div>
          <dl>
            <div>
              <dt>电话 / 飞书手机号</dt>
              <dd>{phoneNumber}</dd>
            </div>
            <div>
              <dt>地点</dt>
              <dd>湖北武汉</dd>
            </div>
            <div>
              <dt>身份</dt>
              <dd>AI 应用创作者 / AI 设计师 / 网页搭建设计师</dd>
            </div>
          </dl>
          <img src="wechat.jpg" alt="微信二维码" />
        </BorderGlow>
      </div>
    </section>
  );
}
