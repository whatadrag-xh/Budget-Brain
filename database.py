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

def add_transaction(date, description, amount, category, type):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute("INSERT INTO transactions (date, description, amount, category, type) VALUES (?, ?, ?, ?, ?)", (date, description, amount, category, type))
        except Exception as e:
            print(f"Error: {e}")

def get_all_transactions():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM transactions")
        transaction_list = [dict(row) for row in cursor.fetchall()]
        return transaction_list
    
def get_spending_by_category():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT category, SUM(amount) as total FROM transactions WHERE type = "expense" GROUP BY category ORDER BY total DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

def get_monthly_totals():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT
                strftime('%Y-%m', date) AS month,
                              SUM(CASE WHEN type='income' THEN amount ELSE 0 END) AS total_monthly_income,
                              SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS total_monthly_expenses
            FROM transactions
            GROUP BY month
            ORDER BY month
        """)
        return [dict(row) for row in cursor.fetchall()]
    
def get_summary():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT 
                PRINTF('%.2f', SUM(CASE WHEN type='income' THEN amount ELSE 0 END)) AS total_income,
                PRINTF('%.2f', SUM(CASE WHEN type='expense' THEN amount ELSE 0 END)) AS total_expenses,
                PRINTF('%.2f', SUM(CASE WHEN type='income' THEN amount ELSE 0 END) - SUM(CASE WHEN type='expense' THEN amount ELSE 0 END)) AS net 
            FROM transactions
        """)
        row = cursor.fetchone()
        return dict(row)

def delete_transaction(id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM transactions WHERE id = ?", (id,))

def clear_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM transactions")
    print("Database cleared")
    
if __name__ == "__main__":
    init_db()
    print(get_spending_by_category())
    print(get_monthly_totals())

