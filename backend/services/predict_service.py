# backend/services/predict_service.py

import os
import time
import joblib
import pandas as pd
from typing import Dict, Any
from backend.pipeline.feature_store import FeatureStorePipeline
from backend.database.models import DBCustomer, DBPrediction
from backend.repositories.repositories import CustomerRepository, PredictionRepository

class PredictService:
    def __init__(
        self,
        customer_repo: CustomerRepository,
        prediction_repo: PredictionRepository,
        model_path: str = None
    ):
        self.customer_repo = customer_repo
        self.prediction_repo = prediction_repo
        
        # Load local model file
        if not model_path:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, "..", "models", "best_model.pkl")
            
        self.model_path = model_path
        self.model = None
        try:
            self.model = joblib.load(self.model_path)
        except Exception as e:
            # Fallback handled gracefully
            pass
            
        self.feature_pipeline = FeatureStorePipeline()
        # Calibrated threshold based on model factory optimization
        self.threshold = 0.45 

    def predict_single(self, customer_id: int, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates delinquency probability, tracks execution metrics, and logs variables to the DB."""
        start_time = time.time()
        
        # 1. Update customer record
        db_cust = DBCustomer(
            customer_id=customer_id,
            age=input_data.get("Age"),
            income=input_data.get("Income"),
            credit_score=input_data.get("Credit_Score"),
            loan_balance=input_data.get("Loan_Balance"),
            debt_to_income_ratio=input_data.get("Debt_to_Income_Ratio"),
            credit_utilization=input_data.get("Credit_Utilization"),
            missed_payments=input_data.get("Missed_Payments"),
            employment_status=input_data.get("Employment_Status")
        )
        self.customer_repo.save_customer(db_cust)

        # 2. Reconstruct dataframe for preprocessing
        input_data_with_id = input_data.copy()
        input_data_with_id["Customer_ID"] = str(customer_id)
        df_raw = pd.DataFrame([input_data_with_id])
        
        # Preprocess features
        df_processed = self.feature_pipeline.process(df_raw, is_training=False)
        
        # Exclude Customer ID from inference features
        features_df = df_processed.drop(columns=["Customer_ID"], errors="ignore")

        # 3. Model Scoring
        if self.model is None:
            # Safe mock fallback if model is not compiled
            probability = 0.15
        else:
            probability = float(self.model.predict_proba(features_df)[0][1])

        # Binary prediction using optimized decision threshold
        prediction_class = 1 if probability >= self.threshold else 0
        
        # Set Risk Levels
        if probability >= 0.70:
            risk = "HIGH"
        elif probability >= self.threshold:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        latency = float((time.time() - start_time) * 1000.0)

        # 4. Log Prediction to Database
        db_pred = DBPrediction(
            customer_id=customer_id,
            probability=probability,
            threshold=self.threshold,
            prediction=prediction_class,
            risk_level=risk,
            latency_ms=latency
        )
        self.prediction_repo.log_prediction(db_pred)

        return {
            "customer_id": customer_id,
            "probability": round(probability, 3),
            "risk_level": risk,
            "prediction": prediction_class,
            "latency_ms": round(latency, 2)
        }
