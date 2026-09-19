import os
import asyncio
import httpx
import pandas as pd
import requests

from dotenv import load_dotenv
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

load_dotenv()

TOKEN = os.getenv("MONDAY_API_TOKEN")
WORK_ORDERS_BOARD_ID = os.getenv("WORK_ORDERS_BOARD_ID")
DEALS_BOARD_ID = os.getenv("DEALS_BOARD_ID")

MONDAY_URL = "https://api.monday.com/v2"


def get_column_mapping(board_id):

    query = """
    query ($boardId: ID!) {
        boards(ids: [$boardId]) {
            columns {
                id
                title
                type
            }
        }
    }
    """

    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }

    response = requests.post(
        MONDAY_URL,
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
        raise Exception(data["errors"])

    columns = data["data"]["boards"][0]["columns"]

    return {
        column["id"]: column["title"]
        for column in columns
    }


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


def items_to_dataframe(items, column_mapping):

    rows = []

    for item in items:

        row = {
            "Name": item.get("name")
        }

        column_values = item.get("column_values", {})

        for column_id, value in column_values.items():

            column_name = column_mapping.get(
                column_id,
                column_id
            )

            row[column_name] = value

        rows.append(row)

    return pd.DataFrame(rows)


def clean_text_values(df):

    df = df.copy()

    # Remove leading/trailing spaces
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    # Convert accidental header-like values to missing values
    header_values = {
        "Deal Status",
        "Deal Stage",
        "Sector/service"
    }

    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].replace(
            list(header_values),
            pd.NA
        )

    # Normalize known billing-status inconsistency
    if "Billing Status" in df.columns:
        df["Billing Status"] = df["Billing Status"].replace(
            {
                "BIlled": "Billed"
            }
        )

    return df


def convert_data_types(df):

    df = df.copy()

    # -------------------------
    # DATE COLUMNS
    # -------------------------

    date_columns = [
        "Data Delivery Date",
        "Date of PO/LOI",
        "Probable Start Date",
        "Probable End Date",
        "Last invoice date",
        "Collection Date",
        "Close Date (A)",
        "Tentative Close Date",
        "Created Date"
    ]

    for column in date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    # -------------------------
    # FINANCIAL COLUMNS
    # -------------------------

    financial_columns = [
        "Amount in Rupees (Excl of GST) (Masked)",
        "Amount in Rupees (Incl of GST) (Masked)",
        "Billed Value in Rupees (Excl of GST.) (Masked)",
        "Billed Value in Rupees (Incl of GST.) (Masked)",
        "Collected Amount in Rupees (Incl. of GST.) (Masked)",
        "Amount to be billed in Rs. (Exl. of GST) (Masked)",
        "Amount to be billed in Rs. (Incl. of GST) (Masked)",
        "Amount Receivable (Masked)",
        "Masked Deal value"
    ]

    for column in financial_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column].astype(str).str.replace(",", ""),
                errors="coerce"
            )

    # -------------------------
    # QUANTITY COLUMNS
    # -------------------------

    quantity_columns = [
        "Quantity by Ops",
        "Quantities as per PO",
        "Quantity billed (till date)",
        "Balance in quantity"
    ]

    for column in quantity_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


def calculate_pipeline_metrics(deals_df):

    total_deals = len(deals_df)

    won = (deals_df["Deal Status"] == "Won").sum()
    open_deals = (deals_df["Deal Status"] == "Open").sum()
    dead = (deals_df["Deal Status"] == "Dead").sum()
    on_hold = (deals_df["Deal Status"] == "On Hold").sum()

    pipeline_value = deals_df.loc[
        deals_df["Deal Status"].isin(["Open", "On Hold"]),
        "Masked Deal value"
    ].sum()

    return {
        "total_deals": total_deals,
        "won_deals": int(won),
        "open_deals": int(open_deals),
        "dead_deals": int(dead),
        "on_hold_deals": int(on_hold),
        "open_pipeline_value": float(pipeline_value)
    }


def calculate_work_order_metrics(work_orders_df):

    total_work_orders = len(work_orders_df)

    execution_counts = (
        work_orders_df["Execution Status"]
        .value_counts(dropna=False)
        .to_dict()
    )

    billing_counts = (
        work_orders_df["Billing Status"]
        .value_counts(dropna=False)
        .to_dict()
    )

    sector_counts = (
        work_orders_df["Sector"]
        .value_counts(dropna=False)
        .to_dict()
    )

    return {
        "total_work_orders": total_work_orders,
        "execution_status": execution_counts,
        "billing_status": billing_counts,
        "sector_distribution": sector_counts
    }


def calculate_sector_metrics(work_orders_df, deals_df):

    work_order_sector = (
        work_orders_df["Sector"]
        .value_counts(dropna=False)
        .to_dict()
    )

    deal_sector = (
        deals_df["Sector/service"]
        .value_counts(dropna=False)
        .to_dict()
    )

    return {
        "work_order_sector": work_order_sector,
        "deal_sector": deal_sector
    }


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
            # WORK ORDERS
            # -------------------------

            print("\nLoading Work Orders...")

            work_orders = await get_all_items(
                client,
                WORK_ORDERS_BOARD_ID
            )

            print("Work Orders:", len(work_orders))

            work_order_mapping = get_column_mapping(
                WORK_ORDERS_BOARD_ID
            )

            work_orders_df = items_to_dataframe(
                work_orders,
                work_order_mapping
            )

            # -------------------------
            # DEALS
            # -------------------------

            print("\nLoading Deals...")

            deals = await get_all_items(
                client,
                DEALS_BOARD_ID
            )

            print("Deals:", len(deals))

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
            # PIPELINE HEALTH
            # -------------------------

            pipeline = calculate_pipeline_metrics(
                deals_df
            )

            print("\n===== PIPELINE HEALTH =====")

            for key, value in pipeline.items():
                print(f"{key}: {value}")

            # -------------------------
            # WORK ORDER OPERATIONS
            # -------------------------

            work_order_metrics = calculate_work_order_metrics(
                work_orders_df
            )

            print("\n===== WORK ORDER OPERATIONS =====")

            print(
                "Total work orders:",
                work_order_metrics["total_work_orders"]
            )

            print("\nExecution Status:")

            for key, value in work_order_metrics[
                "execution_status"
            ].items():
                print(f"{key}: {value}")

            print("\nBilling Status:")

            for key, value in work_order_metrics[
                "billing_status"
            ].items():
                print(f"{key}: {value}")

            print("\nSector Distribution:")

            for key, value in work_order_metrics[
                "sector_distribution"
            ].items():
                print(f"{key}: {value}")

            # -------------------------
            # SECTOR PERFORMANCE
            # -------------------------

            sector_metrics = calculate_sector_metrics(
                work_orders_df,
                deals_df
            )

            print("\n===== SECTOR PERFORMANCE =====")

            print("\nWork Orders by Sector:")

            for sector, count in sector_metrics[
                "work_order_sector"
            ].items():
                print(f"{sector}: {count}")

            print("\nDeals by Sector:")

            for sector, count in sector_metrics[
                "deal_sector"
            ].items():
                print(f"{sector}: {count}")

            # -------------------------
            # RESULTS
            # -------------------------

            print("\n===== WORK ORDERS DATAFRAME =====")

            print("Shape:", work_orders_df.shape)

            print("\nColumns:")

            for column in work_orders_df.columns:
                print("-", column)

            print("\n===== DEALS DATAFRAME =====")

            print("Shape:", deals_df.shape)

            print("\nColumns:")

            for column in deals_df.columns:
                print("-", column)

            # -------------------------
            # DATA QUALITY CHECK
            # -------------------------

            print("\n===== SAMPLE IMPORTANT VALUES =====")

            print("\nWork Order Execution Status:")

            print(
                work_orders_df[
                    "Execution Status"
                ].value_counts(dropna=False)
            )

            print("\nWork Order Billing Status:")

            print(
                work_orders_df[
                    "Billing Status"
                ].value_counts(dropna=False)
            )

            print("\nWork Order Sector:")

            print(
                work_orders_df[
                    "Sector"
                ].value_counts(dropna=False)
            )

            print("\nDeal Status:")

            print(
                deals_df[
                    "Deal Status"
                ].value_counts(dropna=False)
            )

            print("\nDeal Stage:")

            print(
                deals_df[
                    "Deal Stage"
                ].value_counts(dropna=False)
            )

            print("\nDeal Sector/Service:")

            print(
                deals_df[
                    "Sector/service"
                ].value_counts(dropna=False)
            )

            # -------------------------
            # DATE SAMPLE
            # -------------------------

            print("\n===== DATE SAMPLE =====")

            date_columns = [
                "Data Delivery Date",
                "Date of PO/LOI",
                "Probable Start Date",
                "Probable End Date",
                "Last invoice date",
                "Close Date (A)",
                "Tentative Close Date",
                "Created Date"
            ]

            for column in date_columns:

                if column in work_orders_df.columns:

                    print(f"\n{column}:")

                    print(
                        work_orders_df[
                            column
                        ].dropna().head(5).tolist()
                    )

                if column in deals_df.columns:

                    print(f"\n{column}:")

                    print(
                        deals_df[
                            column
                        ].dropna().head(5).tolist()
                    )

            # -------------------------
            # FINANCIAL SAMPLE
            # -------------------------

            print("\n===== FINANCIAL SAMPLE =====")

            financial_columns = [
                "Amount in Rupees (Excl of GST) (Masked)",
                "Amount in Rupees (Incl of GST) (Masked)",
                "Billed Value in Rupees (Excl of GST.) (Masked)",
                "Billed Value in Rupees (Incl of GST.) (Masked)",
                "Collected Amount in Rupees (Incl. of GST.) (Masked)",
                "Amount Receivable (Masked)",
                "Masked Deal value"
            ]

            for column in financial_columns:

                if column in work_orders_df.columns:

                    print(f"\n{column}:")

                    print(
                        work_orders_df[
                            column
                        ].dropna().head(5).tolist()
                    )

                if column in deals_df.columns:

                    print(f"\n{column}:")

                    print(
                        deals_df[
                            column
                        ].dropna().head(5).tolist()
                    )


if __name__ == "__main__":
    asyncio.run(main())