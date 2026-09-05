import psycopg2
from config import DATABASE_URL


def get_connection():
    """
    Creates and returns a PostgreSQL connection.
    """

    if not DATABASE_URL:
        raise ValueError(
            "DATABASE_URL is not set. Check your .env file or Render environment variables."
        )

    return psycopg2.connect(DATABASE_URL)


def create_tables():
    """
    Creates the users table if it doesn't exist
    and safely adds any missing columns.
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:

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

                resume TEXT,
                roadmap TEXT
            )
            """)

            print("Database initialized successfully.")

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
                except psycopg2.Error as e:
                    print(f"Warning: Could not add column '{column}': {e}")

        conn.commit()