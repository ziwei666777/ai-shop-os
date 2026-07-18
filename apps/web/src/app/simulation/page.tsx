import { SimulationView } from "@/features/simulation/simulation-view";
import { getSimulationSummaryForPage } from "@/shared/api/server-commerce-client";
import { AppShell } from "@/shared/ui/app-shell";

export default async function SimulationPage() {
  const summary = await getSimulationSummaryForPage();
  return (
    <AppShell>
      <SimulationView summary={summary} />
    </AppShell>
  );
}

