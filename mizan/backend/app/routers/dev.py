"""Dev-only endpoints for testing LLM explanations without a training session."""
import json
import logging
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dev", tags=["dev"])


class TestExplanationRequest(BaseModel):
    text: str
    ai_label: str = "hate"
    ai_confidence: float = 0.85
    hate_type: str | None = None
    moderator_label: str = "hate"


@router.post("/test-explanation")
async def test_explanation(request: TestExplanationRequest):
    """Test LLM explanation with raw input — no training session needed.

    Streams the explanation via SSE for dev/prompt iteration.
    """
    async def event_generator():
        from app.services.llm_explanation import generate_stream

        full_text = ""
        try:
            async for token in generate_stream(
                tweet_text=request.text,
                ai_label=request.ai_label,
                ai_confidence=request.ai_confidence,
                ai_top_tokens=[],
                hate_type=request.hate_type,
                moderator_label=request.moderator_label,
            ):
                full_text += token
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield f"data: {json.dumps({'done': True, 'full_text': full_text})}\n\n"
        except Exception as e:
            logger.exception("Test explanation error")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
