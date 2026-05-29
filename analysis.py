import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os 
from database import get_all_transactions

def load_data():
    all_transactions = get_all_transactions()
    transactions_df = pd.DataFrame(all_transactions)
    transactions_df["date"] = pd.to_datetime(transactions_df["date"])
    return transactions_df

def chart_spending_by_category():
    transactions_df = load_data()
    expenses_df = transactions_df[transactions_df["type"] == "expense"]
    category_totals = expenses_df.groupby("category")["amount"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(data = category_totals, x= "category", y= "amount", ax= ax)
    os.makedirs("charts", exist_ok= True)
    plt.xticks(rotation= 45, ha="right")
    plt.tight_layout()
    fig.savefig("charts/spending_by_category.png")
    plt.close(fig)
    return "charts/spending_by_category.png"

def chart_monthly_trend():
    transactions_df = load_data()
    transactions_df["month"] = transactions_df["date"].dt.to_period("M")
    monthly_transactions_df = transactions_df.groupby(["month", "type"])["amount"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(data = monthly_transactions_df, x= "month", y= "amount", hue="type", ax= ax)
    os.makedirs("charts", exist_ok= True)
    plt.xticks(rotation= 45, ha="right")
    plt.tight_layout()
    fig.savefig("charts/monthly_trend.png")
    plt.close(fig)
    return "charts/monthly_trend.png"

def generate_all_charts():
    return {
        "spending_by_category": chart_spending_by_category(),
        "monthly_trend": chart_monthly_trend()
    }

if __name__ == "__main__":
    chart_spending_by_category()
    chart_monthly_trend()
    print("Charts saved!")
