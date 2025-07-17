# attestation.py

QUESTIONS = [
    "1. Для чего нужно страхование?",
    "2. Назовите два основных вида страхования.",
    "3. Что нужно знать перед оформлением страхового полиса?"
]

PROMO_CODE = "INSUR2024"

# Состояния для этапов аттестации и собеседования
STATE_ATT_QUESTION = "att_question"
STATE_INTERVIEW = "interview"

def start_attestation(context, user_id):
    context.user_data[user_id] = {'state': STATE_ATT_QUESTION, 'step': 0, 'answers': []}
    return QUESTIONS[0]

def process_attestation(context, user_id, answer):
    user_data = context.user_data[user_id]
    user_data['answers'].append(answer)
    user_data['step'] += 1
    if user_data['step'] < len(QUESTIONS):
        return QUESTIONS[user_data['step']]
    else:
        user_data['state'] = STATE_INTERVIEW
        return (f"Поздравляем! Вы успешно прошли итоговую аттестацию!\n"
                f"Ваш промокод: {PROMO_CODE}\n\n"
                "Для записи на собеседование отправьте свои ФИО и номер телефона в одном сообщении через запятую.\n"
                "Пример: Иванов Иван, +992900000000")

def process_interview(context, user_id, text):
    try:
        name, phone = map(str.strip, text.split(',', 1))
    except Exception:
        return "Пожалуйста, отправьте ФИО и телефон в формате: Иванов Иван, +992900000000"
    with open("interviews.csv", "a", encoding="utf-8") as f:
        f.write(f"{user_id},{name},{phone}\n")
    context.user_data[user_id]['state'] = None
    return f"Спасибо, {name}! Ваша заявка на собеседование принята.\nС вами свяжутся в ближайшее время."

def get_state(context, user_id):
    return context.user_data.get(user_id, {}).get('state')
