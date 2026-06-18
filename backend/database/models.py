# backend/database/models.py

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    create_engine
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class DBModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    parameters = Column(Text, nullable=True)  # JSON serialized parameters
    metrics = Column(Text, nullable=True)     # JSON serialized metrics
    artifact_uri = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    predictions = relationship("DBPrediction", back_populates="model_version")


class DBCustomer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True)
    age = Column(Integer, nullable=False)
    income = Column(Float, nullable=False)
    credit_score = Column(Float, nullable=False)
    loan_balance = Column(Float, nullable=False)
    debt_to_income_ratio = Column(Float, nullable=False)
    credit_utilization = Column(Float, nullable=False)
    missed_payments = Column(Integer, nullable=False)
    employment_status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    predictions = relationship("DBPrediction", back_populates="customer")


class DBPrediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    model_version_id = Column(Integer, ForeignKey("model_versions.id"), nullable=True)
    probability = Column(Float, nullable=False)
    threshold = Column(Float, default=0.5)
    prediction = Column(Integer, nullable=False)  # 0 or 1
    risk_level = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("DBCustomer", back_populates="predictions")
    model_version = relationship("DBModelVersion", back_populates="predictions")
    recommendations = relationship("DBRecommendation", back_populates="prediction")


class DBRecommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False)
    action_type = Column(String(100), nullable=False)  # Repayment, Campaign, Limit change
    recommendation_text = Column(Text, nullable=False)
    status = Column(String(50), default="PENDING")  # PENDING, SENT, EXECUTED
    created_at = Column(DateTime, default=datetime.utcnow)

    prediction = relationship("DBPrediction", back_populates="recommendations")


class DBAuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String(100), nullable=False)
    action = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Helper connection builder (can be overridden by FastAPI settings)
def get_db_session_factory(db_url: str):
    engine = create_engine(db_url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
