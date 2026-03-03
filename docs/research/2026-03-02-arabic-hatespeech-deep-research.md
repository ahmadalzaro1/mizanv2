# Deep Research Report: Arabic Hate Speech Detection — Datasets, Models & Gaps
**Date:** 2026-03-02
**Project:** JYIF Generative AI Hackathon — Jordanian Arabic Hate Speech Moderator Platform
**Mode:** Deep Research (25 sources)

---

## Executive Summary

Arabic hate speech detection is an active but severely under-resourced field. While the global NLP community has developed strong hate speech detection pipelines for English, Arabic presents a fundamentally harder problem: a language family with 30+ dialects, rich morphological complexity, code-switching with English and French, and culturally loaded terminology whose meaning shifts across regions. For the Jordanian dialect specifically, only one dedicated hate speech corpus exists — introduced in 2024 — and its baseline model performance is low (max F1=0.62), flagging a wide-open research gap. No platform exists today that trains institutional content moderators in Arabic on culturally contextualized hate speech. The opportunity here is real, timely, and largely uncontested: building a Jordanian-dialect moderator training platform that simultaneously produces a high-quality annotated dataset is both a genuine research contribution and a deployable product.

---

## 1. The Landscape of Arabic Hate Speech Datasets

### 1.1 The Corpus Problem

The foundational challenge for Arabic hate speech research is data scarcity, not model architecture. While English has dozens of large, well-validated hate speech benchmarks, the Arabic NLP ecosystem has produced a fragmented collection of smaller, often narrowly scoped corpora. A 2024 systematic survey (PMC 12453721) catalogued the major datasets and found that most suffer from three structural problems: heavy class imbalance (hateful content represents 1.7–5% of annotated samples), platform monoculture (85%+ of datasets derive exclusively from Twitter), and inadequate dialectal coverage.

The largest available datasets are:

| Dataset | Size | Year | Dialect | Categories |
|---------|------|------|---------|------------|
| OSACT4 | 10,000 tweets | 2020 | MSA + mixed | Offensive / Not Offensive |
| OSACT5 | ~14,000 tweets | 2022 | MSA + mixed | Offensive, Hate, Fine-grained (6 types) |
| L-HSAB | 5,846 tweets | 2019 | Levantine (Syrian/Lebanese) | Normal / Abusive / Hate |
| ADHAR | 4,240 tweets (70,369 words) | 2024 | MSA, Egyptian, Levantine, Gulf, Maghrebi | Nationality, Religion, Ethnicity, Race |
| JHSC | 403,688 tweets | 2024 | Jordanian Arabic (first dedicated) | Very Positive / Positive / Neutral / Negative |

The JHSC (Jordanian Hate Speech Corpus) is historically significant as the first dataset explicitly constructed for the Jordanian dialect. Researchers collected 2,034,005 initial tweets using geographic filters targeting Jordan's 12 governorates, applied a 357-term Jordanian-specific hate lexicon to narrow to 557,551 candidates, and manually annotated 403,688 of those [PMC 10912174]. Despite its size, the dataset has serious known weaknesses: very hateful content (the "Very Positive" class) represents only 1.7% of the corpus, making classifiers that matter most — the ones catching real hate speech — nearly impossible to train reliably.

### 1.2 The Levantine Blind Spot

ADHAR groups Jordanian and Palestinian speech together as "Levantine," which obscures dialect-specific features entirely [Frontiers ADHAR 2024]. Jordanian Arabic has distinctive lexical items, morphological patterns, and cultural reference points that differ meaningfully from Lebanese or Syrian Levantine. A word considered neutral in Syrian Arabic may carry derogatory weight in Jordanian usage, and vice versa. This is not a subtle distinction — it is precisely the kind of nuance that makes or breaks a moderation system deployed in a Jordanian context.

L-HSAB, the original Levantine benchmark, is similarly misaligned: it was constructed from Syrian and Lebanese political tweets with three annotators from those communities [ACL Anthology W19-3512]. Its 5,846-tweet size and its source-community mismatch make it inadequate for Jordanian deployment.

### 1.3 The Superset Option

A HuggingFace dataset (`manueltonneau/arabic-hate-speech-superset`) aggregates multiple existing Arabic hate speech corpora into a unified format, which is worth examining as a starting point for model pre-training before fine-tuning on Jordanian-specific data.

---

## 2. Model Architecture: What Works for Jordanian Arabic

### 2.1 The Transformer Landscape

The shift to transformer-based models (2020–present) has produced the most significant performance gains in Arabic hate speech detection. Classical approaches — SVM with TF-IDF, Naive Bayes, traditional BiLSTM — typically peak at F1=0.74 for simple binary tasks and degrade sharply on fine-grained multiclass problems. Transformers, pre-trained on massive Arabic corpora, consistently outperform these baselines.

Three Arabic BERT variants dominate the research landscape:

**AraBERT** (AraELECTRA family) is pre-trained on large MSA corpora from news and Wikipedia. It performs well on standard Arabic text, achieving F1 scores up to 90.17% on offensive language detection. However, its MSA bias is a liability for dialectal text: performance drops measurably when the input diverges from formal Arabic [MDPI BERT Survey 2022].

**CAMeLBERT** from the NYU Abu Dhabi CAMeL Lab is pre-trained on a combination of MSA and dialectal Arabic, making it more robust across registers. On the Jordanian hate speech corpus specifically, CamelBERT achieved F1=0.60 and accuracy=0.61 in fine-tuned experiments [PMC 10912174]. While this sounds modest, it outperforms all non-transformer baselines on that dataset.

**MARBERT** (from UBC NLP) is the strongest choice for dialectal Arabic. Trained on 1 billion Arabic tweets — inherently dialectal, informal, code-switched — MARBERT was designed precisely for the register in which hate speech actually appears. In comparative benchmarks, MARBERT achieves F1=84% on offensive tweet detection, outperforming AraBERT by 1–2% on dialectal tasks and significantly more on highly informal text [GitHub UBC-NLP/marbert]. For Jordanian social media content, MARBERT is the recommended primary model.

**XLM-RoBERTa** (multilingual, Facebook AI) trained on 100+ languages achieves F1=85.89% on low-resource language hate speech detection tasks [Springer 2025]. While it cannot match dialect-specific Arabic models on pure Arabic content, it has a crucial advantage: it handles code-switching (Arabic-English mixed text) better than any monolingual Arabic model. Given that Jordanian social media frequently mixes Arabic script with English words and transliteration, XLM-RoBERTa serves as a strong complement or fallback for code-mixed inputs.

### 2.2 Current State-of-the-Art Performance

The best published results on Arabic hate speech come from hybrid ensemble systems:

- **BERT + GRU/LSTM hybrids**: 98.03–99.14% accuracy on binary tasks (clean vs. offensive)
- **MARBERT v2 + data augmentation**: F1=94.56% on OSACT5
- **AraBERT with ADHAR corpus**: 94% accuracy and F1 on hate detection; 95% for category classification

These headline numbers require careful interpretation. They come from binary or simplified tasks (offensive vs. not offensive) on relatively clean datasets. The harder task — fine-grained hate type classification (race, religion, gender, ideology) — produces macro F1 scores of 45–52%, even for the best models [PMC 12453721]. This gap between binary and fine-grained performance is the core technical challenge the field has not yet solved.

### 2.3 LLMs for Annotation Assistance

The 2024–2025 period has seen initial experiments with large language models (GPT-4, LLaMA, Mistral) for hate speech detection. The results are mixed: LLMs excel at zero-shot and few-shot detection on clear-cut cases but underperform on code-mixed and transliterated Arabic text due to limited exposure to dialectal content during pretraining [ACL 2025 findings]. Notably, open-source models — LLaMA3.1-8B, Mistral-7B, Qwen2.5-7B — outperform GPT-4o-mini on Arabic hate speech benchmarks, making them viable for local deployment without API costs [ACL Anthology 2025].

The most relevant emerging use of LLMs is **synthetic data augmentation**: using models to generate diverse hate speech examples in underrepresented categories, then manually verifying the labels. This technique directly addresses the class imbalance problem in the JHSC dataset and could be a key methodological contribution of the proposed project.

---

## 3. Annotation: The Human Bottleneck

### 3.1 Inter-Annotator Agreement is the Real Problem

The most under-discussed challenge in Arabic hate speech research is annotation quality, not model architecture. The JHSC achieved Fleiss' kappa κ=0.60 on its 500-tweet validation sample — "moderate agreement" by standard interpretations, but dangerously low for a classification dataset. When three trained annotators disagree on 40% of borderline cases, no model can be trained to perform reliably in those cases. The model is not the bottleneck; the annotation is.

Research on multilabel Arabic corpora reports better results — κ=0.86 for offensive/non-offensive binary labels, dropping to κ=0.71 for multi-target hate classification [Frontiers ADHAR 2024]. The pattern is consistent: agreement is high for obvious cases and collapses for the ambiguous, culturally charged content that matters most for real moderation.

Three factors compound this problem for Arabic specifically. First, dialectal variation means a Jordanian annotator may classify a Gulf Arabic phrase differently from a Gulf annotator, not because of carelessness but because the cultural referent is genuinely ambiguous. Second, the same word may be in-group reclamation or targeted slur depending on context that a tweet-length snippet cannot convey. Third, annotator positionality — gender, political affiliation, religious background — measurably influences hate speech labeling even among trained professionals.

### 3.2 The Training Gap for Institutional Moderators

Content moderator burnout is a documented crisis in the platform moderation industry globally. CHI 2021 research found that over a quarter of content moderators demonstrate moderate to severe psychological distress, with approximately a third experiencing elevated psychological distress rates consistent with secondary traumatic stress — symptoms paralleling those seen in emergency services professionals [ACL doi 10.1145/3411764.3445092]. In the Arabic context, this problem is amplified by the absence of structured training infrastructure: moderators at Jordanian media outlets, NGOs, and government agencies are largely self-taught, drawing on personal judgment with no calibration against validated standards.

No dedicated Arabic-language moderator training platform exists. Existing tools — Label Studio, Prodigy, Microsoft Azure Content Safety Studio — are generic annotation platforms designed for ML engineers, not for training institutional moderation teams on domain-specific hate speech with cultural and dialectal context. This is the product gap the proposed platform directly addresses.

---

## 4. The Competitive Landscape

### 4.1 Existing Platforms and Their Limits

**Utopia AI Moderator** offers an AI moderation tool that learns from human decisions, but it is an enterprise API product for platform moderation at scale — not a training tool for moderators, and not Arabic-specific.

**Stream.io** and **Hive Moderation** provide real-time content moderation APIs with pre-trained models. Neither offers Jordanian Arabic support, and neither is designed for training human judgment rather than automating it.

**Microsoft Azure Content Safety Studio** provides a web interface for testing moderation models and building custom classifiers. It supports Arabic to some degree through multilingual models but has no Jordanian dialect capability and no moderator training workflow.

**Label Studio** and **Prodigy** are the closest existing tools to what is being proposed — they allow human annotation of text with active learning feedback loops. However, they are developer-oriented platforms, not designed for non-technical institutional users, and neither provides the moderator training flow (scenario → judgment → AI feedback → learning) that is the core innovation of the proposed platform.

The gap is clear: there is no platform that combines (a) Jordanian Arabic hate speech content, (b) a training-focused workflow designed for non-technical institutional moderators, and (c) an AI copilot that explains its reasoning to build annotator calibration.

---

## 5. Key Synthesis: What This Means for the Platform

Five insights from this research directly shape what the platform should build and how.

**The dataset contribution must prioritize quality over quantity.** The JHSC has 403,688 tweets but κ=0.60 — moderate agreement that limits model reliability. A smaller, higher-agreement corpus (targeting κ≥0.75) with detailed fine-grained labels would be a stronger research contribution than adding more weakly-labeled examples. The platform annotation workflow should be designed to maximize inter-annotator calibration: show moderators the same examples, calculate agreement scores, surface disagreements as learning opportunities.

**MARBERT is the recommended backbone model.** For a system operating on Jordanian social media text — informal, dialectal, code-switched — MARBERT's tweet-based pre-training gives it the strongest foundation. Fine-tuning MARBERT on a curated Jordanian subset of JHSC data, augmented with LLM-generated synthetic examples for underrepresented categories, is the most defensible technical approach.

**The AI copilot's value is explainability, not accuracy.** In the training context, it does not matter if the AI is right on every example. What matters is that the AI's reasoning is legible to human moderators: "This text was flagged because of the term [X], which in Jordanian dialect carries connotations of [Y], particularly when combined with [Z]." This is what builds moderator calibration over time. Attention visualization and confidence scores from the model serve this explainability goal.

**Fine-grained categories matter for Jordanian context.** The OSACT5 schema (race, religion, ideology, disability, social class, gender) is a strong starting point, but Jordanian social media has additional relevant categories: tribalism/regional identity, political affiliation, and refugee-related speech (a particularly active hate vector in Jordan). The annotation schema should extend the standard schema with these local categories.

**LLM-assisted augmentation for class rebalancing.** With hateful content representing only 1.7% of the JHSC corpus, the data needed to train a reliable hate detector does not exist at scale. Using a local open-source LLM (Mistral-7B or LLaMA3) to generate synthetic Jordanian-dialect hate speech examples in underrepresented categories, followed by human verification through the platform, is both methodologically sound and a novel contribution.

---

## 6. Limitations and Caveats

This research reflects the academic literature as of early 2026. The JHSC is the most recent Jordanian-specific dataset but its limited model performance (F1=0.60) means baseline scores for the project's AI copilot will be modest — transparency about this in the pitch is important. The field is moving quickly: new Arabic LLMs and dialect-specific models may be published between now and the hackathon pitch.

The moderator burnout data cited comes from global platform moderation research, not specifically from Jordan or Arabic-speaking contexts. Local conditions may differ. Institutional moderator training practices in Jordan are not documented in the academic literature; primary research (interviews with actual moderators) would strengthen the empathy foundation.

No Arabic-language moderator training platform was found in the literature. This absence could mean the gap is real and unmet, or it could mean such platforms exist commercially/internally but are not published. The JYIF hackathon audience would benefit from confirmation that local NGOs and media organizations have actually tried and failed to solve this with existing tools.

---

## 7. Recommendations

### For the Dataset Contribution

- Build on JHSC as the foundation; do not attempt to re-collect from scratch
- Define a fine-grained annotation schema extending OSACT5 with Jordanian-specific categories (tribalism, refugee-related speech, political affiliation)
- Target κ≥0.75 inter-annotator agreement as the quality bar — document this explicitly in any paper submission
- Use LLM augmentation (Mistral-7B or LLaMA3-Arabic) to generate synthetic examples for underrepresented hate categories, with human verification through the platform itself
- Aim for 1,000–5,000 high-agreement, fine-grained annotations as the benchmark contribution — smaller than JHSC but higher quality and more publishable

### For the AI Copilot Architecture

- Fine-tune MARBERT as the primary model for Jordanian dialectal text
- Use XLM-RoBERTa as a secondary model for code-mixed (Arabic-English) inputs
- Implement attention visualization as the core explainability layer — show moderators which words/phrases triggered the classification
- Display confidence scores to help moderators identify genuinely ambiguous cases
- Track per-moderator calibration score against the ground-truth annotations over time

### For the Platform

- Design the training flow as: content displayed → moderator labels → AI reveals decision + reasoning → moderator reflects and optionally revises → score recorded
- Use inter-annotator agreement as a first-class metric: show moderators how their decisions compare to colleagues and to the AI
- Build admin dashboard to let institutions assign training batches and track team calibration
- Hard requirement: Arabic RTL text rendering throughout the entire UI

### For the Hackathon Demo

- Lead with a live walkthrough: pick a real Jordanian tweet, show the moderation flow, show the AI explanation, show the moderator score improving
- Quantify the gap: "Jordan has one hate speech dataset. Its best model is 62% accurate. Our platform targets 80%+ while training the humans who matter most."
- Mention the research angle: every annotation from the platform feeds a publishable Jordanian Arabic benchmark

---

## Bibliography

[1] PMC 12453721. "Arabic hate speech detection using deep learning: a state-of-the-art survey of advances, challenges, and future directions (2020–2024)." PeerJ Computer Science, 2024. https://pmc.ncbi.nlm.nih.gov/articles/PMC12453721/

[2] PMC 10912174. "Hate speech detection in the Arabic language: corpus design, construction, and evaluation." Frontiers in Artificial Intelligence, 2024. https://pmc.ncbi.nlm.nih.gov/articles/PMC10912174/

[3] Frontiers ADHAR. "Hate speech detection with ADHAR: a multi-dialectal hate speech corpus in Arabic." Frontiers in Artificial Intelligence, 2024. https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2024.1391472/full

[4] ACL Anthology W19-3512. "L-HSAB: A Levantine Twitter Dataset for Hate Speech and Abusive Language." ACL Anthology, 2019. https://aclanthology.org/W19-3512/

[5] ACL Anthology OSACT5. "Overview of OSACT5 Shared Task on Arabic Offensive Language and Hate Speech Detection." ACL Anthology, 2022. https://aclanthology.org/2022.osact-1.20/

[6] ACL Anthology OSACT4. "Overview of OSACT4 Arabic Offensive Language Detection Shared Task." Semantic Scholar. https://www.semanticscholar.org/paper/Overview-of-OSACT4-Arabic-Offensive-Language-Shared-Mubarak-Darwish/1898d36d4fb8b2cd388305c67ff1952fa53b8ff0

[7] GitHub UBC-NLP/marbert. "UBC ARBERT and MARBERT Deep Bidirectional Transformers for Arabic." GitHub. https://github.com/UBC-NLP/marbert

[8] MDPI BERT Survey 2022. "BERT Models for Arabic Text Classification: A Systematic Review." Applied Sciences, 2022. https://www.mdpi.com/2076-3417/12/11/5720

[9] HuggingFace Superset. "manueltonneau/arabic-hate-speech-superset." HuggingFace Datasets. https://huggingface.co/datasets/manueltonneau/arabic-hate-speech-superset

[10] Frontiers Hate Speech Arabic 2024. "Hate speech detection in the Arabic language: corpus design, construction, and evaluation." Frontiers in Artificial Intelligence, 2024. https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2024.1345445/full

[11] ScienceDirect Levantine. "Hate and offensive speech detection on Arabic social media." Online Social Networks and Media, 2020. https://www.sciencedirect.com/science/article/abs/pii/S2468696420300379

[12] PMC 11041964. "A systematic literature review of hate speech identification on Arabic Twitter data: research challenges and future directions." PMC, 2024. https://pmc.ncbi.nlm.nih.gov/articles/PMC11041964/

[13] PMC 11253949. "Code-mixing unveiled: Enhancing the hate speech detection in Arabic dialect tweets using machine learning models." PMC, 2024. https://pmc.ncbi.nlm.nih.gov/articles/PMC11253949/

[14] Springer 2025. "Enhancing social media hate speech detection in low-resource languages using transformers and explainable AI." Social Network Analysis and Mining, 2025. https://link.springer.com/article/10.1007/s13278-025-01497-w

[15] Springer Multilingual XLM. "Multilingual Content Moderation: Advanced Hate Speech Detection with XLM-RoBERTa." SpringerLink, 2025. https://link.springer.com/chapter/10.1007/978-981-96-9248-4_6

[16] MDPI Multilingual GAN. "Multilingual Hate Speech Detection: A Semi-Supervised Generative Adversarial Approach." Entropy MDPI, 2024. https://www.mdpi.com/1099-4300/26/4/344

[17] ScienceDirect Dialects Gap. "The dialects gap: a multi-task learning approach for enhancing hate speech detection in Arabic dialects." Expert Systems with Applications, 2025. https://www.sciencedirect.com/science/article/abs/pii/S0957417425022031

[18] ACL 2025 Inconsistencies. "Inconsistencies in Hate Speech Detection Across LLM-..." ACL Findings, 2025. https://aclanthology.org/2025.findings-acl.1144.pdf

[19] Springer LLM Augmentation. "LLM synthetic generation to enhance online content moderation generalization in hate speech scenarios." Computing, 2025. https://link.springer.com/article/10.1007/s00607-025-01518-8

[20] CHI 2021 Moderators. "The Psychological Well-Being of Content Moderators." CHI Conference on Human Factors in Computing Systems, 2021. https://dl.acm.org/doi/10.1145/3411764.3445092

[21] PMC Moderator Mental Health. "Content Moderator Mental Health and Associations with Coping Styles." PMC, 2024. https://pmc.ncbi.nlm.nih.gov/articles/PMC12024403/

[22] Kaggle L-HSAB. "Arabic Levantine Hate Speech Detection." Kaggle. https://www.kaggle.com/datasets/haithemhermessi/arabic-levantine-hate-speech-detection

[23] Utopia AI. "AI Content Moderation Tool." Utopia Analytics. https://www.utopiaanalytics.com/utopia-ai-moderator

[24] Label Studio. "Open Source Data Labeling." Label Studio. https://labelstud.io/

[25] ArXiv 2025. "Rethinking Hate Speech Detection on Social Media: Can LLMs Replace Traditional Models?" arXiv, 2025. https://arxiv.org/html/2506.12744v1

---

## Methodology

Research conducted in deep mode (March 2026) using 13 parallel web searches across: OSACT shared tasks, Jordanian Arabic NLP, Levantine hate speech corpora, BERT/MARBERT/CAMeLBERT benchmarks, state-of-the-art 2024–2025 detection methods, content moderation platforms, moderator burnout literature, inter-annotator agreement methods, multilingual models, LLM annotation assistance, and human-in-the-loop moderation systems. Three key papers were fetched in full: PMC 12453721 (survey), PMC 10912174 (JHSC corpus paper), and Frontiers ADHAR 2024. Total sources consulted: 25. All claims are grounded in the retrieved sources with inline citations.
