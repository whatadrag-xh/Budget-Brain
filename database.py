import sqlite3
import os

DB_PATH = os.path.join("data", "finance.db")

def init_db():
    os.makedirs("data", exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        user_id INTEGER,
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        description TEXT NOT NULL,
                        amount REAL NOT NULL,
                        category TEXT NOT NULL,
                        type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                       );
                    
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password_hash TEXT NOT NULL
                    );
                """)
        conn.commit()
    print("Database initialized successfully.")

def add_transaction(date, description, amount, category, type, user_id):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute(
            "INSERT INTO transactions (date, description, amount, category, type, user_id) VALUES (?, ?, ?, ?, ?, ?)",
            (date, description, float(amount), category, type, user_id)
        )
        except Exception as e:
            print(f"Error: {e}")

def get_all_transactions(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM transactions WHERE user_id = ?", (user_id,))
        transaction_list = [dict(row) for row in cursor.fetchall()]
        return transaction_list
    
def get_spending_by_category(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT category, SUM(amount) as total FROM transactions WHERE type = "expense" AND user_id = ? GROUP BY category ORDER BY total DESC
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]

def get_monthly_totals(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT
                strftime('%Y-%m', date) AS month,
                              SUM(CASE WHEN type='income' THEN amount ELSE 0 END) AS total_monthly_income,
                              SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS total_monthly_expenses
            FROM transactions
            WHERE user_id = ?
            GROUP BY month
            ORDER BY month
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]
    
def get_summary(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT 
                PRINTF('%.2f', SUM(CASE WHEN type='income' THEN amount ELSE 0 END)) AS total_income,
                PRINTF('%.2f', SUM(CASE WHEN type='expense' THEN amount ELSE 0 END)) AS total_expenses,
                PRINTF('%.2f', SUM(CASE WHEN type='income' THEN amount ELSE 0 END) - SUM(CASE WHEN type='expense' THEN amount ELSE 0 END)) AS net 
            FROM transactions
            WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        return dict(row)

def delete_transaction(id, user_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (id, user_id))

def clear_db(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
    print("Database cleared")

def create_user(username, password_hash):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        return cursor.lastrowid

def  get_user_by_username(username):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_user_by_id(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

if __name__ == "__main__":
    init_db()
    print(get_spending_by_category(1))
    print(get_monthly_totals(1))