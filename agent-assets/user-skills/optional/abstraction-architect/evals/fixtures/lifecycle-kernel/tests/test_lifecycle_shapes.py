from src.customer_timeline import (
    notification_badge,
    order_badge,
    payment_badge,
    refund_badge,
)
from src.month_end_reconciliation import ledger_posting_kind


def test_financial_statuses_share_customer_badges():
    assert order_badge("capture_requested") == "moving_money"
    assert payment_badge("capture_queued") == "moving_money"
    assert refund_badge("execution_pending") == "moving_money"

    assert order_badge("settled") == "posted"
    assert payment_badge("reconciled") == "posted"
    assert refund_badge("reconciled") == "posted"


def test_notification_delivery_is_not_a_ledger_lifecycle():
    assert notification_badge("delivered") == "visible"
    assert ledger_posting_kind("notification", "delivered") == "not_a_ledger_event"
