from enum import Enum


class NotificationType(Enum):
    REMINDER = "reminder"  # обычное уведомление
    POLL = "poll"          # ежедневный опрос