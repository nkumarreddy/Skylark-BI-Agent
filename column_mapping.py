import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("MONDAY_API_TOKEN")

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

    data = response.json()

    if "errors" in data:
        print(data["errors"])
        continue

    board = data["data"]["boards"][0]

    print("\n" + "=" * 60)
    print(board_name)
    print("=" * 60)

    for column in board["columns"]:
        print(
            f'{column["id"]}  -->  '
            f'{column["title"]}  '
            f'[{column["type"]}]'
        )