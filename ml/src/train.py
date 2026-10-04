
import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

BASE = Path(__file__).resolve().parents[1]
DATA_PATH = BASE / "data" / "processed" / "processed_data.csv"
MODEL_DIR = BASE / "models"
TARGET = "sub_label"
RANDOM_STATE = 42


def load_split():
    """Stratified 80/20 split. evaluate.py imports this so both use the same test set."""
    df = pd.read_csv(DATA_PATH)
    features = [c for c in df.columns if c != TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        df[features], df[TARGET], test_size=0.2, stratify=df[TARGET], random_state=RANDOM_STATE
    )
    return features, X_train, X_test, y_train, y_test


def main():
    features, X_train, X_test, y_train, y_test = load_split()
    print(f"Train: {X_train.shape}  Test: {X_test.shape}")

    xgb = XGBClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.1,
        eval_metric="logloss", n_jobs=-1, random_state=RANDOM_STATE,
    )
    rf = RandomForestClassifier(
        n_estimators=100, max_depth=15, min_samples_leaf=5,
        n_jobs=-1, random_state=RANDOM_STATE,
    )
    print("Training XGBoost...")
    xgb.fit(X_train, y_train)
    print("Training Random Forest...")
    rf.fit(X_train, y_train)

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(xgb, MODEL_DIR / "xgboost_model.pkl")
    joblib.dump(rf, MODEL_DIR / "random_forest_model.pkl", compress=3)
    joblib.dump(features, MODEL_DIR / "selected_features.pkl")

    importance = dict(zip(features, [round(float(v), 4) for v in xgb.feature_importances_]))
    (MODEL_DIR / "training_info.json").write_text(json.dumps(
        {"features": features, "train_rows": len(X_train), "test_rows": len(X_test),
         "xgboost_feature_importance": importance}, indent=2))
    print("XGBoost feature importance:", importance)
    print("Models saved to", MODEL_DIR)


if __name__ == "__main__":
    main()
