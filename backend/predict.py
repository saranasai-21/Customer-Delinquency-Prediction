# predict.py

import os
import joblib
import pandas as pd

from preprocessing import preprocess_data

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "..", "models", "best_model.pkl")

model = None
model_load_error = None
try:
    model = joblib.load(model_path)
except Exception as e:
    model_load_error = str(e)
    print(f"Warning: Could not load model from {model_path}: {e}")


def predict_customer(customer_dict):

    if model is None:
        exists = os.path.exists(model_path)
        # Check current working directory contents
        cwd_files = os.listdir(".") if os.path.exists(".") else []
        return {
            "probability": 0.0,
            "risk": f"UNKNOWN (Model load error: {model_load_error}. Path: {model_path}. Exists: {exists}. CWD: {os.getcwd()}. CWD files: {cwd_files})"
        }

    df = pd.DataFrame(
        [customer_dict]
    )

    df = preprocess_data(df)

    probability = (
        model.predict_proba(df)[0][1]
    )

    if probability > .7:
        risk = "HIGH"

    elif probability > .4:
        risk = "MEDIUM"

    else:
        risk = "LOW"

    return {

        "probability": round(
            probability,
            3
        ),

        "risk": risk

    }
