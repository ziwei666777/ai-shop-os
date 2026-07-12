import { ModuleStatusView } from "@/features/module-status/module-status-view";
import { AppShell } from "@/shared/ui/app-shell";

export default function AnalyticsPage() {
  return (
    <AppShell>
      <ModuleStatusView
        description="经营分析将汇总销售、利润、库存、退款以及 AI 员工的工作效果。"
        nextStep="接入真实订单数据，形成老板可直接审批和执行的经营结论。"
        title="经营分析"
      />
    </AppShell>
  );
}
