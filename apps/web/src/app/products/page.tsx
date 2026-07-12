import { CommerceDataView } from "@/features/commerce-data/commerce-data-view";
import { listProductsForPage } from "@/shared/api/server-commerce-client";
import { AppShell } from "@/shared/ui/app-shell";

export default async function ProductsPage() {
  const products = await listProductsForPage();
  return <AppShell><CommerceDataView description="统一查看三个国内平台的商品、价格与库存，帮助 AI 客服引用可信商品信息。" eyebrow="多平台商品目录" primaryLabel="商品" secondaryLabel="商家编码" title="商品" valueLabel="价格 / 库存" rows={products.map((product) => ({ id: product.id, platform: product.platform, shopName: product.shop_name, primary: product.title, secondary: product.sku || product.external_id, status: product.status, value: `¥${product.price.toFixed(2)} / ${product.inventory_count}`, updatedAt: product.updated_at, details: [{ label: "商品名称", value: product.title }, { label: "平台商品编号", value: product.external_id }, { label: "商家编码", value: product.sku }, { label: "销售价格", value: `¥${product.price.toFixed(2)}` }, { label: "可售库存", value: `${product.inventory_count}` }, { label: "店铺", value: product.shop_name }] }))} /></AppShell>;
}
