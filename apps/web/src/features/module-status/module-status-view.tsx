import Link from "next/link";
import { ArrowLeft, Clock3 } from "lucide-react";
import { Badge } from "@/shared/ui/badge";
import { Card } from "@/shared/ui/card";

interface ModuleStatusViewProps {
  description: string;
  nextStep: string;
  title: string;
}

export function ModuleStatusView({ description, nextStep, title }: ModuleStatusViewProps) {
  return (
    <div className="space-y-6">
      <header className="border-b border-border pb-5">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-3xl font-semibold">{title}</h1>
          <Badge tone="amber">正在建设</Badge>
        </div>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">{description}</p>
      </header>

      <Card className="max-w-2xl p-5">
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-muted text-primary">
            <Clock3 aria-hidden className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-base font-semibold">下一项开发内容</h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">{nextStep}</p>
          </div>
        </div>
      </Card>

      <Link
        className="inline-flex h-10 items-center justify-center rounded-md border border-border bg-card px-4 text-sm font-medium transition hover:bg-accent"
        href="/dashboard"
      >
        <ArrowLeft aria-hidden className="mr-2 h-4 w-4" />
        返回老板首页
      </Link>
    </div>
  );
}
