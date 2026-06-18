# backend/services/agent_service.py

import os
from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END
import pandas as pd

from backend.repositories.repositories import CustomerRepository, PredictionRepository
from backend.services.predict_service import PredictService
from backend.services.recommendation_service import RecommendationService
from backend.pipeline.explainers import SHAPExplainManager

class AgentState(TypedDict):
    customer_id: int
    user_query: str
    customer_data: Dict[str, Any]
    prediction_result: Dict[str, Any]
    explainability_result: Dict[str, Any]
    recommendation_result: Dict[str, Any]
    policy_result: str
    final_response: str


class DelinquencyAgent:
    def __init__(
        self,
        customer_repo: CustomerRepository,
        prediction_repo: PredictionRepository,
        predict_service: PredictService,
        recommendation_service: RecommendationService
    ):
        self.customer_repo = customer_repo
        self.prediction_repo = prediction_repo
        self.predict_service = predict_service
        self.recommendation_service = recommendation_service
        
        # Build the LangGraph Workflow
        workflow = StateGraph(AgentState)
        
        # Add Nodes
        workflow.add_node("lookup_customer", self.node_lookup_customer)
        workflow.add_node("run_shap_explain", self.node_run_shap)
        workflow.add_node("get_recommendations", self.node_get_recommendations)
        workflow.add_node("check_policy", self.node_check_policy)
        workflow.add_node("generate_response", self.node_generate_response)
        
        # Define Edges
        workflow.set_entry_point("lookup_customer")
        workflow.add_edge("lookup_customer", "run_shap_explain")
        workflow.add_edge("run_shap_explain", "get_recommendations")
        workflow.add_edge("get_recommendations", "check_policy")
        workflow.add_edge("check_policy", "generate_response")
        workflow.add_edge("generate_response", END)
        
        self.app = workflow.compile()

    def node_lookup_customer(self, state: AgentState) -> Dict[str, Any]:
        """Node 1: Retrieves customer demographics and triggers local inference."""
        cust_id = state["customer_id"]
        db_cust = self.customer_repo.get_customer(cust_id)
        
        if not db_cust:
            return {"final_response": f"Customer with ID {cust_id} not found in database."}
            
        cust_data = {
            "Age": db_cust.age,
            "Income": db_cust.income,
            "Credit_Score": db_cust.credit_score,
            "Loan_Balance": db_cust.loan_balance,
            "Debt_to_Income_Ratio": db_cust.debt_to_income_ratio,
            "Credit_Utilization": db_cust.credit_utilization,
            "Missed_Payments": db_cust.missed_payments,
            "Employment_Status": db_cust.employment_status,
        }
        
        pred = self.predict_service.predict_single(cust_id, cust_data)
        return {"customer_data": cust_data, "prediction_result": pred}

    def node_run_shap(self, state: AgentState) -> Dict[str, Any]:
        """Node 2: Generates local SHAP feature attribution to explain why a user is high/low risk."""
        if "customer_data" not in state or not state["customer_data"]:
            return {}
            
        # Reconstruct DataFrame for explainer
        cust_data = state["customer_data"].copy()
        cust_data["Customer_ID"] = str(state["customer_id"])
        df_raw = pd.DataFrame([cust_data])
        
        processed_df = self.predict_service.feature_pipeline.process(df_raw, is_training=False)
        features_df = processed_df.drop(columns=["Customer_ID"], errors="ignore")
        
        # Fetch explainer
        feature_names = list(features_df.columns)
        if self.predict_service.model:
            explainer = SHAPExplainManager(self.predict_service.model, feature_names)
            explanation = explainer.explain_instance(features_df)
        else:
            explanation = {"contributions": [{"feature": "Missed_Payments", "value": cust_data["Missed_Payments"], "shap_value": 0.25}]}
            
        return {"explainability_result": explanation}

    def node_get_recommendations(self, state: AgentState) -> Dict[str, Any]:
        """Node 3: Generates Gemini recommendations based on segment and risk values."""
        if "prediction_result" not in state or not state["prediction_result"]:
            return {}
            
        pred = state["prediction_result"]
        recs = self.recommendation_service.generate_recommendations(
            state["customer_data"],
            pred["risk_level"],
            pred["probability"]
        )
        return {"recommendation_result": recs}

    def node_check_policy(self, state: AgentState) -> Dict[str, Any]:
        """Node 4: Evaluates bank policy limits based on compliance thresholds."""
        pred = state.get("prediction_result", {})
        risk = pred.get("risk_level", "LOW")
        
        if risk == "HIGH":
            policy = "FLAG_FOR_AUDIT: Freeze credit limits immediately. Transfer to secondary collection queue."
        elif risk == "MEDIUM":
            policy = "WATCHLIST: Freeze credit limit increases. Schedule follow-up check in 30 days."
        else:
            policy = "STANDARD: Active risk classification normal. Normal credit operations apply."
            
        return {"policy_result": policy}

    def node_generate_response(self, state: AgentState) -> Dict[str, Any]:
        """Node 5: Uses Gemini to synthesize all context into a conversational analysis response."""
        query = state["user_query"]
        pred = state.get("prediction_result", {})
        shap_exp = state.get("explainability_result", {})
        recs = state.get("recommendation_result", {})
        policy = state.get("policy_result", "")
        
        prompt = f"""
        You are a Senior Credit Risk Officer. Answer this query: "{query}"
        
        Customer ID: {state['customer_id']}
        Risk Level: {pred.get('risk_level')} (Probability: {pred.get('probability')})
        SHAP Key Influences: {shap_exp.get('contributions', [])[:3]}
        Recommended Actions: {recs.get('action_plan')}
        Credit Action: {recs.get('credit_limit_action')}
        Bank Policy Action: {policy}
        
        Generate a conversational, professional, and clear risk assessment dashboard summary.
        """
        
        response_text = f"Customer {state['customer_id']} has a {pred.get('risk_level')} delinquency risk. Policy: {policy}"
        
        if self.recommendation_service.model:
            try:
                response = self.recommendation_service.model.generate_content(prompt)
                response_text = response.text
            except Exception:
                pass
                
        return {"final_response": response_text}

    def run_query(self, customer_id: int, query: str) -> Dict[str, Any]:
        """Runs the conversational agent graph for the given query."""
        initial_state = {
            "customer_id": customer_id,
            "user_query": query,
            "customer_data": {},
            "prediction_result": {},
            "explainability_result": {},
            "recommendation_result": {},
            "policy_result": "",
            "final_response": ""
        }
        return self.app.invoke(initial_state)
