from application.google_sheets.service import GoogleSheetsService
from application.google_sheets.utils import extract_sheet_id


def create_sheets_service(user) -> GoogleSheetsService:
    sheet_id = extract_sheet_id(user.google_sheet_url)
    return GoogleSheetsService(sheet_id)
