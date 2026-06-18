# backend/repositories/repositories.py

from typing import List, Optional, Type, TypeVar, Generic
from sqlalchemy.orm import Session
from backend.database.models import (
    Base,
    DBCustomer,
    DBPrediction,
    DBRecommendation,
    DBAuditLog,
    DBModelVersion
)

T = TypeVar("T", bound=Base)

class CRUDRepository(Generic[T]):
    def __init__(self, session: Session, model_class: Type[T]):
        self.session = session
        self.model_class = model_class

    def get_by_id(self, id: Any) -> Optional[T]:
        return self.session.query(self.model_class).filter(self.model_class.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        return self.session.query(self.model_class).offset(skip).limit(limit).all()

    def save(self, entity: T) -> T:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity


class CustomerRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_customer(self, customer_id: int) -> Optional[DBCustomer]:
        return self.session.query(DBCustomer).filter(DBCustomer.customer_id == customer_id).first()

    def save_customer(self, customer: DBCustomer) -> DBCustomer:
        # Merge to handle existing/new updates
        merged = self.session.merge(customer)
        self.session.commit()
        return merged


class PredictionRepository:
    def __init__(self, session: Session):
        self.session = session

    def log_prediction(self, prediction: DBPrediction) -> DBPrediction:
        self.session.add(prediction)
        self.session.commit()
        self.session.refresh(prediction)
        return prediction

    def get_recent_predictions(self, limit: int = 100) -> List[DBPrediction]:
        return (
            self.session.query(DBPrediction)
            .order_by(DBPrediction.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_predictions_count_by_risk(self) -> List[tuple]:
        from sqlalchemy import func
        return (
            self.session.query(DBPrediction.risk_level, func.count(DBPrediction.id))
            .group_by(DBPrediction.risk_level)
            .all()
        )


class RecommendationRepository:
    def __init__(self, session: Session):
        self.session = session

    def log_recommendation(self, rec: DBRecommendation) -> DBRecommendation:
        self.session.add(rec)
        self.session.commit()
        self.session.refresh(rec)
        return rec

    def get_recommendations_for_customer(self, customer_id: int) -> List[DBRecommendation]:
        return (
            self.session.query(DBRecommendation)
            .join(DBPrediction)
            .filter(DBPrediction.customer_id == customer_id)
            .all()
        )


class AuditLogRepository:
    def __init__(self, session: Session):
        self.session = session

    def log_action(self, audit: DBAuditLog) -> DBAuditLog:
        self.session.add(audit)
        self.session.commit()
        return audit
