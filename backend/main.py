# main.py

import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from fastapi import FastAPI
from pydantic import BaseModel
from predict import predict_customer

app = FastAPI(
    title="Customer Delinquency API"
)


class Customer(BaseModel):

    Age:int
    Income:float
    Credit_Score:float
    Loan_Balance:float
    Debt_to_Income_Ratio:float
    Credit_Utilization:float
    Missed_Payments:int

    Employment_Status:str

    Month_1:str
    Month_2:str
    Month_3:str
    Month_4:str
    Month_5:str
    Month_6:str


@app.get("/health")
def health():

    return {
        "status":"running"
    }


@app.post("/predict")
def predict(customer: Customer):

    result = predict_customer(
        customer.dict()
    )

    return result