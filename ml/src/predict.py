
import joblib
import pandas as pd
from train import MODEL_DIR

LABELS = {0: "Normal", 1: "Attack"}


class Predictor:
    def __init__(self, model_file="xgboost_model.pkl"):
        self.model = joblib.load(MODEL_DIR / model_file)
        self.features = joblib.load(MODEL_DIR / "selected_features.pkl")

    def predict(self, values: dict) -> dict:
        row = pd.DataFrame([values])[self.features]      # enforce training column order
        attack_prob = float(self.model.predict_proba(row)[0, 1])
        label = int(attack_prob >= 0.5)
        return {"prediction": LABELS[label],
                "confidence": round(attack_prob if label else 1 - attack_prob, 4)}


if __name__ == "__main__":
    p = Predictor()
    print(p.predict({"rst_count": 0, "ICMP": 1, "Min": 42, "AVG": 42, "IAT": 83124075.8,
                     "Number": 9.5, "Variance": 0, "Weight": 141.55}))
