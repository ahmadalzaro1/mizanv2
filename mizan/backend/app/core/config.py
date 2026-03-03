import os


class Settings:
    database_url: str = os.environ.get("DATABASE_URL", "")
    jwt_secret: str = os.environ.get("JWT_SECRET", "dev_secret_change_me")
    jwt_algorithm: str = "HS256"
    app_name: str = "Mizan"

    # ML Model Configuration
    hf_home: str = os.environ.get("HF_HOME", "./model_cache")
    marbert_model_id: str = os.environ.get(
        "MARBERT_MODEL_ID", "amitca71/marabert2-levantine-toxic-model-v4"
    )
    xlm_model_id: str = os.environ.get(
        "XLM_MODEL_ID", "Andrazp/multilingual-hate-speech-robacofi"
    )
    code_mixed_threshold: float = float(
        os.environ.get("CODE_MIXED_THRESHOLD", "0.30")
    )

    # LLM Explanation Configuration (Phase 10)
    use_llm_explanations: bool = os.environ.get("USE_LLM_EXPLANATIONS", "true").lower() == "true"
    ollama_host: str = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    ollama_model: str = os.environ.get("OLLAMA_MODEL", "qwen3.5:9b")


settings = Settings()
