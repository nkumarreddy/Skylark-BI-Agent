import asyncio
import httpx
import streamlit as st

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


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Skylark Business Intelligence Agent",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data(ttl=300)
def load_data():

    async def fetch_data():

        headers = {
            "Authorization": f"Bearer {TOKEN}"
        }

        async with httpx.AsyncClient(
            headers=headers,
            timeout=httpx.Timeout(
                30.0,
                read=300.0
            )
        ) as http_client:

            transport = streamable_http_client(
                "https://mcp.monday.com/mcp",
                http_client=http_client
            )

            async with Client(transport) as client:

                # -------------------------
                # WORK ORDERS
                # -------------------------

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
                # DEALS
                # -------------------------

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

                return work_orders_df, deals_df

    return asyncio.run(fetch_data())


# =========================================================
# HEADER
# =========================================================

st.title("📊 Skylark Business Intelligence Agent")

st.write(
    "Ask questions about Work Orders and Deals "
    "from the connected monday.com boards."
)

st.divider()


# =========================================================
# LOAD DATA
# =========================================================

try:

    with st.spinner("Loading live data from monday.com..."):

        work_orders_df, deals_df = load_data()

    st.success(
        f"Connected to monday.com • "
        f"{len(work_orders_df)} Work Orders • "
        f"{len(deals_df)} Deals"
    )

except Exception as e:

    st.error(
        f"Could not load monday.com data: {e}"
    )

    st.stop()


# =========================================================
# KPI CARDS
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Work Orders",
        len(work_orders_df)
    )

with col2:
    completed = (
        work_orders_df["Execution Status"]
        == "Completed"
    ).sum()

    st.metric(
        "Completed",
        int(completed)
    )

with col3:
    open_deals = (
        deals_df["Deal Status"]
        == "Open"
    ).sum()

    st.metric(
        "Open Deals",
        int(open_deals)
    )

with col4:

    won_deals = (
        deals_df["Deal Status"]
        == "Won"
    ).sum()

    st.metric(
        "Won Deals",
        int(won_deals)
    )


st.divider()


# =========================================================
# QUESTION INPUT
# =========================================================

st.subheader("Ask the Business Intelligence Agent")

question = st.text_input(
    "Business question",
    placeholder=(
        "Example: How many completed work orders are there?"
    )
)


# =========================================================
# ANSWER
# =========================================================

if question:

    with st.spinner("Analyzing..."):

        answer = answer_question(
            question,
            work_orders_df,
            deals_df
        )

    st.subheader("Answer")

    st.info(answer)


# =========================================================
# EXAMPLE QUESTIONS
# =========================================================

st.divider()

st.subheader("Example questions")

examples = [
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

for example in examples:
    st.write("• " + example)