from enum import Enum


class JobType(Enum):
    LIST_REMINDER = "list_reminder"
    LIST_POLL = "list_poll"
    DAILY_RESET = "daily_reset"