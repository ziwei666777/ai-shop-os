import { notFound } from "next/navigation";
import { getAgent, listAgentLogs } from "@/shared/api/client";
import { AgentDetailView } from "@/features/ai-employees/agent-detail-view";
import { AppShell } from "@/shared/ui/app-shell";

interface AgentDetailPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function AgentDetailPage({ params }: AgentDetailPageProps) {
  const { id } = await params;
  const agent = await getAgent(id);

  if (!agent) {
    notFound();
  }

  const logs = await listAgentLogs(id);

  return (
    <AppShell>
      <AgentDetailView agent={agent} logs={logs} />
    </AppShell>
  );
}
