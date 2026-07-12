import type { HTMLAttributes } from "react";
import { cn } from "@/shared/lib/utils";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: "green" | "amber" | "neutral";
}

export function Badge({ className, tone = "neutral", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex h-7 items-center rounded-md px-2.5 text-xs font-medium",
        tone === "green" && "bg-primary/12 text-primary",
        tone === "amber" && "bg-warning/15 text-warning",
        tone === "neutral" && "bg-muted text-muted-foreground",
        className
      )}
      {...props}
    />
  );
}
