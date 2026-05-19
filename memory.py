import sqlite3

DB_PATH = "chat_memory.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.commit()
    con.close()

def get_history(user_id: str, limit: int = 15) -> list:
    con = sqlite3.connect(DB_PATH)
    rows = con.execute(
        """SELECT role, content FROM history
           WHERE user_id = ?
           ORDER BY ts DESC LIMIT ?""",
        (user_id, limit)
    ).fetchall()
    con.close()
    # Return in chronological order
    return [{"role": r, "content": c} for r, c in reversed(rows)]

def save_message(user_id: str, role: str, content: str):
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)",
        (user_id, role, content)
    )
    con.commit()
    con.close()

def clear_history(user_id: str):
    con = sqlite3.connect(DB_PATH)
    con.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
    con.commit()
    con.close()