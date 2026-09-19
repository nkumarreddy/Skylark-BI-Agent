import os
import json
import asyncio
import httpx

from dotenv import load_dotenv
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

load_dotenv()

TOKEN = os.getenv("MONDAY_API_TOKEN")
WORK_ORDERS_BOARD_ID = os.getenv("WORK_ORDERS_BOARD_ID")
DEALS_BOARD_ID = os.getenv("DEALS_BOARD_ID")


async def get_all_items(client, board_id):

    all_items = []
    cursor = None

    while True:

        arguments = {
            "boardId": int(board_id),
            "limit": 500,
            "includeColumns": True
        }

        if cursor:
            arguments["cursor"] = cursor

        result = await client.call_tool(
            "get_board_items_page",
            arguments
        )

        data = result.structured_content

        all_items.extend(data["items"])

        pagination = data.get("pagination", {})

        if not pagination.get("has_more"):
            break

        cursor = pagination.get("nextCursor")

        if not cursor:
            break

    return all_items


async def main():

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    async with httpx.AsyncClient(
        headers=headers,
        timeout=httpx.Timeout(30.0, read=300.0)
    ) as http_client:

        transport = streamable_http_client(
            "https://mcp.monday.com/mcp",
            http_client=http_client
        )

        async with Client(transport) as client:

            print("Connected to Monday MCP!")

            print("\nLoading Work Orders...")
            work_orders = await get_all_items(
                client,
                WORK_ORDERS_BOARD_ID
            )

            print("Work Orders:", len(work_orders))

            print("\nLoading Deals...")
            deals = await get_all_items(
                client,
                DEALS_BOARD_ID
            )

            print("Deals:", len(deals))
            print("\n===== SAMPLE WORK ORDER =====")
            print(json.dumps(work_orders[0], indent=2))

            print("\n===== SAMPLE DEAL =====")
            print(json.dumps(deals[0], indent=2))


if __name__ == "__main__":
    asyncio.run(main())