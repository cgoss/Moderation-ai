---
title: Comment Categorization
category: analysis
related:
  - ./README.md
  - ./summarization.md
  - ../standards-and-metrics.md
---

# Comment Categorization

## Overview

Comment categorization classifies comments by topic, theme, or purpose. This helps organize discussions, filter content, and understand what community members are discussing.

## Category Types

| Type | Description | Example Categories |
|------|-------------|-------------------|
| **Topic** | What the comment is about | Technology, Sports, Entertainment |
| **Intent** | Purpose of comment | Question, Feedback, Spam, Report |
| **Emotion** | Emotional tone | Happy, Angry, Sad, Neutral |
| **Engagement** | Level of engagement | High, Medium, Low |

## Categorizer Interface

```python
from moderation_ai.analysis import Categorizer

# Initialize with predefined categories
categorizer = Categorizer(categories=[
    "feedback",
    "question",
    "support",
    "spam"
])

# Categorize single comment
result = categorizer.analyze(comment)
print(f"Category: {result.primary_category}")
print(f"Confidence: {result.confidence}")

# Categorize batch
results = categorizer.batch_analyze(comments)
```

## Category Result

```python
{
    "comment_id": "123",
    "primary_category": "feedback",
    "all_categories": [
        {"category": "feedback", "confidence": 0.85},
        {"category": "support", "confidence": 0.15}
    ],
    "confidence": 0.85,
    "reasoning": "Comment provides positive feedback about content quality"
}
```

## Predefined Category Sets

### Intent Categories

```python
categorizer = Categorizer(categories=[
    "question",        # User asks question
    "feedback",        # User provides feedback
    "suggestion",     # User suggests improvement
    "report",          # User reports issue
    "spam",            # Spam or promotional
    "off_topic"        # Not related to post
])
```

### Topic Categories

```python
categorizer = Categorizer(categories=[
    "technical",       # Technical discussion
    "general",         # General discussion
    "feature_request", # Requests features
    "bug_report",      # Reports bugs
    "meta",            # Meta discussion
])
```

### Emotion Categories

```python
categorizer = Categorizer(categories=[
    "positive",        # Positive emotion
    "neutral",         # Neutral emotion
    "negative",        # Negative emotion
    "angry",          # Angry emotion
    "sad",            # Sad emotion
    "happy",           # Happy emotion
])
```

### Engagement Categories

```python
categorizer = Categorizer(categories=[
    "high_engagement", # Detailed, substantive
    "medium_engagement", # Moderate detail
    "low_engagement"   # Brief, low effort
])
```

## Usage Examples

### Example 1: Basic Categorization

```python
from moderation_ai.analysis import Categorizer

# Initialize categorizer
categorizer = Categorizer(categories=[
    "question",
    "feedback",
    "spam"
])

# Categorize comment
comment = Comment(
    id="123",
    text="Great post! Very informative.",
    platform="twitter"
)

result = categorizer.analyze(comment)
print(f"Category: {result.primary_category}")
print(f"Confidence: {result.confidence}")
# Output:
# Category: feedback
# Confidence: 0.92
```

### Example 2: Multi-Label Categorization

```python
categorizer = Categorizer(
    categories=["question", "feedback", "suggestion"],
    multi_label=True  # Allow multiple categories
)

result = categorizer.analyze(comment)
print(f"Categories: {result.all_categories}")
```

### Example 3: Custom Categories

```python
# Define custom categories
custom_categories = {
    "feature_request": {
        "keywords": ["feature", "add", "would like", "need"],
        "patterns": [r"we need (a|an|the)"]
    },
    "bug_report": {
        "keywords": ["bug", "issue", "error", "problem", "not working"],
        "patterns": [r"(doesn't|does not) work"]
    },
    "praise": {
        "keywords": ["great", "awesome", "love", "excellent"],
        "patterns": [r"great (post|content|job)"]
    }
}

categorizer = Categorizer.from_dict(custom_categories)
result = categorizer.analyze(comment)
```

### Example 4: Category Filtering

```python
categorizer = Categorizer(categories=[
    "question",
    "feedback",
    "spam",
    "off_topic"
])

comments = await platform.fetch_comments(post_id)
results = categorizer.batch_analyze(comments)

# Filter by category
feedback_comments = [
    c for c, r in zip(comments, results)
    if r.primary_category == "feedback"
]

# Filter out spam
legitimate_comments = [
    c for c, r in zip(comments, results)
    if r.primary_category != "spam"
]
```

### Example 5: Category Statistics

```python
comments = await platform.fetch_comments(post_id)
results = categorizer.batch_analyze(comments)

# Count by category
category_counts = {}
for result in results:
    category = result.primary_category
    category_counts[category] = category_counts.get(category, 0) + 1

print("Category distribution:")
for category, count in sorted(category_counts.items()):
    percentage = (count / len(results)) * 100
    print(f"  {category}: {count} ({percentage:.1f}%)")
```

### Example 6: Hierarchical Categorization

```python
# Define hierarchical categories
hierarchy = {
    "support": {
        "technical_issue": ["bug", "error", "problem"],
        "how_to": ["how", "can i", "help with"]
    },
    "feedback": {
        "positive": ["great", "love", "excellent"],
        "negative": ["disappointed", "not good", "issue"]
    }
}

categorizer = Categorizer(hierarchy=hierarchy)
result = categorizer.analyze(comment)

print(f"Primary: {result.primary_category}")
print(f"Subcategory: {result.subcategory}")
```

## Categorization Techniques

### Keyword-Based

```python
categorizer = Categorizer(
    method="keyword",
    categories={
        "feedback": ["great", "good", "helpful"],
        "question": ["how", "what", "why"],
        "spam": ["buy", "click", "visit"]
    }
)
```

### Pattern-Based

```python
import re

categorizer = Categorizer(
    method="pattern",
    categories={
        "question": [r"how (do|can|to)", r"what (is|are)"],
        "feedback": [r"(great|good|bad) (post|content)"],
        "suggestion": [r"(should|could|would) (you|we)"]
    }
)
```

### ML-Based

```python
categorizer = Categorizer(
    method="ml",
    model="bert-base-uncased",
    categories=["question", "feedback", "spam", "off_topic"]
)
```

### Hybrid Approach

```python
categorizer = Categorizer(
    method="hybrid",
    keyword_weight=0.3,
    pattern_weight=0.3,
    ml_weight=0.4,
    categories=["question", "feedback", "spam"]
)
```

## Configuration

### Confidence Thresholds

```python
categorizer = Categorizer(
    categories=["question", "feedback", "spam"],
    min_confidence=0.7  # Minimum confidence for category
)

result = categorizer.analyze(comment)
if result.confidence < categorizer.min_confidence:
    print("Low confidence - manual review needed")
```

### Multi-Label Support

```python
categorizer = Categorizer(
    categories=["question", "feedback", "suggestion"],
    multi_label=True,
    min_label_confidence=0.6  # Minimum for each label
)
```

### Category Priorities

```python
categorizer = Categorizer(
    categories=["spam", "question", "feedback"],
    priorities={
        "spam": 10,      # Highest priority
        "question": 5,
        "feedback": 3
    }
)

# Spam will be selected even if confidence is slightly lower
```

## Best Practices

### 1. Define Clear Categories

```python
# Good - distinct categories
categories = ["question", "feedback", "spam", "off_topic"]

# Bad - overlapping categories
categories = ["question", "inquiry", "help_request", "ask"]
```

### 2. Provide Training Examples

```python
training_data = {
    "question": [
        "How do I do this?",
        "What's the best approach?",
        "Can someone help me?"
    ],
    "feedback": [
        "Great post!",
        "Very helpful information",
        "Thanks for sharing"
    ]
}

categorizer = Categorizer(
    categories=training_data.keys(),
    training_data=training_data
)
```

### 3. Use Appropriate Method

```python
# For simple categories - keyword
categorizer = Categorizer(method="keyword", ...)

# For complex categories - ML
categorizer = Categorizer(method="ml", ...)

# For best results - hybrid
categorizer = Categorizer(method="hybrid", ...)
```

### 4. Validate Categories

```python
result = categorizer.analyze(comment)

# Check confidence
if result.confidence < 0.7:
    # Flag for manual review
    result.flagged = True
```

### 5. Update Categories Regularly

```python
# Periodically review category performance
# Add new categories as needed
# Remove underperforming categories
```

## Use Cases

### Content Moderation

Automatically flag inappropriate categories:

```python
async def moderate_by_category(comment):
    result = categorizer.analyze(comment)
    
    if result.primary_category == "spam":
        return "remove"
    elif result.primary_category == "off_topic":
        return "flag"
    else:
        return "approve"
```

### Customer Support

Route comments to appropriate teams:

```python
async def route_comment(comment):
    result = categorizer.analyze(comment)
    
    routing = {
        "technical_issue": "engineering",
        "billing": "finance",
        "feature_request": "product"
    }
    
    return routing.get(result.primary_category, "general")
```

### Analytics

Analyze discussion themes:

```python
async def analyze_themes(comments):
    results = categorizer.batch_analyze(comments)
    
    themes = {}
    for result in results:
        category = result.primary_category
        themes[category] = themes.get(category, 0) + 1
    
    return themes
```

## Related Documentation

- **Summarization**: `./summarization.md` - Topic summaries
- **Sentiment Analysis**: `./sentiment-analysis.md` - Emotional analysis
- **FAQ Extraction**: `./faq-extraction.md` - Question identification

---

**Last Updated**: January 2024
**Status**: Phase 1 - Documentation Phase
