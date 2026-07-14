import {
  ArrowRight,
  Check,
  ChevronRight,
  Heart,
  Leaf,
  Menu,
  PackageCheck,
  Search,
  ShieldCheck,
  ShoppingBag,
  Sparkles,
  Star,
  Truck
} from "lucide-react";

const heroProduct =
  "https://polo-pecan-73837341.figma.site/_assets/v11/50ad042b3cd48a2e120ea3ba17c8cfeaf3cc334c.png";
const capsuleImage =
  "https://polo-pecan-73837341.figma.site/_assets/v11/6a7de4fbe9c9e2315040607320a9ff5e93117bf4.png";
const miniProduct =
  "https://polo-pecan-73837341.figma.site/_assets/v11/30e8f38d1f993c357a3be2721557fc899d5640fc.png";
const naturalTexture =
  "https://polo-pecan-73837341.figma.site/_assets/v11/6736cbe6e26afa2cd7c04a91892a79f7640785b5.png";
const avatar =
  "https://polo-pecan-73837341.figma.site/_assets/v11/ca8093996e970200cbcf8bde8744175e52da5a79.png";

const products = [
  {
    name: "植萃能量胶囊",
    desc: "适合通勤、健身与高强度工作日",
    price: "¥169",
    image: capsuleImage
  },
  {
    name: "深睡舒缓组合",
    desc: "镁元素 + 草本复配，晚间放松",
    price: "¥219",
    image: miniProduct
  },
  {
    name: "日常平衡套装",
    desc: "30 天装，订阅购更省心",
    price: "¥299",
    image: heroProduct
  }
];

const benefits = [
  { title: "植物配方", desc: "不含人工色素与甜味剂", Icon: Leaf },
  { title: "48小时发货", desc: "顺丰/京东仓优先配送", Icon: Truck },
  { title: "安心追溯", desc: "每批次提供检测编号", Icon: ShieldCheck }
];

const specs = ["30 粒/瓶", "每日 1 粒", "无糖配方", "适合素食"];

export default function Page() {
  return (
    <main className="storefront">
      <section className="hero" id="top">
        <nav className="nav" aria-label="主导航">
          <a className="brand" href="#top" aria-label="TerraElix 首页">
            TerraElix
          </a>
          <div className="navLinks">
            <a href="#products">商品</a>
            <a href="#benefits">成分</a>
            <a href="#reviews">评价</a>
            <a href="#service">售后</a>
          </div>
          <div className="navTools">
            <button aria-label="搜索商品">
              <Search size={20} strokeWidth={1.7} />
            </button>
            <button aria-label="查看购物袋">
              <ShoppingBag size={20} strokeWidth={1.7} />
              <span>2</span>
            </button>
            <img alt="会员头像" src={avatar} />
            <button className="menuButton" aria-label="打开菜单">
              <Menu size={22} strokeWidth={1.7} />
            </button>
          </div>
        </nav>

        <div className="heroGrid">
          <article className="floatingCard topLeft">
            <img alt="植萃能量胶囊小图" src={capsuleImage} />
            <p>热卖单品</p>
            <strong>¥169</strong>
          </article>

          <article className="floatingCard topRight">
            <img alt="用户开箱视频封面" src={avatar} />
            <span className="playDot">
              <ChevronRight size={16} strokeWidth={2.2} />
            </span>
            <p>开箱与服用体验</p>
          </article>

          <div className="headline">
            <span className="eyebrow">
              <Sparkles size={16} strokeWidth={1.8} />
              新品上市 / 30 天装
            </span>
            <h1>
              每日自然能量
              <br />
              从一粒开始
            </h1>
            <p>
              TerraElix 植萃营养胶囊，精选草本与矿物营养，帮助你在忙碌生活中保持清醒、平衡与轻盈。
            </p>
          </div>

          <div className="productStage" aria-label="TerraElix 日常平衡套装展示">
            <img className="texture" alt="" src={naturalTexture} />
            <img className="mainProduct" alt="TerraElix 日常平衡套装" src={heroProduct} />
          </div>

          <article className="purchaseCard">
            <span>爆款组合</span>
            <h2>日常平衡套装</h2>
            <div className="ratingLine" aria-label="评分 4.8 分">
              <strong>4.8</strong>
              <Star size={16} fill="currentColor" />
              <small>12,860 条真实评价</small>
            </div>
            <div className="priceLine">
              <strong>¥299</strong>
              <small>订阅购 ¥254 / 月</small>
            </div>
            <div className="specs">
              {specs.map((spec) => (
                <span key={spec}>{spec}</span>
              ))}
            </div>
            <div className="buyActions">
              <a href="#products">
                立即购买
                <ArrowRight size={18} strokeWidth={1.8} />
              </a>
              <button>
                <Heart size={18} strokeWidth={1.8} />
                收藏
              </button>
            </div>
          </article>
        </div>

        <div className="heroFooter" id="benefits">
          <article>
            <strong>28K+</strong>
            <p>会员正在使用 TerraElix 做日常营养管理</p>
          </article>
          <article className="centerPanel">
            <PackageCheck size={34} strokeWidth={1.5} />
            <div>
              <strong>满 ¥199 包邮</strong>
              <p>支持 7 天无理由退换，破损包赔</p>
            </div>
          </article>
          <article>
            <strong>4.8</strong>
            <div className="footerStars" aria-label="五星评价">
              {Array.from({ length: 5 }).map((_, index) => (
                <Star key={index} size={14} fill="currentColor" />
              ))}
            </div>
            <p>来自高频复购用户的综合评分</p>
          </article>
        </div>
      </section>

      <section className="productSection" id="products">
        <div className="sectionTitle">
          <span>精选商品</span>
          <h2>按你的生活节奏选择营养方案</h2>
        </div>
        <div className="productGrid">
          {products.map((product) => (
            <article className="productCard" key={product.name}>
              <div className="productImageWrap">
                <img alt={product.name} src={product.image} />
              </div>
              <h3>{product.name}</h3>
              <p>{product.desc}</p>
              <div>
                <strong>{product.price}</strong>
                <button aria-label={`加入购物袋：${product.name}`}>
                  <ShoppingBag size={18} strokeWidth={1.8} />
                </button>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="serviceStrip" id="service">
        {benefits.map(({ title, desc, Icon }) => (
          <article key={title}>
            <Icon size={28} strokeWidth={1.7} />
            <div>
              <h3>{title}</h3>
              <p>{desc}</p>
            </div>
            <Check size={18} strokeWidth={2} />
          </article>
        ))}
      </section>

      <section className="reviewSection" id="reviews">
        <div>
          <span>真实反馈</span>
          <h2>“早上不用再靠第三杯咖啡硬撑。”</h2>
          <p>
            购物袋、规格、评价和售后信息都在首屏内完成决策，适合投放页、品牌首页或新品首发活动。
          </p>
        </div>
        <a href="#top">
          回到顶部选购
          <ArrowRight size={18} strokeWidth={1.8} />
        </a>
      </section>
    </main>
  );
}
