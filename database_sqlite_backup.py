import sqlite3
from config import DATABASE


def get_connection():
    return sqlite3.connect(DATABASE)


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT,
        branch TEXT,
        year TEXT,
        skills TEXT
    )
    """)

    conn.commit()
    conn.close()