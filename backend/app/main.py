import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from backend.app.api.routes.history import router as history_router
from backend.app.api.routes.predict import router
from backend.app.core import model_loader

_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _raw.split(",") if o.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_loader._load_artifacts()
    print("Model loaded successfully")
    yield


app = FastAPI(title="FOD-WPT Inference API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(router)
app.include_router(history_router)

Instrumentator().instrument(app).expose(app)
