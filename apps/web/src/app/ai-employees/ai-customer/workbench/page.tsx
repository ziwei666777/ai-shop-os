import { CustomerWorkbenchView } from "@/features/customer-agent/customer-workbench-view";
import { listCustomerInbox } from "@/shared/api/client";
import { AppShell } from "@/shared/ui/app-shell";

export default async function CustomerAgentWorkbenchPage({
  searchParams
}: {
  searchParams?: Promise<{ message?: string }>;
}) {
  const inbox = await listCustomerInbox();
  const params = await searchParams;
  const selectedMessageId = params?.message;

  return (
    <AppShell>
      <CustomerWorkbenchView inbox={inbox} initialSelectedId={selectedMessageId} />
    </AppShell>
  );
}
