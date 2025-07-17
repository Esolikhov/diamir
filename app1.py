from fastapi import FastAPI, Request
from config import VERIFY_TOKEN
from whatsapp_api import send_whatsapp_message, send_whatsapp_quick_reply, send_whatsapp_image
from telegram_api import send_to_telegram
from photo_ai_module import analyze_food_photo
from doctor_ai_module import ask_doctor_ai
from app3 import route_message_app3

app = FastAPI()
user_states = {}

PAGES = [
    [
        {"id": "cmd_vrach", "title": "👩‍⚕️ Врач Эндокринолог"},
        {"id": "cmd_support", "title": "🆘 Поддержка"},
        {"id": "cmd_next_1", "title": "➡️ Ещё"},
    ],
    [
        {"id": "cmd_buy", "title": "🛍️ Пакеты Диамир"},
        {"id": "cmd_back_0", "title": "⬅️ Назад"},
        {"id": "cmd_next_2", "title": "➡️ Ещё"},
    ],
    [
        {"id": "cmd_remind", "title": "🔔 Напомнить о приёме Диамира"},
        {"id": "cmd_back_1", "title": "⬅️ Назад"},
        {"id": "cmd_next_3", "title": "➡️ Ещё"},
    ],
    [
        {"id": "cmd_photo", "title": "🍽️ Оценка еды"},
        {"id": "cmd_back_2", "title": "⬅️ Назад"},
        {"id": "cmd_next_4", "title": "➡️ Ещё"},
    ],
    [
        {"id": "cmd_food", "title": "🍏 Советы по питанию"},
        {"id": "cmd_back_3", "title": "⬅️ Назад"},
        {"id": "cmd_next_5", "title": "➡️ Ещё"},
    ],
    [
        {"id": "cmd_ban", "title": "🚫 Запрещённые продукты"},
        {"id": "cmd_back_4", "title": "⬅️ Назад"},
        {"id": "cmd_close", "title": "❌ Закрыть"},
    ],
]

def show_menu(phone, page=0):
    page = max(0, min(page, len(PAGES) - 1))
    buttons = PAGES[page]
    send_whatsapp_quick_reply(phone, "Главное меню. Выберите действие:", buttons)

@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return int(params.get("hub.challenge"))
    return "Verification failed"

@app.post("/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return {"status": "ok"}
        message = messages[0]
        phone = message["from"]

        # ==== КНОПКИ WhatsApp ====
        if message.get("type") == "interactive":
            btn_id = message["interactive"]["button_reply"]["id"]

            if btn_id.startswith("cmd_next_"):
                page = int(btn_id.split("_")[-1])
                show_menu(phone, page)
                return {"status": "ok"}
            if btn_id.startswith("cmd_back_"):
                page = int(btn_id.split("_")[-1])
                show_menu(phone, page)
                return {"status": "ok"}
            if btn_id == "cmd_close":
                send_whatsapp_message(phone, "Меню закрыто. Если потребуется — напишите /start.")
                return {"status": "ok"}
            if btn_id == "cmd_vrach":
                user_states[phone] = {"doctor_mode": True}
                send_whatsapp_message(phone, "Вы подключены к врачу-эндокринологу. Напишите свой вопрос.")
                return {"status": "ok"}
            if btn_id == "cmd_support":
                user_states[phone] = {"support_mode": True}
                send_whatsapp_message(phone, "Вы в чате поддержки! Опишите свой вопрос. Чтобы выйти, напишите 'закрыть'.")
                return {"status": "ok"}
            if btn_id == "cmd_buy":
                img_url = "https://files.catbox.moe/a3ta98.png"
                send_whatsapp_image(phone, img_url, caption="Выберите пакет: стартовый, премиум или популярный. Напишите название выбранного пакета.")
                user_states[phone] = {"buy_mode": True}
                return {"status": "ok"}
            if btn_id == "cmd_remind":
                send_whatsapp_message(phone, "Напоминалка активирована! (реализация через отдельный worker)")
                show_menu(phone, 2)
                return {"status": "ok"}
            if btn_id == "cmd_photo":
                user_states[phone] = {"photo_mode": True}
                send_whatsapp_message(phone, "Пожалуйста, отправьте фото еды (или ссылку на фото). Я дам подробную оценку и рекомендации для диабетиков.")
                return {"status": "ok"}
            if btn_id == "cmd_food":
                send_whatsapp_message(phone, "Советы по питанию: выбирайте белки, сложные углеводы, больше овощей, минимум сахара и быстрых углеводов.")
                show_menu(phone, 4)
                return {"status": "ok"}
            if btn_id == "cmd_ban":
                send_whatsapp_message(phone, "🚫 Запрещённые продукты: сахар, выпечка, сладости, жирное мясо и т.д.")
                show_menu(phone, 5)
                return {"status": "ok"}
            show_menu(phone, 0)
            return {"status": "ok"}

        # ==== 2. ПОДДЕРЖКА ====
        state = user_states.get(phone, {})
        if state.get("support_mode"):
            text = message.get("text", {}).get("body", "").strip()
            if text.lower() == "закрыть":
                user_states.pop(phone, None)
                send_whatsapp_message(phone, "Чат поддержки закрыт. Возвращаем вас в меню.")
                show_menu(phone, 0)
                return {"status": "ok"}
            send_to_telegram(text, phone)
            send_whatsapp_message(phone, "Ваш вопрос отправлен в поддержку! Ожидайте ответа.")
            return {"status": "ok"}

        # ==== 3. ВРАЧ (ИИ-эндокринолог) ====
        if state.get("doctor_mode"):
            text = message.get("text", {}).get("body", "").strip()
            if text.lower() == "закрыть":
                user_states.pop(phone, None)
                send_whatsapp_message(phone, "Чат с врачом закрыт. Возвращаем вас в меню.")
                show_menu(phone, 0)
                return {"status": "ok"}
            answer = ask_doctor_ai(text, phone)
            send_whatsapp_message(phone, f"Ответ врача: {answer}\n\nЕсли хотите завершить диалог — напишите 'закрыть'.")
            return {"status": "ok"}

        # --- Остальное: передаём управление в app3 ---
        return await route_message_app3(message, phone, user_states, show_menu)

    except Exception as e:
        print("== Ошибка обработки сообщения ==", e)
        return {"status": "error", "detail": str(e)}
