import time
from datetime import datetime, timedelta
from sheets_api import get_users_worksheet
from whatsapp_api import send_whatsapp_message

def parse_times(times_str):
    # Принимает строку типа "7-12:45-19:00" → [(7,0), (12,45), (19,0)]
    times = []
    for part in times_str.replace(' ', '').replace(',', '-').split('-'):
        if not part:
            continue
        if ':' in part:
            h, m = part.split(':', 1)
            try:
                hour, minute = int(h), int(m)
            except Exception:
                continue
        else:
            try:
                hour, minute = int(part), 0
            except Exception:
                continue
        if 0 <= hour < 24 and 0 <= minute < 60:
            times.append((hour, minute))
    return times

def already_notified(notification_log, phone, hour, minute, typ):
    key = f"{phone}_{hour:02d}:{minute:02d}_{typ}"
    # Проверка, не было ли уже напоминания за эту минуту
    return notification_log.get(key, 0) == datetime.now().day

def set_notified(notification_log, phone, hour, minute, typ):
    key = f"{phone}_{hour:02d}:{minute:02d}_{typ}"
    notification_log[key] = datetime.now().day

def main():
    print("== Диамир напоминалка стартовала ==")
    notification_log = {}  # защита от дублей за день

    while True:
        now = datetime.now()
        worksheet = get_users_worksheet()
        records = worksheet.get_all_records()

        for rec in records:
            phone = rec.get("phone") or rec.get("Телефон")
            timestr = rec.get("meals_time") or rec.get("Вопрос 4") or ""
            if not phone or not timestr:
                continue

            times = parse_times(timestr)
            for hour, minute in times:
                # За 1 час до
                minus_1h = (hour - 1) % 24
                if now.hour == minus_1h and now.minute == minute:
                    if not already_notified(notification_log, phone, hour, minute, '1h'):
                        send_whatsapp_message(phone, f"⏰ Через 1 час приём Диамира в {hour:02d}:{minute:02d}!")
                        set_notified(notification_log, phone, hour, minute, '1h')
                # За 5 минут до
                event_time = datetime(now.year, now.month, now.day, hour, minute)
                minus_5m = (event_time - timedelta(minutes=5)).time()
                if now.hour == minus_5m.hour and now.minute == minus_5m.minute:
                    if not already_notified(notification_log, phone, hour, minute, '5m'):
                        send_whatsapp_message(phone, f"⏰ Через 5 минут приём Диамира в {hour:02d}:{minute:02d}!")
                        set_notified(notification_log, phone, hour, minute, '5m')
                # В момент
                if now.hour == hour and now.minute == minute:
                    if not already_notified(notification_log, phone, hour, minute, '0m'):
                        send_whatsapp_message(phone, f"💊 Время приёма Диамира: {hour:02d}:{minute:02d}. Не забудьте выпить лекарство!")
                        set_notified(notification_log, phone, hour, minute, '0m')

        # Ждём 60 секунд (проверка каждую минуту)
        time.sleep(60)

if __name__ == "__main__":
    main()
