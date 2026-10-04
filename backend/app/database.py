from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from .config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


class Prediction(Base):
    """Same columns as database/schema.sql."""
    __tablename__ = "predictions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    rst_count: Mapped[float] = mapped_column(Float)
    icmp: Mapped[float] = mapped_column(Float)
    min_size: Mapped[float] = mapped_column(Float)
    avg_size: Mapped[float] = mapped_column(Float)
    iat: Mapped[float] = mapped_column(Float)
    number: Mapped[float] = mapped_column(Float)
    variance: Mapped[float] = mapped_column(Float)
    weight: Mapped[float] = mapped_column(Float)
    prediction: Mapped[str] = mapped_column(String(10))
    confidence: Mapped[float] = mapped_column(Float)


def init_db():
    Base.metadata.create_all(engine)    # creates the table if it does not exist


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
