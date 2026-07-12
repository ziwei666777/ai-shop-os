import type { Metadata } from "next";
import Image from "next/image";
import { existsSync } from "node:fs";
import path from "node:path";
import {
  ArrowUpRight,
  Bot,
  Boxes,
  Brush,
  Lightbulb,
  MapPin,
  MessageCircle,
  Phone,
  Sparkles
} from "lucide-react";
import { ProfileAvatar } from "./profile-avatar";

export const metadata: Metadata = {
  title: "闵怡强 MIN | 个人介绍",
  description: "18岁美术生、AI应用开发者、AI创业者，关注 AI 辅助硬件、AI 实体落地与创业项目。"
};

const profileTags = [
  "AI 应用开发",
  "AI 辅助硬件",
  "AI 实体落地",
  "美术生",
  "创业项目",
  "黑客松经历"
];

const overview = [
  "18 岁，来自湖北武汉，美术生背景，同时长期实践 AI 应用开发与创业项目。",
  "有多个创业项目和黑客松经历，擅长把一个想法快速推进到可展示、可验证的原型。",
  "当前重点关注 AI 辅助硬件、AI 实体落地和真实场景中的 AI 工作流，让 AI 不只停留在演示里。",
  "希望连接对 AI 产品、创意技术、硬件落地和年轻创业实践感兴趣的伙伴。"
];

const abilityGroups = [
  {
    icon: Bot,
    title: "AI 员工 / 工作流程",
    description:
      "围绕任务拆解、工具调用、流程自动化和知识整理，设计能真正推进事情的 AI 应用。"
  },
  {
    icon: Boxes,
    title: "AI + 硬件落地",
    description:
      "关注 AI 辅助硬件、线下设备与实体场景结合，让智能能力进入具体空间和真实流程。"
  },
  {
    icon: Lightbulb,
    title: "创业 / 产品原型",
    description:
      "从需求观察、MVP 原型、展示表达，到黑客松协作和商业验证，快速把想法做出来。"
  },
  {
    icon: Brush,
    title: "艺术表达 / 视觉判断",
    description:
      "用美术训练带来的审美和表达能力，提升产品界面、演示材料和品牌感知。"
  }
];

const highlights = [
  {
    title: "多个创业项目实践",
    meta: "产品构想 / 原型验证 / 商业表达",
    description: "持续尝试把想法做成真实产品，在项目中验证需求、组织资源并快速迭代。"
  },
  {
    title: "黑客松项目经历",
    meta: "短周期协作 / Demo 搭建 / 路演展示",
    description: "习惯在有限时间内完成原型、表达方案，并把技术能力转化为可展示的结果。"
  },
  {
    title: "AI 实体落地方向",
    meta: "AI 应用 / AI 辅助硬件 / 真实场景",
    description: "关注 AI 应用、AI 辅助硬件和真实场景结合，让智能能力进入具体的工作与生活。"
  }
];

const phoneNumber = "19571023940";

const contactCards = [
  {
    icon: Phone,
    label: "电话",
    value: "195 7102 3940",
    href: `tel:${phoneNumber}`
  },
  {
    icon: MessageCircle,
    label: "飞书手机号",
    value: phoneNumber,
    href: `tel:${phoneNumber}`
  }
];

export default function ProfilePage() {
  const avatarFilePath = path.join(process.cwd(), "public", "profile", "avatar.jpg");
  const hasAvatarImage = existsSync(avatarFilePath);

  return (
    <main className="min-h-screen bg-background px-5 py-6 text-foreground sm:px-8 lg:px-10">
      <section className="mx-auto grid w-full max-w-7xl gap-8 lg:grid-cols-[0.9fr_1.1fr]">
        <aside className="lg:sticky lg:top-6 lg:h-[calc(100vh-3rem)]">
          <div className="flex h-full flex-col justify-between rounded-md border border-border bg-card p-6 shadow-soft sm:p-8">
            <div>
              <div className="flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between lg:flex-col lg:items-start">
                <ProfileAvatar showImage={hasAvatarImage} />
                <div className="inline-flex items-center gap-2 rounded-md border border-border bg-background px-3 py-2 text-sm font-medium text-muted-foreground">
                  <MapPin className="h-4 w-4 text-primary" />
                  湖北武汉
                </div>
              </div>

              <div className="mt-10">
                <p className="inline-flex items-center gap-2 text-sm font-semibold text-primary">
                  <Sparkles className="h-4 w-4" />
                  AI 创作者名片
                </p>
                <h1 className="mt-3 text-4xl font-semibold leading-tight tracking-normal sm:text-5xl">
                  闵怡强 MIN
                </h1>
                <p className="mt-4 max-w-xl text-xl leading-8 text-foreground/82">
                  18 岁美术生，AI 应用开发者，AI 创业者。
                </p>
                <p className="mt-5 max-w-xl text-base leading-7 text-muted-foreground">
                  我把美术生的视觉表达、AI 应用开发和创业项目实践合在一起，探索 AI 辅助硬件与实体场景落地。
                </p>
              </div>

              <div className="mt-8 flex flex-wrap gap-2">
                {profileTags.map((tag) => (
                  <span className="rounded-md border border-border bg-background px-3 py-2 text-sm font-medium text-muted-foreground" key={tag}>
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            <div className="mt-10 border-t border-border pt-6">
              <h2 className="text-sm font-semibold text-primary">联系我</h2>
              <div className="mt-4 grid gap-3">
                {contactCards.map((contact) => {
                  const Icon = contact.icon;

                  return (
                    <a
                      className="group flex min-h-14 items-center justify-between rounded-md border border-border bg-background px-4 py-3 transition hover:border-primary hover:bg-accent"
                      href={contact.href}
                      key={contact.label}
                    >
                      <span className="flex items-center gap-3">
                        <span className="flex h-9 w-9 items-center justify-center rounded-md bg-card text-primary">
                          <Icon className="h-4 w-4" />
                        </span>
                        <span>
                          <span className="block text-sm font-semibold">{contact.label}</span>
                          <span className="block text-sm text-muted-foreground">{contact.value}</span>
                        </span>
                      </span>
                      <ArrowUpRight className="h-4 w-4 text-muted-foreground transition group-hover:text-primary" />
                    </a>
                  );
                })}
              </div>
            </div>
          </div>
        </aside>

        <div className="space-y-6">
          <section className="rounded-md border border-border bg-card p-6 shadow-soft sm:p-8">
            <SectionTitle eyebrow="Overview" title="个人概况" />
            <ul className="mt-5 space-y-3">
              {overview.map((item) => (
                <li className="flex gap-3 text-base leading-7 text-muted-foreground" key={item}>
                  <span className="mt-3 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </section>

          <section className="rounded-md border border-border bg-card p-6 shadow-soft sm:p-8">
            <SectionTitle eyebrow="Stack" title="核心能力与技术栈" />
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              {abilityGroups.map((group) => {
                const Icon = group.icon;

                return (
                  <article className="rounded-md border border-border bg-background p-5" key={group.title}>
                    <div className="flex items-center gap-3">
                      <span className="flex h-10 w-10 items-center justify-center rounded-md bg-accent text-primary">
                        <Icon className="h-5 w-5" />
                      </span>
                      <h3 className="text-base font-semibold">{group.title}</h3>
                    </div>
                    <p className="mt-4 text-sm leading-6 text-muted-foreground">{group.description}</p>
                  </article>
                );
              })}
            </div>
          </section>

          <section className="rounded-md border border-border bg-card p-6 shadow-soft sm:p-8">
            <SectionTitle eyebrow="Projects" title="核心项目经历" />
            <div className="mt-5 divide-y divide-border rounded-md border border-border bg-background">
              {highlights.map((item) => (
                <article className="p-5" key={item.title}>
                  <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-start">
                    <h3 className="text-lg font-semibold">{item.title}</h3>
                    <span className="text-sm font-medium text-primary">{item.meta}</span>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-muted-foreground">{item.description}</p>
                </article>
              ))}
            </div>
          </section>

          <section className="rounded-md border border-border bg-card p-6 shadow-soft sm:p-8">
            <SectionTitle eyebrow="WeChat" title="微信二维码" />
            <div className="mt-5 grid gap-6 md:grid-cols-[0.9fr_1.1fr] md:items-center">
              <div className="overflow-hidden rounded-md border border-border bg-background p-3">
                <Image
                  alt="闵怡强微信二维码"
                  className="h-auto w-full rounded-sm"
                  height={1280}
                  priority
                  src="/profile/wechat.jpg"
                  width={928}
                />
              </div>
              <div>
                <h3 className="text-xl font-semibold">扫码添加微信</h3>
                <p className="mt-4 text-base leading-7 text-muted-foreground">
                  适合聊 AI 应用、AI 辅助硬件、实体落地、黑客松、创业项目合作和创意技术想法。
                </p>
                <div className="mt-5 rounded-md border border-border bg-background p-4">
                  <p className="text-sm font-semibold text-primary">当前公开联系方式</p>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">
                    电话 / 飞书手机号：{phoneNumber}
                  </p>
                </div>
              </div>
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}

function SectionTitle({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">{eyebrow}</p>
      <h2 className="mt-2 text-2xl font-semibold leading-tight tracking-normal">{title}</h2>
    </div>
  );
}
