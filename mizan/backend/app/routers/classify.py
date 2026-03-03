from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.classify import ClassifyRequest, ClassifyResponse, HealthResponse

router = APIRouter(prefix="/api/classify", tags=["classify"])


def get_model_manager():
    """Dependency to get the global ModelManager instance."""
    from app.main import model_manager

    if model_manager is None or not model_manager.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="النماذج غير جاهزة بعد. يرجى الانتظار.",
        )
    return model_manager


@router.post("", response_model=ClassifyResponse)
def classify_text(
    request: ClassifyRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    mm=Depends(get_model_manager),
):
    """Classify Arabic text as hate/not_hate using MARBERT (or XLM-RoBERTa for code-mixed)."""
    from app.core.config import settings

    result = mm.classify(request.text, code_mixed_threshold=settings.code_mixed_threshold)
    return result


@router.get("/health", response_model=HealthResponse)
async def classify_health(mm=Depends(get_model_manager)):
    """Check model loading status including Ollama."""
    from app.core.config import settings

    status = mm.get_status()

    # Check Ollama availability
    ollama_ready = False
    qwen_model_loaded = False
    if settings.use_llm_explanations:
        try:
            from ollama import AsyncClient

            client = AsyncClient(host=settings.ollama_host)
            model_list = await client.list()
            ollama_ready = True
            # Check if the configured model is loaded
            model_names = [m.model for m in model_list.models]
            qwen_model_loaded = any(
                settings.ollama_model in name for name in model_names
            )
        except Exception:
            pass  # Ollama not reachable — fail gracefully

    return HealthResponse(
        **status,
        ollama_ready=ollama_ready,
        qwen_model_loaded=qwen_model_loaded,
    )
