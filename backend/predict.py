# backend/predict.py

import os
import sys
import joblib
import pandas as pd

# Inject paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from feature_pipeline import FeatureStorePipeline

# Model path
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "best_model.pkl")

# Sample customer for test run
SAMPLE_CUSTOMER = {
    "Age": 38,
    "Income": 75000.0,
    "Credit_Score": 680.0,
    "Loan_Balance": 22000.0,
    "Debt_to_Income_Ratio": 0.42,
    "Credit_Utilization": 0.65,
    "Missed_Payments": 1,
    "Employment_Status": "employed",
    "Month_1": "On-time",
    "Month_2": "Late",
    "Month_3": "On-time",
    "Month_4": "On-time",
    "Month_5": "On-time",
    "Month_6": "On-time"
}

def predict(customer_data: dict) -> dict:
    # 1. Load Model
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Please run train_model.py first.")
        
    model = joblib.load(MODEL_PATH)
    
    # 2. Build Pipeline and Preprocess
    pipeline = FeatureStorePipeline()
    df_raw = pd.DataFrame([customer_data])
    df_processed = pipeline.process(df_raw)
    
    # Drop Customer_ID and target columns if present
    features_df = df_processed.drop(columns=["Customer_ID", "Delinquent_Account"], errors="ignore")
    
    # 3. Predict probability
    probability = float(model.predict_proba(features_df)[0][1])
    
    # Decisional risk classification
    if probability >= 0.70:
        risk = "HIGH"
    elif probability >= 0.45:
        risk = "MEDIUM"
    else:
        risk = "LOW"
        
    return {
        "probability": round(probability, 4),
        "risk_level": risk,
        "prediction": 1 if probability >= 0.45 else 0
    }

if __name__ == "__main__":
    print("--- Running Customer Delinquency Prediction Sample ---")
    print(f"Loading model from: {MODEL_PATH}")
    try:
        res = predict(SAMPLE_CUSTOMER)
        print("\nInput Customer Data:")
        for k, v in SAMPLE_CUSTOMER.items():
            print(f"  {k}: {v}")
        print("\nPrediction Results:")
        print(f"  Probability of Delinquency: {res['probability'] * 100:.2f}%")
        print(f"  Risk Level: {res['risk_level']}")
        print(f"  Binary Outcome: {res['prediction']}")
    except Exception as e:
        print(f"Error executing prediction: {e}")
