import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "TerraElix | 中文商品展示页",
  description: "TerraElix 植萃营养胶囊中文电商商品展示页，包含商品、价格、卖点、评价与购买入口。"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
