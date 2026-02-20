from enum import Enum


class NotificationType(Enum):
    REMINDER = "reminder"  # обычное уведомление
    POLL = "poll"          # ежедневный опрос

    def toggle(self):
        if self == NotificationType.REMINDER:
            return NotificationType.POLL
        return NotificationType.REMINDER

    def label(self):
        return {
            NotificationType.REMINDER: "⏰ Напоминание",
            NotificationType.POLL: "📊 Опрос",
        }[self]