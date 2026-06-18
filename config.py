import os
import pytz

MAX_BOT_TOKEN = os.getenv("MAX_BOT_TOKEN") or os.getenv("BOT_TOKEN") or os.getenv("MAX_TOKEN")
VPOSTER_API_TOKEN = os.getenv("VPOSTER_API_TOKEN")

MAX_API_URL = "https://httpbin.org"
VPOSTER_API_URL = "https://api.vposter.ru/v1"

MOSCOW_TZ = pytz.timezone('Europe/Moscow')
