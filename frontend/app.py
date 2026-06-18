import streamlit as st

from predict import predict_customer

st.title(
    "Customer Delinquency Risk Prediction"
)

age = st.number_input("Age")

income = st.number_input("Income")

credit_score = st.number_input(
    "Credit Score"
)

loan_balance = st.number_input(
    "Loan Balance"
)

dti = st.slider(
    "Debt-to-Income Ratio",
    0.0,
    1.0
)

utilization = st.slider(
    "Credit Utilization",
    0.0,
    1.0
)

missed = st.number_input(
    "Missed Payments"
)

employment = st.selectbox(
    "Employment Status",
    [
        "Employed",
        "Student",
        "Unemployed"
    ]
)

months = ["On-time","Late","Missed"]

month1 = st.selectbox(
    "Month 1",
    months
)

month2 = st.selectbox(
    "Month 2",
    months
)

month3 = st.selectbox(
    "Month 3",
    months
)

month4 = st.selectbox(
    "Month 4",
    months
)

month5 = st.selectbox(
    "Month 5",
    months
)

month6 = st.selectbox(
    "Month 6",
    months
)


if st.button("Predict"):

    customer = {

        "Age":age,

        "Income":income,

        "Credit_Score":credit_score,

        "Loan_Balance":loan_balance,

        "Debt_to_Income_Ratio":dti,

        "Credit_Utilization":utilization,

        "Missed_Payments":missed,

        "Employment_Status":employment,

        "Month_1":month1,
        "Month_2":month2,
        "Month_3":month3,
        "Month_4":month4,
        "Month_5":month5,
        "Month_6":month6

    }

    result = predict_customer(
        customer
    )

    st.metric(
        "Probability",
        result["probability"]
    )

    st.success(
        result["risk"]
    )