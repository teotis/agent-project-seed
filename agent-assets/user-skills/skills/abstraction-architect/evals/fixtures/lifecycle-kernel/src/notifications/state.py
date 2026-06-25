from enum import Enum


class NotificationState(str, Enum):
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    SNOOZED = "snoozed"
    BOUNCED = "bounced"
    EXPIRED = "expired"


NOTIFICATION_TRANSITIONS = {
    NotificationState.QUEUED: {
        NotificationState.SENT,
        NotificationState.SNOOZED,
        NotificationState.EXPIRED,
    },
    NotificationState.SENT: {
        NotificationState.DELIVERED,
        NotificationState.BOUNCED,
        NotificationState.EXPIRED,
    },
    NotificationState.DELIVERED: {NotificationState.READ, NotificationState.EXPIRED},
    NotificationState.READ: set(),
    NotificationState.SNOOZED: {NotificationState.QUEUED, NotificationState.EXPIRED},
    NotificationState.BOUNCED: {NotificationState.QUEUED, NotificationState.EXPIRED},
    NotificationState.EXPIRED: set(),
}


def should_retry_delivery(state: NotificationState) -> bool:
    return state in {NotificationState.SNOOZED, NotificationState.BOUNCED}


def is_visible_to_customer(state: NotificationState) -> bool:
    return state in {NotificationState.DELIVERED, NotificationState.READ}
