# backend/api/routers/model.py

import os
import pandas as pd
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from backend.api.dependencies import (
    get_predict_service,
    get_prediction_repo,
    get_customer_repo,
    require_role
)
from backend.services.predict_service import PredictService
from backend.repositories.repositories import PredictionRepository, CustomerRepository

# Try to import Evidently AI metrics
HAS_EVIDENTLY = False
try:
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset
    HAS_EVIDENTLY = True
except ImportError:
    pass

router = APIRouter(prefix="/model", tags=["model"])

@router.get("/info")
def get_model_info(
    predict_service: PredictService = Depends(get_predict_service),
    _ = Depends(require_role(["admin", "analyst"]))
):
    """Returns metadata about the active ML model."""
    has_model = predict_service.model is not None
    return {
        "model_loaded": has_model,
        "model_path": predict_service.model_path,
        "algorithm": str(predict_service.model.named_steps["model"]) if has_model else "HistGradientBoosting-Stacked (Mocked)",
        "features": predict_service.feature_pipeline.month_cols + [
            "Total_Late", "Total_Missed", "Repayment_Score", "Avg_Repayment",
            "Utilization_DTI", "Payment_Stress", "Income_to_Loan_Ratio"
        ]
    }


@router.post("/shap")
def get_shap_explanation(
    customer_id: int,
    customer_data: Dict[str, Any],
    predict_service: PredictService = Depends(get_predict_service),
    _ = Depends(require_role(["admin", "analyst"]))
):
    """Generates local SHAP explanation values for a specific customer risk score."""
    from backend.services.agent_service import SHAPExplainManager
    
    # Preprocess instance
    cust_data = customer_data.copy()
    cust_data["Customer_ID"] = str(customer_id)
    df_raw = pd.DataFrame([cust_data])
    processed_df = predict_service.feature_pipeline.process(df_raw, is_training=False)
    features_df = processed_df.drop(columns=["Customer_ID"], errors="ignore")
    
    if predict_service.model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model is not loaded. Cannot run SHAP explanation."
        )
        
    try:
        explainer = SHAPExplainManager(predict_service.model, list(features_df.columns))
        explanation = explainer.explain_instance(features_df)
        return explanation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SHAP explanation failed: {str(e)}"
        )


@router.get("/drift_report")
def get_drift_report(
    prediction_repo: PredictionRepository = Depends(get_prediction_repo),
    customer_repo: CustomerRepository = Depends(get_customer_repo),
    _ = Depends(require_role(["admin"]))
):
    """Calculates data distribution drift using Evidently AI comparing baseline and current inputs."""
    if not HAS_EVIDENTLY:
        return {
            "status": "warning",
            "message": "Evidently AI is not installed in the current environment.",
            "drift_detected": False,
            "metrics": {"numerical_drift_ratio": 0.0, "categorical_drift_ratio": 0.0}
        }
        
    try:
        # Load baseline dataset
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dataset_path = os.path.join(base_dir, "..", "..", "data", "Delinquency_prediction_dataset.xlsx")
        
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Baseline dataset not found at {dataset_path}")
            
        reference_df = pd.read_excel(dataset_path)
        
        # Load recent logged predictions as inference dataset
        recent_preds = prediction_repo.get_recent_predictions(limit=100)
        if len(recent_preds) < 10:
            return {
                "status": "warning",
                "message": "Insufficient prediction logs to calculate drift. Need at least 10 logs.",
                "drift_detected": False
            }
            
        # Reconstruct inference DataFrame
        records = []
        for p in recent_preds:
            cust = customer_repo.get_customer(p.customer_id)
            if cust:
                records.append({
                    "Age": cust.age,
                    "Income": cust.income,
                    "Credit_Score": cust.credit_score,
                    "Loan_Balance": cust.loan_balance,
                    "Debt_to_Income_Ratio": cust.debt_to_income_ratio,
                    "Credit_Utilization": cust.credit_utilization,
                    "Missed_Payments": cust.missed_payments,
                    "Employment_Status": cust.employment_status
                })
        
        current_df = pd.DataFrame(records)
        
        # Align features
        features = ["Age", "Income", "Credit_Score", "Loan_Balance", "Debt_to_Income_Ratio", "Credit_Utilization", "Missed_Payments"]
        ref_features = reference_df[features].dropna()
        cur_features = current_df[features].dropna()
        
        data_drift_report = Report(metrics=[DataDriftPreset()])
        data_drift_report.run(reference_data=ref_features, current_data=cur_features)
        report_dict = data_drift_report.as_dict()
        
        return {
            "status": "success",
            "drift_detected": report_dict["metrics"][0]["result"]["dataset_drift"],
            "number_of_drifted_features": report_dict["metrics"][0]["result"]["number_of_drifted_features"],
            "share_of_drifted_features": report_dict["metrics"][0]["result"]["share_of_drifted_features"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Drift analysis execution failed: {str(e)}"
        )
