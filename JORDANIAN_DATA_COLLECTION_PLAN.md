# Comprehensive Jordanian Arabic Hate Speech Data Collection Plan

## Executive Summary

This document provides a complete strategy for collecting Jordanian Arabic hate speech data across multiple platforms and sources. The plan includes specific hashtags, keywords, tools, methods, and realistic yield estimates for building a comprehensive Jordanian dialect hate speech dataset.

---

## 1. Social Media Platforms for Scraping

### 1.1 Twitter/X Strategy

#### Geographic Filtering Methods:
- **Location-based filtering**: Search for users with location containing "Jordan", "Amman", "Irbid", "Zarqa", "Aqaba", "الاردن", "عمان"
- **Language + Location**: Combine Arabic language tweets (`lang:ar`) with geographic indicators
- **Timezone filtering**: Target users in Jordan timezone (UTC+3)

#### Jordanian-Specific Search Queries:
```python
# Twitter Advanced Search Examples
location_queries = [
    "الاردن",
    "عمان",
    "الزرقاء", 
    "اربد",
    "العقبة",
    "السلط",
    "الكرك",
    "مادبا",
    "البلقاء"
]

# Geographic operators
geo_queries = [
    "place:Jordan",
    "place:Amman", 
    "point_radius:[35.9450 31.9539 25mi]",  # Amman radius
]
```

#### Target Accounts (Jordanian Public Figures):
**Journalists & Media:**
- @AlGhadNews (Al Ghad Newspaper)
- @AmmonNewsAr (Ammon News)
- @AlraiMedia (Al Rai)
- @SarayaNews (Saraya News)

**Politicians & Officials:**
- Jordanian Parliament members
- Government officials
- Political commentators

**Influencers:**
- Jordanian comedians (critical for understanding cultural context)
- Social commentators
- Youth activists

#### Expected Yield:
- **Tweets per day from Jordan**: ~50,000-100,000
- **Political/controversial tweets**: ~10,000-20,000 per week
- **Realistic hate speech subset**: 500-1,500 examples per week

### 1.2 Facebook Strategy

#### Target Pages & Groups:

**News & Politics:**
- Jordanian News Pages (Al Ghad, Ammon, Al Rai)
- Political discussion groups
- Government official pages

**Tribal/Family Groups:**
- Search for groups with keywords: "عشائر", "قبيلة", "العشائر الأردنية"
- Family/tribe Facebook groups (many are public)
- Regional community groups

**Political Movements:**
- Opposition groups
- Reform movement pages
- Youth political groups

#### Scraping Strategy:
```python
# Using facebook-scraper or similar tools
# Focus on comments sections where hate speech is more common

target_pages = [
    "JordanianNewsPages",
    "JordanParliament",
    "JordanianPoliticalDiscussion"
]

target_groups = [
    # Tribal groups (names vary, need manual identification)
    "عشائر الأردن",
    "العشائر الأردنية"
]
```

#### Expected Yield:
- **Comments per controversial post**: 100-500
- **Weekly collection from 10 active pages**: 5,000-10,000 comments
- **Hate speech subset**: 500-1,000 examples per week

### 1.3 YouTube Strategy

#### Target Channels:

**Jordanian News Channels:**
- Jordan TV (القناة الأردنية)
- Roya TV (رؤيا)
- Al Mamlaka TV (المملكة)
- Jo24

**Political Shows:**
- "Jo Academy" programs
- Political talk shows
- Parliamentary session recordings

**Social Commentary:**
- Jordanian vloggers
- Social critics
- Youth content creators

#### Comment Scraping Method:
```python
# Using yt-dlp or youtube-comment-downloader

# Step 1: Collect video IDs from Jordanian channels
channels = [
    "RoyaTV",
    "AlMamlakaTV",
    "Jo24News"
]

# Step 2: Scrape comments with metadata
# Focus on videos with controversial topics:
# - Political debates
# - Refugee discussions
# - Economic policies
# - Tribal conflicts
```

#### Expected Yield:
- **Comments per political video**: 200-1,000
- **Weekly from 5 major channels**: 3,000-5,000 comments
- **Hate speech subset**: 300-700 examples per week

### 1.4 Telegram Strategy

#### Target Channels:

**Political Channels:**
- Jordanian political parties
- Opposition groups
- Government announcements (comments)
- News aggregators

**Community Channels:**
- University groups
- Regional community channels
- Professional groups

#### Scraping Tools:
```python
# Using telethon or pyrogram
from telethon.sync import TelegramClient

# Monitor these channel types:
jordanian_channels = [
    # Need to identify specific channels
    # Search for: الأردن, سياسة, أخبار
]
```

#### Expected Yield:
- **Messages per day from 20 channels**: 2,000-5,000
- **Hate speech subset**: 200-400 examples per week

### 1.5 Reddit & Forums

#### Target Communities:
- r/Jordan (English/Arabic mix)
- r/ArabicPolitics
- Jordanian diaspora forums

#### Expected Yield:
- **Lower volume but high quality**: 50-100 examples per week
- Better for understanding cross-cultural hate speech

### 1.6 TikTok

#### Content Types:
- Political commentary videos
- Social criticism
- News reaction videos
- Cultural commentary

#### Scraping Method:
```python
# Using TikTokApi or similar
# Focus on comments and video descriptions

hashtags = [
    "#الأردن",
    "#عمان",
    "#سياسة_أردنية"
]
```

#### Expected Yield:
- **Comments per video**: 50-200
- **Weekly collection**: 1,000-2,000 comments
- **Hate speech subset**: 100-300 examples per week

---

## 2. Jordanian-Specific Hashtags and Keywords

### 2.1 Political Hashtags

**General Politics:**
- `#الأردن` (Jordan)
- `#الاردن` (Jordan - alternative spelling)
- `#عمان` (Amman)
- `#برلمان_أردني` (Jordanian Parliament)
- `#حكومة_الأردن` (Jordan Government)
- `#سياسة_أردنية` (Jordanian Politics)
- `#إصلاح` (Reform)
- `#معارضة_أردنية` (Jordanian Opposition)

**Specific Events/Issues:**
- `#احتجاجات_الأردن` (Jordan Protests)
- `#الإقتصاد_الأردني` (Jordanian Economy)
- `#ديون_الأردن` (Jordan's Debt)
- `#بطالة_الأردن` (Jordan Unemployment)

### 2.2 Tribal/عشائر Keywords

**General Tribal Terms:**
- `عشائر` (Tribes)
- `قبيلة` (Tribe)
- `العشائر_الأردنية` (Jordanian Tribes)
- `عشائر_الشمال` (Northern Tribes)
- `عشائر_الجنوب` (Southern Tribes)
- `عشائر_البادية` (Bedouin Tribes)
- `عشائر_البلقاء` (Balqa Tribes)

**Specific Tribal Names (High Sensitivity):**
- Major tribal names (research needed for specific list)
- Regional tribal conflicts keywords

**Tribal Conflict Indicators:**
- `التحشيش` (used in tribal conflicts)
- `حشري` (troublemaker)
- `شماتة` (gloating)
- `نخوة` (tribal pride)
- `غزوة` (raid - used metaphorically)

### 2.3 Refugee-Related Terms

**General Refugee Terms:**
- `لاجئين` (Refugees)
- `سوريين` (Syrians)
- `سوريا` (Syria)
- `اللاجئين_السوريين` (Syrian Refugees)
- `مخيمات_اللاجئين` (Refugee Camps)
- `الزرعري` (Zaatari Camp)
- `اللاجئين_الفلسطينيين` (Palestinian Refugees)

**Negative Terms (Monitor for Hate Speech):**
- `غزو_سوري` (Syrian Invasion)
- `احتلال_سوري` (Syrian Occupation)
- `لاجئين_خونة` (Traitor Refugees)
- `طابور_خامس` (Fifth Column)
- `سرقة_فرص_العمل` (Stealing Jobs)
- `عبء_اقتصادي` (Economic Burden)

### 2.4 Jordanian Dialect Markers

**Jordanian-Specific Words:**
- `بدو` (Bedouin - can be neutral or derogatory)
- `شو` (What - Jordanian dialect)
- `ليش` (Why)
- `هيدا` (This)
- `هلأ` (Now)
- `إمتى` (When)
- `عالدوام` (At work)
- `زلمة` (Man/Guy)

**Regional Variations:**
- `شمالي` (Northern - can have class connotations)
- `جنوبي` (Southern - can have class connotations)
- `بدوي` (Bedouin - can be derogatory)
- `حضر` (Urban/Non-Bedouin)

**Class/Social Markers:**
- `فلاح` (Farmer - can be derogatory)
- `بدوي` (Bedouin - context-dependent)
- `أصل` (Origin/Lineage - used in social hierarchy)
- `عائلة` (Family - importance in social status)

### 2.5 Religious Sectarian Terms

**Muslim Sectarian:**
- `سلفي` (Salafi)
- `إخوان` (Muslim Brotherhood)
- `تکفيري` (Takfiri)
- `رافضي` (Shia - derogatory)
- `ناصبي` (Anti-Shia - derogatory)

**Christian-Muslim:**
- `نصارى` (Christians - context-dependent)
- `كفار` (Infidels - hate speech indicator)
- `صليبي` (Crusader - can be derogatory)

### 2.6 Gender-Based Terms

**Misogyny Indicators:**
- `حرمة` (Woman - can be respectful or derogatory)
- `ست` (Woman - often derogatory in certain contexts)
- `بنت_الحرام` (Bastard - literally "daughter of the forbidden")
- `عاهرة` (Whore)
- `شقية` (Shameless woman)
- `مسترجلة` (Masculine woman - derogatory)

### 2.7 National Origin/Racism

**Anti-Syrian:**
- `سوري_قذر` (Dirty Syrian)
- `سوري_مجرم` (Criminal Syrian)
- `الأجنبي_السوري` (Syrian Foreigner - derogatory)

**Anti-Palestinian:**
- `لاجئ` (Refugee - context-dependent)
- `وافد` (Newcomer - often derogatory)
- `غريب` (Foreigner - context-dependent)

**Anti-Egyptian:**
- `مصري` (Egyptian - context-dependent)
- Various stereotypical terms

---

## 3. Existing Datasets with Jordanian Content

### 3.1 Arabic Hate Speech Superset (449,078 samples)

**Source:** https://huggingface.co/datasets/manueltonneau/arabic-hate-speech-superset

**Contains Jordanian Content:**
- **L-HSAB**: Levantine Twitter Dataset (includes Jordanian)
- **Let-Mi**: Levantine Misogyny Dataset
- **Brothers**: Religious hate speech (some Jordanian content)

**How to Extract Jordanian Subset:**
```python
from datasets import load_dataset

# Load the superset
dataset = load_dataset("manueltonneau/arabic-hate-speech-superset")

# Filter for Jordanian content
jordanian_keywords = [
    "الاردن", "الأردن", "عمان", "اربد", "الزرقاء",
    "العقبة", "السلط", "الكرك", "مادبا", "بدو"
]

def is_jordanian(example):
    text = example['text'].lower()
    return any(keyword in text for keyword in jordanian_keywords)

jordanian_subset = dataset.filter(is_jordanian)

print(f"Estimated Jordanian samples: {len(jordanian_subset['train'])}")
# Expected: 5,000-15,000 samples with Jordanian markers
```

**Realistic Yield:** 5,000-15,000 Jordanian-labeled examples

### 3.2 L-HSAB (Levantine Hate Speech Dataset)

**Source:** https://github.com/Hala-Mulki/L-HSAB-First-Arabic-Levantine-HateSpeech-Dataset

**Description:** First Levantine Arabic hate speech dataset focusing on Lebanon, Syria, Jordan, and Palestine.

**Content:**
- 7,000+ tweets
- Dialect-specific annotations
- Binary hate speech labels

**Jordanian Subset:**
- Estimated 1,000-2,000 Jordanian tweets
- High quality annotations
- Levantine dialect focus

### 3.3 Let-Mi (Levantine Misogyny Dataset)

**Source:** https://aclanthology.org/2021.wanlp-1.16/

**Content:**
- Levantine dialect misogynistic language
- 5,000+ tweets
- Multi-label annotations

**Jordanian Content:**
- Estimated 500-1,000 Jordanian examples
- Focus on gender-based hate speech

### 3.4 ADHAR (Arabic Dialect Hate Speech and Abuse Recognition)

**Status:** Check availability
**Potential:** May contain Jordanian dialect content

### 3.5 Extraction Strategy from Mixed Datasets

**Method 1: Keyword Filtering**
```python
jordanian_markers = {
    # Geographic
    "الاردن", "عمان", "اربد", "الزرقاء", "العقبة",
    
    # Dialect markers
    "شو", "ليش", "هيدا", "هلأ", "إمتى", "عالدوام",
    
    # Cultural references
    "بدو", "عشائر", "قبيلة"
}

def extract_jordanian_samples(dataset):
    jordanian_samples = []
    
    for sample in dataset:
        text = sample['text']
        
        # Check for Jordanian markers
        jordanian_score = sum(
            1 for marker in jordanian_markers 
            if marker in text
        )
        
        # Threshold for Jordanian content
        if jordanian_score >= 2:
            jordanian_samples.append(sample)
    
    return jordanian_samples
```

**Method 2: Dialect Identification Model**
```python
# Use pre-trained Arabic dialect identification
from transformers import pipeline

# Option 1: Use AraBERT with dialect classification head
dialect_classifier = pipeline(
    "text-classification",
    model="aubmindlab/bert-base-arabertv02"
)

# Option 2: Train custom classifier
# Label samples from known Jordanian accounts
# Use to classify unlabeled data
```

**Method 3: User Location Metadata**
```python
# If available, use user location field
jordanian_locations = [
    "jordan", "amman", "irbid", "zarqa", "aqaba",
    "الاردن", "عمان", "اربد", "الزرقاء", "العقبة"
]

def filter_by_location(sample):
    user_location = sample.get('user_location', '').lower()
    return any(loc in user_location for loc in jordanian_locations)
```

---

## 4. Academic/Government Sources

### 4.1 Jordanian University Research

**Jordan University of Science and Technology (JUST):**
- Department of Computer Science
- Potential NLP research groups
- Contact: https://www.just.edu.jo

**University of Jordan (UJ):**
- Faculty of Information Technology
- Arabic language processing research
- Contact: https://www.ju.edu.jo

**Yarmouk University:**
- Computer Science Department
- Potential for collaboration

**Hashemite University:**
- Faculty of Prince Al-Hussein bin Abdullah II for Information Technology

**Potential Research Contacts:**
- Search for publications by Jordanian researchers on:
  - Arabic NLP
  - Hate speech detection
  - Social media analysis
  - Computational linguistics

### 4.2 Government & NGO Reports

**Jordanian Government Sources:**
- **Jordan Media Commission**: May have reports on media monitoring
- **Ministry of Digital Economy**: Digital content policies
- **Jordan Data Forum**: May have social media studies

**International Organizations:**
- **UNHCR Jordan**: Reports on hate speech against refugees
- **UNICEF Jordan**: Youth and social media studies
- **Human Rights Watch**: Jordan country reports
- **Amnesty International**: Jordan human rights reports

**NGOs:**
- **Jordanian Women's Union**: Gender-based hate speech reports
- **Sisterhood Is Global Institute (SIGI)**: Women's rights reports
- **Arab Network for the Protection of Nature**: Environmental hate speech
- **Jordanian Youth Commission**: Youth-targeted hate speech

### 4.3 Media Monitoring Organizations

**Regional:**
- **Media Diversity Institute**: May have Jordan-focused reports
- **Arab Reporters for Investigative Journalism (ARIJ)**: Jordan office
- **Internews**: Jordan programs

**Local:**
- **Jordan Press Association**: Media ethics reports
- **Center for Defending Freedom of Journalists**: May have relevant reports

### 4.4 Research Strategy

**Academic Paper Search:**
```python
# Search terms for academic databases
search_queries = [
    "Jordanian Arabic hate speech",
    "Arabic dialect hate speech Jordan",
    "Levantine Arabic offensive language",
    "Jordan social media hate speech",
    "Arabic NLP Jordan",
    "Jordanian dialect computational linguistics"
]

# Databases to search:
# - Google Scholar
# - arXiv (cs.CL, cs.CY)
# - ACL Anthology
# - IEEE Xplore
# - ScienceDirect
# - ResearchGate
# - Semantic Scholar
```

**Contacting Researchers:**
1. Identify Jordanian NLP researchers
2. Search for publications at Jordanian universities
3. Reach out for potential collaboration or data sharing
4. Check for existing datasets not yet public

---

## 5. Crowdsourcing Strategies for Mizan Platform

### 5.1 Data Collection Methods

**Method 1: Active Contribution Interface**

```python
# Mizan platform feature: User submission portal

class UserSubmission:
    """
    Allow users to submit hate speech examples they encounter
    """
    
    submission_fields = {
        "text": "Original text (required)",
        "source": "Twitter/Facebook/YouTube/etc.",
        "category": "Hate/Offensive/Both/Not Sure",
        "target": "Race/Religion/Gender/Nationality/Other",
        "context": "Optional context",
        "url": "Original post URL (optional)"
    }
    
    # Incentives
    reward_system = {
        "submission": 5 points,
        "quality_bonus": 10 points (if validated),
        "referral": 20 points
    }
```

**Method 2: Annotation Tasks**

```python
# Crowdsourced annotation for unlabeled data

class AnnotationTask:
    """
    Present users with text samples to annotate
    """
    
    task_types = [
        "binary_classification",  # Hate vs Not Hate
        "multi_label",            # Race, Religion, Gender, etc.
        "severity_rating",        # 1-5 scale
        "dialect_identification", # Jordanian vs Other
        "target_identification"   # Who is being targeted
    ]
    
    # Quality control
    validation_method = "golden_set"
    # Include known-labeled samples to check annotator quality
```

### 5.2 Incentive Mechanisms

**Gamification System:**
```python
class RewardSystem:
    """
    Multi-tier reward system for contributors
    """
    
    # Tier 1: Basic Rewards
    basic_rewards = {
        "points_per_annotation": 2,
        "points_per_submission": 5,
        "daily_bonus": 10 (for 10+ tasks)
    }
    
    # Tier 2: Quality Bonuses
    quality_rewards = {
        "accuracy_bonus": 20 points (if >90% accuracy),
        "expert_reviewer": 50 points (after 1000 tasks),
        "golden_master": 100 points (after 5000 tasks)
    }
    
    # Tier 3: Leaderboard
    leaderboard = {
        "weekly_top_contributors": Public recognition,
        "monthly_champions": Certificate,
        "annual_top_10": Special rewards
    }
    
    # Tier 4: Monetary Rewards (if budget allows)
    monetary_rewards = {
        "per_1000_valid_annotations": $5-10,
        "quality_bonus": $20 (top performers),
        "research_assistant": $100/month (top contributors)
    }
```

**Non-Monetary Incentives:**
1. **Certificates**: Digital badges for contributors
2. **Recognition**: Public acknowledgment in research papers
3. **Learning**: Training in NLP and annotation
4. **Community**: Exclusive contributor community
5. **Impact**: Show how their work is being used

### 5.3 Quality Control Mechanisms

**Multi-Layer Validation:**
```python
class QualityControl:
    """
    Ensure high-quality annotations
    """
    
    # Layer 1: Golden Set Validation
    def golden_set_check(self, user_annotations):
        """
        Insert known-labeled samples randomly
        Check if user accuracy > threshold
        """
        accuracy = calculate_accuracy(user_annotations, golden_set)
        
        if accuracy < 0.7:
            return "Training mode - more guidance needed"
        elif accuracy < 0.85:
            return "Standard mode"
        else:
            return "Expert mode - harder tasks"
    
    # Layer 2: Inter-Annotator Agreement
    def calculate_agreement(self):
        """
        Each sample annotated by 3+ users
        Calculate Cohen's Kappa or Krippendorff's Alpha
        """
        min_agreement = 0.6  # Threshold
        
        # If low agreement, escalate to expert
        if agreement < min_agreement:
            escalate_to_expert(sample)
    
    # Layer 3: Expert Review
    def expert_review(self, controversial_samples):
        """
        Domain experts resolve disagreements
        """
        # Recruit linguists, sociologists, psychologists
        # Pay higher rates for expert annotation
        expert_rate = 5 * standard_rate
    
    # Layer 4: Consistency Checks
    def temporal_consistency(self):
        """
        Re-show same sample after time gap
        Check if user gives same annotation
        """
        # Expected: >90% consistency
```

**Annotator Screening:**
```python
def screen_annotators(candidate):
    """
    Initial screening test before allowing contributions
    """
    
    screening_test = {
        "language_proficiency": "Jordanian Arabic comprehension",
        "cultural_knowledge": "Jordanian social context",
        "annotation_skill": "Sample annotation tasks",
        "bias_check": "Implicit bias test"
    }
    
    # Minimum requirements:
    requirements = {
        "proficiency_score": 80,
        "cultural_score": 70,
        "annotation_accuracy": 85
    }
```

### 5.4 Platform Design for Mizan

**User Interface Features:**
```python
class MizanAnnotationUI:
    """
    User-friendly annotation interface
    """
    
    features = {
        # Text Display
        "text_display": {
            "font_size": "Adjustable",
            "highlight_keywords": "Auto-highlight hate words",
            "show_context": "Show original post context"
        },
        
        # Annotation Options
        "labels": [
            "Not Hate Speech",
            "Hate Speech - Race/Ethnicity",
            "Hate Speech - Religion",
            "Hate Speech - Gender",
            "Hate Speech - Nationality",
            "Hate Speech - Sexual Orientation",
            "Hate Speech - Disability",
            "Hate Speech - Multiple",
            "Offensive but Not Hate",
            "Unclear"
        ],
        
        # Assistance
        "help_tooltips": "Explain each category",
        "examples": "Show example annotations",
        "guidelines": "Link to detailed guidelines",
        
        # Progress Tracking
        "dashboard": {
            "tasks_completed": "Count",
            "accuracy": "Percentage",
            "points": "Total earned",
            "rank": "Leaderboard position"
        }
    }
```

### 5.5 Recruitment Strategy

**Target Demographics:**
1. **University Students**: 
   - Jordanian universities (JUST, UJ, Yarmouk, etc.)
   - Students of Arabic, Sociology, Media Studies, CS
   - Offer course credit or volunteer hours

2. **Social Media Users**:
   - Twitter/Facebook Jordanian users
   - Reddit r/Jordan community
   - Jordanian diaspora

3. **Professionals**:
   - Journalists
   - Teachers/educators
   - Social workers
   - Psychologists

4. **Community Members**:
   - Tribal representatives (for cultural context)
   - Religious leaders (for religious hate speech)
   - Refugee community members

**Outreach Methods:**
```python
outreach_channels = {
    "Social Media": [
        "Twitter: @MizanPlatform",
        "Facebook: Jordanian academic groups",
        "Instagram: Targeted ads to Jordanian users"
    ],
    
    "Academic": [
        "Email professors at Jordanian universities",
        "Post on university notice boards",
        "Partner with research centers"
    ],
    
    "Influencer Partnerships": [
        "Collaborate with Jordanian YouTubers",
        "Partner with Jordanian podcasters",
        "Work with social media influencers"
    ],
    
    "Incentives": [
        "Offer certificates for contributors",
        "Co-authorship opportunities for top contributors",
        "Scholarship opportunities (if budget allows)"
    ]
}
```

### 5.6 Expected Crowdsourcing Yields

**Conservative Estimates:**
- **Active annotators**: 50-100
- **Annotations per user per week**: 50-100
- **Weekly total**: 2,500-10,000 annotations
- **Monthly unique samples**: 5,000-15,000
- **High-quality subset (after quality control)**: 3,000-10,000 per month

**Optimistic Estimates:**
- **Active annotators**: 200-500
- **Annotations per user per week**: 100-200
- **Weekly total**: 20,000-100,000 annotations
- **Monthly unique samples**: 15,000-40,000
- **High-quality subset**: 10,000-30,000 per month

---

## 6. Tools & Methods for Scraping

### 6.1 Twitter/X Scraping

#### Tool 1: Twarc (Recommended)
**Installation:**
```bash
pip3 install twarc
twarc2 configure
```

**Usage for Jordanian Content:**
```bash
# Search with geographic filter
twarc2 search --start-time "2024-01-01" \
              --end-time "2024-12-31" \
              "place:Jordan OR الأردن OR عمان lang:ar" \
              jordanian_tweets.jsonl

# Search with Jordanian keywords
twarc2 search --start-time "2024-01-01" \
              "(بدو OR عشائر OR قبيلة) lang:ar" \
              tribal_tweets.jsonl

# Get tweets from specific users
twarc2 tweets --usernames username1,username2 \
              jordanian_users.jsonl

# Academic Access (if available)
# Full archive search with no rate limits
twarc2 search --archive "place:Jordan lang:ar" \
              jordanian_full_archive.jsonl
```

**API Requirements:**
- Twitter API v2 Basic: $100/month (10,000 tweets/month)
- Twitter API v2 Pro: $5,000/month (1M tweets/month)
- Academic Research Track: Free (10M tweets/month) - requires application

**Realistic Yield:**
- **Basic tier**: 10,000 tweets/month (limited)
- **Pro tier**: 500,000-1,000,000 tweets/month
- **Academic tier**: 5-10M tweets/month

#### Tool 2: Snscrape (Free Alternative)
**Installation:**
```bash
pip3 install snscrape
```

**Usage:**
```bash
# Search tweets by keyword
snscrape --jsonl --max-results 1000 \
         twitter-search "الأردن lang:ar since:2024-01-01" \
         > jordanian_tweets.jsonl

# Search by hashtag
snscrape --jsonl --max-results 500 \
         twitter-hashtag "الأردن" \
         > hashtag_tweets.jsonl

# Scrape user timeline
snscrape --jsonl --max-results 1000 \
         twitter-user username \
         > user_tweets.jsonl
```

**Pros:**
- Free, no API key needed
- Can scrape historical data

**Cons:**
- Less reliable than official API
- May violate ToS
- Rate limiting issues
- Can stop working without notice

**Realistic Yield:**
- 10,000-50,000 tweets/day (with rate limiting)
- Best for targeted searches, not large-scale collection

#### Tool 3: GetOldTweets3 (Historical)
```python
import GetOldTweets3 as got

# Search for old Jordanian tweets
tweetCriteria = got.manager.TweetCriteria()\
    .setQuerySearch("الأردن")\
    .setSince("2020-01-01")\
    .setUntil("2024-12-31")\
    .setMaxTweets(10000)

tweets = got.manager.TweetManager.getTweets(tweetCriteria)
```

### 6.2 Facebook Scraping

#### Tool 1: facebook-scraper
**Installation:**
```bash
pip3 install facebook-scraper
```

**Usage:**
```python
from facebook_scraper import get_posts

# Scrape posts from a public page
for post in get_posts('page_name', pages=10):
    print(post['text'])
    print(post['comments_full'])  # Comments
    
    # Save to JSON
    save_post(post)

# Scrape group posts
for post in get_posts(group='group_id', pages=5):
    process_post(post)
```

**Limitations:**
- Only works for public pages/groups
- May require login for some content
- Facebook actively blocks scrapers
- Use with caution and respect rate limits

**Realistic Yield:**
- 1,000-5,000 posts/comments per day (with caution)
- Comments are often more valuable than posts

#### Tool 2: Selenium/Playwright (Custom)
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Set up browser
driver = webdriver.Chrome()

# Navigate to page
driver.get("https://www.facebook.com/page_name")

# Scroll to load more posts
for i in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

# Extract posts
posts = driver.find_elements(By.CLASS_NAME, "post_class")

# Extract comments
for post in posts:
    comments = post.find_elements(By.CLASS_NAME, "comment_class")
    # Process comments
```

**Pros:**
- Can access content requiring login
- More flexible

**Cons:**
- Slower than API-based methods
- Higher risk of being blocked
- Requires more maintenance

### 6.3 YouTube Comment Scraping

#### Tool 1: yt-dlp (Recommended)
**Installation:**
```bash
pip3 install yt-dlp
```

**Usage:**
```bash
# Get comments from a video
yt-dlp --write-comments --skip-download \
       "https://www.youtube.com/watch?v=VIDEO_ID" \
       -o "output.%(ext)s"

# Get comments with specific format
yt-dlp --write-comments --skip-download \
       --print-json \
       "VIDEO_URL" \
       > comments.json

# Batch processing
for url in $(cat video_urls.txt); do
    yt-dlp --write-comments --skip-download "$url"
done
```

**Python Library Usage:**
```python
import yt_dlp

def get_video_comments(video_url):
    ydl_opts = {
        'writecomments': True,
        'skip_download': True,
        'quiet': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        
        # Access comments
        if 'comments' in info:
            for comment in info['comments']:
                print(f"Author: {comment['author']}")
                print(f"Text: {comment['text']}")
                print(f"Likes: {comment['like_count']}")
                # Process comment

# Get all videos from Jordanian channel
def scrape_channel(channel_url):
    ydl_opts = {
        'extract_flat': 'in_playlist',
        'quiet': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist = ydl.extract_info(channel_url, download=False)
        
        for video in playlist['entries']:
            get_video_comments(video['url'])
```

**Realistic Yield:**
- 500-2,000 comments per hour (with rate limiting)
- 10,000-50,000 comments per day from multiple videos

#### Tool 2: youtube-comment-downloader
```bash
pip install youtube-comment-downloader

# Download comments
youtube-comment-downloader --url VIDEO_URL --output comments.txt

# Python usage
from youtube_comment_downloader import YoutubeCommentDownloader

downloader = YoutubeCommentDownloader()
comments = downloader.get_comments_from_url('VIDEO_URL')

for comment in comments:
    print(comment['text'])
```

### 6.4 Telegram Scraping

#### Tool: Telethon
**Installation:**
```bash
pip3 install telethon
```

**Setup:**
```python
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty

api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
phone = 'YOUR_PHONE_NUMBER'

client = TelegramClient('session_name', api_id, api_hash)
client.connect()

if not client.is_user_authorized():
    client.send_code_request(phone)
    client.sign_in(phone, input('Enter the code: '))
```

**Scraping Messages:**
```python
# Get messages from a channel
async def scrape_channel(channel_username, limit=1000):
    async for message in client.iter_messages(
        channel_username, 
        limit=limit
    ):
        if message.text:
            print(f"Date: {message.date}")
            print(f"Text: {message.text}")
            print(f"Views: {message.views}")
            
            # Check for Jordanian keywords
            if is_jordanian(message.text):
                save_message(message)

# Get comments on posts
async def scrape_comments(channel_username, message_id):
    async for comment in client.iter_messages(
        channel_username,
        reply_to=message_id
    ):
        print(f"Comment: {comment.text}")
```

**Realistic Yield:**
- 5,000-10,000 messages per day (with rate limiting)
- Comments are often more valuable than posts

**Important Notes:**
- Requires phone number verification
- Telegram may ban accounts for aggressive scraping
- Use with caution and respect rate limits
- Some channels are private/require membership

### 6.5 Reddit Scraping

#### Tool: PRAW (Python Reddit API Wrapper)
```bash
pip3 install praw
```

**Usage:**
```python
import praw

reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="JordanianHateSpeechResearch/1.0"
)

# Search r/Jordan
subreddit = reddit.subreddit("Jordan")

# Get hot posts
for post in subreddit.hot(limit=100):
    print(f"Title: {post.title}")
    print(f"Text: {post.selftext}")
    
    # Get comments
    post.comments.replace_more(limit=0)
    for comment in post.comments.list():
        if is_arabic(comment.body):
            print(f"Comment: {comment.body}")
```

**Realistic Yield:**
- 1,000-2,000 comments per day
- Lower volume but higher quality discussions

### 6.6 General Web Scraping Tools

#### Scrapy Framework
```python
import scrapy

class JordanianForumSpider(scrapy.Spider):
    name = "jordanian_forum"
    start_urls = ['https://forum.example.com']
    
    def parse(self, response):
        # Extract posts
        for post in response.css('div.post'):
            yield {
                'text': post.css('p.text::text').get(),
                'author': post.css('span.author::text').get(),
                'date': post.css('span.date::text').get()
            }
        
        # Follow pagination
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
```

### 6.7 Data Processing Pipeline

```python
class DataCollectionPipeline:
    """
    Unified pipeline for all data sources
    """
    
    def __init__(self):
        self.collected_data = []
    
    def collect_from_twitter(self, query, limit=10000):
        # Use twarc or snscrape
        pass
    
    def collect_from_facebook(self, pages, limit=5000):
        # Use facebook-scraper
        pass
    
    def collect_from_youtube(self, video_urls):
        # Use yt-dlp
        pass
    
    def collect_from_telegram(self, channels, limit=5000):
        # Use telethon
        pass
    
    def preprocess(self, data):
        """
        Clean and standardize data
        """
        for item in data:
            # Remove URLs
            item['text'] = re.sub(r'http\S+', '', item['text'])
            
            # Remove usernames
            item['text'] = re.sub(r'@\w+', '', item['text'])
            
            # Normalize Arabic text
            item['text'] = normalize_arabic(item['text'])
            
            # Detect Jordanian dialect
            item['is_jordanian'] = detect_jordanian(item['text'])
        
        return data
    
    def save_data(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
```

---

## 7. Legal & Ethical Considerations

### 7.1 Platform Terms of Service

**Twitter/X:**
- ✅ Official API: Allowed with proper credentials
- ⚠️ Scraping: Against ToS, risk of IP ban
- ✅ Academic Research Track: Recommended

**Facebook:**
- ❌ Scraping: Against ToS
- ✅ Crowdsourcing: Users can submit what they see
- ⚠️ Research: Contact Facebook Research for data access

**YouTube:**
- ⚠️ Comment scraping: Gray area
- ✅ yt-dlp: Generally tolerated for research
- ✅ Official API: Limited quota

**Telegram:**
- ⚠️ Scraping: Against ToS
- ✅ Public channels: More acceptable
- ✅ Own account: Can scrape messages you can see

**Recommendations:**
1. Prioritize official APIs where possible
2. If scraping, use respectful rate limiting
3. Never republish full datasets with user data
4. Anonymize user information in research
5. Obtain IRB approval for human subjects research

### 7.2 Privacy Protection

**Data Anonymization:**
```python
def anonymize_data(sample):
    """
    Remove personally identifiable information
    """
    # Remove usernames
    sample['text'] = re.sub(r'@\w+', '[USER]', sample['text'])
    
    # Remove URLs
    sample['text'] = re.sub(r'http\S+', '[URL]', sample['text'])
    
    # Remove or hash user IDs
    if 'user_id' in sample:
        sample['user_id'] = hash_user_id(sample['user_id'])
    
    # Remove location data (optional, depends on research needs)
    if 'location' in sample and not needed_for_research:
        del sample['location']
    
    # Keep only essential metadata
    return {
        'text': sample['text'],
        'label': sample.get('label'),
        'date': sample.get('date'),
        'source': sample.get('source')
        # Remove other fields
    }
```

**IRB Considerations:**
1. Public vs private data distinction
2. Consent requirements
3. Data storage and security
4. Participant compensation ethics
5. Risk assessment for vulnerable populations

### 7.3 Ethical Use Policy

**Dataset Usage Agreement:**
```
By accessing this dataset, users agree to:

1. NOT use the data to harass, threaten, or discriminate
2. NOT attempt to identify or contact individuals in the dataset
3. Use data ONLY for research purposes
4. Properly anonymize any derived datasets
5. Cite the dataset appropriately
6. Share derived datasets under similar terms
7. Report any ethical concerns to the maintainers
```

---

## 8. Realistic Collection Targets & Timeline

### 8.1 Monthly Collection Targets

**Month 1-2: Setup & Initial Collection**
- Twitter: 10,000-20,000 tweets
- Facebook: 5,000-10,000 comments
- YouTube: 3,000-5,000 comments
- Existing datasets: 5,000-15,000 samples
- **Total**: 23,000-50,000 samples

**Month 3-4: Scale Up**
- Twitter: 30,000-50,000 tweets
- Facebook: 15,000-20,000 comments
- YouTube: 5,000-10,000 comments
- Telegram: 5,000-10,000 messages
- Crowdsourced: 5,000-10,000 annotations
- **Total**: 60,000-100,000 samples

**Month 5-6: Refinement**
- Continue collection
- Focus on quality over quantity
- Expert annotation of controversial cases
- **Total**: 80,000-120,000 samples

### 8.2 Final Dataset Composition

**Realistic Final Dataset:**
- **Total samples**: 150,000-250,000
- **Hate speech**: 20,000-40,000 (10-15%)
- **Offensive but not hate**: 30,000-50,000 (15-25%)
- **Neutral/negative**: 100,000-160,000 (60-70%)

**Quality Distribution:**
- High confidence: 60%
- Medium confidence: 30%
- Low confidence: 10% (review by experts)

### 8.3 Resource Requirements

**Personnel:**
- 1-2 data engineers/scrapers
- 3-5 annotators (part-time)
- 1-2 domain experts (consultants)
- 1 project manager

**Infrastructure:**
- Server/Cloud: $100-300/month
- API costs: $100-5,000/month (depending on tier)
- Storage: $50-100/month
- Annotation platform: $50-200/month

**Budget Estimate:**
- Personnel: $10,000-25,000 (6 months, part-time)
- Infrastructure: $2,000-5,000 (6 months)
- Incentives: $2,000-5,000
- **Total**: $15,000-35,000 for 6-month project

---

## 9. Implementation Roadmap

### Phase 1: Week 1-4 - Setup & Testing
- [ ] Set up API credentials (Twitter, Reddit)
- [ ] Install and test scraping tools
- [ ] Download existing datasets
- [ ] Extract Jordanian subset from existing data
- [ ] Develop initial annotation guidelines
- [ ] Build basic crowdsourcing interface

### Phase 2: Week 5-8 - Initial Collection
- [ ] Begin systematic Twitter collection
- [ ] Start Facebook page monitoring
- [ ] Identify YouTube channels and videos
- [ ] Set up Telegram monitoring
- [ ] Recruit initial annotators (10-20)
- [ ] Pilot annotation process

### Phase 3: Week 9-12 - Scale Up
- [ ] Increase scraping volume
- [ ] Recruit more annotators (50-100)
- [ ] Implement quality control
- [ ] Expert review of controversial cases
- [ ] Refine annotation guidelines
- [ ] Mid-project evaluation

### Phase 4: Week 13-16 - Refinement
- [ ] Focus on quality improvement
- [ ] Address gaps in coverage
- [ ] Expert annotation of difficult cases
- [ ] Inter-annotator agreement analysis
- [ ] Dataset cleaning and validation

### Phase 5: Week 17-20 - Finalization
- [ ] Complete data collection
- [ ] Final annotation pass
- [ ] Dataset documentation
- [ ] Quality assurance checks
- [ ] Prepare dataset for release

### Phase 6: Week 21-24 - Release & Documentation
- [ ] Create dataset card
- [ ] Write data statement
- [ ] Ethical review
- [ ] Public release (with restrictions)
- [ ] Publish research paper

---

## 10. Specific Jordanian Accounts & Hashtags to Monitor

### 10.1 Twitter Accounts (Examples - Research Needed)

**News Media:**
- @AlGhadNews
- @AmmonNewsAr
- @AlraiMedia
- @SarayaNews
- @RoyaNews

**Political Figures:**
- Parliament members (research for specific handles)
- Government officials
- Political commentators

**Influencers:**
- Jordanian comedians
- Social critics
- Youth activists

**Note:** Manual research needed to identify specific accounts and verify their activity levels.

### 10.2 High-Value Hashtags

**Political Events:**
- Monitor trending hashtags during:
  - Elections
  - Parliamentary sessions
  - Political protests
  - Government announcements

**Social Issues:**
- Economic protests
- Refugee-related discussions
- Tribal conflicts
- Religious controversies

**Weekly Monitoring:**
```python
# Check Twitter trending topics for Jordan daily
# Identify new hashtags as they emerge
# Add to monitoring list if relevant
```

---

## 11. Conclusion & Recommendations

### Key Success Factors:

1. **Diversify Data Sources**: Don't rely on a single platform
2. **Quality Over Quantity**: Better to have 50,000 high-quality samples than 200,000 noisy ones
3. **Expert Involvement**: Crucial for cultural context and difficult cases
4. **Ethical Practices**: Protect users, follow ToS, obtain proper approvals
5. **Community Engagement**: Crowdsourcing can significantly boost dataset size
6. **Continuous Refinement**: Annotation guidelines should evolve with the project

### Recommended Starting Strategy:

1. **Week 1-2**: Extract Jordanian subset from existing datasets (5,000-15,000 samples)
2. **Week 3-4**: Set up Twitter API and begin systematic collection
3. **Week 5-8**: Expand to Facebook and YouTube, launch crowdsourcing
4. **Week 9-12**: Add Telegram and Reddit, focus on quality
5. **Week 13-16**: Expert annotation, dataset refinement

### Expected Outcomes:

- **Minimum viable dataset**: 50,000-100,000 samples (3-4 months)
- **Comprehensive dataset**: 150,000-250,000 samples (6 months)
- **Research-grade dataset**: 200,000-300,000 samples (8-12 months)

### Next Steps:

1. Obtain necessary API credentials
2. Set up data collection infrastructure
3. Recruit annotation team
4. Develop detailed annotation guidelines
5. Launch pilot collection phase
6. Iterate and improve based on initial results

---

## Appendices

### Appendix A: Python Scripts Repository

All scripts mentioned in this document should be version-controlled and available in a dedicated repository.

### Appendix B: Annotation Guidelines Template

Detailed guidelines for annotators, including:
- Definitions of hate speech categories
- Examples with explanations
- Edge cases and how to handle them
- Cultural context notes
- Jordanian dialect peculiarities

### Appendix C: Data Collection Log Template

Daily/weekly tracking of:
- Collection targets vs actual
- Quality metrics
- Issues encountered
- Solutions implemented

### Appendix D: Ethical Approval Documents

- IRB application template
- Consent forms for annotators
- Data usage agreement template

---

## Contact & Collaboration

For questions about this data collection plan or to discuss collaboration opportunities, please contact:

[Your Contact Information]
[Project Website]
[Email]

---

**Document Version:** 1.0
**Last Updated:** 2026-03-03
**Authors:** [Your Name]
**Status:** Draft for Review
