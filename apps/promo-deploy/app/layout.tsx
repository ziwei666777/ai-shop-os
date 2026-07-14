import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "TerraElix | Plant-Based Wellness Supplements",
  description:
    "A responsive product showcase for TerraElix plant-based supplements, featuring natural formulas, clean energy, and daily wellness essentials."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
