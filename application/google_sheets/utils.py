import re


def extract_sheet_id(sheet_url: str) -> str:
    """
    Извлекает sheet_id из Google Sheets URL
    """
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", sheet_url)
    if not match:
        raise ValueError("Invalid Google Sheets URL")

    return match.group(1)
