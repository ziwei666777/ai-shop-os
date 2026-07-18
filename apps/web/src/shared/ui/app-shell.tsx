"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  BarChart3,
  Bot,
  Brain,
  Boxes,
  CheckCircle2,
  Dumbbell,
  Database,
  LayoutDashboard,
  LogOut,
  Menu,
  PackageSearch,
  Gauge,
  RotateCcw,
  FlaskConical,
  Settings,
  ShoppingBag,
  Users,
  Workflow,
  X
} from "lucide-react";
import { PRIMARY_NAVIGATION_ITEMS } from "@ai-shop-os/shared";
import { cn } from "@/shared/lib/utils";
import { Button } from "@/shared/ui/button";
import { ThemeToggle } from "@/shared/ui/theme-toggle";

const navigationIcons = {
  "/dashboard": LayoutDashboard,
  "/ai-employees": Bot,
  "/orders": ShoppingBag,
  "/products": PackageSearch,
  "/customers": Users,
  "/commerce-dataset": Database,
  "/replay": RotateCcw,
  "/evaluation": Gauge,
  "/training-center": Dumbbell,
  "/simulation": FlaskConical,
  "/knowledge-base": Brain,
  "/workflow": Workflow,
  "/analytics": BarChart3,
  "/settings": Settings
} as const;

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  async function handleSignOut() {
    try {
      const { createBrowserSupabaseClient } = await import("@/shared/api/supabase-client");
      await createBrowserSupabaseClient().auth.signOut();
    } finally {
      window.location.assign("/login");
    }
  }

  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="flex min-h-screen">
        <aside className="hidden w-64 shrink-0 border-r border-border bg-card/86 backdrop-blur-xl lg:block">
          <SidebarContent pathname={pathname} />
        </aside>

        {mobileOpen ? (
          <div className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden">
            <aside className="h-full w-72 border-r border-border bg-card shadow-soft">
              <div className="flex h-14 items-center justify-between border-b border-border px-4">
                <Link className="text-sm font-semibold" href="/dashboard" onClick={() => setMobileOpen(false)}>
                  AI Shop OS
                </Link>
                <Button aria-label="关闭导航" className="h-9 w-9 px-0" onClick={() => setMobileOpen(false)} type="button" variant="ghost">
                  <X aria-hidden className="h-4 w-4" />
                </Button>
              </div>
              <SidebarContent onNavigate={() => setMobileOpen(false)} pathname={pathname} />
            </aside>
          </div>
        ) : null}

        <section className="min-w-0 flex-1">
          <header className="sticky top-0 z-30 border-b border-border bg-background/82 backdrop-blur-xl">
            <div className="mx-auto flex h-14 w-full max-w-7xl items-center justify-between px-4 sm:px-6">
              <div className="flex min-w-0 items-center gap-3">
                <Button aria-label="打开导航" className="h-9 w-9 px-0 lg:hidden" onClick={() => setMobileOpen(true)} type="button" variant="ghost">
                  <Menu aria-hidden className="h-4 w-4" />
                </Button>
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold">AI Shop OS</p>
                  <p className="truncate text-xs text-muted-foreground">AI 电商员工操作系统</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="hidden items-center gap-2 rounded-md border border-border bg-card px-3 py-1.5 text-xs text-muted-foreground sm:flex">
                  <CheckCircle2 aria-hidden className="h-3.5 w-3.5 text-primary" />
                  <span>试用版数据采集中</span>
                </div>
                <ThemeToggle />
                <Button aria-label="退出登录" className="h-9 w-9 px-0" onClick={handleSignOut} type="button" variant="ghost">
                  <LogOut aria-hidden className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </header>
          <div className="mx-auto w-full max-w-7xl px-4 py-5 sm:px-6">{children}</div>
        </section>
      </div>
    </main>
  );
}

function SidebarContent({
  onNavigate,
  pathname
}: {
  onNavigate?: () => void;
  pathname: string;
}) {
  return (
    <div className="flex h-full min-h-0 flex-col px-3 py-4">
      <div className="px-3">
        <Link className="block text-lg font-semibold" href="/dashboard" onClick={onNavigate}>
          AI Shop OS
        </Link>
        <p className="mt-1 text-xs text-muted-foreground">AI 电商员工操作系统</p>
      </div>

      <nav className="mt-8 space-y-1 text-sm">
        {PRIMARY_NAVIGATION_ITEMS.map((item) => {
          const Icon = navigationIcons[item.href as keyof typeof navigationIcons] ?? Boxes;
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);

          return (
            <Link
              className={cn(
                "flex h-10 items-center gap-3 rounded-md px-3 text-muted-foreground transition hover:bg-accent hover:text-foreground",
                active && "bg-accent text-foreground"
              )}
              href={item.href}
              key={item.href}
              onClick={onNavigate}
            >
              <Icon aria-hidden className="h-4 w-4 shrink-0" />
              <span className="truncate">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto rounded-md border border-border bg-background/70 p-3">
        <p className="text-xs font-medium">AI 权限边界</p>
        <p className="mt-1 text-xs leading-5 text-muted-foreground">
          高风险退款、赔偿、投诉和预算动作必须进入人工审批。
        </p>
      </div>
    </div>
  );
}
