import Link from "next/link";

export default function NotFoundPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-6 text-foreground">
      <section className="w-full max-w-lg text-center">
        <p className="text-sm font-medium text-primary">页面不存在</p>
        <h1 className="mt-3 text-3xl font-semibold">没有找到你要打开的页面</h1>
        <p className="mt-3 text-sm leading-6 text-muted-foreground">该入口可能正在建设，或者地址已经发生变化。</p>
        <Link
          className="mt-6 inline-flex h-10 items-center justify-center rounded-md border border-border bg-card px-4 text-sm font-medium transition hover:bg-accent"
          href="/dashboard"
        >
          返回老板首页
        </Link>
      </section>
    </main>
  );
}
