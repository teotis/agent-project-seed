from enum import Enum


class PaymentPhase(str, Enum):
    CREATED = "created"
    AUTH_HELD = "auth_held"
    CAPTURE_QUEUED = "capture_queued"
    CAPTURED = "captured"
    RECONCILED = "reconciled"
    VOIDED = "voided"


PAYMENT_TRANSITIONS = {
    PaymentPhase.CREATED: {PaymentPhase.AUTH_HELD, PaymentPhase.VOIDED},
    PaymentPhase.AUTH_HELD: {PaymentPhase.CAPTURE_QUEUED, PaymentPhase.VOIDED},
    PaymentPhase.CAPTURE_QUEUED: {PaymentPhase.CAPTURED, PaymentPhase.VOIDED},
    PaymentPhase.CAPTURED: {PaymentPhase.RECONCILED},
    PaymentPhase.RECONCILED: set(),
    PaymentPhase.VOIDED: set(),
}


def is_payment_closed(phase: PaymentPhase) -> bool:
    return phase in {PaymentPhase.RECONCILED, PaymentPhase.VOIDED}


def is_payment_posted_to_ledger(phase: PaymentPhase) -> bool:
    return phase == PaymentPhase.RECONCILED
