import requests
import json
from decouple import config
from typing import List, Optional
from pydantic import BaseModel
import openpyxl


# Define Pydantic models
class Car(BaseModel):
    id: Optional[str] = None


class Order(BaseModel):
    id: Optional[str] = None
    status: Optional[str] = None
    booked_at: Optional[str] = None
    categories: Optional[List[str]] = None
    price: Optional[float] = None
    car: Optional[Car] = None


# API endpoint
url = "https://fleet-api.taxi.yandex.net/v1/parks/orders/list"

# Load and parse headers from environment variable
headers = config('HEADERS')


def fetch_orders(cursor=None):
    params = {
        "query": {
            "park": {
                "id": "8598e6c9c9084e0e9bda58d0e380878e",
                "order": {
                    "booked_at": {
                        "from": "2024-07-09T00:00:00.000Z",
                        "to": "2024-07-09T23:59:59.999Z"
                    }
                }
            }
        },
        "limit": 1,
        "cursor": cursor
    }

    try:
        response = requests.post(url, headers=headers, json=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return {"orders": [], "cursor": None}


def fetch_all_orders():
    all_orders = []
    cursor = None

    while True:
        data = fetch_orders(cursor)
        orders_data = data.get('orders', [])
        if not orders_data:
            break

        orders = []
        for order_data in orders_data:
            try:
                order = Order(**order_data)
                orders.append(order)
            except Exception as e:
                print(f"Error validating order data: {e}")

        all_orders.extend(orders)
        cursor = data.get('cursor')
        if not cursor:
            break

    return all_orders


def save_to_excel(orders: List[Order], output_file: str):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Orders"

    # Define headers
    e_headers = [
        "id", "status", "booked_at", "categories", "price",
        "car_id"
    ]
    sheet.append(e_headers)

    # Add data
    for order in orders:
        sheet.append([
            order.id or "",
            order.status or "",
            order.booked_at or "",
            ", ".join(order.categories or []) or "",
            order.price or "",
            order.car.id if order.car else ""
        ])

    workbook.save(output_file)
    print(f"Orders have been saved to {output_file}")


# Fetch all orders
orders = fetch_all_orders()

# Output the total number of orders
print(f"Total orders: {len(orders)}")

# Save the list of orders to a JSON file
json_output_file = r'F:\PycharmProjects\Yandex-taxi\drivers\orderstest.json'
with open(json_output_file, 'w', encoding='utf-8') as f:
    json.dump([order.dict() for order in orders], f, ensure_ascii=False, indent=4)

print(f"Orders saved to {json_output_file}")

# Save the list of orders to an Excel file
excel_output_file = r'F:\PycharmProjects\Yandex-taxi\drivers\orders.xlsx'
save_to_excel(orders, excel_output_file)
