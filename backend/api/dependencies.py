# backend/api/dependencies.py

import os
from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Import models & database
from backend.database.models import get_db_session_factory
from backend.repositories.repositories import (
    CustomerRepository,
    PredictionRepository,
    RecommendationRepository,
    AuditLogRepository
)
from backend.services.predict_service import PredictService
from backend.services.recommendation_service import RecommendationService
from backend.services.agent_service import DelinquencyAgent

# Fetch database URL from environment (default to a local SQLite database for ease of testing)
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    if "VERCEL" in os.environ:
        DATABASE_URL = "sqlite:////tmp/predictions.db"
    else:
        DATABASE_URL = "sqlite:///./predictions.db"
session_factory = get_db_session_factory(DATABASE_URL)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

def get_db() -> Generator[Session, None, None]:
    """Generates database sessions per request, ensuring clean resource disposal."""
    db = session_factory()
    try:
        yield db
    finally:
        db.close()

# Repository dependencies
def get_customer_repo(db: Session = Depends(get_db)) -> CustomerRepository:
    return CustomerRepository(db)

def get_prediction_repo(db: Session = Depends(get_db)) -> PredictionRepository:
    return PredictionRepository(db)

def get_recommendation_repo(db: Session = Depends(get_db)) -> RecommendationRepository:
    return RecommendationRepository(db)

def get_audit_repo(db: Session = Depends(get_db)) -> AuditLogRepository:
    return AuditLogRepository(db)

# Service dependencies
def get_predict_service(
    customer_repo: CustomerRepository = Depends(get_customer_repo),
    prediction_repo: PredictionRepository = Depends(get_prediction_repo)
) -> PredictService:
    return PredictService(customer_repo, prediction_repo)

def get_recommendation_service() -> RecommendationService:
    return RecommendationService()

def get_agent_service(
    customer_repo: CustomerRepository = Depends(get_customer_repo),
    prediction_repo: PredictionRepository = Depends(get_prediction_repo),
    predict_service: PredictService = Depends(get_predict_service),
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
) -> DelinquencyAgent:
    return DelinquencyAgent(customer_repo, prediction_repo, predict_service, recommendation_service)

# Authentication and Role-Based Access Control (RBAC)
def get_current_user_role(token: str = Depends(oauth2_scheme)) -> str:
    """Mock JWT auth token parser. Verifies user roles for secure operations."""
    if token == "admin-token-secret":
        return "admin"
    elif token == "analyst-token-secret":
        return "analyst"
    else:
        # Standard fallback for demonstration purposes
        return "read_only"

def require_role(allowed_roles: list):
    """Enforces role boundaries on endpoints."""
    def decorator(role: str = Depends(get_current_user_role)):
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for this user role."
            )
        return role
    return decorator
