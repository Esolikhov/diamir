import telebot
from config import TELEGRAM_BOT_TOKEN
from whatsapp_api import send_whatsapp_message

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    # Если оператор отвечает реплаем (reply) на обращение — пересылаем в WhatsApp пользователя
    if message.reply_to_message:
        lines = message.reply_to_message.text.splitlines()
        wa_phone = None
        for line in lines:
            if line.lower().startswith("телефон:"):
                wa_phone = line.split(":", 1)[1].strip()
        if wa_phone:
            send_whatsapp_message(wa_phone, f"Ответ поддержки: {message.text}")
            bot.reply_to(message, "✅ Ответ отправлен в WhatsApp!")
            return
    # Альтернативно: /ответ <номер> <текст>
    if message.text.startswith("/ответ"):
        parts = message.text.split(maxsplit=2)
        if len(parts) == 3:
            wa_phone, reply_text = parts[1], parts[2]
            send_whatsapp_message(wa_phone, f"Ответ поддержки: {reply_text}")
            bot.reply_to(message, "✅ Ответ отправлен в WhatsApp!")
        else:
            bot.reply_to(message, "Используйте: /ответ <номер> <текст>")

bot.polling(none_stop=True)
