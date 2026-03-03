import time
import unicodedata

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


def detect_code_mixed(text: str, threshold: float = 0.30) -> bool:
    """Detect if text is code-mixed (Arabic + Latin) based on character script ratio.

    Returns True if Latin character ratio >= threshold.
    """
    arabic_count = 0
    latin_count = 0
    for char in text:
        if unicodedata.category(char).startswith("L"):
            name = unicodedata.name(char, "")
            if "ARABIC" in name:
                arabic_count += 1
            elif "LATIN" in name:
                latin_count += 1

    total_alpha = arabic_count + latin_count
    if total_alpha == 0:
        return False

    latin_ratio = latin_count / total_alpha
    return latin_ratio >= threshold


class ModelManager:
    """Manages MARBERT and XLM-RoBERTa models for hate speech classification."""

    # Label mappings for each model
    MARBERT_LABEL_MAP = {0: "not_hate", 1: "hate"}  # normal=0, toxic=1
    XLM_LABEL_MAP = {0: "not_hate", 1: "hate"}  # not-offensive=0, offensive=1

    def __init__(self) -> None:
        self.marbert_model = None
        self.marbert_tokenizer = None
        self.xlm_model = None
        self.xlm_tokenizer = None
        self.device: torch.device | None = None
        self._loaded = False

    def detect_device(self) -> torch.device:
        """Detect best available device: MPS -> CUDA -> CPU."""
        if torch.backends.mps.is_available():
            return torch.device("mps")
        if torch.cuda.is_available():
            return torch.device("cuda")
        return torch.device("cpu")

    def load_models(self, marbert_id: str, xlm_id: str) -> None:
        """Load both models at startup. XLM-RoBERTa is optional (skip on memory pressure)."""
        self.device = self.detect_device()

        # Load MARBERT (primary — required)
        self.marbert_tokenizer = AutoTokenizer.from_pretrained(marbert_id)
        self.marbert_model = AutoModelForSequenceClassification.from_pretrained(
            marbert_id
        )
        self.marbert_model.to(self.device)
        self.marbert_model.eval()

        # Load XLM-RoBERTa (fallback — optional)
        try:
            self.xlm_tokenizer = AutoTokenizer.from_pretrained(xlm_id)
            self.xlm_model = AutoModelForSequenceClassification.from_pretrained(xlm_id)
            self.xlm_model.to(self.device)
            self.xlm_model.eval()
        except Exception:
            self.xlm_model = None
            self.xlm_tokenizer = None

        self._warmup()
        self._loaded = True

    def _warmup(self) -> None:
        """Run dummy inference to eliminate first-run latency (MPS kernel compilation)."""
        dummy_text = "اختبار"
        if self.marbert_model and self.marbert_tokenizer:
            inputs = self.marbert_tokenizer(
                dummy_text, return_tensors="pt", truncation=True, max_length=128
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.inference_mode():
                self.marbert_model(**inputs)

        if self.xlm_model and self.xlm_tokenizer:
            inputs = self.xlm_tokenizer(
                dummy_text, return_tensors="pt", truncation=True, max_length=128
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.inference_mode():
                self.xlm_model(**inputs)

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def has_xlm(self) -> bool:
        return self.xlm_model is not None

    def get_status(self) -> dict:
        """Return model loading status for health endpoint."""
        return {
            "loaded": self._loaded,
            "device": str(self.device) if self.device else None,
            "marbert_loaded": self.marbert_model is not None,
            "xlm_loaded": self.xlm_model is not None,
        }

    def classify(self, text: str, code_mixed_threshold: float = 0.30) -> dict:
        """Classify text as hate/not_hate. Routes to XLM-RoBERTa if code-mixed."""
        start_time = time.perf_counter()

        is_code_mixed = detect_code_mixed(text, code_mixed_threshold)
        use_xlm = is_code_mixed and self.has_xlm

        if use_xlm:
            model = self.xlm_model
            tokenizer = self.xlm_tokenizer
            label_map = self.XLM_LABEL_MAP
            model_name = "xlm-roberta"
        else:
            model = self.marbert_model
            tokenizer = self.marbert_tokenizer
            label_map = self.MARBERT_LABEL_MAP
            model_name = "marbert"

        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=256,
            padding=True,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.inference_mode():
            outputs = model(**inputs)

        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        probs = probs[0].cpu().tolist()

        predicted_idx = probs.index(max(probs))
        label = label_map.get(predicted_idx, "not_hate")
        confidence = max(probs)

        probabilities = {}
        for idx, prob in enumerate(probs):
            mapped_label = label_map.get(idx, f"label_{idx}")
            probabilities[mapped_label] = round(prob, 4)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000)

        return {
            "label": label,
            "confidence": round(confidence, 4),
            "probabilities": probabilities,
            "model_used": model_name,
            "processing_time_ms": elapsed_ms,
        }

    def classify_with_explanation(
        self, text: str, code_mixed_threshold: float = 0.30, top_k: int = 3
    ) -> dict:
        """Classify text and extract top-k attended tokens for explanation."""
        start_time = time.perf_counter()

        is_code_mixed = detect_code_mixed(text, code_mixed_threshold)
        use_xlm = is_code_mixed and self.has_xlm

        if use_xlm:
            model, tokenizer = self.xlm_model, self.xlm_tokenizer
            label_map, model_name = self.XLM_LABEL_MAP, "xlm-roberta"
        else:
            model, tokenizer = self.marbert_model, self.marbert_tokenizer
            label_map, model_name = self.MARBERT_LABEL_MAP, "marbert"

        inputs = tokenizer(
            text, return_tensors="pt", truncation=True, max_length=256, padding=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.inference_mode():
            outputs = model(**inputs, output_attentions=True)

        # Classification (same logic as classify)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        probs = probs[0].cpu().tolist()
        predicted_idx = probs.index(max(probs))
        label = label_map.get(predicted_idx, "not_hate")
        confidence = max(probs)

        probabilities = {}
        for idx, prob in enumerate(probs):
            mapped_label = label_map.get(idx, f"label_{idx}")
            probabilities[mapped_label] = round(prob, 4)

        # Attention extraction — last layer, avg across heads, CLS row
        last_layer_attn = outputs.attentions[-1]  # (1, 12, seq_len, seq_len)
        avg_attn = last_layer_attn.mean(dim=1)  # (1, seq_len, seq_len)

        attention_mask = inputs["attention_mask"][0].cpu()
        seq_len = int(attention_mask.sum().item())
        cls_attn = avg_attn[0, 0, :seq_len].cpu()

        input_ids = inputs["input_ids"][0].cpu().tolist()[:seq_len]
        tokens = tokenizer.convert_ids_to_tokens(input_ids)

        # Aggregate subwords -> words, filter special tokens
        special_tokens = {
            "[CLS]", "[SEP]", "[PAD]", "[UNK]", "[MASK]",
            "<s>", "</s>", "<pad>",
        }
        word_scores: list[dict] = []
        current_word = ""
        current_scores: list[float] = []

        for i, token in enumerate(tokens):
            if token in special_tokens:
                continue

            if model_name == "xlm-roberta":
                # SentencePiece: word-initial has ▁ prefix
                is_word_start = token.startswith("\u2581")
                clean_token = token.lstrip("\u2581") if is_word_start else token
                if is_word_start:
                    if current_word and current_scores:
                        word_scores.append({
                            "token": current_word,
                            "score": sum(current_scores) / len(current_scores),
                        })
                    current_word = clean_token
                    current_scores = [cls_attn[i].item()]
                else:
                    current_word += token
                    current_scores.append(cls_attn[i].item())
            else:
                # MARBERT WordPiece: continuation has ## prefix
                if token.startswith("##"):
                    current_word += token[2:]
                    current_scores.append(cls_attn[i].item())
                else:
                    if current_word and current_scores:
                        word_scores.append({
                            "token": current_word,
                            "score": sum(current_scores) / len(current_scores),
                        })
                    current_word = token
                    current_scores = [cls_attn[i].item()]

        if current_word and current_scores:
            word_scores.append({
                "token": current_word,
                "score": sum(current_scores) / len(current_scores),
            })

        word_scores.sort(key=lambda x: x["score"], reverse=True)
        top_tokens = word_scores[:top_k]

        # Normalize scores
        total = sum(t["score"] for t in top_tokens)
        if total > 0:
            for t in top_tokens:
                t["score"] = round(t["score"] / total, 4)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000)

        return {
            "label": label,
            "confidence": round(confidence, 4),
            "probabilities": probabilities,
            "model_used": model_name,
            "processing_time_ms": elapsed_ms,
            "top_tokens": top_tokens,
        }
