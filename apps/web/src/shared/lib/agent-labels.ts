const agentNames: Record<string, string> = {
  "ai-boss": "AI 老板",
  "ai-customer": "AI 客服",
  "ai-operator": "AI 运营",
  "ai-after-sale": "AI 售后"
};

export function getAgentDisplayName(agentId: string, fallbackName: string): string {
  return agentNames[agentId] ?? fallbackName;
}
