# app3.py

from sheets_api import save_to_google_sheets, user_exists_in_sheets, save_food_decision
from questions import QUESTIONS
from photo_ai_module import analyze_food_photo
from telegram_api import send_to_telegram
from whatsapp_api import send_whatsapp_message

async def route_message_app3(message, phone, user_states, show_menu):
    state = user_states.get(phone, {})

    # 1. Покупка Диамир (buy_mode)
    if state.get("buy_mode"):
        pkg = message.get("text", {}).get("body", "").strip()
        if pkg.lower() in ["стартовый", "премиум", "популярный"]:
            send_to_telegram(f"Пользователь {phone} выбрал пакет: {pkg}", phone)
            send_whatsapp_message(phone, f"Спасибо! Вы выбрали пакет: {pkg}. С вами свяжется менеджер.")
            user_states.pop(phone, None)
            show_menu(phone, 1)
            return {"status": "ok"}
        else:
            send_whatsapp_message(phone, "Пожалуйста, напишите одно из: стартовый, премиум, популярный.")
            return {"status": "ok"}

    # 2. Оценка еды (photo_mode)
    if state.get("photo_mode"):
        # Фото из WhatsApp
        if message.get("type") == "image":
            media_id = message["image"]["id"]
            result, score, comment = analyze_food_photo(media_id, phone)
            if "Ошибка" not in result:
                send_whatsapp_message(phone, f"{result}\n\nОценка: {score} балл(а)\nКомментарий: {comment}")
                user_states[phone] = {"food_result": (result, score, comment)}
                send_whatsapp_message(phone, "Вы будете это есть? Ответьте 'Да' или 'Нет'.")
            else:
                send_whatsapp_message(phone, result)
            return {"status": "ok"}
        # Ссылка на фото
        elif message.get("text", {}):
            url = message["text"]["body"].strip()
            if url.startswith("http"):
                result, score, comment = analyze_food_photo(url, phone)
                if "Ошибка" not in result:
                    send_whatsapp_message(phone, f"{result}\n\nОценка: {score} балл(а)\nКомментарий: {comment}")
                    user_states[phone] = {"food_result": (result, score, comment)}
                    send_whatsapp_message(phone, "Вы будете это есть? Ответьте 'Да' или 'Нет'.")
                else:
                    send_whatsapp_message(phone, result)
                return {"status": "ok"}
            else:
                send_whatsapp_message(phone, "Отправьте ссылку на фото или загрузите фото!")
                return {"status": "ok"}

    # 3. Подтверждение, будет ли есть это блюдо (ответ 'Да' или 'Нет')
    if state.get("food_result"):
        text = message.get("text", {}).get("body", "").strip().lower()
        if text in ["да", "yes"]:
            result, score, comment = state["food_result"]
            save_food_decision(phone, result, score, comment, "Да")
            send_whatsapp_message(phone, "Ваш ответ сохранён! Спасибо.")
            user_states.pop(phone, None)
            show_menu(phone, 0)
            return {"status": "ok"}
        elif text in ["нет", "no"]:
            result, score, comment = state["food_result"]
            save_food_decision(phone, result, score, comment, "Нет")
            send_whatsapp_message(phone, "Ваш ответ сохранён! Спасибо.")
            user_states.pop(phone, None)
            show_menu(phone, 0)
            return {"status": "ok"}
        else:
            send_whatsapp_message(phone, "Пожалуйста, ответьте 'Да' или 'Нет'.")
            return {"status": "ok"}

    # 4. АНКЕТИРОВАНИЕ
    if not user_exists_in_sheets(phone):
        state = user_states.get(phone)
        text = message.get("text", {}).get("body", "").strip()
        if not state:
            send_whatsapp_message(phone, "Добро пожаловать! Ответьте на несколько вопросов для знакомства.")
            send_whatsapp_message(phone, QUESTIONS[0])
            user_states[phone] = {"step": 1, "answers": []}
            return {"status": "ok"}
        elif state["step"] < len(QUESTIONS):
            state["answers"].append(text)
            question = QUESTIONS[state["step"]]
            send_whatsapp_message(phone, question)
            state["step"] += 1
            user_states[phone] = state
            return {"status": "ok"}
        else:
            state["answers"].append(text)
            save_to_google_sheets(phone, state["answers"])
            send_whatsapp_message(phone, "Спасибо! Анкета завершена, ваши ответы записаны.")
            user_states.pop(phone, None)
            show_menu(phone, 0)
            return {"status": "ok"}

    # Если ничего не подошло — показать меню
    show_menu(phone, 0)
    return {"status": "ok"}
