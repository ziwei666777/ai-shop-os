import { CustomerWorkbenchView } from "@/features/customer-agent/customer-workbench-view";
import { listCustomerInbox } from "@/shared/api/client";
import { AppShell } from "@/shared/ui/app-shell";

export default async function CustomerAgentWorkbenchPage() {
  const inbox = await listCustomerInbox();

  return (
    <AppShell>
      <CustomerWorkbenchView inbox={inbox} />
    </AppShell>
  );
}
