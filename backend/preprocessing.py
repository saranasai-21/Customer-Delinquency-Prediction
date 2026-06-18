# preprocessing.py

import pandas as pd


def preprocess_data(df):

    # ------------------------
    # Standardize employment status
    # ------------------------
    if "Employment_Status" in df.columns:

        df["Employment_Status"] = (
            df["Employment_Status"]
            .str.strip()
            .str.lower()
            .replace({
                "emp": "employed",
                "employed": "employed"
            })
        )

    # ------------------------
    # Convert month status into numbers
    # ------------------------
    month_cols = [
        "Month_1",
        "Month_2",
        "Month_3",
        "Month_4",
        "Month_5",
        "Month_6"
    ]

    mapping = {
        "On-time": 0,
        "Late": 1,
        "Missed": 2
    }

    for col in month_cols:
        if col in df.columns:
            df[col] = df[col].map(mapping)

    # ------------------------
    # Feature engineering
    # ------------------------
    df["Total_Late"] = (
        df[month_cols] == 1
    ).sum(axis=1)

    df["Total_Missed"] = (
        df[month_cols] == 2
    ).sum(axis=1)

    df["Repayment_Score"] = (
        df[month_cols]
    ).sum(axis=1)

    df["Avg_Repayment"] = (
        df[month_cols]
    ).mean(axis=1)

    df["Utilization_DTI"] = (
        df["Credit_Utilization"]
        *
        df["Debt_to_Income_Ratio"]
    )

    df["Payment_Stress"] = (
        df["Missed_Payments"]
        *
        df["Credit_Utilization"]
    )

    df["Income_to_Loan_Ratio"] = (
        df["Income"]
        /
        (df["Loan_Balance"] + 1)
    )

    return df
