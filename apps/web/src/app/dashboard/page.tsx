import { getCeoDailyReport, getDashboardSummary, getLiveOperationSummary, getSavingsSummary } from "@/shared/api/client";
import { AppShell } from "@/shared/ui/app-shell";
import { DashboardView } from "@/features/dashboard/dashboard-view";

export default async function DashboardPage() {
  const [ceoReport, summary, liveOperation, savings] = await Promise.all([
    getCeoDailyReport(),
    getDashboardSummary(),
    getLiveOperationSummary(),
    getSavingsSummary()
  ]);

  return (
    <AppShell>
      <DashboardView ceoReport={ceoReport} liveOperation={liveOperation} savings={savings} summary={summary} />
    </AppShell>
  );
}