import { getDashboardSummary } from "@/shared/api/client";
import { AppShell } from "@/shared/ui/app-shell";
import { DashboardView } from "@/features/dashboard/dashboard-view";

export default async function DashboardPage() {
  const summary = await getDashboardSummary();

  return (
    <AppShell>
      <DashboardView summary={summary} />
    </AppShell>
  );
}
