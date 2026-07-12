import { ModuleStatusView } from "@/features/module-status/module-status-view";
import { AppShell } from "@/shared/ui/app-shell";

export default function WorkflowPage() {
  return (
    <AppShell>
      <ModuleStatusView
        description="工作流程用于约束 AI 员工的处理步骤、权限边界和人工审批节点。"
        nextStep="先完成客户消息处理和退款审批两条可追踪的工作流程（Workflow）。"
        title="工作流程"
      />
    </AppShell>
  );
}
