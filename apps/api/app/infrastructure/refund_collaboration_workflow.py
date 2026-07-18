from __future__ import annotations

from uuid import uuid4

from apps.api.app.domain.refund_collaboration import RefundCollaborationRun, RefundWorkflowStep
from apps.api.app.infrastructure.approval_records import record_refund_workflow_approval
from apps.api.app.infrastructure.refund_business_evidence import RefundBusinessEvidence, manual_refund_business_evidence


_RUNS: list[RefundCollaborationRun] = []


def run_refund_collaboration_workflow(
    source_message_id: str,
    customer_message: str,
    order_amount_yuan: float,
    refund_amount_yuan: float,
    delivered: bool,
    evidence_count: int,
    inventory_available: bool,
    complaint_risk: bool,
    business_evidence: RefundBusinessEvidence | None = None,
) -> RefundCollaborationRun:
    """Run an execution-level collaboration workflow for refund/complaint cases."""

    evidence = business_evidence or manual_refund_business_evidence(
        order_amount_yuan=order_amount_yuan,
        delivered=delivered,
        inventory_available=inventory_available,
        evidence_count=evidence_count,
    )
    order_amount_yuan = evidence.order_amount_yuan
    delivered = evidence.delivered
    inventory_available = evidence.inventory_available
    evidence_count = evidence.evidence_count

    refund_ratio = refund_amount_yuan / order_amount_yuan if order_amount_yuan else 1
    needs_more_evidence = evidence_count <= 0
    high_money_risk = refund_ratio >= 0.5 or refund_amount_yuan >= 200
    requires_boss = complaint_risk or high_money_risk

    if needs_more_evidence:
        decision = "need_more_evidence"
        status = "blocked"
        reply = "Evidence is missing. Customer service should request photos, order number, and logistics status before AI after-sale continues."
        next_actions = (
            "Ask the customer for photos, order number, and logistics status.",
            "Re-enter the after-sale workflow after evidence is complete.",
        )
    elif not delivered and inventory_available:
        decision = "replacement"
        status = "approval_required" if requires_boss else "ready_to_reply"
        reply = "Order and inventory evidence support replacement first, avoiding direct refund loss."
        next_actions = (
            "After-sale Agent generates a replacement recommendation.",
            "Warehouse confirms replacement inventory.",
            "Customer service replies based on approval result.",
        )
    elif requires_boss:
        decision = "refund_review"
        status = "approval_required"
        reply = "This case has high amount or complaint risk. AI has organized evidence and is waiting for boss approval."
        next_actions = (
            "Boss approves refund, compensation, or rejection.",
            "After-sale Agent records refund reason and after-sale cost.",
            "Customer service replies according to the boss decision.",
        )
    else:
        decision = "compensation_review"
        status = "ready_to_reply"
        reply = "Low-risk after-sale case verified. Recommend small compensation or exchange and record the reason."
        next_actions = (
            "After-sale Agent generates low-risk handling plan.",
            "Customer service sends confirmation script.",
            "Training Center keeps this handling experience for review.",
        )

    run_id = f"refund-workflow-{uuid4()}"
    saved_minutes = 18 if status == "ready_to_reply" else 24
    estimated_saving_yuan = _minutes_to_yuan(saved_minutes)
    approval_required = status == "approval_required"
    proof = (
        f"Refund workflow handled message {source_message_id}: decision={decision}, "
        f"refund={refund_amount_yuan:.0f}, order_amount={order_amount_yuan:.0f}, "
        f"evidence={evidence_count}, approval={approval_required}, source={evidence.source}. {evidence.proof}"
    )

    approval_id = None
    if approval_required:
        approval = record_refund_workflow_approval(
            workflow_run_id=run_id,
            source_message_id=source_message_id,
            refund_amount_yuan=refund_amount_yuan,
            reason=proof,
        )
        approval_id = approval.id

    steps = (
        RefundWorkflowStep(
            id="customer-detect-refund",
            agent_id="ai-customer",
            title="Detect refund or complaint intent",
            status="done",
            evidence=customer_message[:160],
            requires_approval=False,
        ),
        RefundWorkflowStep(
            id="after-sale-policy-check",
            agent_id="ai-after-sale",
            title="Judge refund, replacement, compensation, or evidence gap",
            status="blocked" if needs_more_evidence else "done",
            evidence=f"refund_ratio={refund_ratio:.2f}, delivered={delivered}, evidence_count={evidence_count}, source={evidence.source}",
            requires_approval=False,
        ),
        RefundWorkflowStep(
            id="inventory-order-check",
            agent_id="ai-operator",
            title="Check order state, logistics, and replacement inventory",
            status="done" if evidence.source == "real_order_records" or not needs_more_evidence else "blocked",
            evidence=f"inventory_available={inventory_available}, order_amount_yuan={order_amount_yuan:.0f}; {evidence.proof}",
            requires_approval=False,
        ),
        RefundWorkflowStep(
            id="boss-approval",
            agent_id="ai-boss",
            title="Approve high-risk refund or compensation",
            status="needs_approval" if approval_required else "done",
            evidence=f"complaint_risk={complaint_risk}, high_money_risk={high_money_risk}, approval_id={approval_id}",
            requires_approval=approval_required,
        ),
        RefundWorkflowStep(
            id="customer-reply",
            agent_id="ai-customer",
            title="Generate final customer reply after workflow decision",
            status="blocked" if needs_more_evidence else ("needs_approval" if approval_required else "done"),
            evidence=reply,
            requires_approval=approval_required,
        ),
    )

    run = RefundCollaborationRun(
        id=run_id,
        source_message_id=source_message_id,
        status=status,  # type: ignore[arg-type]
        decision=decision,  # type: ignore[arg-type]
        saved_minutes=saved_minutes,
        estimated_saving_yuan=estimated_saving_yuan,
        evidence_source=evidence.source,
        proof=proof,
        approval_id=approval_id,
        customer_reply=reply,
        next_actions=next_actions,
        steps=steps,
    )
    _RUNS.append(run)
    return run


def list_refund_collaboration_runs(limit: int = 50) -> tuple[RefundCollaborationRun, ...]:
    return tuple(reversed(_RUNS[-limit:]))


def summarize_refund_collaboration_runs() -> dict[str, int | str]:
    if not _RUNS:
        return {
            "completed_work_count": 0,
            "saved_minutes": 0,
            "saved_yuan": 0,
            "proof": "",
        }
    saved_minutes = sum(run.saved_minutes for run in _RUNS)
    saved_yuan = sum(run.estimated_saving_yuan for run in _RUNS)
    latest = _RUNS[-1]
    return {
        "completed_work_count": len(_RUNS),
        "saved_minutes": saved_minutes,
        "saved_yuan": saved_yuan,
        "proof": f"Recorded {len(_RUNS)} refund collaboration workflows. Latest: {latest.proof}",
    }


def clear_refund_collaboration_runs_for_test() -> None:
    _RUNS.clear()


def _minutes_to_yuan(minutes: int) -> int:
    hourly_cost_yuan = 45
    return round(minutes / 60 * hourly_cost_yuan)