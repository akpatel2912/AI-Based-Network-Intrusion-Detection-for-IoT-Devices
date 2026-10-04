from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    rst_count: float = Field(ge=0)
    ICMP: float = Field(ge=0, le=1)
    Min: float = Field(ge=0)
    AVG: float = Field(ge=0)
    IAT: float = Field(ge=0)
    Number: float = Field(ge=0)
    Variance: float = Field(ge=0)
    Weight: float = Field(ge=0)

    model_config = {"json_schema_extra": {"example": {
        "rst_count": 7391.2, "ICMP": 0, "Min": 66, "AVG": 1144.67, "IAT": 166522106.15,
        "Number": 13.5, "Variance": 1.0, "Weight": 244.6}}}


class PredictionResponse(BaseModel):
    prediction: Literal["Normal", "Attack"]
    confidence: float


class PredictionRecord(PredictionResponse):
    id: int
    timestamp: datetime
    features: PredictionRequest
