from typing import List

import requests
import pandas as pd

from pydantic import ValidationError, TypeAdapter
from models import DriverProfiles

# API endpoint and headers
url = "https://fleet-api.taxi.yandex.net/v1/parks/driver-profiles/list"
headers = {
    "X-Client-ID": "taxi/park/8598e6c9c9084e0e9bda58d0e380878e",
    "X-Api-Key": "cNhyVUPniPBJBEuxSdeStsUrPHXWywNdJq",
    "Content-Type": "application/json"
}


# Function to fetch driver profiles
def fetch_driver_profiles(limit):
    all_driver_profiles = []
    offset = 0

    while True:
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

            driver_profiles = response.json().get('driver_profiles', [])
            if not driver_profiles:
                break

            all_driver_profiles.extend(driver_profiles)
            offset += limit

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            break

    return all_driver_profiles


data = fetch_driver_profiles(1000)
try:
    for item in data:
        if 'car' not in item:
            item['car'] = None

    adapter = TypeAdapter(List[DriverProfiles])
    driver_profiles = adapter.validate_python(data)

    records = []
    for profile in driver_profiles:
        for account in profile.accounts:
            updated_at_no_tz = profile.updated_at.replace(tzinfo=None)
            records.append({
                "updated_at": updated_at_no_tz,
                "account_balance": account.balance,
                "account_id": account.id,
                "car_callsign": profile.car.callsign if profile.car else None,
                "car_id": profile.car.id if profile.car else None,
                "car_vin": profile.car.vin if profile.car else None,
                "driver_first_name": profile.driver_profile.first_name,
                "driver_last_name": profile.driver_profile.last_name,
                "driver_id": profile.driver_profile.id,
                "driver_park_id": profile.driver_profile.park_id,
                "driver_work_rule_id": profile.driver_profile.work_rule_id,
                "driver_work_status": profile.driver_profile.work_status,
                "current_status": profile.current_status.status
            })

    df = pd.DataFrame(records)
    df.to_excel("output.xlsx", index=False)

    print("Данные успешно записаны в Excel файл.")
except ValidationError as e:
    print("Ошибка валидации данных:", e)
except Exception as e:
    print("Произошла ошибка:", e)
# Save the driver profiles to a JSON file
# output_file = os.path.join(os.path.dirname(__file__), 'driver_profiles.json')
# with open(output_file, 'w', encoding='utf-8') as f:
#     json.dump(driver_profiles, f, ensure_ascii=False, indent=4)
#
# print(f"Driver profiles have been saved to {output_file}")

# Print the total number of drivers with the status "working" and "not_working"
# working_count = sum(
#     1 for profile in driver_profiles if profile.get('driver_profile', {}).get('work_status') == 'working')
# not_working_count = sum(
#     1 for profile in driver_profiles if profile.get('driver_profile', {}).get('work_status') == 'not_working')
#
# print(f"Total number of drivers with 'working' status: {working_count}")
# print(f"Total number of drivers with 'not_working' status: {not_working_count}")
