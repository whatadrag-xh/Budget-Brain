from openai import OpenAI
from database import get_summary, get_all_transactions, get_monthly_totals, get_spending_by_category

client = OpenAI(
    base_url = "http://localhost:11434/v1",
    api_key="ollama"
)

def build_context():
    summary = get_summary()
    all_transactions = get_all_transactions()
    monthly_totals = get_monthly_totals()
    spending_by_category = get_spending_by_category()

    return f"Here is my total summary: {summary}. Here is my spending by cateogory: {spending_by_category}. Here is my monthly breakdown: {monthly_totals}. Here is my recent transactions: {all_transactions}."

def chat(user_message, conversation_history):
    messages = [
        {"role": "system", "content": build_context()},
    ] + conversation_history + [
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model = "tinyllama",
        messages = messages
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    print(chat("What is my total income?", []))