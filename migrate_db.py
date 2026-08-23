"""One-time migration for an existing local signup.db.

This migration upgrades the old plaintext-password schema to the Stage 1A
schema and hashes existing passwords. Do NOT commit the database afterward.
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

    columns = [row[1] for row in connection.execute("PRAGMA table_info(info)")]
    if not columns:
        print("The info table does not exist. Nothing to migrate.")
        connection.close()
        return

    if "role" not in columns:
        connection.execute(
            "ALTER TABLE info ADD COLUMN role TEXT NOT NULL DEFAULT 'user'"
        )

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

    connection.commit()
    connection.close()
    print(f"Migration complete. Hashed {updated} existing password(s).")
    print("IMPORTANT: keep signup.db local and out of Git.")


if __name__ == "__main__":
    migrate()
