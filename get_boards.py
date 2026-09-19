import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("MONDAY_API_TOKEN")
WORK_ORDERS_BOARD_ID = os.getenv("WORK_ORDERS_BOARD_ID")
DEALS_BOARD_ID = os.getenv("DEALS_BOARD_ID")

URL = "https://api.monday.com/v2"

query = """
query ($board_ids: [ID!]) {
    boards(ids: $board_ids) {
        id
        name
        items_page(limit: 10) {
            items {
                id
                name
                column_values {
                    id
                    text
                }
            }
        }
    }
}
"""

headers = {
    "Authorization": TOKEN,
    "Content-Type": "application/json"
}

variables = {
    "board_ids": [
        WORK_ORDERS_BOARD_ID,
        DEALS_BOARD_ID
    ]
}

response = requests.post(
    URL,
    json={
        "query": query,
        "variables": variables
    },
    headers=headers
)

print("Status:", response.status_code)

data = response.json()

if "errors" in data:
    print("❌ Error:")
    print(data["errors"])
    exit()

for board in data["data"]["boards"]:

    print("\n" + "=" * 60)
    print("BOARD:", board["name"])
    print("BOARD ID:", board["id"])
    print("=" * 60)

    for item in board["items_page"]["items"]:

        print("\nItem:", item["name"])

        for column in item["column_values"]:
            print(
                f"  {column['id']}: {column['text']}"
            )