def answer_question(question, work_orders_df, deals_df):

    question = question.lower().strip()

    # =========================================================
    # WORK ORDER METRICS — SPECIFIC CONDITIONS FIRST
    # =========================================================

    # Completed work orders
    if "completed" in question and "work order" in question:
        count = (
            work_orders_df["Execution Status"]
            == "Completed"
        ).sum()

        return f"There are {count} completed work orders."

    # Ongoing work orders
    if "ongoing" in question and "work order" in question:
        count = (
            work_orders_df["Execution Status"]
            == "Ongoing"
        ).sum()

        return f"There are {count} ongoing work orders."

    # Billed work orders
    if "billed" in question and "work order" in question:
        count = (
            work_orders_df["Billing Status"]
            == "Billed"
        ).sum()

        return f"There are {count} billed work orders."

    # Work orders by sector
    if (
        "sector" in question
        and (
            "work order" in question
            or "working" in question
            or "work" in question
        )
    ):
        sector_counts = (
            work_orders_df["Sector"]
            .value_counts()
            .to_dict()
        )

        return f"Work orders by sector: {sector_counts}"

    # Total work orders
    if "work order" in question and (
        "total" in question
        or "how many" in question
    ):
        return f"There are {len(work_orders_df)} total work orders."

    # =========================================================
    # DEAL METRICS — SPECIFIC CONDITIONS FIRST
    # =========================================================

    # Open deals
    if "open deal" in question:
        count = (
            deals_df["Deal Status"]
            == "Open"
        ).sum()

        return f"There are {count} open deals."

    # Won deals
    if "won deal" in question:
        count = (
            deals_df["Deal Status"]
            == "Won"
        ).sum()

        return f"There are {count} won deals."

    # Deals by sector
    if (
        "sector" in question
        and (
            "deal" in question
            or "deals" in question
        )
    ):
        sector_counts = (
            deals_df["Sector/service"]
            .value_counts()
            .to_dict()
        )

        return f"Deals by sector: {sector_counts}"

    # Total deals
    if "total deal" in question:
        return f"There are {len(deals_df)} total deals."

    # =========================================================
    # PIPELINE VALUE
    # =========================================================

    # Open pipeline value
    if (
        "pipeline" in question
        and (
            "value" in question
            or "amount" in question
            or "worth" in question
        )
    ):
        open_deals = deals_df[
            deals_df["Deal Status"].isin(
                ["Open", "On Hold"]
            )
        ]

        pipeline_value = (
            open_deals["Masked Deal value"]
            .sum()
        )

        return (
            f"The open pipeline value is "
            f"₹{pipeline_value:,.2f}."
        )

    # Pipeline health
    if "pipeline" in question:

        total_deals = len(deals_df)

        open_deals = (
            deals_df["Deal Status"]
            == "Open"
        ).sum()

        won_deals = (
            deals_df["Deal Status"]
            == "Won"
        ).sum()

        dead_deals = (
            deals_df["Deal Status"]
            == "Dead"
        ).sum()

        on_hold_deals = (
            deals_df["Deal Status"]
            == "On Hold"
        ).sum()

        return (
            f"Pipeline summary: "
            f"{total_deals} total deals, "
            f"{open_deals} open, "
            f"{won_deals} won, "
            f"{dead_deals} dead, "
            f"{on_hold_deals} on hold."
        )

    # =========================================================
    # FALLBACK
    # =========================================================

    return (
        "I could not answer that question yet. "
        "Try asking about work orders, deals, "
        "execution status, billing, sectors, or pipeline."
    )