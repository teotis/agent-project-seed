from enum import Enum


class OrderState(str, Enum):
    OPEN = "open"
    AUTHORIZED = "authorized"
    CAPTURE_REQUESTED = "capture_requested"
    CAPTURED = "captured"
    SETTLED = "settled"
    CANCELED = "canceled"


ORDER_TRANSITIONS = {
    OrderState.OPEN: {OrderState.AUTHORIZED, OrderState.CANCELED},
    OrderState.AUTHORIZED: {OrderState.CAPTURE_REQUESTED, OrderState.CANCELED},
    OrderState.CAPTURE_REQUESTED: {OrderState.CAPTURED, OrderState.CANCELED},
    OrderState.CAPTURED: {OrderState.SETTLED},
    OrderState.SETTLED: set(),
    OrderState.CANCELED: set(),
}


def is_order_closed(state: OrderState) -> bool:
    return state in {OrderState.SETTLED, OrderState.CANCELED}


def is_order_posted_to_ledger(state: OrderState) -> bool:
    return state == OrderState.SETTLED
