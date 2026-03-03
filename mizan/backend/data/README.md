# Mizan Datasets

Data files used by the Mizan platform for Arabic hate speech detection and moderator training.

## JHSC — Jordanian Hate Speech Corpus

- **Files**: `jhsc/annotated-hatetweets-4-classes_train.csv`, `jhsc/annotated-hatetweets-4-classes_test.csv`
- **Rows**: 302,766 (train) + 100,923 (test) = 403,689 total
- **Columns**: `tweet_id`, `new_tweet_content`, `Label`
- **Labels**: `negative`, `neutral`, `positive`, `very positive`
- **Mizan mapping**: `negative` -> hate (unknown); others -> not_hate
- **Dialect**: Jordanian Arabic
- **License**: CC BY 4.0
- **Citation**: Ahmad et al. 2024, "Hate Speech Detection in Jordanian Arabic Tweets", Frontiers in AI

## Let-Mi — Levantine Misogyny Dataset

- **File**: `let-mi/let-mi_train_part.csv`
- **Rows**: 5,240
- **Columns**: `text`, `category`, `misogyny`, `target`
- **Labels**: `misogyny` field values (none, discredit, derailing, etc.)
- **Mizan mapping**: `misogyny != "none"` -> hate (gender); `"none"` -> not_hate
- **Dialect**: Levantine Arabic
- **Citation**: Mulki & Ghanem, "Let-Mi: An Arabic Levantine Twitter Dataset for Misogynistic Language", WANLP @ EACL 2021

## MLMA Arabic — Multilingual Multi-Aspect Hate Speech

- **File**: `mlma/ar_dataset.csv`
- **Rows**: 3,353
- **Columns**: `HITId`, `tweet`, `sentiment`, `directness`, `annotator_sentiment`, `target`, `group`
- **Labels**: sentiment values including `hateful`, `abusive_hateful`, `offensive_hateful`, `normal`, `offensive`
- **Mizan mapping**: `*hateful*` -> hate; `normal` -> not_hate; `offensive` -> offensive; target -> hate_type (gender, religion, origin->race, disability, other->unknown)
- **Dialect**: Mixed Arabic
- **Citation**: Ousidhoum et al. 2019, "Multilingual and Multi-Aspect Hate Speech Analysis", EMNLP

## AJ Comments — Al Jazeera Arabic Comments (CrowdFlower)

- **File**: `aj-comments/AJCommentsClassification-CF.xlsx`
- **Rows**: 31,692 total
- **Columns**: `body`, `languagecomment`, `languagecomment:confidence`
- **Labels**: `-2` (hate speech), `-1` (normal), `0` (off-topic/spam)
- **Mizan mapping**: `-2` (confidence >= 0.75) -> hate; `-1` -> not_hate; `0` -> drop
- **Usable hate examples**: ~533 rows at -2, ~400 after confidence filter
- **Dialect**: Mixed Arabic

## Arabic Religious — Albadi 2018 (Reserved)

- **Files**: `arabic-religious/` — Tweet IDs + AraHate lexicons
- **Status**: Reserved for Phase 4 lexicon-based features
- **Note**: Contains tweet IDs only (not hydrated); AraHate lexicons for hate speech keyword detection
