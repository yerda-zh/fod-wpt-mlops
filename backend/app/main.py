from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from backend.app.api.routes.predict import router
from backend.app.core import model_loader


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_loader._load_artifacts()
    print("Model loaded successfully")
    yield


app = FastAPI(title="FOD-WPT Inference API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

Instrumentator().instrument(app).expose(app)
