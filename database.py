import sqlite3
import os

DB_PATH = os.path.join("data", "finance.db")

def init_db():
    os.makedirs("data", exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        description TEXT NOT NULL,
                        amount REAL NOT NULL,
                        category TEXT NOT NULL,
                        type TEXT NOT NULL CHECK(type IN ('income', 'expense'))
                       );
                """)
        conn.commit()
    print("Database initialized successfully.")