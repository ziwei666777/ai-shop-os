import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "AI Commerce OS | AI 电商员工操作系统",
  description: "面向电商企业的 AI 员工操作系统，从客服、售后、运营开始验证真实降本。"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
