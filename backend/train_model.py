# train_model.py

import os
import pandas as pd
import joblib

from preprocessing import preprocess_data

from sklearn.model_selection import train_test_split

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from sklearn.ensemble import (
    ExtraTreesClassifier,
    StackingClassifier
)

from sklearn.linear_model import LogisticRegression

from xgboost import XGBClassifier
from catboost import CatBoostClassifier

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

df = preprocess_data(df)

TARGET = "Delinquent_Account"

X = df.drop(
    columns=[
        "Customer_ID",
        TARGET
    ]
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
cat_model = CatBoostClassifier(
    iterations=300,
    verbose=0,
    auto_class_weights='Balanced'
)

extra_model = ExtraTreesClassifier(
    n_estimators=300,
    class_weight='balanced',
    random_state=42
)

xgb_model = XGBClassifier(
    n_estimators=300,
    eval_metric="logloss",
    scale_pos_weight=5.25
)

stack_model = StackingClassifier(

    estimators=[
        ("cat", cat_model),
        ("extra", extra_model),
        ("xgb", xgb_model)
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
# Save with interactive permission prompt
# -----------------------------
print("\nTraining complete.")
ans = input("Do you want to save the trained model to disk? (y/n): ")
if ans.strip().lower() in ['y', 'yes']:
    joblib.dump(
        pipeline,
        os.path.join(BASE_DIR, "..", "models", "best_model.pkl")
    )
    print("Model saved to '../models/best_model.pkl'")
else:
    print("Save cancelled. Model was not saved.")
