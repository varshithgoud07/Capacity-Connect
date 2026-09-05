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
        college VARCHAR(150),
        branch VARCHAR(100),
        year VARCHAR(20),
        cgpa DECIMAL(3,2),

        skills TEXT,
        interests TEXT,
        preferred_role VARCHAR(100),

        linkedin TEXT,
        github TEXT,
        portfolio TEXT,

        resume TEXT
    )
    """)

    # Add new columns for existing databases
    print("database.py updated successfully")
    columns = [
        ("phone", "VARCHAR(20)"),
        ("college", "VARCHAR(150)"),
        ("branch", "VARCHAR(100)"),
        ("year", "VARCHAR(20)"),
        ("cgpa", "DECIMAL(3,2)"),
        ("skills", "TEXT"),
        ("interests", "TEXT"),
        ("preferred_role", "VARCHAR(100)"),
        ("linkedin", "TEXT"),
        ("github", "TEXT"),
        ("portfolio", "TEXT"),
        ("resume", "TEXT"),
        ("roadmap", "TEXT")
    ]

    for column, datatype in columns:
        try:
            cursor.execute(
                f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {column} {datatype}"
            )
        except Exception:
            pass

    conn.commit()
    cursor.close()
    conn.close()