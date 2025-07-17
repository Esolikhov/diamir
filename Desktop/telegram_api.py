import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_SUPPORT_CHAT_ID
from whatsapp_api import send_whatsapp_message

def send_to_telegram(text, phone):
    """Отправляет сообщение в Telegram оператору поддержки"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    # Внимание! ВАЖНО: вставляем номер в начало сообщения для reply!
    message = f"Пользователь WhatsApp: {phone}\n\n{text}"
    data = {"chat_id": TELEGRAM_SUPPORT_CHAT_ID, "text": message}
    resp = requests.post(url, data=data)
    print("Ответ Telegram:", resp.status_code, resp.text)
    return resp



import telebot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(func=lambda m: m.reply_to_message is not None)
def reply_handler(message):
    # Извлекаем номер WhatsApp из текста сообщения, на которое оператор отвечает
    lines = message.reply_to_message.text.splitlines()
    wa_phone = None
    for line in lines:
        if line.lower().startswith("пользователь whatsapp"):
            wa_phone = line.split(":", 1)[1].strip()
    if wa_phone:
        send_whatsapp_message(wa_phone, f"Ответ поддержки:\n{message.text}")
        bot.reply_to(message, "Ответ отправлен пользователю WhatsApp!")
    else:
        bot.reply_to(message, "❗ Не найден номер WhatsApp для ответа.")

if __name__ == "__main__":
    print("Telegram поддержка-бот запущен.")
    bot.polling(none_stop=True)
