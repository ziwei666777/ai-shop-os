import { CommerceDataView } from "@/features/commerce-data/commerce-data-view";
import { listCustomersForPage } from "@/shared/api/server-commerce-client";
import { AppShell } from "@/shared/ui/app-shell";

export default async function CustomersPage() {
  const customers = await listCustomersForPage();
  return <AppShell><CommerceDataView description="按平台和店铺汇总客户交易信息，只展示经营所需字段，不复制身份证或完整地址。" eyebrow="客户数据" primaryLabel="客户" secondaryLabel="平台客户编号" title="客户" valueLabel="订单 / 累计消费" rows={customers.map((customer) => ({ id: customer.id, platform: customer.platform, shopName: customer.shop_name, primary: customer.name, secondary: customer.external_id, status: customer.tags[0] ?? "普通客户", value: `${customer.order_count} 单 / ¥${customer.total_spent.toFixed(2)}`, updatedAt: customer.updated_at, details: [{ label: "客户名称", value: customer.name }, { label: "平台客户编号", value: customer.external_id }, { label: "累计订单", value: `${customer.order_count} 单` }, { label: "累计消费", value: `¥${customer.total_spent.toFixed(2)}` }, { label: "客户标签", value: customer.tags.join("、") }, { label: "店铺", value: customer.shop_name }] }))} /></AppShell>;
}
