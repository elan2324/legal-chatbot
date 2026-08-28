import sqlite3

DB_NAME = "signup.db"


def create_conversation(user_id, title="New Chat"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO conversations(user_id,title) VALUES(?,?)",
        (user_id, title)
    )

    conn.commit()

    conversation_id = cursor.lastrowid
    conn.close()

    return conversation_id


def save_message(conversation_id, role, content):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO messages(conversation_id,role,content) VALUES(?,?,?)",
        (conversation_id, role, content)
    )

    conn.commit()
    conn.close()


def get_messages(conversation_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role,content,created_at
        FROM messages
        WHERE conversation_id=?
        ORDER BY created_at
    """, (conversation_id,))

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_user_conversations(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id,title,created_at
        FROM conversations
        WHERE user_id=?
        ORDER BY updated_at DESC
    """, (user_id,))

    rows = cursor.fetchall()

    conn.close()

    return rows