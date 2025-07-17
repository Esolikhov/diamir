# bot.py
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from db_utils import db_init, add_user, get_user, get_material_by_day, update_user_lesson

import os

TOKEN = '7785563549:AAG9MXHaIaGLGwAtLaScrOO-_1q7DUAG-Gk'

# Инициализация базы данных
db_init()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if user:
        await update.message.reply_text(
            f"Вы уже зарегистрированы, {user['name']}!\n"
            "Чтобы получить урок, напишите /lesson"
        )
    else:
        await update.message.reply_text("Здравствуйте! Введите ваше имя для регистрации:")
        return 1  # Ожидание имени

async def register_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    add_user(update.effective_user.id, name)
    await update.message.reply_text(
        f"Спасибо, {name}! Вы зарегистрированы.\n"
        "Чтобы получить урок, напишите /lesson"
    )
    return -1  # Завершить регистрацию

async def send_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("Сначала зарегистрируйтесь командой /start")
        return
    day = user['current_lesson']
    lesson = get_material_by_day(day)
    if lesson:
        # Отправить текст
        if lesson['text']:
            await update.message.reply_text(lesson['text'])
        # Отправить файл(ы)
        if lesson['file_paths']:
            files = lesson['file_paths'].split('|')
            for file_path in files:
                ext = os.path.splitext(file_path)[1].lower()
                if ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
                    with open(file_path, "rb") as f:
                        await update.message.reply_photo(photo=InputFile(f))
                else:
                    with open(file_path, "rb") as f:
                        await update.message.reply_document(document=InputFile(f))
        # Отправить ссылку
        if lesson.get('link'):
            await update.message.reply_text(f"Ссылка: {lesson['link']}")
        # Обновить прогресс пользователя
        update_user_lesson(update.effective_user.id, day + 1)
    else:
        await update.message.reply_text("На сегодня уроков больше нет. Вы молодец!")

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        1: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_name)],
    },
    fallbacks=[],
)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("lesson", send_lesson))
    print("Бот запущен.")
    app.run_polling()
