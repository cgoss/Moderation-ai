---
title: Sentiment Analysis
category: analysis
related:
  - ./README.md
  - ./summarization.md
  - ../standards-and-metrics.md
---

# Sentiment Analysis

## Overview

Sentiment analysis detects the emotional tone of comments, helping content creators understand audience reactions, identify negative feedback, and track community sentiment over time.

## Sentiment Types

| Type | Range | Description |
|------|-------|-------------|
| **Positive** | 0.5 to 1.0 | Happy, satisfied, enthusiastic |
| **Neutral** | -0.5 to 0.5 | Objective, informational, balanced |
| **Negative** | -1.0 to -0.5 | Unhappy, disappointed, frustrated |

## Emotion Categories

| Emotion | Description | Example Phrases |
|----------|-------------|----------------|
| **Joy** | Happiness, excitement | "Love this!", "So happy!" |
| **Anger** | Frustration, annoyance | "This is terrible!", "Frustrated!" |
| **Sadness** | Disappointment, sorrow | "So disappointed", "Sad to see..." |
| **Fear** | Concern, worry | "Worried about...", "Concerning..." |
| **Surprise** | Shock, amazement | "Wow!", "Can't believe!" |
| **Disgust** | Dislike, aversion | "This is gross", "Disappointed" |

## Sentiment Analyzer Interface

```python
from moderation_ai.analysis import SentimentAnalyzer

# Initialize analyzer
analyzer = SentimentAnalyzer()

# Analyze single comment
result = analyzer.analyze(comment)
print(f"Sentiment: {result.sentiment}")
print(f"Score: {result.score}")
print(f"Emotions: {result.emotions}")

# Batch analyze
results = analyzer.batch_analyze(comments)

# Analyze thread
thread_result = analyzer.analyze_thread(comments)
```

## Sentiment Result

```python
{
    "comment_id": "123",
    "sentiment": "positive",
    "score": 0.85,
    "confidence": 0.92,
    "emotions": {
        "joy": 0.75,
        "surprise": 0.20,
        "anger": 0.05
    },
    "reasoning": "Comment expresses strong positive sentiment with enthusiasm"
}
```

## Usage Examples

### Example 1: Basic Sentiment Analysis

```python
from moderation_ai.analysis import SentimentAnalyzer

analyzer = SentimentAnalyzer()

comment = Comment(
    id="123",
    text="This is absolutely amazing! I love the content!",
    platform="twitter"
)

result = analyzer.analyze(comment)
print(f"Sentiment: {result.sentiment}")
print(f"Score: {result.score}")
print(f"Confidence: {result.confidence}")
# Output:
# Sentiment: positive
# Score: 0.92
# Confidence: 0.95
```

### Example 2: Batch Analysis

```python
analyzer = SentimentAnalyzer()

comments = await platform.fetch_comments(post_id)
results = analyzer.batch_analyze(comments)

# Process results
for result in results:
    print(f"{result.comment_id}: {result.sentiment} ({result.score})")
```

### Example 3: Thread Sentiment

```python
analyzer = SentimentAnalyzer()

comments = await platform.fetch_comments(post_id)

# Analyze entire thread
thread_result = analyzer.analyze_thread(comments)

print(f"Overall sentiment: {thread_result.sentiment}")
print(f"Average score: {thread_result.average_score}")
print(f"Positive: {thread_result.positive_count}")
print(f"Negative: {thread_result.negative_count}")
print(f"Neutral: {thread_result.neutral_count}")
```

### Example 4: Emotion Detection

```python
analyzer = SentimentAnalyzer()

comment = Comment(
    id="123",
    text="I'm so frustrated! This doesn't work as expected.",
    platform="reddit"
)

result = analyzer.analyze(comment)

print("Emotions:")
for emotion, score in result.emotions.items():
    print(f"  {emotion}: {score:.2f}")

# Output:
# Emotions:
#   anger: 0.65
#   sadness: 0.20
#   fear: 0.10
#   surprise: 0.05
```

### Example 5: Sentiment Over Time

```python
analyzer = SentimentAnalyzer()

# Track sentiment for multiple posts
posts = ["post1", "post2", "post3"]
sentiment_over_time = []

for post_id in posts:
    comments = await platform.fetch_comments(post_id)
    result = analyzer.analyze_thread(comments)
    
    sentiment_over_time.append({
        "post_id": post_id,
        "sentiment": result.sentiment,
        "score": result.average_score,
        "timestamp": datetime.now()
    })

# Analyze trend
sentiment_scores = [s["score"] for s in sentiment_over_time]
if sentiment_scores[-1] > sentiment_scores[0]:
    print("Sentiment improving over time")
else:
    print("Sentiment declining over time")
```

### Example 6: Comment Filtering by Sentiment

```python
analyzer = SentimentAnalyzer()

comments = await platform.fetch_comments(post_id)
results = analyzer.batch_analyze(comments)

# Filter by sentiment
positive_comments = [
    c for c, r in zip(comments, results)
    if r.sentiment == "positive"
]

negative_comments = [
    c for c, r in zip(comments, results)
    if r.sentiment == "negative"
]

print(f"Positive comments: {len(positive_comments)}")
print(f"Negative comments: {len(negative_comments)}")
```

## Sentiment Analysis Techniques

### Lexicon-Based

Uses sentiment dictionaries:

```python
analyzer = SentimentAnalyzer(method="lexicon")

result = analyzer.analyze(comment)
```

### Machine Learning

Uses trained models:

```python
analyzer = SentimentAnalyzer(
    method="ml",
    model="bert-base-uncased-finetuned-sst-2"
)

result = analyzer.analyze(comment)
```

### Hybrid Approach

Combines multiple methods:

```python
analyzer = SentimentAnalyzer(
    method="hybrid",
    lexicon_weight=0.3,
    ml_weight=0.7
)

result = analyzer.analyze(comment)
```

## Configuration

### Sentiment Thresholds

```python
analyzer = SentimentAnalyzer(
    positive_threshold=0.5,
    negative_threshold=-0.5
)
```

### Emotion Detection

```python
analyzer = SentimentAnalyzer(
    detect_emotions=True,
    emotion_model="goemotions"
)
```

### Confidence Threshold

```python
analyzer = SentimentAnalyzer(
    min_confidence=0.7
)

result = analyzer.analyze(comment)
if result.confidence < analyzer.min_confidence:
    print("Low confidence - manual review")
```

## Use Cases

### Content Performance

Measure audience reaction:

```python
async def measure_performance(post_id):
    comments = await platform.fetch_comments(post_id)
    result = analyzer.analyze_thread(comments)
    
    return {
        "overall_sentiment": result.sentiment,
        "positive_percentage": result.positive_percentage,
        "negative_percentage": result.negative_percentage
    }
```

### Issue Detection

Identify negative feedback:

```python
async def detect_issues(comments):
    results = analyzer.batch_analyze(comments)
    
    issues = [
        c for c, r in zip(comments, results)
        if r.sentiment == "negative" and r.confidence > 0.8
    ]
    
    return issues
```

### Community Health

Track community sentiment trends:

```python
async def community_health(comments):
    result = analyzer.analyze_thread(comments)
    
    health_score = (
        result.positive_count / len(comments) * 100
    )
    
    if health_score > 70:
        return "healthy"
    elif health_score > 40:
        return "moderate"
    else:
        return "concerning"
```

### Response Prioritization

Prioritize comments based on sentiment:

```python
async def prioritize_responses(comments):
    results = analyzer.batch_analyze(comments)
    
    # Prioritize negative comments
    prioritized = sorted(
        zip(comments, results),
        key=lambda x: x[1].score
    )
    
    return prioritized
```

## Best Practices

### 1. Choose Appropriate Method

```python
# For quick results - lexicon
analyzer = SentimentAnalyzer(method="lexicon")

# For accuracy - ML
analyzer = SentimentAnalyzer(method="ml")

# For best results - hybrid
analyzer = SentimentAnalyzer(method="hybrid")
```

### 2. Consider Platform Context

```python
# Different platforms have different sentiment baselines
twitter_analyzer = SentimentAnalyzer(
    baseline=0.1,  # Twitter tends to be more negative
)

reddit_analyzer = SentimentAnalyzer(
    baseline=0.0
)
```

### 3. Validate Confidence

```python
result = analyzer.analyze(comment)

if result.confidence < 0.7:
    print("Low confidence - review manually")
```

### 4. Analyze in Context

```python
# Analyze thread, not just individual comments
thread_result = analyzer.analyze_thread(comments)

# This provides better overall picture
```

### 5. Track Over Time

```python
# Store sentiment history
# Identify trends and patterns
# Take action on declining sentiment
```

## Related Documentation

- **Summarization**: `./summarization.md` - Content summaries
- **Categorization**: `./categorization.md` - Topic classification
- **Abuse Detection**: `./abuse-detection.md` - Harmful content

---

**Last Updated**: January 2024
**Status**: Phase 1 - Documentation Phase
