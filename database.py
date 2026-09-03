import psycopg2
from config import DATABASE_URL


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        phone VARCHAR(20),
        branch VARCHAR(100),
        year VARCHAR(20),
        skills TEXT,
        resume TEXT
    )
    """)

    try:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS resume TEXT
        """)
    except Exception:
        pass

    conn.commit()
    cursor.close()
    conn.close()