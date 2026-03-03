# Phase 5 Research — AI Explanation Layer

> Research completed 2026-03-02 for planning Phase 5.

---

## Key Findings

### 1. Attention Weight Extraction from HuggingFace Transformers

**How to get attention weights:**
- Pass `output_attentions=True` to the model's forward call
- Returns `outputs.attentions` — tuple of 12 tensors (one per layer)
- Each tensor shape: `(batch_size, num_heads, seq_len, seq_len)`
- Fully compatible with `torch.inference_mode()`

**Best strategy for classification explainability:**
- **Last layer attention**, averaged across all 12 heads
- Extract CLS token row (row 0) — shows what the classifier "looked at"
- This is the standard approach for BERT classification explainability

**Code pattern:**
```python
outputs = model(**inputs, output_attentions=True)
last_layer_attn = outputs.attentions[-1]          # (1, 12, seq_len, seq_len)
avg_attn = last_layer_attn.mean(dim=1)             # (1, seq_len, seq_len)
cls_attn = avg_attn[0, 0, :seq_len].cpu()          # (seq_len,)
```

### 2. Subword Tokenization Handling

**MARBERT:** Uses WordPiece tokenizer (BertTokenizer), 100K vocab
- Continuation tokens prefixed with `##`
- `do_lower_case=true` (no-op for Arabic)
- Large vocab = fewer Arabic word splits

**XLM-RoBERTa:** Uses SentencePiece tokenizer
- Word-initial tokens prefixed with `▁` (U+2581)
- Continuation tokens have NO prefix (inverted logic vs WordPiece)

**Aggregation:** Mean of subword attention scores → word-level score

### 3. Performance Impact

- Memory: ~37.5 MB extra for 256-token input (12 layers × 12 heads × 256² × 4 bytes)
- `output_attentions=True` causes SDPA → eager attention fallback (HF v4.36+)
- Expected overhead: ~50-100ms on top of ~250ms baseline
- Total: ~300-350ms — well under 3s target (AI-03)

### 4. Critical Gotchas

1. **Filter special tokens:** [CLS], [SEP], [PAD] absorb disproportionate attention. Always exclude.
2. **Respect attention_mask:** Padding tokens inflate the attention matrix. Use `attention_mask` to truncate.
3. **XLM-R subword logic is inverted:** Word-initial has `▁` prefix, not continuation.
4. **BertTokenizer doesn't support `return_offsets_mapping`:** Use `use_fast=True` for `BertTokenizerFast` or reconstruct positions by finding tokens in original text.
5. **Attention is approximate:** Jain & Wallace (2019) showed attention isn't always faithful. For hackathon demo purposes, this is the accepted standard approach.

### 5. Token-to-Original-Text Mapping

Two options for frontend highlighting:
1. **Find token in original text:** Search for each top token's text in the original Arabic string. Simple, works for whole words.
2. **Use offset mapping:** Load tokenizer with `use_fast=True` and `return_offsets_mapping=True`. More precise but requires fast tokenizer.

**Recommendation:** Use option 1 (string search) since most Arabic words in MARBERT's 100K vocab remain unsplit. For the rare subword case, the reconstructed word from `##` merging will still be findable in the original text.

---

## Architecture Decision

**2 plans, 2 waves:**

| Plan | Wave | Scope |
|------|------|-------|
| 5.1: Backend — Migration + Explanation Service | Wave 1 | DB schema, ModelManager attention, ExplanationService templates, training router integration |
| 5.2: Frontend — AI Explanation Display | Wave 2 | TypeScript types, TweetCard highlights, AIExplanation component, FeedbackReveal integration |

Wave 2 depends on Wave 1 (frontend needs the API response shape).

---

*Created: 2026-03-02*
