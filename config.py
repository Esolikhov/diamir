from dotenv import load_dotenv
import os

# Загружаем переменные из .env
load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
SHEET_ID = os.getenv("SHEET_ID")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_SUPPORT_CHAT_ID = int(os.getenv("TELEGRAM_SUPPORT_CHAT_ID"))  # число
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_ID}/messages"

# Проверим, что переменные загрузились
if not all([WHATSAPP_TOKEN, WHATSAPP_PHONE_ID, VERIFY_TOKEN, SHEET_ID, SERVICE_ACCOUNT_FILE, TELEGRAM_BOT_TOKEN, TELEGRAM_SUPPORT_CHAT_ID, OPENAI_API_KEY]):
    raise ValueError("Одна или несколько переменных окружения не установлены!")
