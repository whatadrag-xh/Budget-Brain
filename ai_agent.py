from openai import OpenAI
from database import get_summary, get_all_transactions, get_monthly_totals, get_spending_by_category

client = OpenAI(
    base_url = "http://localhost:11434/v1",
    api_key="ollama"
)

def build_context(user_id):
    summary = get_summary(user_id)
    monthly_totals = get_monthly_totals(user_id)
    spending_by_category = get_spending_by_category(user_id)
    recent = get_all_transactions(user_id)[-10:]

    context = f"""You are a personal finance assistant. Answer ONLY questions about the user's finances.
Rules:
- Answer in 3-5 sentences maximum
- Be specific with numbers
- Only discuss the user's financial data below
- Never mention missing data or dates that don't exist
- Get straight to the point
- Never make up information or guess
- Never write code
- If you don't know the answer, say you don't know

FINANCIAL SUMMARY:
- Total Income: RM {summary['total_income']}
- Total Expenses: RM {summary['total_expenses']}
- Net Balance: RM {summary['net']}
TOP SPENDING CATEGORIES:
"""
    for item in spending_by_category[:5]:
        context += f"- {item['category']}: RM {item['total']:.2f}\n"

    context += "\nMONTHLY BREAKDOWN:\n"
    for m in monthly_totals[-3:]:
        context += f"- {m['month']}: Income RM {m['total_monthly_income']:.2f}, Expenses RM {m['total_monthly_expenses']:.2f}\n"

    context += "\nRECENT TRANSACTIONS:\n"
    for t in recent:
        context += f"- {t['date']}: {t['description']} ({t['category']}) RM {t['amount']} [{t['type']}]\n"

    return context

def chat(user_message, conversation_history):
    messages = [
        {"role": "system", "content": build_context()},
    ] + conversation_history + [
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model = "llama3.2",
        messages = messages
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    print(chat("What is my total income?", []))