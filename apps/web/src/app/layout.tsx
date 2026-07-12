import type { Metadata } from "next";
import { ThemeProvider } from "@/shared/ui/theme-provider";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "AI Shop OS",
    template: "%s | AI Shop OS"
  },
  description: "AI 电商员工操作系统"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
