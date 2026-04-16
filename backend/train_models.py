import json
import os
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error, precision_score, r2_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(__file__).parent
DATASET_PATH = BASE_DIR / "data" / "ML_Feature_Set_Cleaned.csv"
APTITUDE_MODEL_PATH = BASE_DIR / "models" / "aptitude_model.pkl"
PLACEMENT_MODEL_PATH = BASE_DIR / "models" / "placement_model.pkl"
IMPORTANCE_PATH = BASE_DIR / "models" / "feature_importance.json"

PLACEMENT_THRESHOLD = 70

def load_dataset():
    df = pd.read_csv(DATASET_PATH)
    expected_columns = {"CGPA", "Internships", "Projects", "AptitudeTestScore", "Certificates"}
    missing_columns = expected_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")
    return df

def build_regression_models():
    return {
        "linear_regression": Pipeline([("scaler", StandardScaler()), ("model", LinearRegression())]),
    }

def build_classification_models():
    return {
        "random_forest": RandomForestClassifier(n_estimators=200, random_state=42),
        "logistic_regression": Pipeline([("scaler", StandardScaler()), ("model", LogisticRegression(max_iter=1000))]),
        "gradient_boosting": GradientBoostingClassifier(random_state=42),
    }

def train_aptitude_models(df):
    features = df[["CGPA", "Internships", "Projects", "Certificates"]]
    target = df["AptitudeTestScore"]

    x_train, x_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

    best_rmse = float("inf")
    best_model = None

    for name, model in build_regression_models().items():
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        rmse = mean_squared_error(y_test, predictions) ** 0.5

        if rmse < best_rmse:
            best_rmse = rmse
            best_model = model

    joblib.dump(best_model, APTITUDE_MODEL_PATH)
    print(f"Aptitude Model Trained (RMSE: {best_rmse:.4f})")

def train_placement_models(df):
    features_cols = ["CGPA", "Internships", "Projects", "Certificates", "AptitudeTestScore"]
    features = df[features_cols]
    target = (df["AptitudeTestScore"] >= PLACEMENT_THRESHOLD).astype(int)

    x_train, x_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42, stratify=target)

    best_f1 = -1
    best_model = None
    best_name = None

    for name, model in build_classification_models().items():
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        f1 = f1_score(y_test, predictions)

        if f1 > best_f1:
            best_f1 = f1
            best_model = model
            best_name = name

    joblib.dump(best_model, PLACEMENT_MODEL_PATH)
    print(f"Placement Model Trained ({best_name}, F1: {best_f1:.4f})")

    # Extract or approximate feature importance
    importance_dict = {}
    if hasattr(best_model, "feature_importances_"):
        importance_dict = dict(zip(features_cols, best_model.feature_importances_))
    elif hasattr(best_model, "named_steps") and hasattr(best_model.named_steps["model"], "coef_"):
        coefs = best_model.named_steps["model"].coef_[0]
        abs_coefs = [abs(c) for c in coefs]
        total = sum(abs_coefs)
        importance_dict = dict(zip(features_cols, [c/total for c in abs_coefs]))
    else:
        # Default fallback weights if model doesn't support easy extraction
        importance_dict = {"CGPA": 0.35, "Internships": 0.25, "AptitudeTestScore": 0.20, "Projects": 0.15, "Certificates": 0.05}

    with open(IMPORTANCE_PATH, "w") as f:
        json.dump(importance_dict, f, indent=4)
        
    print("Saved feature importance metadata.")

def main():
    os.makedirs(BASE_DIR / "models", exist_ok=True)
    df = load_dataset()
    train_aptitude_models(df)
    train_placement_models(df)

if __name__ == "__main__":
    main()
