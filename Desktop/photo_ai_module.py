import requests
import base64
from config import OPENAI_API_KEY
from whatsapp_api import download_whatsapp_media

# Словарь для быстрой проверки и "примерного" сканирования баллов/комментариев для разных блюд
SCORES = [
    # (ключевое_слово, балл, комментарий)
    ("плов", 4, "Плов — высокая нагрузка, салат/чай — безопасно"),
    ("каша", 3, "Каша — осторожно, остальные — отлично"),
    ("сырники", 4, "Сырники — быстрые углеводы и жир"),
    ("салат", 1, "Отлично: белок, клетчатка"),
    ("рыба", 1, "Хороший вариант для вечера"),
    # ...можно расширять!
]

def guess_score_comment(food_result):
    result_lower = food_result.lower()
    for kw, score, comment in SCORES:
        if kw in result_lower:
            return score, comment
    # По умолчанию — "нейтрально"
    return 2, "Требуется индивидуальная оценка"

def analyze_food_photo(media_id_or_url, phone):
    if media_id_or_url.startswith("wamid.") or media_id_or_url.isalnum():
        img_bytes = download_whatsapp_media(media_id_or_url)
        if not img_bytes:
            return "Ошибка: Не удалось скачать изображение из WhatsApp."
        base64_image = base64.b64encode(img_bytes).decode()
        image_url = f"data:image/jpeg;base64,{base64_image}"
    else:
        image_url = media_id_or_url

    prompt = (
        "Ты опытный диетолог, который оценивает блюда для диабетиков. "
        "Определи название блюда, вес, калорийность, белки, жиры, углеводы, гликемический индекс для продукта на фото "
        "и сделай краткое заключение: подходит ли для диабетика (да/нет и почему). "
        "Формат:\n"
        "Название блюда - ...\n"
        "Вес - ... г\n"
        "Калорийность - ... ккал на 100 г\n"
        "Белки - ... г\n"
        "Жиры - ... г\n"
        "Углеводы - ... г\n"
        "Гликемический индекс (ГИ) - ...\n"
        "Заключение - ...\n"
    )

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": image_url}}
            ]}
        ],
        "max_tokens": 512
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=40)
        if resp.status_code == 200:
            result = resp.json()["choices"][0]["message"]["content"].strip()
            # Автоопределение балла и комментария по ключевым словам
            score, comment = guess_score_comment(result)
            return result[:4096], score, comment
        else:
            print("Ошибка при анализе еды:", resp.text)
            return f"❗Ошибка при анализе еды: {resp.text}", None, None
    except Exception as e:
        print("Ошибка при анализе еды:", e)
        return f"❗Ошибка при анализе еды: {e}", None, None
