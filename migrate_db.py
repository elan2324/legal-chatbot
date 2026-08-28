"""
One-time migration for an existing local signup.db.

This migration upgrades the old plaintext-password schema to the Stage 1A
schema, hashes existing passwords, and creates the Stage 2 chat tables.
Do NOT commit the database afterward.
"""

from pathlib import Path
import sqlite3

from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "signup.db"


def migrate():
    if not DATABASE_PATH.exists():
        print("signup.db does not exist. Nothing to migrate.")
        return

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    # Enable foreign key support in SQLite
    connection.execute("PRAGMA foreign_keys = ON")

    columns = [row[1] for row in connection.execute("PRAGMA table_info(info)")]

    if not columns:
        print("The info table does not exist. Nothing to migrate.")
        connection.close()
        return

    # Stage 1: Add role column if missing
    if "role" not in columns:
        connection.execute(
            "ALTER TABLE info ADD COLUMN role TEXT NOT NULL DEFAULT 'user'"
        )

    # Stage 1: Hash old plaintext passwords
    rows = connection.execute("SELECT rowid, password FROM info").fetchall()
    updated = 0

    for row in rows:
        password = row["password"]
        if password and not password.startswith(("scrypt:", "pbkdf2:")):
            connection.execute(
                "UPDATE info SET password = ? WHERE rowid = ?",
                (generate_password_hash(password), row["rowid"]),
            )
            updated += 1

    # Stage 2: Create conversations table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT DEFAULT 'New Chat',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES info(id) ON DELETE CASCADE
        )
    """)

    # Stage 2: Create messages table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        )
    """)

    connection.commit()
    connection.close()

    print(f"Migration complete. Hashed {updated} existing password(s).")
    print("Stage 2 chat tables verified: conversations, messages.")
    print("IMPORTANT: keep signup.db local and out of Git.")


if __name__ == "__main__":
    migrate()