---
title: Comment Analysis Framework
category: core
related:
  - ../standards-and-metrics.md
  - ../ARCHITECTURE.md
  - ./summarization.md
  - ./categorization.md
---

# Comment Analysis Framework

## Overview

The Comment Analysis Framework provides a comprehensive set of tools for analyzing social media comments across multiple dimensions. This includes summarization, categorization, sentiment analysis, FAQ extraction, content ideation, community metrics, and abuse detection.

## Analysis Architecture

```
Comment Input
    ↓
Preprocessing (cleaning, normalization)
    ↓
┌─────────────────────────────────────┐
│     Analysis Modules                │
│  ┌─────────────┬────────────────┐  │
│  │Sentiment   │Categorization  │  │
│  │Analysis    │               │  │
│  ├─────────────┼────────────────┤  │
│  │Summarizer  │FAQ Extractor  │  │
│  │            │               │  │
│  ├─────────────┼────────────────┤  │
│  │Content     │Community      │  │
│  │Ideation    │Metrics        │  │
│  │            │               │  │
│  ├─────────────┼────────────────┤  │
│  │Abuse       │               │  │
│  │Detector    │               │  │
│  └─────────────┴────────────────┘  │
└─────────────────────────────────────┘
    ↓
Standards Engine
    ↓
Moderation Decision
```

## Available Analysis Types

| Analysis Type | Description | Output |
|---------------|-------------|--------|
| **Summarization** | Generate concise comment summaries | Summary text |
| **Categorization** | Classify comments by topic | Topic tags |
| **Sentiment Analysis** | Detect emotional tone | Sentiment score |
| **FAQ Extraction** | Identify frequently asked questions | FAQ list |
| **Content Ideation** | Suggest content ideas | Content suggestions |
| **Community Metrics** | Analyze engagement patterns | Metrics report |
| **Abuse Detection** | Identify harmful content | Abuse flags |

## Common Analyzer Interface

All analysis modules implement a common interface:

```python
from moderation_ai.analysis import BaseAnalyzer

class MyAnalyzer(BaseAnalyzer):
    def analyze(self, comment: Comment) -> AnalysisResult:
        # Single comment analysis
        pass

    def batch_analyze(self, comments: List[Comment]) -> List[AnalysisResult]:
        # Batch analysis
        pass
```

## Data Models

### Comment

```python
class Comment:
    id: str
    post_id: str
    author_id: str
    author_username: str
    text: str
    created_at: datetime
    platform: str
    metadata: Dict[str, Any]
```

### AnalysisResult

```python
class AnalysisResult:
    comment_id: str
    analysis_type: str
    result: Any  # Type-specific result
    confidence_score: float
    metadata: Dict[str, Any]
```

### SentimentResult

```python
class SentimentResult:
    sentiment: str  # positive, negative, neutral
    score: float  # -1.0 to 1.0
    emotions: Dict[str, float]  # joy, anger, fear, sadness, etc.
```

### CategoryResult

```python
class CategoryResult:
    categories: List[str]
    primary_category: str
    confidence: float
```

## Quick Start Examples

### Example 1: Single Comment Analysis

```python
from moderation_ai.analysis import SentimentAnalyzer

# Initialize analyzer
analyzer = SentimentAnalyzer()

# Analyze single comment
comment = Comment(
    id="123",
    text="Great post! Really helpful.",
    platform="twitter"
)

result = analyzer.analyze(comment)
print(f"Sentiment: {result.sentiment}")
print(f"Score: {result.score}")
# Output:
# Sentiment: positive
# Score: 0.85
```

### Example 2: Batch Analysis

```python
from moderation_ai.analysis import Categorizer

# Initialize analyzer
analyzer = Categorizer()

# Fetch comments
comments = await platform.fetch_comments(post_id)

# Batch analyze
results = analyzer.batch_analyze(comments)

# Process results
for result in results:
    print(f"{result.comment_id}: {result.primary_category}")
```

### Example 3: Multi-Dimension Analysis

```python
from moderation_ai.analysis import (
    SentimentAnalyzer,
    Categorizer,
    AbuseDetector
)

# Initialize analyzers
sentiment = SentimentAnalyzer()
categorizer = Categorizer()
abuse = AbuseDetector()

# Analyze comment across dimensions
comment = await platform.fetch_comment(comment_id)

sentiment_result = sentiment.analyze(comment)
category_result = categorizer.analyze(comment)
abuse_result = abuse.analyze(comment)

print(f"Sentiment: {sentiment_result.sentiment}")
print(f"Category: {category_result.primary_category}")
print(f"Abuse Detected: {abuse_result.is_abuse}")
```

### Example 4: Pipeline Analysis

```python
from moderation_ai.analysis import AnalysisPipeline

# Create analysis pipeline
pipeline = AnalysisPipeline([
    SentimentAnalyzer(),
    Categorizer(),
    AbuseDetector()
])

# Analyze comment through pipeline
results = pipeline.analyze(comment)

for result in results:
    print(f"{result.analysis_type}: {result.result}")
```

### Example 5: Moderation Integration

```python
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector, SentimentAnalyzer

# Initialize components
standards = StandardsEngine()
abuse = AbuseDetector()
sentiment = SentimentAnalyzer()

# Analyze comment
comment = await platform.fetch_comment(comment_id)

abuse_result = abuse.analyze(comment)
sentiment_result = sentiment.analyze(comment)

# Check against standards
if abuse_result.is_abuse:
    decision = await platform.moderate_comment(
        comment_id,
        "remove"
    )
elif sentiment_result.score < -0.5:
    decision = await platform.moderate_comment(
        comment_id,
        "flag"
    )
```

## Analysis Types in Detail

### 1. Summarization

Generate concise summaries of comment discussions.

**Use Cases**:
- Provide quick overview of comment threads
- Identify key themes and opinions
- Reduce information overload

**Example**:
```python
from moderation_ai.analysis import Summarizer

summarizer = Summarizer()

# Summarize single comment
summary = summarizer.summarize(comment)

# Summarize comment thread
summary = summarizer.summarize_thread(comments)
```

### 2. Categorization

Classify comments by topic or theme.

**Use Cases**:
- Organize comments by subject
- Filter comments by category
- Track discussion topics

**Example**:
```python
from moderation_ai.analysis import Categorizer

categorizer = Categorizer(categories=[
    "support",
    "feedback",
    "question",
    "spam"
])

result = categorizer.analyze(comment)
print(f"Category: {result.primary_category}")
```

### 3. Sentiment Analysis

Detect emotional tone of comments.

**Use Cases**:
- Gauge audience reaction
- Identify positive/negative feedback
- Track sentiment over time

**Example**:
```python
from moderation_ai.analysis import SentimentAnalyzer

sentiment = SentimentAnalyzer()

result = sentiment.analyze(comment)
print(f"Sentiment: {result.sentiment}")
print(f"Score: {result.score}")
print(f"Emotions: {result.emotions}")
```

### 4. FAQ Extraction

Identify frequently asked questions in comments.

**Use Cases**:
- Generate FAQ sections
- Identify common concerns
- Improve content based on questions

**Example**:
```python
from moderation_ai.analysis import FAQExtractor

extractor = FAQExtractor()

# Extract FAQs from comment thread
faqs = extractor.extract(comments)

for faq in faqs:
    print(f"Question: {faq.question}")
    print(f"Frequency: {faq.frequency}")
```

### 5. Content Ideation

Suggest content ideas based on comment feedback.

**Use Cases**:
- Generate follow-up content
- Identify content gaps
- Prioritize content creation

**Example**:
```python
from moderation_ai.analysis import ContentIdeation

ideation = ContentIdeation()

# Generate content ideas
ideas = ideation.generate_ideas(comments)

for idea in ideas:
    print(f"Topic: {idea.topic}")
    print(f"Priority: {idea.priority}")
    print(f"Reasoning: {idea.reasoning}")
```

### 6. Community Metrics

Analyze engagement patterns and community health.

**Use Cases**:
- Track community growth
- Measure engagement quality
- Identify community trends

**Example**:
```python
from moderation_ai.analysis import CommunityMetrics

metrics = CommunityMetrics()

# Analyze community metrics
report = metrics.analyze(comments)

print(f"Total comments: {report.total_comments}")
print(f"Active users: {report.active_users}")
print(f"Engagement rate: {report.engagement_rate}")
```

### 7. Abuse Detection

Identify harmful, spam, or inappropriate content.

**Use Cases**:
- Auto-moderate harmful content
- Reduce moderator workload
- Protect community members

**Example**:
```python
from moderation_ai.analysis import AbuseDetector

abuse = AbuseDetector()

# Detect abuse
result = abuse.analyze(comment)

if result.is_abuse:
    print(f"Abuse type: {result.abuse_type}")
    print(f"Severity: {result.severity}")
    print(f"Confidence: {result.confidence}")
```

## Analysis Pipeline

Chain multiple analyzers together:

```python
from moderation_ai.analysis import AnalysisPipeline

# Define pipeline
pipeline = AnalysisPipeline([
    SentimentAnalyzer(),
    Categorizer(),
    AbuseDetector()
])

# Analyze through pipeline
results = pipeline.analyze(comment)

# Access results by type
sentiment = pipeline.get_result(results, "sentiment")
category = pipeline.get_result(results, "category")
abuse = pipeline.get_result(results, "abuse")
```

## Preprocessing

Clean and normalize comments before analysis:

```python
from moderation_ai.analysis import preprocess_comment

# Preprocess comment
cleaned = preprocess_comment(comment.text)

# Apply preprocessing
analyzer = SentimentAnalyzer()
result = analyzer.analyze(
    Comment(text=cleaned, ...)
)
```

## Post-Processing

Process and format analysis results:

```python
from moderation_ai.analysis import format_results

# Format results for display
formatted = format_results(results, output="json")

# Export to file
with open("results.json", "w") as f:
    f.write(formatted)
```

## Analysis Configuration

Configure analyzers for specific use cases:

```python
from moderation_ai.analysis import SentimentAnalyzer

# Configure analyzer
analyzer = SentimentAnalyzer(
    thresholds={
        "positive": 0.5,
        "negative": -0.5
    },
    emotions=["joy", "anger", "fear", "sadness"]
)
```

## Performance Optimization

### Batch Processing

```python
# Efficient batch processing
results = analyzer.batch_analyze(comments, batch_size=100)
```

### Parallel Processing

```python
import asyncio

# Process in parallel
results = await asyncio.gather(*[
    analyzer.analyze(comment)
    for comment in comments
])
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def analyze_cached(comment_id):
    return analyzer.analyze(comment)
```

## Best Practices

### 1. Choose Right Analyzer for Use Case

```python
# Good - use appropriate analyzer
sentiment = SentimentAnalyzer()
abuse = AbuseDetector()

# Bad - use wrong tool
# Don't use categorizer for sentiment detection
```

### 2. Combine Multiple Analyzers

```python
# Good - multi-dimension analysis
sentiment = SentimentAnalyzer().analyze(comment)
category = Categorizer().analyze(comment)
abuse = AbuseDetector().analyze(comment)
```

### 3. Consider Context

```python
# Good - analyze in context
summary = Summarizer().summarize_thread(comments)

# Acceptable - single comment
summary = Summarizer().summarize(comment)
```

### 4. Handle Edge Cases

```python
# Good - handle empty comments
if not comment.text.strip():
    return AnalysisResult(comment_id="", result=None)

# Good - handle short comments
if len(comment.text) < 10:
    return AnalysisResult(
        comment_id=comment.id,
        result=SentimentResult(sentiment="neutral", score=0.0)
    )
```

### 5. Validate Confidence Scores

```python
result = analyzer.analyze(comment)

# Good - check confidence
if result.confidence_score < 0.5:
    print("Low confidence, manual review needed")
```

## Testing Analysis

### Unit Tests

```python
import pytest
from moderation_ai.analysis import SentimentAnalyzer

@pytest.mark.asyncio
async def test_sentiment_analysis():
    analyzer = SentimentAnalyzer()
    comment = Comment(text="Great post!", platform="twitter")
    result = analyzer.analyze(comment)
    assert result.sentiment == "positive"
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_moderation_workflow():
    # Fetch comment
    comment = await platform.fetch_comment(comment_id)

    # Analyze
    abuse_result = AbuseDetector().analyze(comment)

    # Moderate if abuse detected
    if abuse_result.is_abuse:
        await platform.moderate_comment(comment_id, "remove")
```

## Troubleshooting

### Issue: Low confidence scores

**Possible causes**:
- Short or ambiguous comments
- Insufficient training data
- Wrong analyzer for content type

**Resolution**:
- Use appropriate analyzer
- Combine multiple analyzers
- Manual review for low confidence

### Issue: Inconsistent results

**Possible causes**:
- Platform-specific language patterns
- Context not considered
- Configuration issues

**Resolution**:
- Account for platform differences
- Analyze in context
- Verify configuration

## Related Documentation

- **Standards & Metrics**: `../standards-and-metrics.md` - Moderation rules
- **Specific Analyzers**: See individual analysis documents below
- **Architecture**: `../ARCHITECTURE.md` - System design

---

**Last Updated**: January 2024
**Status**: Phase 1 - Documentation Phase
