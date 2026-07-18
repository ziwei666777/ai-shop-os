import { ReplayView } from "@/features/replay/replay-view";
import { getReplaySummaryForPage } from "@/shared/api/server-commerce-client";
import { AppShell } from "@/shared/ui/app-shell";

export default async function ReplayPage() {
  const summary = await getReplaySummaryForPage();
  return (
    <AppShell>
      <ReplayView summary={summary} />
    </AppShell>
  );
}
