---
title: Comment Summarization
category: analysis
related:
  - ./README.md
  - ./categorization.md
  - ../standards-and-metrics.md
---

# Comment Summarization

## Overview

Comment summarization generates concise summaries of comment discussions, helping content creators quickly understand feedback, identify key themes, and reduce information overload.

## Summarization Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Extractive** | Selects most important sentences | Quick overview, direct quotes |
| **Abstractive** | Generates new summary text | Natural language, cohesive |
| **Key Points** | Lists main discussion points | Bullet-style summary |
| **Opinion Summary** | Summarizes opinions by sentiment | Understand audience reaction |

## Summarizer Interface

```python
from moderation_ai.analysis import Summarizer

# Initialize summarizer
summarizer = Summarizer()

# Summarize single comment
summary = summarizer.summarize(comment)

# Summarize comment thread
summary = summarizer.summarize_thread(comments)

# Extract key points
points = summarizer.extract_key_points(comments)

# Generate opinion summary
opinions = summarizer.summarize_opinions(comments)
```

## Summarization Results

### Extractive Summary

```python
{
    "summary": "Great post! The tips on time management are really helpful. Would love to see more content like this.",
    "sentences": [
        "Great post!",
        "The tips on time management are really helpful.",
        "Would love to see more content like this."
    ],
    "confidence": 0.85
}
```

### Abstractive Summary

```python
{
    "summary": "Commenters praised the post for its time management tips and expressed interest in similar future content.",
    "style": "abstractive",
    "confidence": 0.78
}
```

### Key Points

```python
{
    "points": [
        "Time management tips were helpful",
        "Appreciation for the post content",
        "Request for similar future content"
    ],
    "confidence": 0.82
}
```

### Opinion Summary

```python
{
    "opinions": {
        "positive": [
            "Helpful time management tips",
            "Great post structure",
            "Clear explanations"
        ],
        "neutral": [
            "Request for more details",
            "Questions about implementation"
        ],
        "negative": [
            "Suggestions for improvement",
            "Minor critiques"
        ]
    },
    "overall_sentiment": "positive"
}
```

## Usage Examples

### Example 1: Single Comment Summary

```python
from moderation_ai.analysis import Summarizer

summarizer = Summarizer()

comment = Comment(
    id="123",
    text="This is an excellent post about productivity. The section on prioritizing tasks was particularly useful for me. I've already started implementing the techniques mentioned and they're working great!",
    platform="twitter"
)

# Generate summary
summary = summarizer.summarize(comment)
print(summary["summary"])
# Output: "Commenter found the post excellent, especially the task prioritization section, and has successfully implemented the techniques."
```

### Example 2: Thread Summary

```python
from moderation_ai.analysis import Summarizer

summarizer = Summarizer()

# Fetch comments
comments = await platform.fetch_comments(post_id)

# Summarize entire thread
summary = summarizer.summarize_thread(comments)
print(f"Summary: {summary['summary']}")
print(f"Total comments: {summary['comment_count']}")
print(f"Key themes: {summary['themes']}")
```

### Example 3: Key Points Extraction

```python
from moderation_ai.analysis import Summarizer

summarizer = Summarizer()

comments = await platform.fetch_comments(post_id)

# Extract key points
points = summarizer.extract_key_points(comments)

for i, point in enumerate(points["points"], 1):
    print(f"{i}. {point}")
```

### Example 4: Opinion Summary by Sentiment

```python
from moderation_ai.analysis import Summarizer

summarizer = Summarizer()

comments = await platform.fetch_comments(post_id)

# Summarize opinions
opinions = summarizer.summarize_opinions(comments)

print("Positive feedback:")
for opinion in opinions["opinions"]["positive"][:3]:
    print(f"  - {opinion}")

print("\nNegative feedback:")
for opinion in opinions["opinions"]["negative"][:3]:
    print(f"  - {opinion}")
```

### Example 5: Topic-Based Summary

```python
from moderation_ai.analysis import Summarizer, Categorizer

summarizer = Summarizer()
categorizer = Categorizer()

comments = await platform.fetch_comments(post_id)

# Categorize comments
categories = categorizer.batch_analyze(comments)

# Summarize by category
for category in set(c.primary_category for c in categories):
    category_comments = [
        c for c, cat in zip(comments, categories)
        if cat.primary_category == category
    ]
    
    summary = summarizer.summarize_thread(category_comments)
    print(f"\n{category.upper()}:")
    print(f"  {summary['summary']}")
```

## Summarization Techniques

### Extractive Summarization

Selects most important sentences based on:
- Sentence importance score
- Keyword frequency
- Position in comment thread
- User engagement (likes, replies)

```python
summarizer = Summarizer(method="extractive")
summary = summarizer.summarize_thread(comments)
```

### Abstractive Summarization

Generates new summary text using:
- Natural language generation
- Key information extraction
- Coherence and flow
- Original text rewriting

```python
summarizer = Summarizer(method="abstractive")
summary = summarizer.summarize_thread(comments)
```

### Key Point Extraction

Identifies main discussion points:
- Frequent topics
- Unique ideas
- Consensus points
- Controversial issues

```python
summarizer = Summarizer(method="key_points")
points = summarizer.extract_key_points(comments)
```

### Opinion Analysis

Summarizes opinions by sentiment:
- Positive feedback themes
- Negative feedback themes
- Neutral observations
- Overall sentiment

```python
summarizer = Summarizer(method="opinion")
opinions = summarizer.summarize_opinions(comments)
```

## Configuration

### Length Control

```python
summarizer = Summarizer(
    max_length=200,  # Maximum summary length
    min_length=50    # Minimum summary length
)
```

### Focus Control

```python
summarizer = Summarizer(
    focus="questions"  # Focus on questions in comments
)

# Or focus on specific topics
summarizer = Summarizer(
    focus_topics=["feedback", "suggestions"]
)
```

### Confidence Threshold

```python
summarizer = Summarizer(
    min_confidence=0.7  # Only high-confidence results
)
```

## Best Practices

### 1. Choose Right Summarization Type

```python
# For quick overview - extractive
summarizer = Summarizer(method="extractive")

# For natural reading - abstractive
summarizer = Summarizer(method="abstractive")

# For understanding themes - key points
summarizer = Summarizer(method="key_points")
```

### 2. Consider Thread Size

```python
# For small threads (< 10 comments)
summary = summarizer.summarize_thread(comments)

# For large threads (> 100 comments)
# Summarize in chunks or sample first
top_comments = sorted(comments, key=lambda c: c.engagement)[:50]
summary = summarizer.summarize_thread(top_comments)
```

### 3. Combine with Sentiment Analysis

```python
from moderation_ai.analysis import Summarizer, SentimentAnalyzer

summarizer = Summarizer()
sentiment = SentimentAnalyzer()

summary = summarizer.summarize_thread(comments)
overall_sentiment = sentiment.analyze_thread(comments)

print(f"Summary: {summary['summary']}")
print(f"Overall sentiment: {overall_sentiment.sentiment}")
```

### 4. Validate Summaries

```python
summary = summarizer.summarize_thread(comments)

# Check confidence
if summary["confidence"] < 0.7:
    print("Low confidence summary - manual review recommended")
```

## Use Cases

### Content Creator Dashboard

Provide creators with quick feedback overview:

```python
async def get_feedback_summary(post_id):
    comments = await platform.fetch_comments(post_id)
    
    summary = summarizer.summarize_thread(comments)
    opinions = summarizer.summarize_opinions(comments)
    
    return {
        "summary": summary["summary"],
        "positive_feedback": opinions["opinions"]["positive"],
        "negative_feedback": opinions["opinions"]["negative"],
        "suggestions": summary["points"]
    }
```

### Community Management

Identify key discussion themes:

```python
async def identify_themes(post_id):
    comments = await platform.fetch_comments(post_id)
    
    points = summarizer.extract_key_points(comments)
    
    return {
        "themes": points["points"],
        "confidence": points["confidence"]
    }
```

### Content Ideation

Use summaries to generate follow-up content:

```python
async def content_opportunities(post_id):
    comments = await platform.fetch_comments(post_id)
    
    opinions = summarizer.summarize_opinions(comments)
    
    # Identify requested topics
    requested_topics = [
        point for point in points["points"]
        if "request" in point.lower() or "would like" in point.lower()
    ]
    
    return requested_topics
```

## Performance Considerations

| Operation | Time | Notes |
|-----------|------|-------|
| Single comment | < 100ms | Fast |
| Thread (10 comments) | < 500ms | Acceptable |
| Thread (100 comments) | < 2s | Longer threads |
| Thread (1000 comments) | < 10s | Consider sampling |

## Related Documentation

- **Categorization**: `./categorization.md` - Topic classification
- **Sentiment Analysis**: `./sentiment-analysis.md` - Opinion analysis
- **Content Ideation**: `./content-ideation.md` - Content suggestions

---

**Last Updated**: January 2024
**Status**: Phase 1 - Documentation Phase
