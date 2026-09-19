import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("MONDAY_API_TOKEN")

print("Token loaded:", TOKEN is not None)
print("Token length:", len(TOKEN) if TOKEN else 0)

BOARDS = {
    "WORK ORDERS": os.getenv("WORK_ORDERS_BOARD_ID"),
    "DEALS": os.getenv("DEALS_BOARD_ID"),
}

URL = "https://api.monday.com/v2"

headers = {
    "Authorization": TOKEN,
    "Content-Type": "application/json"
}

query = """
query ($boardId: ID!) {
    boards(ids: [$boardId]) {
        id
        name
        columns {
            id
            title
            type
        }
    }
}
"""

for board_name, board_id in BOARDS.items():

    print("\n" + "=" * 60)
    print(board_name)
    print("=" * 60)

    response = requests.post(
        URL,
        json={
            "query": query,
            "variables": {
                "boardId": board_id
            }
        },
        headers=headers
    )

    print("Status:", response.status_code)

    data = response.json()

    if "errors" in data:
        print("ERROR:")
        print(data["errors"])
        continue

    board = data["data"]["boards"][0]

    print("Board ID:", board["id"])
    print("Board Name:", board["name"])
    print("\nColumns:")

    for column in board["columns"]:
        print(
            f'ID: {column["id"]} | '
            f'TITLE: {column["title"]} | '
            f'TYPE: {column["type"]}'
        )