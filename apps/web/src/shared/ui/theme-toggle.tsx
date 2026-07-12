"use client";

import { Laptop, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { Button } from "@/shared/ui/button";

export function ThemeToggle() {
  const [mounted, setMounted] = useState(false);
  const { setTheme, theme } = useTheme();

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <Button aria-label="主题" className="h-9 w-9 px-0" type="button" variant="ghost">
        <Laptop aria-hidden className="h-4 w-4" />
      </Button>
    );
  }

  const nextTheme = theme === "dark" ? "light" : theme === "light" ? "system" : "dark";
  const Icon = theme === "dark" ? Moon : theme === "light" ? Sun : Laptop;

  return (
    <Button
      aria-label="切换主题"
      className="h-9 w-9 px-0"
      onClick={() => setTheme(nextTheme)}
      title={`当前主题：${theme === "dark" ? "暗色" : theme === "light" ? "浅色" : "跟随系统"}`}
      type="button"
      variant="ghost"
    >
      <Icon aria-hidden className="h-4 w-4" />
    </Button>
  );
}
