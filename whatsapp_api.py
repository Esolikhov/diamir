import requests
from config import WHATSAPP_TOKEN, WHATSAPP_PHONE_ID

def send_whatsapp_message(phone, text):
    url = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": text},
    }
    resp = requests.post(url, headers=headers, json=data)
    print("Ответ WhatsApp:", resp.status_code, resp.text)
    return resp

def send_whatsapp_quick_reply(phone, text, buttons):
    url = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    quick_replies = [{
        "type": "reply",
        "reply": {
            "id": btn["id"],
            "title": btn["title"][:20]
        }
    } for btn in buttons]
    data = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": text},
            "action": {"buttons": quick_replies}
        }
    }
    resp = requests.post(url, headers=headers, json=data)
    print("Ответ WhatsApp:", resp.status_code, resp.text)
    return resp

def send_whatsapp_image(phone, image_url, caption=None):
    url = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "image",
        "image": {"link": image_url}
    }
    if caption:
        data["image"]["caption"] = caption
    resp = requests.post(url, headers=headers, json=data)
    print("Ответ WhatsApp:", resp.status_code, resp.text)
    return resp

def download_whatsapp_media(media_id):
    url = f"https://graph.facebook.com/v19.0/{media_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Ошибка получения URL медиа: {resp.status_code} {resp.text}")
        return None
    media_url = resp.json().get("url")
    if not media_url:
        print("URL медиафайла не найден")
        return None
    media_resp = requests.get(media_url, headers=headers)
    if media_resp.status_code == 200:
        return media_resp.content
    print(f"Ошибка скачивания медиа: {media_resp.status_code} {media_resp.text}")
    return None
