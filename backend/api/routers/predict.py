# backend/api/routers/predict.py

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from backend.api.dependencies import (
    get_predict_service,
    get_recommendation_service,
    get_recommendation_repo,
    get_prediction_repo,
    require_role
)
from backend.services.predict_service import PredictService
from backend.services.recommendation_service import RecommendationService
from backend.repositories.repositories import RecommendationRepository, PredictionRepository
from backend.database.models import DBRecommendation

router = APIRouter(prefix="/predict", tags=["prediction"])

# Request/Response schemas
class CustomerInput(BaseModel):
    Age: int = Field(..., ge=18, le=120)
    Income: float = Field(..., ge=0)
    Credit_Score: float = Field(..., ge=300, le=850)
    Loan_Balance: float = Field(..., ge=0)
    Debt_to_Income_Ratio: float = Field(..., ge=0.0, le=1.0)
    Credit_Utilization: float = Field(..., ge=0.0, le=1.0)
    Missed_Payments: int = Field(..., ge=0)
    Employment_Status: str = Field(..., pattern="^(employed|student|unemployed)$")
    Month_1: str = Field("On-time", pattern="^(On-time|Late|Missed)$")
    Month_2: str = Field("On-time", pattern="^(On-time|Late|Missed)$")
    Month_3: str = Field("On-time", pattern="^(On-time|Late|Missed)$")
    Month_4: str = Field("On-time", pattern="^(On-time|Late|Missed)$")
    Month_5: str = Field("On-time", pattern="^(On-time|Late|Missed)$")
    Month_6: str = Field("On-time", pattern="^(On-time|Late|Missed)$")


class PredictResponse(BaseModel):
    customer_id: int
    probability: float
    risk_level: str
    prediction: int
    latency_ms: float


class BatchPredictRequest(BaseModel):
    customers: List[Dict[str, Any]]


@router.post("", response_model=PredictResponse)
def predict_single(
    customer_id: int,
    payload: CustomerInput,
    predict_service: PredictService = Depends(get_predict_service),
    _ = Depends(require_role(["admin", "analyst"]))
):
    """Predicts delinquency risk for a single customer ID, log records, and updates repositories."""
    try:
        result = predict_service.predict_single(customer_id, payload.dict())
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference execution failed: {str(e)}"
        )


@router.post("/batch", response_model=List[PredictResponse])
def batch_predict(
    payload: BatchPredictRequest,
    predict_service: PredictService = Depends(get_predict_service),
    _ = Depends(require_role(["admin", "analyst"]))
):
    """Processes batch inference for multiple customer dictionaries asynchronously."""
    results = []
    # Loop over customers and perform inference (Celery can be integrated here for background queues)
    for idx, customer in enumerate(payload.customers):
        cust_id = customer.get("customer_id", 1000 + idx)
        try:
            res = predict_service.predict_single(cust_id, customer)
            results.append(res)
        except Exception:
            # Continue batch processing even if single row fails
            pass
    return results


@router.post("/recommend")
def recommend(
    prediction_id: int,
    customer_data: Dict[str, Any],
    risk_level: str,
    probability: float,
    rec_service: RecommendationService = Depends(get_recommendation_service),
    rec_repo: RecommendationRepository = Depends(get_recommendation_repo),
    _ = Depends(require_role(["admin", "analyst"]))
):
    """Invokes Gemini to build mitigation plans and writes recommendation records to the database."""
    recs = rec_service.generate_recommendations(customer_data, risk_level, probability)
    
    # Save recommendation
    db_rec = DBRecommendation(
        prediction_id=prediction_id,
        action_type=recs["action_type"],
        recommendation_text=recs["action_plan"]
    )
    rec_repo.log_recommendation(db_rec)
    return recs
