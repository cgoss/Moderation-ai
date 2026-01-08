---
title: Abuse Detection
category: analysis
related:
  - ./README.md
  - ./sentiment-analysis.md
  - ../standards-and-metrics.md
---

# Abuse Detection

## Overview

Abuse detection identifies harmful, inappropriate, or rule-violating content in comments. This helps protect community members, reduce moderator workload, and maintain safe discussion spaces.

## Abuse Categories

| Category | Description | Severity |
|----------|-------------|-----------|
| **Harassment** | Targeted negative behavior | HIGH |
| **Hate Speech** | Attacks on protected groups | CRITICAL |
| **Bullying** | Intimidating or demeaning behavior | HIGH |
| **Threats** | Violent or harmful intent | CRITICAL |
| **Spam** | Unwanted promotional content | MEDIUM |
| **Profanity** | Inappropriate language | LOW-MEDIUM |

## Abuse Detector Interface

```python
from moderation_ai.analysis import AbuseDetector

# Initialize detector
detector = AbuseDetector()

# Detect abuse in comment
result = detector.analyze(comment)

# Batch detect
results = detector.batch_detect(comments)

# Detect specific abuse type
harassment_result = detector.detect_harassment(comment)
```

## Abuse Detection Result

```python
{
    "comment_id": "123",
    "is_abuse": True,
    "abuse_type": "harassment",
    "severity": "high",
    "confidence": 0.92,
    "reasoning": "Comment contains targeted personal attacks and demeaning language",
    "evidence": {
        "harassment_indicators": [
            "you're so stupid",
            "nobody likes you"
        ],
        "profanity_count": 2,
        "targeted_user": "username"
    },
    "recommended_action": "hide"
}
```

## Usage Examples

### Example 1: Basic Abuse Detection

```python
from moderation_ai.analysis import AbuseDetector

detector = AbuseDetector()

comment = Comment(
    id="123",
    text="You're so stupid, nobody likes you!",
    platform="reddit"
)

result = detector.analyze(comment)

if result.is_abuse:
    print(f"Abuse detected: {result.abuse_type}")
    print(f"Severity: {result.severity}")
    print(f"Confidence: {result.confidence}")
    print(f"Recommended action: {result.recommended_action}")
else:
    print("No abuse detected")
```

### Example 2: Batch Detection

```python
detector = AbuseDetector()

comments = await platform.fetch_comments(post_id)

# Detect abuse in batch
results = detector.batch_detect(comments)

# Process results
for comment, result in zip(comments, results):
    if result.is_abuse:
        print(f"Comment {comment.id}: {result.abuse_type}")
        # Apply moderation action
        await platform.moderate_comment(
            comment.id,
            result.recommended_action
        )
```

### Example 3: Specific Abuse Types

```python
detector = AbuseDetector()

comment = Comment(
    id="123",
    text="All [group] are inferior",
    platform="twitter"
)

# Detect specific abuse types
hate_speech = detector.detect_hate_speech(comment)
harassment = detector.detect_harassment(comment)
threats = detector.detect_threats(comment)

if hate_speech.is_abuse:
    print("Hate speech detected")

if harassment.is_abuse:
    print("Harassment detected")

if threats.is_abuse:
    print("Threat detected")
```

### Example 4: Severity-Based Actions

```python
detector = AbuseDetector()

comments = await platform.fetch_comments(post_id)
results = detector.batch_detect(comments)

# Apply actions based on severity
for comment, result in zip(comments, results):
    if not result.is_abuse:
        continue
    
    if result.severity == "critical":
        # Remove immediately
        await platform.moderate_comment(comment.id, "remove")
    elif result.severity == "high":
        # Hide and flag for review
        await platform.moderate_comment(comment.id, "hide")
    elif result.severity == "medium":
        # Flag for review
        await platform.moderate_comment(comment.id, "flag")
```

### Example 5: Abuse Statistics

```python
detector = AbuseDetector()

comments = await platform.fetch_comments(post_id)
results = detector.batch_detect(comments)

# Calculate abuse statistics
abuse_comments = [r for r in results if r.is_abuse]
abuse_rate = len(abuse_comments) / len(results) * 100

# Categorize by abuse type
abuse_types = {}
for result in abuse_comments:
    abuse_type = result.abuse_type
    abuse_types[abuse_type] = abuse_types.get(abuse_type, 0) + 1

print(f"Total comments: {len(results)}")
print(f"Abuse comments: {len(abuse_comments)}")
print(f"Abuse rate: {abuse_rate:.1f}%")
print("\nAbuse types:")
for abuse_type, count in abuse_types.items():
    percentage = (count / len(abuse_comments)) * 100
    print(f"  {abuse_type}: {count} ({percentage:.1f}%)")
```

### Example 6: Repeat Offender Detection

```python
detector = AbuseDetector()

comments = await platform.fetch_comments(post_id)
results = detector.batch_detect(comments)

# Identify repeat offenders
offenders = {}
for comment, result in zip(comments, results):
    if result.is_abuse:
        user = comment.author_username
        offenders[user] = offenders.get(user, 0) + 1

# Flag repeat offenders
repeat_offenders = [
    user for user, count in offenders.items()
    if count >= 3
]

print("Repeat offenders:")
for user in repeat_offenders:
    print(f"  {user}: {offenders[user]} abuse comments")
```

## Abuse Detection Techniques

### Keyword-Based

Uses hate speech and harassment word lists:

```python
detector = AbuseDetector(
    method="keyword",
    abuse_keywords={
        "harassment": ["stupid", "idiot", "loser"],
        "hate_speech": ["slur1", "slur2"],
        "profanity": ["profanity1", "profanity2"]
    }
)
```

### Pattern-Based

Uses regex patterns for abuse detection:

```python
detector = AbuseDetector(
    method="pattern",
    abuse_patterns={
        "harassment": [r"you('re| are) (so|too) (stupid|idiotic)"],
        "threats": [r"i('m| am) going to (kill|hurt)"],
        "hate_speech": [r"all ([a-z]+) (are|should)"]
    }
)
```

### Machine Learning

Uses trained ML models:

```python
detector = AbuseDetector(
    method="ml",
    model="toxic-bert",
    threshold=0.7
)
```

### Hybrid Approach

Combines multiple methods:

```python
detector = AbuseDetector(
    method="hybrid",
    keyword_weight=0.3,
    pattern_weight=0.3,
    ml_weight=0.4
)
```

## Abuse Type Detection

### Harassment

```python
result = detector.detect_harassment(comment)

{
    "is_abuse": True,
    "abuse_type": "harassment",
    "indicators": ["targeted insults", "repetitive attacks"]
}
```

### Hate Speech

```python
result = detector.detect_hate_speech(comment)

{
    "is_abuse": True,
    "abuse_type": "hate_speech",
    "targeted_group": "religious_group",
    "severity": "critical"
}
```

### Threats

```python
result = detector.detect_threats(comment)

{
    "is_abuse": True,
    "abuse_type": "threats",
    "threat_type": "violence",
    "severity": "critical"
}
```

### Bullying

```python
result = detector.detect_bullying(comment)

{
    "is_abuse": True,
    "abuse_type": "bullying",
    "pattern": "repeated_targeted_attacks",
    "severity": "high"
}
```

### Spam

```python
result = detector.detect_spam(comment)

{
    "is_abuse": True,
    "abuse_type": "spam",
    "spam_type": "promotional",
    "confidence": 0.85
}
```

## Configuration

### Severity Thresholds

```python
detector = AbuseDetector(
    severity_thresholds={
        "critical": 0.9,
        "high": 0.7,
        "medium": 0.5,
        "low": 0.3
    }
)
```

### Confidence Threshold

```python
detector = AbuseDetector(
    min_confidence=0.7  # Minimum confidence to flag
)
```

### Abuse Type Configuration

```python
detector = AbuseDetector(
    detect_types=[
        "harassment",
        "hate_speech",
        "threats",
        "bullying",
        "spam"
    ]
)
```

## Best Practices

### 1. Use Appropriate Thresholds

```python
# For strict moderation
detector = AbuseDetector(min_confidence=0.6)

# For lenient moderation
detector = AbuseDetector(min_confidence=0.8)
```

### 2. Combine with Sentiment Analysis

```python
abuse_detector = AbuseDetector()
sentiment = SentimentAnalyzer()

comment = await platform.fetch_comment(comment_id)

abuse_result = abuse_detector.analyze(comment)
sentiment_result = sentiment.analyze(comment)

# Negative sentiment + abuse = higher priority
if abuse_result.is_abuse and sentiment_result.sentiment == "negative":
    return "remove_immediately"
```

### 3. Review Low Confidence Results

```python
result = detector.analyze(comment)

if result.is_abuse and result.confidence < 0.7:
    # Flag for human review
    result.flagged_for_review = True
```

### 4. Track Repeat Offenders

```python
# Track users who repeatedly post abusive content
# Apply escalating sanctions
# Monitor behavior patterns
```

### 5. Consider Context

```python
# Analyze comment in context of thread
# Consider conversation history
# Account for sarcasm and jokes
```

## Use Cases

### Auto-Moderation

Automatically moderate abusive comments:

```python
async def auto_moderate(comments):
    detector = AbuseDetector()
    results = detector.batch_detect(comments)
    
    for comment, result in zip(comments, results):
        if result.is_abuse:
            action = result.recommended_action
            await platform.moderate_comment(comment.id, action)
```

### Review Queue

Flag comments for human review:

```python
async def create_review_queue(comments):
    detector = AbuseDetector()
    results = detector.batch_detect(comments)
    
    review_queue = []
    
    for comment, result in zip(comments, results):
        # Flag low confidence for review
        if result.is_abuse and result.confidence < 0.8:
            review_queue.append({
                "comment": comment,
                "result": result,
                "priority": "high" if result.severity == "critical" else "medium"
            })
    
    return review_queue
```

### Abuse Reporting

Generate abuse reports:

```python
async def abuse_report(post_id):
    comments = await platform.fetch_comments(post_id)
    detector = AbuseDetector()
    results = detector.batch_detect(comments)
    
    abuse_comments = [r for r in results if r.is_abuse]
    
    report = {
        "total_comments": len(comments),
        "abuse_comments": len(abuse_comments),
        "abuse_rate": len(abuse_comments) / len(comments),
        "abuse_types": categorize_by_type(abuse_comments),
        "severity_distribution": severity_distribution(abuse_comments)
    }
    
    return report
```

## Related Documentation

- **Standards & Metrics**: `../standards-and-metrics.md` - Moderation rules
- **Sentiment Analysis**: `./sentiment-analysis.md` - Emotional analysis
- **Error Handling**: `../api-reference/error-handling.md` - Error patterns

---

**Last Updated**: January 2024
**Status**: Phase 1 - Documentation Phase
