import random
from datetime import date, timedelta
from database import init_db, add_transaction, clear_db

EXPENSE_CATEGORIES = {
    "Rent":              (1000,  1000),
    "Groceries":         (150,  350),
    "Utilities":         (80,   150),
    "Transport":         (100,  200),
    "Eating Out":        (150,  350),
    "Coffee/Snacks":     (30,   100),
    "Entertainment":     (40,   150),
    "Shopping":          (50,   200),
    "Health & Fitness":  (30,   120),
    "Student Loan":      (500,  500),
    "Savings":           (200,  500),
    "Emergency Fund":    (100,  300),
    "Gifts/Donations":   (20,   100),
    "Travel":            (0,    150),
    "Subscriptions":     (20,   60),
}

INCOME_SOURCES = {
    "Salary":                 (2800, 4000),
    "Freelance":              (0,    800),
    "Allowance (Family)":     (0,    200),
    "Side Hustle":            (0,    300),
    "Investment/Interest":    (0,    50),
}

def random_date_in_month(year, month):
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days = 1)
    else: 
        end = date(year, month + 1, 1) - timedelta(days = 1)
    delta = (end - start).days
    return start + timedelta(days = random.randint(0, delta))

def seed(months):
    init_db()
    today = date.today()
    for m in range(months, 0, -1):
        target_month = today.month - m
        target_year = today.year
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        for expense, (min_amt, max_amt) in EXPENSE_CATEGORIES.items():
            expense_amt = round(random.uniform(min_amt, max_amt), 2)
            random_date = random_date_in_month(target_year, target_month)
            add_transaction(str(random_date), expense, expense_amt, expense, "expense")
        for income, (min_amt, max_amt) in INCOME_SOURCES.items():
            income_amt = round(random.uniform(min_amt, max_amt), 2)
            random_date = random_date_in_month(target_year, target_month)
            add_transaction(str(random_date), income, income_amt, income, "income")           

if __name__ == "__main__":
    clear_db()
    seed(6)
    print("Seed data generated!")