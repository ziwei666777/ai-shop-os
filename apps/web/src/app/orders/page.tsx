import { CommerceDataView } from "@/features/commerce-data/commerce-data-view";
import { listOrdersForPage } from "@/shared/api/server-commerce-client";
import { AppShell } from "@/shared/ui/app-shell";

export default async function OrdersPage() {
  const orders = await listOrdersForPage();
  return <AppShell><CommerceDataView description="统一查看淘宝、抖音商店和闲鱼订单。当前模块只读，不会自动改价、发货或退款。" eyebrow="多平台交易数据" primaryLabel="订单号" secondaryLabel="客户" title="订单" valueLabel="实付金额" rows={orders.map((order) => ({ id: order.id, platform: order.platform, shopName: order.shop_name, primary: order.external_id, secondary: order.customer_name, status: order.status, value: `¥${order.total_amount.toFixed(2)}`, updatedAt: order.updated_at, details: [{ label: "平台订单号", value: order.external_id }, { label: "客户", value: order.customer_name }, { label: "订单状态", value: order.status }, { label: "实付金额", value: `¥${order.total_amount.toFixed(2)}` }, { label: "付款时间", value: order.paid_at ?? "未付款" }, { label: "店铺", value: order.shop_name }] }))} /></AppShell>;
}
