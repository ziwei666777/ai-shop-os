import { AfterSaleWorkbenchView } from "@/features/after-sale-agent/after-sale-workbench-view";
import { listAfterSaleCases } from "@/shared/api/client";
import { AppShell } from "@/shared/ui/app-shell";

export default async function AfterSaleWorkbenchPage() {
  const cases = await listAfterSaleCases();

  return (
    <AppShell>
      <AfterSaleWorkbenchView cases={cases} />
    </AppShell>
  );
}
