import requests

TELEGRAM_BOT_TOKEN = "8035255326:AAEQ9ZVC2jfXQJ6bIHXy6mKDfJ4vunFJLuE"
SUPPORT_CHAT_ID = 623765402

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": SUPPORT_CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

def send_to_telegram_with_info(phone, user_message):
    text = f"Вопрос от WhatsApp пользователя {phone}:\n{user_message}\n\nОтветьте на это сообщение — ваш ответ уйдет пользователю!"
    send_to_telegram(text)

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {"timeout": 60}
    if offset:
        params["offset"] = offset
    return requests.get(url, params=params).json()

def send_message_to_whatsapp(phone, text):
    from whatsapp_api import send_whatsapp_message
    send_whatsapp_message(phone, text)
