import asyncio
import httpx

from dotenv import load_dotenv
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

from data_processor import (
    TOKEN,
    WORK_ORDERS_BOARD_ID,
    DEALS_BOARD_ID,
    get_all_items,
    get_column_mapping,
    items_to_dataframe,
    clean_text_values,
    convert_data_types
)

from query_engine import answer_question


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

            # -------------------------
            # LOAD WORK ORDERS
            # -------------------------

            print("\nLoading Work Orders...")

            work_orders = await get_all_items(
                client,
                WORK_ORDERS_BOARD_ID
            )

            work_order_mapping = get_column_mapping(
                WORK_ORDERS_BOARD_ID
            )

            work_orders_df = items_to_dataframe(
                work_orders,
                work_order_mapping
            )

            # -------------------------
            # LOAD DEALS
            # -------------------------

            print("Loading Deals...")

            deals = await get_all_items(
                client,
                DEALS_BOARD_ID
            )

            deal_mapping = get_column_mapping(
                DEALS_BOARD_ID
            )

            deals_df = items_to_dataframe(
                deals,
                deal_mapping
            )

            # -------------------------
            # CLEAN DATA
            # -------------------------

            work_orders_df = clean_text_values(
                work_orders_df
            )

            deals_df = clean_text_values(
                deals_df
            )

            work_orders_df = convert_data_types(
                work_orders_df
            )

            deals_df = convert_data_types(
                deals_df
            )

            # -------------------------
            # TEST QUESTIONS
            # -------------------------

            questions = [
                "How many work orders are there?",
                "How many completed work orders are there?",
                "How many ongoing work orders are there?",
                "How many work orders are billed?",
                "How many open deals are there?",
                "How many won deals are there?",
                "Show me work orders by sector",
                "Show me deals by sector",
                "Give me a pipeline summary",
                "What is the open pipeline value?"
            ]

            for question in questions:

                print("\n" + "=" * 60)
                print("QUESTION:", question)

                answer = answer_question(
                    question,
                    work_orders_df,
                    deals_df
                )

                print("ANSWER:", answer)


if __name__ == "__main__":
    asyncio.run(main())