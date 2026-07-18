from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from sqlalchemy import text
from sqlalchemy.orm import Session

from apps.api.app.infrastructure.config import get_settings
from apps.api.app.infrastructure.database import SessionFactory


SessionProvider = Callable[[], Session]
EvidenceSource = Literal["manual_payload", "real_order_records"]


@dataclass(frozen=True)
class RefundBusinessEvidence:
    source: EvidenceSource
    order_external_id: str | None
    order_amount_yuan: float
    delivered: bool
    inventory_available: bool
    evidence_count: int
    proof: str


def manual_refund_business_evidence(
    order_amount_yuan: float,
    delivered: bool,
    inventory_available: bool,
    evidence_count: int,
) -> RefundBusinessEvidence:
    return RefundBusinessEvidence(
        source="manual_payload",
        order_external_id=None,
        order_amount_yuan=order_amount_yuan,
        delivered=delivered,
        inventory_available=inventory_available,
        evidence_count=evidence_count,
        proof="manual payload supplied refund amount, delivery state, inventory state, and evidence count.",
    )


class PostgresRefundBusinessEvidenceRepository:
    def __init__(self, session_provider: SessionProvider) -> None:
        self.session_provider = session_provider
        self.company_id = get_settings().local_company_id

    def get_by_order_external_id(self, order_external_id: str) -> RefundBusinessEvidence | None:
        with self.session_provider() as session:
            order = session.execute(
                text(
                    """
                    select id::text, external_id, status, total_amount
                    from orders
                    where company_id = :company_id
                      and external_id = :external_id
                    order by updated_at desc
                    limit 1
                    """
                ),
                {"company_id": self.company_id, "external_id": order_external_id},
            ).mappings().one_or_none()
            if order is None:
                return None

            shipments = session.execute(
                text(
                    """
                    select status
                    from shipments
                    where company_id = :company_id
                      and order_id = cast(:order_id as uuid)
                    order by updated_at desc
                    """
                ),
                {"company_id": self.company_id, "order_id": str(order["id"])},
            ).mappings().all()

            inventory = session.execute(
                text(
                    """
                    select
                      count(*) as item_count,
                      coalesce(sum(oi.quantity), 0) as total_quantity,
                      coalesce(sum(case when p.inventory_count > 0 then 1 else 0 end), 0) as available_sku_count,
                      coalesce(sum(p.inventory_count), 0) as total_inventory
                    from order_items oi
                    left join products p
                      on p.company_id = oi.company_id
                     and (p.sku = oi.sku or p.external_id = oi.external_id)
                    where oi.company_id = :company_id
                      and oi.order_id = cast(:order_id as uuid)
                    """
                ),
                {"company_id": self.company_id, "order_id": str(order["id"])},
            ).mappings().one()

        shipment_statuses = [str(item["status"] or "unknown") for item in shipments]
        delivered = _order_is_delivered(str(order["status"]), shipment_statuses)
        item_count = int(inventory["item_count"] or 0)
        available_sku_count = int(inventory["available_sku_count"] or 0)
        total_inventory = int(inventory["total_inventory"] or 0)
        inventory_available = item_count > 0 and available_sku_count > 0 and total_inventory > 0
        evidence_count = 1 + item_count + len(shipment_statuses)
        proof = (
            f"real order evidence: order={order_external_id}, status={order['status']}, "
            f"shipments={shipment_statuses or ['missing']}, items={item_count}, "
            f"available_sku_count={available_sku_count}, total_inventory={total_inventory}."
        )

        return RefundBusinessEvidence(
            source="real_order_records",
            order_external_id=order_external_id,
            order_amount_yuan=float(order["total_amount"] or 0),
            delivered=delivered,
            inventory_available=inventory_available,
            evidence_count=evidence_count,
            proof=proof,
        )


def get_refund_business_evidence(order_external_id: str | None) -> RefundBusinessEvidence | None:
    if not order_external_id or SessionFactory is None:
        return None
    return PostgresRefundBusinessEvidenceRepository(lambda: SessionFactory()).get_by_order_external_id(order_external_id)


def _order_is_delivered(order_status: str, shipment_statuses: list[str]) -> bool:
    markers = ("delivered", "signed", "received", "completed", "已签收", "已收货", "已完成")
    values = [order_status.lower(), *(item.lower() for item in shipment_statuses)]
    return any(any(marker in value for marker in markers) for value in values)