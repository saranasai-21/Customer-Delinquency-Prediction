# backend/pipeline/feature_store.py

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.feature_selection import mutual_info_classif
from sklearn.preprocessing import StandardScaler

class FeatureStorePipeline:
    def __init__(self, use_isolation_forest: bool = True):
        self.use_isolation_forest = use_isolation_forest
        self.scaler = StandardScaler()
        self.month_cols = ["Month_1", "Month_2", "Month_3", "Month_4", "Month_5", "Month_6"]
        self.mapping = {"On-time": 0, "Late": 1, "Missed": 2}

    def clean_and_map_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardizes employment status and maps historical monthly statuses to numeric scores."""
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

        # Map monthly columns to integers (0, 1, 2)
        for col in self.month_cols:
            if col in df.columns:
                # If they are already numeric, do not map
                if not pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].map(self.mapping).fillna(0).astype(int)
        return df

    def calculate_engineered_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Computes advanced features, interaction columns, and rolling/historical trends."""
        df = df.copy()

        # 1. Base Delinquency Aggregations
        df["Total_Late"] = (df[self.month_cols] == 1).sum(axis=1)
        df["Total_Missed"] = (df[self.month_cols] == 2).sum(axis=1)
        df["Repayment_Score"] = df[self.month_cols].sum(axis=1)
        df["Avg_Repayment"] = df[self.month_cols].mean(axis=1)
        
        # 2. Rolling statistics (Standard deviation over 6 months)
        df["Repayment_Std"] = df[self.month_cols].std(axis=1).fillna(0.0)

        # 3. Delinquency Trend (difference between recent Month_6 and historical Month_1)
        df["Repayment_Trend"] = df["Month_6"] - df["Month_1"]

        # 4. Financial Ratios & Interactions
        df["Utilization_DTI"] = df["Credit_Utilization"] * df["Debt_to_Income_Ratio"]
        df["Payment_Stress"] = df["Missed_Payments"] * df["Credit_Utilization"]
        df["Income_to_Loan_Ratio"] = df["Income"] / (df["Loan_Balance"] + 1.0)
        df["Credit_Score_Utilization"] = df["Credit_Score"] * (1.0 - df["Credit_Utilization"])
        
        # 5. Segment interactions
        if "Age" in df.columns:
            df["Income_per_Age"] = df["Income"] / (df["Age"] + 1.0)
            
        return df

    def detect_outliers(self, df: pd.DataFrame, contamination: float = 0.02) -> pd.DataFrame:
        """Flags statistical outliers using Isolation Forest to preserve clean training inputs."""
        if not self.use_isolation_forest:
            return df
        
        df = df.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Exclude Target and Customer IDs from outlier detection
        cols_to_use = [c for c in numeric_cols if c not in ["Customer_ID", "Delinquent_Account"]]
        
        if len(cols_to_use) > 0:
            iso = IsolationForest(contamination=contamination, random_state=42)
            # Impute temporarily for outlier check
            temp_df = df[cols_to_use].fillna(df[cols_to_use].median())
            outliers = iso.fit_predict(temp_df)
            df["Is_Outlier"] = np.where(outliers == -1, 1, 0)
        else:
            df["Is_Outlier"] = 0
            
        return df

    def get_mutual_information_scores(self, X: pd.DataFrame, y: pd.Series) -> pd.Series:
        """Computes Mutual Information coefficient scores to prioritize top features."""
        # Convert categoricals temporarily to numeric codes
        X_encoded = X.copy()
        for col in X_encoded.select_dtypes(include=["object", "str"]).columns:
            X_encoded[col] = X_encoded[col].astype("category").cat.codes
            
        # Impute missing values for mutual info computation
        X_imputed = X_encoded.fillna(X_encoded.median())
        
        scores = mutual_info_classif(X_imputed, y, random_state=42)
        return pd.Series(scores, index=X.columns).sort_values(ascending=False)

    def process(self, df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
        """Full pipeline processing raw inputs into an ML-ready feature DataFrame."""
        df = self.clean_and_map_categorical(df)
        df = self.calculate_engineered_features(df)
        
        if is_training:
            df = self.detect_outliers(df)
            # Drop outliers for cleaner model fitting
            df = df[df["Is_Outlier"] == 0].drop(columns=["Is_Outlier"])
            
        return df
