import { IntegrationsView } from "@/features/settings/integrations-view";
import { listConnectorStatuses } from "@/shared/api/client";
import { AppShell } from "@/shared/ui/app-shell";

export default async function IntegrationsPage() {
  const connectors = await listConnectorStatuses();

  return (
    <AppShell>
      <IntegrationsView connectors={connectors} />
    </AppShell>
  );
}
