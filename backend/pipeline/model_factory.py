# backend/pipeline/model_factory.py

import logging
from typing import Dict, Any, List, Tuple, Union
import numpy as np
import pandas as pd
import optuna

from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    StackingClassifier,
    VotingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, f1_score, precision_recall_curve

# Optional imports handled gracefully for production serverless size limits
HAS_XGB = False
try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    pass

HAS_CAT = False
try:
    from catboost import CatBoostClassifier
    HAS_CAT = True
except ImportError:
    pass

logger = logging.getLogger(__name__)

class ModelFactory:
    @staticmethod
    def get_base_classifier(model_name: str, params: Dict[str, Any] = None) -> Any:
        """Instantiates classifiers with custom hyperparameters."""
        params = params or {}
        model_name = model_name.lower()
        
        if model_name == "random_forest":
            return RandomForestClassifier(class_weight="balanced", random_state=42, **params)
        elif model_name == "extra_trees":
            return ExtraTreesClassifier(class_weight="balanced", random_state=42, **params)
        elif model_name == "logistic_regression":
            return LogisticRegression(class_weight="balanced", random_state=42, max_iter=1000, **params)
        elif model_name == "xgboost":
            if not HAS_XGB:
                raise ImportError("XGBoost is not installed in the environment.")
            return XGBClassifier(random_state=42, **params)
        elif model_name == "catboost":
            if not HAS_CAT:
                raise ImportError("CatBoost is not installed in the environment.")
            return CatBoostClassifier(random_state=42, verbose=0, **params)
        else:
            # Fallback to standard scikit-learn random forest
            return RandomForestClassifier(class_weight="balanced", random_state=42, **params)

    @staticmethod
    def calibrate_classifier(base_clf: Any, method: str = "sigmoid", cv: int = 5) -> CalibratedClassifierCV:
        """Calibrates prediction probabilities using Platt Scaling (sigmoid) or Isotonic Regression."""
        return CalibratedClassifierCV(estimator=base_clf, method=method, cv=cv)

    @staticmethod
    def build_stacking_classifier(
        estimators: List[Tuple[str, Any]],
        final_estimator: Any = None
    ) -> StackingClassifier:
        """Stacks multiple base classifiers with a final logistic meta-classifier."""
        final_estimator = final_estimator or LogisticRegression(class_weight="balanced", random_state=42)
        return StackingClassifier(
            estimators=estimators,
            final_estimator=final_estimator,
            cv=5,
            n_jobs=-1
        )


class PipelineTuner:
    def __init__(self, X: pd.DataFrame, y: pd.Series, cv_folds: int = 5):
        self.X = X
        self.y = y
        self.cv_folds = cv_folds

    def tune_random_forest(self, n_trials: int = 20) -> Dict[str, Any]:
        """Runs an Optuna study to find optimal Random Forest hyperparameters."""
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 100, 500, step=100),
                "max_depth": trial.suggest_int("max_depth", 3, 12),
                "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
                "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
            }
            
            skf = StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=42)
            scores = []
            
            for train_idx, val_idx in skf.split(self.X, self.y):
                X_train, X_val = self.X.iloc[train_idx], self.X.iloc[val_idx]
                y_train, y_val = self.y.iloc[train_idx], self.y.iloc[val_idx]
                
                clf = ModelFactory.get_base_classifier("random_forest", params)
                clf.fit(X_train, y_train)
                preds = clf.predict_proba(X_val)[:, 1]
                scores.append(roc_auc_score(y_val, preds))
                
            return np.mean(scores)

        optuna.logging.set_verbosity(optuna.logging.WARNING)
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials)
        return study.best_params


class ThresholdOptimizer:
    @staticmethod
    def find_optimal_threshold(
        y_true: np.ndarray,
        y_probs: np.ndarray,
        cost_false_negative: float = 5.0,
        cost_false_positive: float = 1.0
    ) -> float:
        """
        Determines the optimal prediction probability decision threshold by minimizing
        the financial risk equation: Cost = (FN * Cost_FN) + (FP * Cost_FP).
        """
        precisions, recalls, thresholds = precision_recall_curve(y_true, y_probs)
        best_threshold = 0.5
        min_cost = float("inf")
        
        # Add 1.0 to thresholds to handle boundary case
        extended_thresholds = np.concatenate([thresholds, [1.0]])
        
        for t in extended_thresholds:
            y_pred = (y_probs >= t).astype(int)
            
            # Confusion matrix metrics
            fp = np.sum((y_pred == 1) & (y_true == 0))
            fn = np.sum((y_pred == 0) & (y_true == 1))
            
            cost = (fn * cost_false_negative) + (fp * cost_false_positive)
            
            if cost < min_cost:
                min_cost = cost
                best_threshold = t
                
        return float(best_threshold)
