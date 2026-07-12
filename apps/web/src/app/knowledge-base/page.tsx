import { ModuleStatusView } from "@/features/module-status/module-status-view";
import { AppShell } from "@/shared/ui/app-shell";

export default function KnowledgeBasePage() {
  return (
    <AppShell>
      <ModuleStatusView
        description="知识库将保存商品说明、售后规则和老板经验，供所有 AI 员工共享。"
        nextStep="完成文件上传、内容切分和检索增强知识库（RAG）查询流程。"
        title="知识库"
      />
    </AppShell>
  );
}
