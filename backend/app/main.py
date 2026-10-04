import json
from contextlib import asynccontextmanager
from datetime import timezone
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .database import Prediction, get_db, init_db
from .model_service import get_predictor
from .schemas import PredictionRecord, PredictionRequest, PredictionResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    try:
        get_predictor()      # fail fast if the model files are missing
    except FileNotFoundError as e:
        raise RuntimeError(
            "Model files not found in ml/models/. Train them first: open a terminal in ml/src and run "
            "'python preprocess.py', 'python train.py', 'python evaluate.py'. Details: " + str(e)) from e
    yield


app = FastAPI(title="IoT Shield API", version="1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                   allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(req: PredictionRequest, db: Session = Depends(get_db)):
    result = get_predictor().predict(req.model_dump())
    db.add(Prediction(
        rst_count=req.rst_count, icmp=req.ICMP, min_size=req.Min, avg_size=req.AVG, iat=req.IAT,
        number=req.Number, variance=req.Variance, weight=req.Weight, **result))
    db.commit()
    return result


@app.get("/predictions", response_model=list[PredictionRecord])
def predictions(limit: int = 500, db: Session = Depends(get_db)):
    rows = db.scalars(select(Prediction).order_by(Prediction.id.desc()).limit(limit)).all()
    return [PredictionRecord(
        id=r.id, timestamp=r.created_at if r.created_at.tzinfo else r.created_at.replace(tzinfo=timezone.utc), prediction=r.prediction, confidence=r.confidence,
        features=PredictionRequest(rst_count=r.rst_count, ICMP=r.icmp, Min=r.min_size, AVG=r.avg_size,
                                   IAT=r.iat, Number=r.number, Variance=r.variance, Weight=r.weight),
    ) for r in reversed(rows)]          # oldest first, like the frontend expects


@app.get("/metrics")
def metrics():
    if not settings.metrics_path.exists():
        raise HTTPException(404, "metrics.json not found. Run ml/src/evaluate.py first.")
    return json.loads(settings.metrics_path.read_text())
