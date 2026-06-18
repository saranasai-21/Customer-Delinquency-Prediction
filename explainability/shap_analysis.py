import os
import shap
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "..", "models", "best_model.pkl")

model = None
explainer = None

try:
    model = joblib.load(model_path)
    explainer = shap.Explainer(
        model.named_steps["model"]
    )
except Exception as e:
    print(f"Warning: Could not load model from {model_path}: {e}")

def explain(df):

    if explainer is None:
        print("Explainer is not initialized because the model could not be loaded.")
        return

    values = explainer(df)

    shap.plots.waterfall(
        values[0]
    )