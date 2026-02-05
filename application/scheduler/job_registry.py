from domain.enums.job_type import JobType


# =========================================================
# Job registry
# =========================================================




class JobRegistry:
    @staticmethod
    def list_reminder(user_id: int, list_id: int) -> str:
        return f"{JobType.LIST_REMINDER.value}:{user_id}:{list_id}"

    @staticmethod
    def list_poll(user_id: int, list_id: int) -> str:
        return f"{JobType.LIST_POLL.value}:{user_id}:{list_id}"

    @staticmethod
    def daily_reset() -> str:
        return JobType.DAILY_RESET.value