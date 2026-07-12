import { DataCollectionView } from "@/features/settings/data-collection-view";
import { listFeedbackMetrics } from "@/shared/api/client";
import { AppShell } from "@/shared/ui/app-shell";

export default async function DataCollectionPage() {
  const metrics = await listFeedbackMetrics();

  return (
    <AppShell>
      <DataCollectionView metrics={metrics} />
    </AppShell>
  );
}
