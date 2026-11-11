
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen2.5:3b"


def ask_clearflow(question, income, expenses):
    net_cash_flow = income - expenses

    system_prompt = """
You are Clearflow AI, a financial intelligence
assistant for small businesses.

You explain financial information clearly and accurately.

Important rules:
- Use only the financial data provided.
- Never invent transactions, balances, or forecasts.
- Do not claim to access real bank accounts.
- Clearly identify synthetic demonstration data.
- Explain financial risks and opportunities.
- If information is missing, say so.
- Do not provide guaranteed investment advice.
"""

    user_prompt = f"""
Financial data (synthetic INR demonstration):

Total income: INR {income:,.2f}
Total expenses: INR {expenses:,.2f}
Net cash flow: INR {net_cash_flow:,.2f}

User question:
{question}

Answer using the provided financial data.
Keep the response practical and concise.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "options": {
                "temperature": 0.2,
                "num_predict": 400
            }
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()
    return data["message"]["content"]
