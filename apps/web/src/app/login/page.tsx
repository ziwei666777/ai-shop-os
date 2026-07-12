"use client";

import { useState } from "react";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { createBrowserSupabaseClient } from "@/shared/api/supabase-client";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("仅限内部授权成员登录。");

  async function handleLogin() {
    if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
      setMessage("请先配置 Supabase 环境变量。");
      return;
    }

    const supabase = createBrowserSupabaseClient();
    const { error } = await supabase.auth.signInWithPassword({ email, password });

    if (error) {
      setMessage(error.message);
      return;
    }

    const redirectTo = new URLSearchParams(window.location.search).get("next") ?? "/dashboard";
    window.location.assign(redirectTo.startsWith("/") && !redirectTo.startsWith("//") ? redirectTo : "/dashboard");
  }

  return (
    <main className="min-h-screen bg-background px-6 py-8 text-foreground">
      <section className="mx-auto grid min-h-[calc(100vh-4rem)] w-full max-w-6xl items-center gap-10 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="max-w-2xl">
          <p className="mb-4 text-sm font-semibold uppercase tracking-[0.16em] text-primary">AI Shop OS</p>
          <h1 className="text-4xl font-semibold leading-tight md:text-5xl">
            登录你的 AI 电商员工操作系统
          </h1>
          <p className="mt-5 max-w-xl text-base leading-7 text-muted-foreground">
            老板每天打开系统，看到 AI 老板已经整理好的经营状态、风险事项和审批动作。
          </p>
        </div>

        <Card className="w-full p-6">
          <div>
            <label className="text-sm font-medium" htmlFor="email">
              邮箱
            </label>
            <input
              className="mt-2 h-11 w-full rounded-md border border-border bg-background px-3 outline-none focus:border-primary"
              id="email"
              onChange={(event) => setEmail(event.target.value)}
              placeholder="boss@example.com"
              type="email"
              value={email}
            />
          </div>

          <div className="mt-5">
            <label className="text-sm font-medium" htmlFor="password">
              密码
            </label>
            <input
              className="mt-2 h-11 w-full rounded-md border border-border bg-background px-3 outline-none focus:border-primary"
              id="password"
              onChange={(event) => setPassword(event.target.value)}
              placeholder="请输入密码"
              type="password"
              value={password}
            />
          </div>

          <Button className="mt-6 w-full" onClick={handleLogin} type="button">
            进入系统
          </Button>

          <p className="mt-4 text-xs leading-5 text-muted-foreground">{message}</p>
        </Card>
      </section>
    </main>
  );
}
