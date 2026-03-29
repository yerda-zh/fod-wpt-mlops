import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    prediction: Mapped[int] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(String)
    confidence: Mapped[float] = mapped_column(Float)
    no_object_prob: Mapped[float] = mapped_column(Float)
    fod_detected_prob: Mapped[float] = mapped_column(Float)
    latency_ms: Mapped[float] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


engine = create_engine("sqlite:///./fod.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(engine)
