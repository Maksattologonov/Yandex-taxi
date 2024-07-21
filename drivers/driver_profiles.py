import requests
import json
import os
import openpyxl

from decouple import config
from driver_prifile_models import *

url = "https://fleet-api.taxi.yandex.net/v1/parks/driver-profiles/list"
headers = config('HEADERS')


def fetch_driver_profiles(limit=1000, offset=0) -> List[Driver]:
    params = {
        "query": {
            "park": {
                "id": "8598e6c9c9084e0e9bda58d0e380878e",
                "driver_profile": {
                    "work_status": ["working", "not_working"]
                },
            }
        },
        "fields": {
            "account": [
                "id",
                "balance",
            ],
            "car": [
                "id",
                "callsign",
                "vin",
            ],
            "current_status": [
                "status",
            ],
            "driver_profile": [
                "id",
                "park_id",
                "first_name",
                "last_name",
                "work_rule_id",
                "work_status",
            ],
        },
        "limit": limit,
        "offset": offset
    }

    try:
        response = requests.post(url, headers=headers, json=params)
        response.raise_for_status()

        driver_profiles_data = response.json().get('driver_profiles', [])
        if not driver_profiles_data:
            return []

        driver_profiles = [
            Driver(
                account=Account(**profile.get('account', {})),
                car=Car(**profile.get('car', {})),
                current_status=CurrentStatus(**profile.get('current_status', {})),
                driver_profile=DriverProfile(**profile.get('driver_profile', {})),
            )
            for profile in driver_profiles_data
        ]

        return driver_profiles + fetch_driver_profiles(limit, offset + limit)

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []


def save_to_excel(driver_profiles: List[Driver], output_file: str):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Driver Profiles"

    headers = [
        "account_id", "account_balance",
        "car_id", "car_callsign", "car_vin",
        "current_status",
        "driver_id", "park_id", "first_name", "last_name", "work_rule_id", "work_status"
    ]
    sheet.append(headers)

    # Add data
    for profile in driver_profiles:
        sheet.append([
            profile.account.id if profile.account and profile.account.id else "",
            profile.account.balance if profile.account and profile.account.balance else "",
            profile.car.id if profile.car and profile.car.id else "",
            profile.car.callsign if profile.car and profile.car.callsign else "",
            profile.car.vin if profile.car and profile.car.vin else "",
            profile.current_status.status if profile.current_status and profile.current_status.status else "",
            profile.driver_profile.id if profile.driver_profile and profile.driver_profile.id else "",
            profile.driver_profile.park_id if profile.driver_profile and profile.driver_profile.park_id else "",
            profile.driver_profile.first_name if profile.driver_profile and profile.driver_profile.first_name else "",
            profile.driver_profile.last_name if profile.driver_profile and profile.driver_profile.last_name else "",
            profile.driver_profile.work_rule_id if profile.driver_profile and profile.driver_profile.work_rule_id else "",
            profile.driver_profile.work_status if profile.driver_profile and profile.driver_profile.work_status else ""
        ])

    workbook.save(output_file)
    print(f"Driver profiles have been saved to {output_file}")


driver_profiles = fetch_driver_profiles()

json_output_file = os.path.join(os.path.dirname(__file__), 'driver_profiles.json')
with open(json_output_file, 'w', encoding='utf-8') as f:
    json.dump([profile.dict() for profile in driver_profiles], f, ensure_ascii=False, indent=4)

print(f"Driver profiles have been saved to {json_output_file}")

excel_output_file = os.path.join(os.path.dirname(__file__), 'driver_profiles.xlsx')
save_to_excel(driver_profiles, excel_output_file)

working_count = sum(
    1 for profile in driver_profiles if profile.driver_profile and profile.driver_profile.work_status == 'working')
not_working_count = sum(
    1 for profile in driver_profiles if profile.driver_profile and profile.driver_profile.work_status == 'not_working')

print(f"Total number of drivers with 'working' status: {working_count}")
print(f"Total number of drivers with 'not_working' status: {not_working_count}")
