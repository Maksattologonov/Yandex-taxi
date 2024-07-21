from typing import List, Optional, Union
import requests
import json
import pandas as pd
from pydantic import BaseModel, ValidationError


# Определяем Pydantic модели
class Transaction(BaseModel):
    id: str = ""
    event_at: str = ""
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    amount: float = 0.0
    currency_code: str = ""
    description: Optional[str] = None
    created_by: Optional[Union[str, dict]] = None
    driver_profile_id: Optional[str] = None
    order_id: Optional[str] = None

    # Конвертируем все поля в строки, где это необходимо
    @staticmethod
    def clean(transaction: dict) -> dict:
        if isinstance(transaction.get('created_by'), dict):
            transaction['created_by'] = json.dumps(transaction['created_by'])
        if isinstance(transaction.get('order_id'), dict):
            transaction['order_id'] = json.dumps(transaction['order_id'])
        return transaction


class TransactionResponse(BaseModel):
    transactions: List[Transaction] = []
    cursor: Optional[str] = None


# API endpoint and headers
url = "https://fleet-api.taxi.yandex.net/v2/parks/transactions/list"
headers = {
    "X-Client-ID": "taxi/park/8598e6c9c9084e0e9bda58d0e380878e",
    "X-Api-Key": "cNhyVUPniPBJBEuxSdeStsUrPHXWywNdJq",
    "Content-Type": "application/json"
}


# Function to fetch transactions
def fetch_transactions(cursor=None):
    params = {
        "query": {
            "park": {
                "id": "8598e6c9c9084e0e9bda58d0e380878e",
                "transaction": {
                    "event_at": {
                        "from": "2024-07-09T00:00:00.000Z",
                        "to": "2024-07-09T23:59:59.999Z"
                    }
                }
            }
        },
        "limit": 10,
        "cursor": cursor
    }

    try:
        response = requests.post(url, headers=headers, json=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


# Recursive function to gather all transactions
def get_all_transactions(cursor=None, all_transactions=None):
    if all_transactions is None:
        all_transactions = []

    print(f"Fetching transactions with cursor: {cursor}")
    data = fetch_transactions(cursor)
    if not data:
        return all_transactions

    cleaned_transactions = [Transaction.clean(txn) for txn in data.get('transactions', [])]

    try:
        transaction_response = TransactionResponse(transactions=cleaned_transactions, cursor=data.get('cursor'))
        all_transactions.extend(transaction_response.transactions)
        print(f"Fetched {len(transaction_response.transactions)} transactions, cursor: {transaction_response.cursor}")
        if transaction_response.cursor:
            return get_all_transactions(cursor=transaction_response.cursor, all_transactions=all_transactions)
        else:
            return all_transactions
    except ValidationError as e:
        print(f"Validation error: {e}")
        return all_transactions


# Fetch all transactions
transactions = get_all_transactions()

# Convert transactions to a DataFrame and save to Excel
if transactions:
    df = pd.DataFrame([txn.dict() for txn in transactions])
    output_file = r'F:\PycharmProjects\Yandex-taxi\drivers\transactions.xlsx'
    df.to_excel(output_file, index=False)
    print(f"Transactions saved to {output_file}")
else:
    print("No transactions to save.")
