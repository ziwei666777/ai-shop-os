import { listAgents } from "@/shared/api/client";
import { AppShell } from "@/shared/ui/app-shell";
import { AgentsListView } from "@/features/ai-employees/agents-list-view";

export default async function AiEmployeesPage() {
  const agents = await listAgents();

  return (
    <AppShell>
      <AgentsListView agents={agents} />
    </AppShell>
  );
}
