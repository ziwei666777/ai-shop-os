"use client";

import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";
import { useEffect, type ReactNode } from "react";
import { Button } from "@/shared/ui/button";
import { cn } from "@/shared/lib/utils";

interface DetailDrawerProps {
  children: ReactNode;
  description?: string;
  footer?: ReactNode;
  onClose: () => void;
  open: boolean;
  title: string;
}

export function DetailDrawer({ children, description, footer, onClose, open, title }: DetailDrawerProps) {
  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    if (!open) {
      return;
    }

    document.addEventListener("keydown", handleKeyDown);
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [onClose, open]);

  return (
    <AnimatePresence>
      {open ? (
        <div className="fixed inset-0 z-50">
          <motion.button
            aria-label="关闭详情"
            className="absolute inset-0 bg-background/70 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            type="button"
          />
          <motion.aside
            aria-modal="true"
            className={cn(
              "absolute right-0 top-0 flex h-full w-full max-w-xl flex-col border-l border-border bg-card shadow-soft",
              "sm:rounded-l-md"
            )}
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ duration: 0.2, ease: "easeOut" }}
          >
            <header className="flex items-start justify-between gap-4 border-b border-border px-5 py-4">
              <div className="min-w-0">
                <h2 className="truncate text-lg font-semibold">{title}</h2>
                {description ? <p className="mt-1 text-sm leading-6 text-muted-foreground">{description}</p> : null}
              </div>
              <Button aria-label="关闭详情" className="h-9 w-9 shrink-0 px-0" onClick={onClose} type="button" variant="ghost">
                <X aria-hidden className="h-4 w-4" />
              </Button>
            </header>

            <div className="min-h-0 flex-1 overflow-y-auto px-5 py-5">{children}</div>

            {footer ? <footer className="border-t border-border bg-background/70 px-5 py-4">{footer}</footer> : null}
          </motion.aside>
        </div>
      ) : null}
    </AnimatePresence>
  );
}
