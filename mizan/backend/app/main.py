import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, export, training, classify, observatory, audit, dev
from app.services.ml_models import ModelManager

# Global model manager — accessed by classify router dependency
model_manager: ModelManager | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ML models at startup, release at shutdown."""
    global model_manager

    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

    from app.core.config import settings

    mm = ModelManager()
    mm.load_models(
        marbert_id=settings.marbert_model_id,
        xlm_id=settings.xlm_model_id,
    )
    model_manager = mm

    yield

    model_manager = None


app = FastAPI(title="Mizan API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(export.router)
app.include_router(training.router)
app.include_router(classify.router)
app.include_router(observatory.router)
app.include_router(audit.router)
app.include_router(dev.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "mizan-backend"}
