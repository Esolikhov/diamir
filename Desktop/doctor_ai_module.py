# doctor_ai_module.py

import requests
from config import OPENAI_API_KEY

def ask_doctor_ai(question, phone):
    prompt = (
        "Ты опытный эндокринолог. Отвечай просто, понятно и с заботой о человеке. "
        "Дай совет по диабету, питанию, образу жизни или симптомам. "
        "Если вопрос не по профилю — вежливо попроси обратиться к врачу лично. "
        "Не ставь диагноз, не назначай лекарства дистанционно!"
    )
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": question}
        ],
        "max_tokens": 500
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=40)
        if resp.status_code == 200:
            result = resp.json()["choices"][0]["message"]["content"].strip()
            return result[:4096]
        else:
            print("Ошибка врача:", resp.text)
            return "❗Извините, не удалось получить ответ от врача. Попробуйте позже."
    except Exception as e:
        print("Ошибка врача:", e)
        return "❗Ошибка обработки. Попробуйте ещё раз."
