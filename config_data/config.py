from os import getenv
from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = getenv('BOT_TOKEN')
GOOGLE_SERVICE_ACCOUNT_JSON = getenv('GOOGLE_SERVICE_ACCOUNT_JSON')