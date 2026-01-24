import json
import os

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta


class GoogleSheetsService:
    """
    Сервис для работы с Google Таблицами.
    """

    def __init__(self, sheet_id: str):
        """
        Инициализация сервиса Google Sheets.
        """
        service_json = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
        creds_dict = json.loads(service_json)

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]


        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=scopes
        )

        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(sheet_id).sheet1

    def append_task(self,
                    list_title: str,
                    task_value: str,
                    completed: bool
                    ):

        status_emoji = "🟢" if completed else "🔴"
        """
        Добавляет информацию об одной задаче в Google Таблицу.
        Одна строка в таблице = одна задача пользователя.
        """
        self.sheet.append_row([
            datetime.now().strftime("%Y-%m-%d"),
            list_title,
            task_value,
            status_emoji,
            "done" if completed else "missed"
        ])

    def append_day_header(self, date_str: str):
        """
        Добавляет строку-заголовок нового дня
        """
        self.sheet.append_row([
            date_str,
            "📅 ОТЧЁТ ЗА ДЕНЬ",
            "",
            "",
            ""
        ])

    def ensure_day_header(self):
        # Получаем вчерашнюю дату
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        values = self.sheet.col_values(1)

        last_date = None
        for value in reversed(values):
            if value.strip():
                last_date = value
                break

        if last_date != yesterday:
            self.append_day_header(yesterday)