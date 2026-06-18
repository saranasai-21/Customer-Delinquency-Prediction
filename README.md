# Customer-Delinquency-Prediction

A production-ready credit risk assessment and default prediction pipeline. This repository showcases software engineering design patterns applied to machine learning systems, featuring clean feature pipeline isolation, cost-sensitive threshold calibration, and automated model diagnostics.

---

## 🏛️ Project Structure

The project follows a neat, decoupled structure separating data engineering (preprocessing) from training and inference pipelines:

```text
customer-delinquency-prediction/
├── backend/
│   ├── feature_pipeline.py   # Data engineering (clean mappings, rolling aggregations)
│   ├── predict.py            # Inference engine (loads model and scores sample inputs)
│   └── train_model.py        # Model training automation & diagnostic reports
├── data/
│   └── Delinquency_prediction_dataset.xlsx  # Baseline spreadsheet training data
├── models/
│   └── best_model.pkl        # Preserved pre-trained stacking classifier
├── Dockerfile                # Configures containerized runtimes
├── requirements.txt          # Minimal dependency registry
└── README.md                 # Project documentation
```

### Key Modules:
- **`backend/feature_pipeline.py`**: A dedicated feature store mapping client statuses to numeric scales, calculating rolling credit utilization stress, debt-to-income interaction variables, and historical trends.
- **`backend/predict.py`**: The model scoring gateway. Loads the pre-trained classifier, runs client inputs through the feature pipeline, and outputs risk categories.
- **`backend/train_model.py`**: Model training orchestration script, compiling model fit reports (ROC AUC, recall, precision) and diagnostic parameters.

---

## 📈 Engineering Highlights & Business Impact

### 1. Cost-Sensitive Threshold Calibration
In risk management, a False Negative (failing to identify a delinquent client) is significantly more expensive than a False Positive (restricting credit for a safe client). 
A custom optimization function calibrates the classification decision boundary by minimizing the financial risk formula:
$$\text{Cost} = (\text{False Negatives} \times 5.0) + (\text{False Positives} \times 1.0)$$

### 2. Platt Scaling & Isotonic Probability Calibration
Estimators (RandomForest, ExtraTrees, HistGradientBoosting) are calibrated using Platt Sigmoid Scaling. This ensures that the output probabilities reflect realistic default frequencies rather than uncalibrated confidence intervals.

---

## 🚀 How to Run & Verify

### 1. Run Predictions Locally
To run a sample default risk prediction using the pre-trained model:
```bash
python backend/predict.py
```
**Sample Output:**
```text
Input Customer Data:
  Age: 38
  Income: 75000.0
  Credit_Score: 680.0
  Loan_Balance: 22000.0
  Debt_to_Income_Ratio: 0.42
  Credit_Utilization: 0.65
  Missed_Payments: 1
  Employment_Status: employed
  Month_1: On-time
  Month_2: Late
  Month_3: On-time
  Month_4: On-time
  Month_5: On-time
  Month_6: On-time

Prediction Results:
  Probability of Delinquency: 46.11%
  Risk Level: MEDIUM
  Binary Outcome: 1
```

### 2. Run in a Docker Container
Build and execute the prediction system in an isolated container environment:
```bash
# Build the image
docker build -t delinquency-predictor .

# Run sample prediction
docker run --rm delinquency-predictor
```
