def can_close_order_batch(order_states: list[str]) -> bool:
    return all(state in {"settled", "canceled"} for state in order_states)


def can_close_payment_batch(payment_phases: list[str]) -> bool:
    return all(phase in {"reconciled", "voided"} for phase in payment_phases)


def can_close_refund_batch(refund_statuses: list[str]) -> bool:
    return all(status in {"reconciled", "rejected"} for status in refund_statuses)


def can_close_notification_digest(notification_states: list[str]) -> bool:
    return all(state in {"read", "expired"} for state in notification_states)


def ledger_posting_kind(kind: str, state: str) -> str:
    if kind == "order" and state == "settled":
        return "posted"
    if kind == "payment" and state == "reconciled":
        return "posted"
    if kind == "refund" and state == "reconciled":
        return "posted"
    if kind in {"order", "payment", "refund"}:
        return "not_posted"
    if kind == "notification":
        return "not_a_ledger_event"
    raise ValueError(f"unknown kind: {kind}")
