
import json
import joblib
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from train import MODEL_DIR, load_split


def main():
    features, _, X_test, _, y_test = load_split()
    results = {}
    for key, file in [("xgboost", "xgboost_model.pkl"), ("random_forest", "random_forest_model.pkl")]:
        model = joblib.load(MODEL_DIR / file)
        pred = model.predict(X_test[features])
        proba = model.predict_proba(X_test[features])[:, 1]
        results[key] = {
            "accuracy": round(accuracy_score(y_test, pred), 4),
            "precision": round(precision_score(y_test, pred), 4),
            "recall": round(recall_score(y_test, pred), 4),
            "f1": round(f1_score(y_test, pred), 4),
            "roc_auc": round(roc_auc_score(y_test, proba), 4),
            "confusion_matrix": confusion_matrix(y_test, pred).tolist(),  # [[TN, FP], [FN, TP]]
        }
        print(key, json.dumps(results[key]))
    (MODEL_DIR / "metrics.json").write_text(json.dumps(results, indent=2))
    print("Saved", MODEL_DIR / "metrics.json")


if __name__ == "__main__":
    main()
