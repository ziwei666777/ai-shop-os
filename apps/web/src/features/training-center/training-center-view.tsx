"use client";

import Link from "next/link";
import { ArrowRight, Brain, Database, Workflow } from "lucide-react";
import { useState } from "react";
import { commitTrainingAsset } from "@/shared/api/client";
import type { TrainingAssetCandidate, TrainingCenterSummary, TrainingSample } from "@/shared/api/types";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";

const targetLabels: Record<TrainingSample["training_target"], string> = {
  knowledge: "进入知识库",
  memory: "进入记忆",
  workflow: "进入流程"
};

export function TrainingCenterView({ summary }: { summary: TrainingCenterSummary }) {
  const [candidates, setCandidates] = useState(summary.asset_candidates);
  const [feedback, setFeedback] = useState<string | null>(null);

  async function handleCommit(candidateId: string) {
    setFeedback(null);
    const result = await commitTrainingAsset(candidateId);
    if (result.error || !result.data) {
      setFeedback(result.error ?? "沉淀失败，请稍后再试。");
      return;
    }
    setCandidates((items) => items.map((item) => (item.id === candidateId ? result.data! : item)));
    setFeedback("已沉淀到长期候选资产，后续可被 Memory / Knowledge / Workflow 复用。");
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 border-b border-border pb-5 lg:flex-row lg:items-end">
        <div>
          <p className="text-sm font-medium text-primary">Training Center V0.1</p>
          <h1 className="mt-2 text-3xl font-semibold">训练中心</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            老板每改一次回复、每审批一次售后，系统都要把经验沉淀下来。这里负责把修改样本转成记忆、知识库和工作流程。
          </p>
        </div>
        <Link className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground" href="/simulation">
          去模拟压测
          <ArrowRight aria-hidden className="ml-2 h-4 w-4" />
        </Link>
      </header>

      <section className="grid gap-3 md:grid-cols-5">
        <Metric label="学习样本" value={`${summary.total_samples}`} />
        <Metric label="可用样本" value={`${summary.usable_samples}`} />
        <Metric label="记忆候选" value={`${summary.memory_candidates}`} />
        <Metric label="知识候选" value={`${summary.knowledge_candidates}`} />
        <Metric label="流程候选" value={`${summary.workflow_candidates}`} />
      </section>

      <section className="grid gap-4">
        {summary.samples.map((sample) => (
          <TrainingSampleCard key={sample.id} sample={sample} />
        ))}
      </section>

      <Card className="p-5">
        <div className="flex flex-col gap-2 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h2 className="font-semibold">沉淀候选池</h2>
            <p className="mt-1 text-sm text-muted-foreground">这里显示每条老板修改会进入记忆、知识库还是工作流程。当前是候选池，后续再写入长期存储。</p>
          </div>
          <Badge tone="green">{candidates.filter((item) => item.status === "candidate").length} 条可沉淀</Badge>
        </div>
        {feedback ? <p className="mt-4 rounded-md bg-muted p-3 text-sm text-muted-foreground">{feedback}</p> : null}
        <div className="mt-4 grid gap-3 lg:grid-cols-3">
          {candidates.map((candidate) => (
            <AssetCandidateCard candidate={candidate} key={candidate.id} onCommit={handleCommit} />
          ))}
        </div>
      </Card>

      <Card className="p-5">
        <h2 className="font-semibold">训练中心下一步</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          {summary.next_actions.map((item, index) => (
            <div key={item} className="rounded-md bg-muted p-3 text-sm leading-6 text-muted-foreground">
              <span className="mb-2 block text-xs font-medium text-foreground">步骤 {index + 1}</span>
              {item}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

function AssetCandidateCard({ candidate, onCommit }: { candidate: TrainingAssetCandidate; onCommit: (candidateId: string) => Promise<void> }) {
  const Icon = candidate.target === "memory" ? Brain : candidate.target === "knowledge" ? Database : Workflow;
  const isCommitted = candidate.status === "committed";
  const canCommit = candidate.status === "candidate";
  return (
    <div className="rounded-md border border-border bg-background p-4">
      <div className="flex items-start justify-between gap-3">
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
          <Icon aria-hidden className="h-4 w-4" />
        </span>
        <Badge tone={isCommitted || candidate.status === "candidate" ? "green" : "amber"}>
          {isCommitted ? "已沉淀" : candidate.status === "candidate" ? "候选" : "待复核"}
        </Badge>
      </div>
      <h3 className="mt-3 text-sm font-semibold">{candidate.title}</h3>
      <p className="mt-2 text-xs leading-5 text-muted-foreground">{candidate.content}</p>
      <p className="mt-3 rounded-md bg-muted p-2 text-xs leading-5 text-muted-foreground">{candidate.business_value}</p>
      <Button className="mt-4 w-full" disabled={!canCommit} onClick={() => void onCommit(candidate.id)} type="button" variant={canCommit ? "primary" : "secondary"}>
        {isCommitted ? "已沉淀" : canCommit ? "确认沉淀" : "等待复核"}
      </Button>
    </div>
  );
}

function TrainingSampleCard({ sample }: { sample: TrainingSample }) {
  const Icon = sample.training_target === "memory" ? Brain : sample.training_target === "knowledge" ? Database : Workflow;
  return (
    <Card className="p-5">
      <div className="flex flex-col justify-between gap-3 lg:flex-row lg:items-start">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 text-primary">
            <Icon aria-hidden className="h-4 w-4" />
          </span>
          <div>
            <p className="font-semibold">{sample.agent_name}</p>
            <p className="text-xs text-muted-foreground">{targetLabels[sample.training_target]}</p>
          </div>
        </div>
        <Badge tone={sample.status === "ready" ? "green" : "amber"}>{sample.status === "ready" ? "可训练" : "待复核"}</Badge>
      </div>
      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <TextPanel title="AI 原内容" text={sample.original_content} />
        <TextPanel title="老板最终修改" text={sample.final_content} />
      </div>
    </Card>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <Card className="p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </Card>
  );
}

function TextPanel({ text, title }: { text: string; title: string }) {
  return (
    <div className="rounded-md border border-border bg-background p-4">
      <p className="text-xs font-medium text-muted-foreground">{title}</p>
      <p className="mt-2 text-sm leading-6">{text}</p>
    </div>
  );
}
