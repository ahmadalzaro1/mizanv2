"""Unified Arabic explanation service — LLM primary, template fallback.

Merges Phase 5 template functions (from old explanation.py) with Phase 10
Qwen 3.5 streaming via Ollama. Single module used by training + bias auditor.
"""
import logging
from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────
# Arabic constants (from old explanation.py)
# ──────────────────────────────────────────

HATE_TYPE_AR: dict[str, str] = {
    "race": "عنصري",
    "religion": "ديني",
    "ideology": "أيديولوجي",
    "gender": "جنساني",
    "disability": "متعلق بالإعاقة",
    "social_class": "طبقي",
    "tribalism": "عشائري",
    "refugee_related": "متعلق باللاجئين",
    "political_affiliation": "سياسي",
    "unknown": "غير محدد",
}

# ──────────────────────────────────────────
# LLM system prompts
# ──────────────────────────────────────────

TRAINING_SYSTEM_PROMPT = """You are an Arabic-language assistant helping content moderators understand AI hate speech classifications.

Given a tweet, the AI model's classification, and the moderator's own label, write a 2-3 sentence Arabic explanation.

Rules:
- Write in natural Arabic prose. Do not use bullet points, numbered lists, or formatting markers.
- When the AI classifies content as hate speech, always mention the specific hate category in Arabic.
- When the moderator's label disagrees with the AI, acknowledge the disagreement and explain why the model may have seen it differently.
- Include subtle educational guidance — point out linguistic markers or context clues that are easy to miss.
- Do not repeat the tweet text verbatim. Refer to specific words or phrases naturally.
- Keep the tone respectful and educational, not prescriptive.
- Output ONLY the Arabic explanation text. No headers, no labels, no metadata."""

INSIGHT_SYSTEM_PROMPT = """You are an Arabic-language AI assistant analyzing bias audit results for a hate speech classification model.

Given the overall metrics and per-category performance breakdown, write a 2-3 sentence Arabic summary for a researcher.

Rules:
- Write in natural Arabic prose.
- Mention the overall F1 score and highlight the weakest category.
- If there are false positives, note the pattern.
- Include one actionable recommendation for improving the model.
- Output ONLY the Arabic analysis text. No headers, no labels, no metadata."""

# ──────────────────────────────────────────
# Template fallback functions (Phase 5)
# ──────────────────────────────────────────


def confidence_phrase(confidence: float) -> str:
    """Map confidence score to Arabic phrase."""
    if confidence >= 0.90:
        return "بثقة عالية"
    elif confidence >= 0.70:
        return "بثقة متوسطة"
    else:
        return "بثقة منخفضة"


def format_trigger_words(top_tokens: list[dict]) -> str:
    """Format trigger words with guillemets: «word1» و«word2»."""
    if not top_tokens:
        return ""
    words = [f"\u00ab{t['token']}\u00bb" for t in top_tokens]
    if len(words) == 1:
        return words[0]
    return " و".join(["، ".join(words[:-1]), words[-1]])


def generate_explanation(
    ai_label: str,
    confidence: float,
    top_tokens: list[dict],
    hate_type: str | None = None,
) -> str:
    """Generate a one-sentence Arabic explanation.

    Args:
        ai_label: "hate" or "not_hate"
        confidence: 0.0-1.0
        top_tokens: list of {"token": str, "score": float}
        hate_type: optional hate category for context

    Returns:
        Arabic explanation sentence.
    """
    conf_phrase = confidence_phrase(confidence)
    trigger_text = format_trigger_words(top_tokens)

    if ai_label == "hate":
        category_text = ""
        if hate_type and hate_type in HATE_TYPE_AR:
            category_text = f" {HATE_TYPE_AR[hate_type]}"

        if trigger_text:
            return (
                f"صنّف النموذج هذا المحتوى كخطاب كراهية{category_text} "
                f"{conf_phrase}، حيث رصد كلمات مؤثرة مثل {trigger_text}."
            )
        else:
            return (
                f"صنّف النموذج هذا المحتوى كخطاب كراهية{category_text} "
                f"{conf_phrase}."
            )
    else:
        if trigger_text:
            return (
                f"صنّف النموذج هذا المحتوى كمحتوى آمن "
                f"{conf_phrase}، حيث رصد مؤشرات إيجابية مثل {trigger_text}."
            )
        else:
            return (
                f"صنّف النموذج هذا المحتوى كمحتوى آمن "
                f"{conf_phrase}، حيث لم يرصد مؤشرات على خطاب كراهية."
            )


# ──────────────────────────────────────────
# Prompt builders
# ──────────────────────────────────────────


def _build_training_prompt(
    tweet_text: str,
    ai_label: str,
    ai_confidence: float,
    ai_top_tokens: list[dict],
    hate_type: str | None,
    moderator_label: str,
) -> list[dict]:
    """Build chat messages for training explanation."""
    trigger_words = ", ".join(t["token"] for t in (ai_top_tokens or []))
    category_ar = HATE_TYPE_AR.get(hate_type, "") if hate_type else ""
    conf_pct = round(ai_confidence * 100)

    user_content = f"""Tweet: {tweet_text}

AI classification: {ai_label} (confidence: {conf_pct}%)
{"Hate category: " + category_ar if category_ar and ai_label == "hate" else ""}
Top trigger words: {trigger_words if trigger_words else "none detected"}
Moderator's label: {moderator_label}
{"(Moderator DISAGREES with AI)" if moderator_label != ai_label else "(Moderator AGREES with AI)"}"""

    return [
        {"role": "system", "content": TRAINING_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def _build_insight_prompt(audit_results: dict) -> list[dict]:
    """Build chat messages for bias auditor insight."""
    overall = audit_results.get("overall", {})
    per_category = audit_results.get("per_category", [])
    false_positives = audit_results.get("false_positives", [])

    # Build context string
    cat_lines = []
    for cat in per_category:
        if cat.get("sample_count", 0) > 0:
            cat_lines.append(
                f"- {cat.get('category_ar', cat['category'])}: "
                f"F1={round(cat['f1'] * 100)}%, "
                f"samples={cat['sample_count']}"
            )

    user_content = f"""Bias audit results for MARBERT hate speech model:

Overall: F1={round(overall.get('f1', 0) * 100)}%, Precision={round(overall.get('precision', 0) * 100)}%, Recall={round(overall.get('recall', 0) * 100)}%
Total examples: {overall.get('total', 0)}

Per-category performance (sorted weakest first):
{chr(10).join(cat_lines) if cat_lines else "No category data"}

False positive count: {len(false_positives)}"""

    return [
        {"role": "system", "content": INSIGHT_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


# ──────────────────────────────────────────
# Async generators (LLM streaming)
# ──────────────────────────────────────────


async def generate_stream(
    tweet_text: str,
    ai_label: str,
    ai_confidence: float,
    ai_top_tokens: list[dict],
    hate_type: str | None,
    moderator_label: str,
) -> AsyncIterator[str]:
    """Yield Arabic explanation tokens from Qwen 3.5.

    Falls back to template if USE_LLM_EXPLANATIONS is false or Ollama fails.
    """
    from app.core.config import settings

    if not settings.use_llm_explanations:
        yield generate_explanation(ai_label, ai_confidence, ai_top_tokens, hate_type)
        return

    try:
        from ollama import AsyncClient

        client = AsyncClient(host=settings.ollama_host)
        messages = _build_training_prompt(
            tweet_text, ai_label, ai_confidence, ai_top_tokens, hate_type, moderator_label
        )

        async for chunk in await client.chat(
            model=settings.ollama_model,
            messages=messages,
            stream=True,
            think=True,
        ):
            # CRITICAL: Only yield content tokens, never thinking tokens
            if chunk.message.content:
                yield chunk.message.content

    except Exception:
        logger.warning("LLM explanation failed, falling back to template", exc_info=True)
        yield generate_explanation(ai_label, ai_confidence, ai_top_tokens, hate_type)


async def generate_insight_stream(audit_results: dict) -> AsyncIterator[str]:
    """Yield Arabic insight tokens for bias audit results.

    Falls back to a simple template if Ollama is unavailable.
    """
    from app.core.config import settings

    if not settings.use_llm_explanations:
        # Simple fallback: overall F1 sentence
        overall = audit_results.get("overall", {})
        f1_pct = round(overall.get("f1", 0) * 100)
        yield f"أداء النموذج الإجمالي: F1 = {f1_pct}٪"
        return

    try:
        from ollama import AsyncClient

        client = AsyncClient(host=settings.ollama_host)
        messages = _build_insight_prompt(audit_results)

        async for chunk in await client.chat(
            model=settings.ollama_model,
            messages=messages,
            stream=True,
            think=True,
        ):
            if chunk.message.content:
                yield chunk.message.content

    except Exception:
        logger.warning("LLM insight failed, falling back to template", exc_info=True)
        overall = audit_results.get("overall", {})
        f1_pct = round(overall.get("f1", 0) * 100)
        yield f"أداء النموذج الإجمالي: F1 = {f1_pct}٪"
