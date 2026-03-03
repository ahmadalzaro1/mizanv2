from pydantic import BaseModel, Field


class ClassifyRequest(BaseModel):
    text: str = Field(
        ..., min_length=1, max_length=5000, description="Arabic text to classify"
    )


class ClassifyProbabilities(BaseModel):
    hate: float
    not_hate: float


class ClassifyResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    label: str
    confidence: float
    probabilities: ClassifyProbabilities
    model_used: str
    processing_time_ms: int


class HealthResponse(BaseModel):
    loaded: bool
    device: str | None
    marbert_loaded: bool
    xlm_loaded: bool
    # Phase 10: Ollama status
    ollama_ready: bool = False
    qwen_model_loaded: bool = False
