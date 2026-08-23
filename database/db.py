import sqlite3
from config.settings import Config


def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS info (
                user TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                mobile TEXT,
                name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
                    CHECK(role IN ('user', 'admin'))
            )
            """
        )
        conn.commit()