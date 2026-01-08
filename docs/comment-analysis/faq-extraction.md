---
title: FAQ Extraction
category: analysis
related:
  - ./README.md
  - ./categorization.md
  - ./content-ideation.md
---

# FAQ Extraction

## Overview

FAQ extraction identifies frequently asked questions from comment discussions, helping content creators understand common concerns, answer recurring questions, and improve content accordingly.

## FAQ Types

| Type | Description | Example |
|------|-------------|---------|
| **Direct Question** | Explicit question | "How do I do this?" |
| **Implicit Question** | Question phrased as statement | "I'm not sure how to..." |
| **Help Request** | Request for assistance | "Can someone help me with...?" |
| **Clarification** | Request for more info | "Could you explain more about...?" |

## FAQ Extractor Interface

```python
from moderation_ai.analysis import FAQExtractor

# Initialize extractor
extractor = FAQExtractor()

# Extract FAQs from comments
faqs = extractor.extract(comments)

# Extract by frequency
top_faqs = extractor.extract_top_n(comments, n=10)

# Extract by category
category_faqs = extractor.extract_by_category(comments, category="technical")
```

## FAQ Result

```python
{
    "question": "How do I implement this in Python?",
    "frequency": 15,
    "percentage": 5.2,
    "similar_questions": [
        "Can you show Python code?",
        "Python implementation please?",
        "How to do this in Python?"
    ],
    "answered": True,
    "answer_quality": 0.75
}
```

## Usage Examples

### Example 1: Basic FAQ Extraction

```python
from moderation_ai.analysis import FAQExtractor

extractor = FAQExtractor()

comments = await platform.fetch_comments(post_id)

# Extract FAQs
faqs = extractor.extract(comments)

print(f"Found {len(faqs)} unique questions")
for faq in faqs[:10]:
    print(f"\n{faq.question}")
    print(f"  Frequency: {faq.frequency}")
    print(f"  Similar: {len(faq.similar_questions)}")
```

### Example 2: Top N FAQs

```python
extractor = FAQExtractor()

comments = await platform.fetch_comments(post_id)

# Get top 10 most frequent questions
top_faqs = extractor.extract_top_n(comments, n=10)

print("Top 10 FAQs:")
for i, faq in enumerate(top_faqs, 1):
    print(f"{i}. {faq.question} ({faq.frequency}x)")
```

### Example 3: FAQ Clustering

```python
extractor = FAQExtractor()

comments = await platform.fetch_comments(post_id)

# Cluster similar questions
faqs = extractor.extract(
    comments,
    cluster_similar=True,
    similarity_threshold=0.8
)

print(f"Found {len(faqs)} FAQ clusters")
for faq in faqs:
    print(f"\n{faq.question}")
    print(f"  Similar questions: {len(faq.similar_questions)}")
```

### Example 4: FAQ by Category

```python
extractor = FAQExtractor()
categorizer = Categorizer(categories=[
    "technical",
    "general",
    "content"
])

comments = await platform.fetch_comments(post_id)

# Categorize comments
categories = categorizer.batch_analyze(comments)

# Extract FAQs by category
for category in ["technical", "general", "content"]:
    category_comments = [
        c for c, cat in zip(comments, categories)
        if cat.primary_category == category
    ]
    
    faqs = extractor.extract_top_n(category_comments, n=5)
    
    print(f"\n{category.upper()} FAQs:")
    for i, faq in enumerate(faqs, 1):
        print(f"  {i}. {faq.question}")
```

### Example 5: Answered vs Unanswered

```python
extractor = FAQExtractor()

comments = await platform.fetch_comments(post_id)

# Extract FAQs with answer status
faqs = extractor.extract(
    comments,
    track_answers=True
)

answered = [f for f in faqs if f.answered]
unanswered = [f for f in faqs if not f.answered]

print(f"Answered: {len(answered)}")
print(f"Unanswered: {len(unanswered)}")

print("\nTop unanswered questions:")
for faq in unanswered[:5]:
    print(f"  - {faq.question}")
```

### Example 6: FAQ Trend Analysis

```python
extractor = FAQExtractor()

# Track FAQs over time
posts = ["post1", "post2", "post3"]
faq_timeline = []

for post_id in posts:
    comments = await platform.fetch_comments(post_id)
    faqs = extractor.extract(comments)
    
    faq_timeline.append({
        "post_id": post_id,
        "faqs": faqs,
        "timestamp": datetime.now()
    })

# Identify trending questions
trending = extractor.find_trending(faq_timeline)

print("Trending questions:")
for faq in trending[:5]:
    print(f"  - {faq.question}")
    print(f"    Growth: {faq.growth}%")
```

## Question Detection Techniques

### Keyword-Based

```python
extractor = FAQExtractor(
    method="keyword",
    question_words=[
        "how", "what", "why", "when", "where",
        "can", "could", "would", "will", "is",
        "are", "do", "does"
    ]
)
```

### Pattern-Based

```python
extractor = FAQExtractor(
    method="pattern",
    question_patterns=[
        r"how (do|can|to)",
        r"what (is|are)",
        r"(can|could) (you|someone)",
        r"help (me|with)"
    ]
)
```

### ML-Based

```python
extractor = FAQExtractor(
    method="ml",
    model="bert-question-detection"
)
```

### Hybrid Approach

```python
extractor = FAQExtractor(
    method="hybrid",
    keyword_weight=0.3,
    pattern_weight=0.3,
    ml_weight=0.4
)
```

## Configuration

### Frequency Threshold

```python
extractor = FAQExtractor(
    min_frequency=5,  # Minimum times asked
    min_percentage=1.0  # Minimum percentage of comments
)
```

### Clustering

```python
extractor = FAQExtractor(
    cluster_similar=True,
    similarity_threshold=0.8,  # Jaccard similarity
    clustering_method="jaccard"
)
```

### Answer Tracking

```python
extractor = FAQExtractor(
    track_answers=True,
    answer_quality_threshold=0.7,
    min_answer_length=50
)
```

## Best Practices

### 1. Set Appropriate Thresholds

```python
# For large communities
extractor = FAQExtractor(min_frequency=10)

# For smaller communities
extractor = FAQExtractor(min_frequency=2)
```

### 2. Cluster Similar Questions

```python
extractor = FAQExtractor(
    cluster_similar=True,
    similarity_threshold=0.8
)
```

### 3. Track Answer Status

```python
extractor = FAQExtractor(track_answers=True)

# This helps identify content gaps
```

### 4. Analyze Over Time

```python
# Track FAQ trends
# Identify emerging questions
# Address trending topics
```

### 5. Combine with Categorization

```python
# Categorize FAQs
# Understand topic distribution
# Prioritize by category importance
```

## Use Cases

### Content Planning

Use FAQs to guide future content:

```python
async def content_plan_from_faqs(post_id):
    comments = await platform.fetch_comments(post_id)
    faqs = extractor.extract(comments)
    
    # Identify content gaps
    unanswered = [f for f in faqs if not f.answered]
    
    # Prioritize by frequency
    priority_content = sorted(
        unanswered,
        key=lambda f: f.frequency,
        reverse=True
    )
    
    return priority_content
```

### FAQ Section Generation

Generate FAQ documentation:

```python
async def generate_faq_section(post_id):
    comments = await platform.fetch_comments(post_id)
    faqs = extractor.extract_top_n(comments, n=10)
    
    faq_section = {
        "title": "Frequently Asked Questions",
        "questions": []
    }
    
    for faq in faqs:
        faq_section["questions"].append({
            "question": faq.question,
            "answer": faq.best_answer if faq.answered else None,
            "frequency": faq.frequency
        })
    
    return faq_section
```

### Community Support

Identify community knowledge gaps:

```python
async def support_gaps(comments):
    faqs = extractor.extract(comments)
    
    unanswered = [f for f in faqs if not f.answered]
    high_priority = [
        f for f in unanswered
        if f.frequency > 10
    ]
    
    return {
        "total_faqs": len(faqs),
        "unanswered": len(unanswered),
        "high_priority_gaps": high_priority
    }
```

## Related Documentation

- **Categorization**: `./categorization.md` - Topic classification
- **Content Ideation**: `./content-ideation.md` - Content suggestions
- **Summarization**: `./summarization.md` - Discussion summaries

---

**Last Updated**: January 2024
**Status**: Phase 1 - Documentation Phase
