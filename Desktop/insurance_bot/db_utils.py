# db_utils.py
import sqlite3

DB_PATH = 'insurancebot.db'

def db_init():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_number INTEGER,
            type TEXT,
            text TEXT,
            file_paths TEXT,
            link TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            name TEXT,
            registration_date DATE,
            current_lesson INTEGER DEFAULT 1
        )
    """)
    con.commit()
    con.close()

def add_material(day_number, type, text, file_paths, link):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        INSERT INTO materials (day_number, type, text, file_paths, link)
        VALUES (?, ?, ?, ?, ?)
    """, (day_number, type, text, file_paths, link))
    con.commit()
    con.close()

def get_material_by_day(day_number):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM materials WHERE day_number=?", (day_number,))
    lesson = cur.fetchone()
    con.close()
    return dict(lesson) if lesson else None

def add_user(telegram_id, name):
    import datetime
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO users (telegram_id, name, registration_date)
        VALUES (?, ?, ?)
    """, (telegram_id, name, datetime.date.today()))
    con.commit()
    con.close()

def get_user(telegram_id):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,))
    user = cur.fetchone()
    con.close()
    return dict(user) if user else None

def update_user_lesson(telegram_id, lesson):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("UPDATE users SET current_lesson=? WHERE telegram_id=?", (lesson, telegram_id))
    con.commit()
    con.close()
