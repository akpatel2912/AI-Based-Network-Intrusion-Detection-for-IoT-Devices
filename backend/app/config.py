from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]          # project root


class Settings(BaseSettings):
    # SQLite works with zero setup. For PostgreSQL/Supabase put this in backend/.env:
    # DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:5432/postgres
    database_url: str = "sqlite:///./iot_shield.db"
    cors_origins: list[str] = ["http://127.0.0.1:5500", "http://localhost:5500"]
    model_file: str = "xgboost_model.pkl"
    ml_src_dir: Path = ROOT / "ml" / "src"
    metrics_path: Path = ROOT / "ml" / "models" / "metrics.json"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
