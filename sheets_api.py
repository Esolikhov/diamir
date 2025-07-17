import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import SERVICE_ACCOUNT_FILE, SHEET_ID

def get_gsheets():
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    client = gspread.authorize(creds)
    return client

def get_users_worksheet(sheet_name="Users"):
    gc = get_gsheets()
    sh = gc.open_by_key(SHEET_ID)
    worksheet = sh.worksheet(sheet_name)
    return worksheet

# Проверка: есть ли пользователь с таким телефоном в Google Sheets?
def user_exists_in_sheets(phone):
    try:
        worksheet = get_users_worksheet()
        records = worksheet.get_all_records()
        for rec in records:
            # Если телефон совпадает с первым столбцом
            if str(rec.get("phone") or rec.get("Телефон") or "").strip() == str(phone).strip():
                return True
        return False
    except Exception as e:
        print("== Ошибка при проверке пользователя в Google Sheets ==", e)
        return False

# Сохранить анкету пользователя (добавить строку в Users)
def save_to_google_sheets(phone, answers):
    try:
        worksheet = get_users_worksheet()
        # Для первого раза: если нет заголовков, добавляем.
        if not worksheet.get_all_records():
            header = ["Телефон"] + [f"Вопрос {i+1}" for i in range(len(answers))]
            worksheet.append_row(header)
        row = [phone] + answers
        worksheet.append_row(row)
        print("== Пользователь успешно записан в Google Sheets ==")
    except Exception as e:
        print("== Ошибка записи в Google Sheets ==", e)

# Сохранить результат еды в FoodLog (с проверкой заголовков)
def save_food_decision(phone, food_result, score, comment, decision):
    """
    Сохраняет результат анализа еды в отдельный лист FoodLog:
    phone | result | score | comment | decision
    """
    try:
        worksheet = get_users_worksheet("FoodLog")
        # Проверим заголовок
        headers = worksheet.row_values(1)
        correct_headers = ["Телефон", "Результат", "Оценка (баллы)", "Описание", "Будет есть"]
        # Если пусто или некорректно — перезаписываем
        if headers != correct_headers:
            worksheet.update('A1:E1', [correct_headers])
        row = [phone, food_result, score, comment, decision]
        worksheet.append_row(row)
        print("== Результат еды успешно записан в FoodLog Google Sheets ==")
    except Exception as e:
        print("== Ошибка записи FoodLog в Google Sheets ==", e)

# Получить профиль из анкеты
def get_profile_from_google_sheets(phone):
    try:
        worksheet = get_users_worksheet()
        records = worksheet.get_all_records()
        for rec in records:
            if str(rec.get("phone") or rec.get("Телефон") or "") == str(phone):
                lines = [f"{k}: {v}" for k, v in rec.items() if k != "Телефон"]
                return "Ваш профиль:\n" + "\n".join(lines)
        return "Профиль не найден."
    except Exception as e:
        print("Ошибка профиля:", e)
        return "Ошибка получения профиля."

# Заглушка под другие функции
# def your_other_func(): pass
