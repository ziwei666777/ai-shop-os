import { CommerceDatasetView } from "@/features/commerce-dataset/commerce-dataset-view";
import { getCommerceDatasetReadinessForPage } from "@/shared/api/server-commerce-client";
import { AppShell } from "@/shared/ui/app-shell";

export default async function CommerceDatasetPage() {
  const summary = await getCommerceDatasetReadinessForPage();
  return (
    <AppShell>
      <CommerceDatasetView summary={summary} />
    </AppShell>
  );
}
