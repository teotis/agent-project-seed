from enum import Enum


class RefundStatus(str, Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    EXECUTION_PENDING = "execution_pending"
    EXECUTED = "executed"
    RECONCILED = "reconciled"
    REJECTED = "rejected"


REFUND_TRANSITIONS = {
    RefundStatus.REQUESTED: {RefundStatus.APPROVED, RefundStatus.REJECTED},
    RefundStatus.APPROVED: {
        RefundStatus.EXECUTION_PENDING,
        RefundStatus.REJECTED,
    },
    RefundStatus.EXECUTION_PENDING: {RefundStatus.EXECUTED, RefundStatus.REJECTED},
    RefundStatus.EXECUTED: {RefundStatus.RECONCILED},
    RefundStatus.RECONCILED: set(),
    RefundStatus.REJECTED: set(),
}


def is_refund_closed(status: RefundStatus) -> bool:
    return status in {RefundStatus.RECONCILED, RefundStatus.REJECTED}


def is_refund_posted_to_ledger(status: RefundStatus) -> bool:
    return status == RefundStatus.RECONCILED
