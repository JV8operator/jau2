import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


DATASET_PATH = Path("ML_Feature_Set_Cleaned.csv")
APTITUDE_MODEL_PATH = Path("aptitude_model.pkl")
PLACEMENT_MODEL_PATH = Path("placement_model.pkl")
REPORT_PATH = Path("phase1_model_report.json")
PLACEMENT_THRESHOLD = 70


def load_dataset():
    df = pd.read_csv(DATASET_PATH)

    expected_columns = {
        "CGPA",
        "Internships",
        "Projects",
        "AptitudeTestScore",
        "Certificates",
    }
    missing_columns = expected_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    return df


def build_regression_models():
    return {
        "linear_regression": Pipeline(
            [
                ("scaler", StandardScaler()),
                ("model", LinearRegression()),
            ]
        ),
        "random_forest_regressor": RandomForestRegressor(
            n_estimators=200,
            random_state=42,
        ),
    }


def build_classification_models():
    return {
        "logistic_regression": Pipeline(
            [
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(max_iter=1000)),
            ]
        ),
        "gradient_boosting_classifier": GradientBoostingClassifier(random_state=42),
    }


def train_aptitude_models(df):
    features = df[["CGPA", "Internships", "Projects", "Certificates"]]
    target = df["AptitudeTestScore"]

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=42,
    )

    report = {}
    best_name = None
    best_model = None
    best_rmse = None

    for name, model in build_regression_models().items():
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        rmse = mean_squared_error(y_test, predictions) ** 0.5
        result = {
            "mae": round(mean_absolute_error(y_test, predictions), 4),
            "rmse": round(rmse, 4),
            "r2": round(r2_score(y_test, predictions), 4),
        }
        report[name] = result

        if best_rmse is None or rmse < best_rmse:
            best_rmse = rmse
            best_name = name
            best_model = model

    joblib.dump(best_model, APTITUDE_MODEL_PATH)

    return {
        "task": "aptitude_regression",
        "target": "AptitudeTestScore",
        "best_model": best_name,
        "metrics": report,
        "saved_model": str(APTITUDE_MODEL_PATH),
    }


def train_placement_models(df):
    features = df[["CGPA", "Internships", "Projects", "Certificates", "AptitudeTestScore"]]
    target = (df["AptitudeTestScore"] >= PLACEMENT_THRESHOLD).astype(int)

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=42,
        stratify=target,
    )

    report = {}
    best_name = None
    best_model = None
    best_f1 = None

    for name, model in build_classification_models().items():
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        result = {
            "accuracy": round(accuracy_score(y_test, predictions), 4),
            "precision": round(precision_score(y_test, predictions), 4),
            "recall": round(recall_score(y_test, predictions), 4),
            "f1": round(f1_score(y_test, predictions), 4),
        }
        report[name] = result

        if best_f1 is None or result["f1"] > best_f1:
            best_f1 = result["f1"]
            best_name = name
            best_model = model

    joblib.dump(best_model, PLACEMENT_MODEL_PATH)

    return {
        "task": "placement_classification_proxy",
        "target": f"AptitudeTestScore >= {PLACEMENT_THRESHOLD}",
        "note": (
            "This is a first-pass proxy label because the main 5000-row dataset "
            "does not contain a real placement outcome column yet."
        ),
        "best_model": best_name,
        "metrics": report,
        "saved_model": str(PLACEMENT_MODEL_PATH),
    }


def main():
    df = load_dataset()
    report = {
        "dataset": {
            "path": str(DATASET_PATH),
            "rows": int(len(df)),
            "columns": list(df.columns),
        },
        "phase1": [
            train_aptitude_models(df),
            train_placement_models(df),
        ],
        "next_step": (
            "Add a real placement target and salary target to move from proxy "
            "models to production-style placement and salary prediction."
        ),
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
