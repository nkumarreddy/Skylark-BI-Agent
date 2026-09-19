import os
import asyncio
import httpx

from dotenv import load_dotenv
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

load_dotenv()

TOKEN = os.getenv("MONDAY_API_TOKEN")
WORK_ORDERS_BOARD_ID = os.getenv("WORK_ORDERS_BOARD_ID")
DEALS_BOARD_ID = os.getenv("DEALS_BOARD_ID")


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

            result = await client.call_tool(
                "get_board_items_page",
                {
                    "boardId": int(WORK_ORDERS_BOARD_ID),
                    "limit": 10
                }
            )

            print("\nWORK ORDERS DATA:\n")
            print(result)


if __name__ == "__main__":
    asyncio.run(main())