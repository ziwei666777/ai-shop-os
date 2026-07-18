import { EvaluationView } from "@/features/evaluation/evaluation-view";
import { getEvaluationSummaryForPage } from "@/shared/api/server-commerce-client";
import { AppShell } from "@/shared/ui/app-shell";

export default async function EvaluationPage() {
  const summary = await getEvaluationSummaryForPage();
  return (
    <AppShell>
      <EvaluationView summary={summary} />
    </AppShell>
  );
}

