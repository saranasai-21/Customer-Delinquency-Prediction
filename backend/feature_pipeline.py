# backend/feature_pipeline.py

import pandas as pd

class FeatureStorePipeline:
    def __init__(self):
        self.month_cols = ["Month_1", "Month_2", "Month_3", "Month_4", "Month_5", "Month_6"]
        self.mapping = {"On-time": 0, "Late": 1, "Missed": 2}

    def clean_and_map_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Standardize Employment Status
        if "Employment_Status" in df.columns:
            df["Employment_Status"] = (
                df["Employment_Status"]
                .astype(str)
                .str.strip()
                .str.lower()
                .replace({"emp": "employed", "student": "student", "unemployed": "unemployed"})
            )

        # Map monthly columns to integers
        for col in self.month_cols:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].map(self.mapping).fillna(0).astype(int)
        return df

    def calculate_engineered_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Base Delinquency Aggregations
        df["Total_Late"] = (df[self.month_cols] == 1).sum(axis=1)
        df["Total_Missed"] = (df[self.month_cols] == 2).sum(axis=1)
        df["Repayment_Score"] = df[self.month_cols].sum(axis=1)
        df["Avg_Repayment"] = df[self.month_cols].mean(axis=1)
        df["Repayment_Std"] = df[self.month_cols].std(axis=1).fillna(0.0)
        df["Repayment_Trend"] = df["Month_6"] - df["Month_1"]

        # Financial Ratios & Interactions
        df["Utilization_DTI"] = df["Credit_Utilization"] * df["Debt_to_Income_Ratio"]
        df["Payment_Stress"] = df["Missed_Payments"] * df["Credit_Utilization"]
        df["Income_to_Loan_Ratio"] = df["Income"] / (df["Loan_Balance"] + 1.0)
        df["Credit_Score_Utilization"] = df["Credit_Score"] * (1.0 - df["Credit_Utilization"])
        
        if "Age" in df.columns:
            df["Income_per_Age"] = df["Income"] / (df["Age"] + 1.0)
            
        return df

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """Processes raw inputs into a model-ready feature DataFrame."""
        df = self.clean_and_map_categorical(df)
        df = self.calculate_engineered_features(df)
        return df
