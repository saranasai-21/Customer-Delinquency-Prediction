# backend/services/recommendation_service.py

import os
import google.generativeai as genai

class RecommendationService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
        else:
            self.model = None

    def segment_customer(self, credit_score: float, utilization: float, missed_payments: int) -> str:
        """Determines the risk classification bucket of the customer."""
        if missed_payments > 2 or utilization > 0.8:
            return "Critical Risk Segment"
        elif missed_payments > 0 or utilization > 0.5:
            return "Attention Segment"
        else:
            return "Healthy Segment"

    def generate_recommendations(self, customer_data: dict, risk_level: str, probability: float) -> dict:
        """Invokes Gemini to construct highly targeted, personalized banking recommendations."""
        segment = self.segment_customer(
            customer_data.get("Credit_Score", 650),
            customer_data.get("Credit_Utilization", 0.5),
            customer_data.get("Missed_Payments", 0)
        )
        
        prompt = f"""
        Analyze customer risk indicators:
        - Segment: {segment}
        - Current Risk Level: {risk_level}
        - Delinquency Probability: {probability:.3f}
        - Customer Age: {customer_data.get("Age")}
        - Debt-to-Income: {customer_data.get("Debt_to_Income_Ratio")}
        - Credit Score: {customer_data.get("Credit_Score")}
        - Current Loan Balance: ${customer_data.get("Loan_Balance")}

        Write three strategic deliverables in raw text format:
        1. Action Plan: Business decisions to mitigate delinquency.
        2. SMS Reminder: A payment reminder text under 140 characters.
        3. Campaign: An email template outlining supportive restructuring options.
        """
        
        action_plan = "Establish immediate contact and limit further card usage."
        sms = "Payment Reminder: Please check your account dashboard to review repayment options."
        email = "Subject: Support Options for Your Account\n\nDear Customer, we noticed your utilization is high. Please contact our support team."
        
        if self.model:
            try:
                response = self.model.generate_content(prompt)
                raw_text = response.text
                
                # Split output dynamically or format
                action_plan = raw_text
                # Try simple format splits if structured
                lines = raw_text.split("\n\n")
                if len(lines) >= 3:
                    action_plan = lines[0]
                    sms = lines[1]
                    email = "\n\n".join(lines[2:])
            except Exception as e:
                # Fallback to local default recommendations
                pass

        # Formulate credit limit recommendation
        credit_limit_action = "MAINTAIN"
        if risk_level == "HIGH":
            credit_limit_action = "DECREASE_BY_50"
        elif risk_level == "MEDIUM":
            credit_limit_action = "FREEZE"
        elif risk_level == "LOW" and customer_data.get("Credit_Score", 650) > 750:
            credit_limit_action = "INCREASE_BY_10"

        return {
            "segment": segment,
            "action_type": "Mitigation Plan" if risk_level != "LOW" else "Retention Plan",
            "action_plan": action_plan,
            "sms_reminder": sms,
            "email_campaign": email,
            "credit_limit_action": credit_limit_action
        }
