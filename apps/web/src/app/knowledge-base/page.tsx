import { KnowledgeBaseView } from "@/features/knowledge-base/knowledge-base-view";
import { AppShell } from "@/shared/ui/app-shell";

export default function KnowledgeBasePage() {
  return (
    <AppShell>
      <KnowledgeBaseView />
    </AppShell>
  );
}
