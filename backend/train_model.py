# train_model.py

import os
import pandas as pd
import joblib

import sys

# Inject path logic for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from backend.pipeline.feature_store import FeatureStorePipeline

from sklearn.model_selection import train_test_split

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from sklearn.ensemble import (
    ExtraTreesClassifier,
    RandomForestClassifier,
    HistGradientBoostingClassifier,
    StackingClassifier
)

from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    classification_report,
    roc_auc_score
)

# -----------------------------
# Load data
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_excel(
    os.path.join(BASE_DIR, "..", "data", "Delinquency_prediction_dataset.xlsx")
)

feature_pipeline = FeatureStorePipeline()
df = feature_pipeline.process(df, is_training=True)

TARGET = "Delinquent_Account"

X = df.drop(
    columns=[
        "Customer_ID",
        "Account_Tenure",
        "Credit_Card_Type",
        "Location",
        TARGET
    ],
    errors="ignore"
)

y = df[TARGET]

# -----------------------------
# Split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    stratify=y,
    test_size=.2,
    random_state=42
)

# -----------------------------
# Column types
# -----------------------------
num_cols = X.select_dtypes(
    include=["int64", "float64"]
).columns

cat_cols = X.select_dtypes(
    include=["object", "str"]
).columns

# -----------------------------
# Transformers
# -----------------------------
numeric_transformer = Pipeline(
    [
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "scaler",
            StandardScaler()
        )
    ]
)

categorical_transformer = Pipeline(
    [
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)

preprocessor = ColumnTransformer(
    [
        (
            "num",
            numeric_transformer,
            num_cols
        ),
        (
            "cat",
            categorical_transformer,
            cat_cols
        )
    ]
)

# -----------------------------
# Models
# -----------------------------
rf_model = RandomForestClassifier(
    n_estimators=300,
    class_weight='balanced',
    random_state=42
)

extra_model = ExtraTreesClassifier(
    n_estimators=300,
    class_weight='balanced',
    random_state=42
)

hgb_model = HistGradientBoostingClassifier(
    max_iter=300,
    class_weight='balanced',
    random_state=42
)

stack_model = StackingClassifier(

    estimators=[
        ("rf", rf_model),
        ("extra", extra_model),
        ("hgb", hgb_model)
    ],

    final_estimator=LogisticRegression(class_weight='balanced')

)

pipeline = Pipeline(

    [
        (
            "preprocessor",
            preprocessor
        ),

        (
            "model",
            stack_model
        )
    ]

)

# -----------------------------
# Train
# -----------------------------
pipeline.fit(
    X_train,
    y_train
)

# -----------------------------
# Evaluation
# -----------------------------
preds = pipeline.predict(X_test)

prob = pipeline.predict_proba(X_test)[:, 1]

print(
    classification_report(
        y_test,
        preds
    )
)

print(
    "ROC AUC:",
    roc_auc_score(
        y_test,
        prob
    )
)

# -----------------------------
# Save with interactive permission prompt (non-interactive fallback for Docker)
# -----------------------------
print("\nTraining complete.")
if os.environ.get("FORCE_SAVE", "0") == "1":
    ans = "y"
else:
    try:
        ans = input("Do you want to save the trained model to disk? (y/n): ")
    except EOFError:
        print("Non-interactive environment detected. Defaulting to saving the model.")
        ans = "y"

if ans.strip().lower() in ['y', 'yes']:
    joblib.dump(
        pipeline,
        os.path.join(BASE_DIR, "..", "models", "best_model.pkl")
    )
    print("Model saved to '../models/best_model.pkl'")
else:
    print("Save cancelled. Model was not saved.")
