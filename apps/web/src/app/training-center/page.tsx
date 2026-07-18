import { TrainingCenterView } from "@/features/training-center/training-center-view";
import { getTrainingCenterSummaryForPage } from "@/shared/api/server-commerce-client";
import { AppShell } from "@/shared/ui/app-shell";

export default async function TrainingCenterPage() {
  const summary = await getTrainingCenterSummaryForPage();
  return (
    <AppShell>
      <TrainingCenterView summary={summary} />
    </AppShell>
  );
}

