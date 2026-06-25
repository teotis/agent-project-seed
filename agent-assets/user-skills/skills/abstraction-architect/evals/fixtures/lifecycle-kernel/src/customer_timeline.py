def order_badge(order_state: str) -> str:
    if order_state in {"open", "authorized"}:
        return "waiting"
    if order_state in {"capture_requested", "captured"}:
        return "moving_money"
    if order_state == "settled":
        return "posted"
    if order_state == "canceled":
        return "closed_without_posting"
    raise ValueError(f"unknown order state: {order_state}")


def payment_badge(payment_phase: str) -> str:
    if payment_phase in {"created", "auth_held"}:
        return "waiting"
    if payment_phase in {"capture_queued", "captured"}:
        return "moving_money"
    if payment_phase == "reconciled":
        return "posted"
    if payment_phase == "voided":
        return "closed_without_posting"
    raise ValueError(f"unknown payment phase: {payment_phase}")


def refund_badge(refund_status: str) -> str:
    if refund_status in {"requested", "approved"}:
        return "waiting"
    if refund_status in {"execution_pending", "executed"}:
        return "moving_money"
    if refund_status == "reconciled":
        return "posted"
    if refund_status == "rejected":
        return "closed_without_posting"
    raise ValueError(f"unknown refund status: {refund_status}")


def notification_badge(notification_state: str) -> str:
    if notification_state in {"queued", "sent", "snoozed"}:
        return "pending_delivery"
    if notification_state in {"delivered", "read"}:
        return "visible"
    if notification_state in {"bounced", "expired"}:
        return "not_visible"
    raise ValueError(f"unknown notification state: {notification_state}")
