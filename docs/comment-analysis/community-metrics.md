---
title: Community Metrics
category: analysis
related:
  - ./README.md
  - ./sentiment-analysis.md
  - ./categorization.md
---

# Community Metrics

## Overview

Community metrics analyzes engagement patterns, measures community health, and tracks growth trends. This helps content creators understand their audience, identify engagement opportunities, and monitor community well-being.

## Metric Categories

| Category | Metrics | Purpose |
|----------|---------|---------|
| **Engagement** | Likes, replies, shares | Measure activity level |
| **Growth** | New members, followers | Track community size |
| **Retention** | Return users, churn | Measure loyalty |
| **Quality** | Substantive comments, spam | Measure discussion quality |
| **Sentiment** | Positive/negative ratio | Gauge community mood |

## Community Metrics Interface

```python
from moderation_ai.analysis import CommunityMetrics

# Initialize metrics
metrics = CommunityMetrics()

# Analyze comments
report = metrics.analyze(comments)

# Analyze over time
timeline = metrics.analyze_timeline(comments, interval="daily")

# Compare periods
comparison = metrics.compare_periods(
    comments_period1,
    comments_period2
)
```

## Metrics Report

```python
{
    "period": {
        "start": "2024-01-01",
        "end": "2024-01-31"
    },
    "engagement": {
        "total_comments": 1500,
        "unique_users": 450,
        "avg_comments_per_user": 3.33,
        "engagement_rate": 0.15
    },
    "quality": {
        "substantive_comments": 1200,
        "quality_score": 0.80,
        "spam_comments": 30,
        "spam_rate": 0.02
    },
    "sentiment": {
        "overall_sentiment": "positive",
        "sentiment_score": 0.35,
        "positive_percentage": 65.5,
        "negative_percentage": 15.0
    },
    "activity": {
        "peak_hour": 14,
        "peak_day": "Wednesday",
        "most_active_users": ["user1", "user2", "user3"]
    }
}
```

## Usage Examples

### Example 1: Basic Metrics

```python
from moderation_ai.analysis import CommunityMetrics

metrics = CommunityMetrics()

comments = await platform.fetch_comments(post_id)

# Analyze metrics
report = metrics.analyze(comments)

print(f"Total comments: {report['engagement']['total_comments']}")
print(f"Unique users: {report['engagement']['unique_users']}")
print(f"Engagement rate: {report['engagement']['engagement_rate']:.2%}")
print(f"Quality score: {report['quality']['quality_score']:.2f}")
print(f"Overall sentiment: {report['sentiment']['overall_sentiment']}")
```

### Example 2: Timeline Analysis

```python
metrics = CommunityMetrics()

comments = await platform.fetch_comments(post_id)

# Analyze over time
timeline = metrics.analyze_timeline(
    comments,
    interval="daily"  # or "hourly", "weekly"
)

print("Daily Activity:")
for day_data in timeline:
    date = day_data["date"]
    comments_count = day_data["comments_count"]
    sentiment = day_data["sentiment"]
    
    print(f"{date}: {comments_count} comments, sentiment: {sentiment}")
```

### Example 3: Period Comparison

```python
metrics = CommunityMetrics()

comments_week1 = await platform.fetch_comments(post_id_week1)
comments_week2 = await platform.fetch_comments(post_id_week2)

# Compare periods
comparison = metrics.compare_periods(
    comments_week1,
    comments_week2,
    label1="Week 1",
    label2="Week 2"
)

print(f"Comment growth: {comparison['engagement']['comment_growth']:.1%}")
print(f"User growth: {comparison['engagement']['user_growth']:.1%}")
print(f"Sentiment change: {comparison['sentiment']['sentiment_change']:.2f}")
print(f"Quality change: {comparison['quality']['quality_change']:.2f}")
```

### Example 4: User Activity Analysis

```python
metrics = CommunityMetrics()

comments = await platform.fetch_comments(post_id)

# Analyze user activity
user_activity = metrics.analyze_users(comments)

print("Top Contributors:")
for user in user_activity["top_contributors"][:10]:
    print(f"  {user['username']}: {user['comment_count']} comments")

print("\nNew Users:")
for user in user_activity["new_users"][:5]:
    print(f"  {user['username']}")

print("\nMost Active Hour:")
print(f"  {user_activity['peak_hour']}:00")
```

### Example 5: Quality Analysis

```python
metrics = CommunityMetrics()

comments = await platform.fetch_comments(post_id)

# Analyze comment quality
quality = metrics.analyze_quality(comments)

print(f"Substantive comments: {quality['substantive_comments']}")
print(f"Low quality comments: {quality['low_quality_comments']}")
print(f"Spam comments: {quality['spam_comments']}")
print(f"Overall quality score: {quality['quality_score']:.2f}")

# Quality breakdown
print("\nQuality Breakdown:")
for quality_level, count in quality["quality_distribution"].items():
    percentage = (count / quality["total_comments"]) * 100
    print(f"  {quality_level}: {count} ({percentage:.1f}%)")
```

### Example 6: Sentiment Trends

```python
metrics = CommunityMetrics()

comments = await platform.fetch_comments(post_id)

# Analyze sentiment trends
sentiment_trends = metrics.analyze_sentiment_timeline(comments)

print("Sentiment Over Time:")
for day_data in sentiment_trends:
    date = day_data["date"]
    sentiment = day_data["sentiment"]
    positive = day_data["positive_percentage"]
    
    print(f"{date}: {sentiment} ({positive:.1f}% positive)")
```

### Example 7: Community Health Score

```python
metrics = CommunityMetrics()

comments = await platform.fetch_comments(post_id)

# Calculate overall health
health = metrics.calculate_health_score(comments)

print(f"Overall Health: {health['overall_score']}/100")
print(f"Engagement: {health['engagement_score']}/100")
print(f"Quality: {health['quality_score']}/100")
print(f"Sentiment: {health['sentiment_score']}/100")

# Health assessment
if health['overall_score'] > 75:
    print("\nCommunity Health: Excellent")
elif health['overall_score'] > 50:
    print("\nCommunity Health: Good")
elif health['overall_score'] > 25:
    print("\nCommunity Health: Moderate")
else:
    print("\nCommunity Health: Needs Improvement")
```

## Metric Calculations

### Engagement Metrics

```python
{
    "total_comments": 1500,
    "unique_users": 450,
    "avg_comments_per_user": 3.33,
    "engagement_rate": 0.15,  # comments / total_views
    "total_likes": 5000,
    "avg_likes_per_comment": 3.33
}
```

### Quality Metrics

```python
{
    "substantive_comments": 1200,
    "low_quality_comments": 270,
    "spam_comments": 30,
    "quality_score": 0.80,
    "spam_rate": 0.02
}
```

### Sentiment Metrics

```python
{
    "overall_sentiment": "positive",
    "sentiment_score": 0.35,
    "positive_percentage": 65.5,
    "negative_percentage": 15.0,
    "neutral_percentage": 19.5
}
```

### Activity Metrics

```python
{
    "peak_hour": 14,
    "peak_day": "Wednesday",
    "most_active_users": ["user1", "user2", "user3"],
    "activity_distribution": {
        "hourly": [10, 15, 20, ...],
        "daily": [100, 150, 200, ...]
    }
}
```

## Configuration

### Quality Thresholds

```python
metrics = CommunityMetrics(
    quality_thresholds={
        "substantive": 50,    # minimum length
        "low_quality": 10,    # minimum length
        "spam": 3             # very short comments
    }
)
```

### Engagement Definition

```python
metrics = CommunityMetrics(
    engagement_metrics=[
        "likes",
        "replies",
        "shares"
    ]
)
```

### Timezone

```python
metrics = CommunityMetrics(
    timezone="UTC"
)
```

## Best Practices

### 1. Analyze Over Time

```python
# Don't just analyze single post
# Track metrics over time
# Identify trends and patterns
```

### 2. Compare Periods

```python
# Week-over-week comparison
# Month-over-month comparison
# Identify growth or decline
```

### 3. Focus on Health Score

```python
# Overall health is more important
# than individual metrics
# Balance engagement, quality, and sentiment
```

### 4. Identify Top Contributors

```python
# Recognize active users
# Engage with top contributors
# Encourage community participation
```

### 5. Monitor Quality

```python
# Track spam rate
# Monitor low-quality comments
# Take action on declining quality
```

## Use Cases

### Community Dashboard

Create real-time dashboard:

```python
async def community_dashboard(post_id):
    comments = await platform.fetch_comments(post_id)
    metrics = CommunityMetrics()
    
    return {
        "engagement": metrics.analyze(comments)["engagement"],
        "quality": metrics.analyze_quality(comments),
        "sentiment": metrics.analyze_sentiment_timeline(comments)[-7:],
        "health": metrics.calculate_health_score(comments)
    }
```

### Growth Tracking

Track community growth:

```python
async def track_growth(post_ids):
    metrics = CommunityMetrics()
    growth_data = []
    
    for post_id in post_ids:
        comments = await platform.fetch_comments(post_id)
        report = metrics.analyze(comments)
        
        growth_data.append({
            "post_id": post_id,
            "unique_users": report["engagement"]["unique_users"],
            "new_users": report["engagement"]["new_users"],
            "timestamp": datetime.now()
        })
    
    return growth_data
```

### Quality Monitoring

Monitor content quality:

```python
async def monitor_quality(comments):
    metrics = CommunityMetrics()
    quality = metrics.analyze_quality(comments)
    
    if quality["spam_rate"] > 0.05:
        return {"alert": "High spam rate", "rate": quality["spam_rate"]}
    
    if quality["quality_score"] < 0.5:
        return {"alert": "Low quality", "score": quality["quality_score"]}
    
    return {"status": "Normal"}
```

## Related Documentation

- **Sentiment Analysis**: `./sentiment-analysis.md` - Emotional analysis
- **Categorization**: `./categorization.md` - Topic classification
- **Abuse Detection**: `./abuse-detection.md` - Harmful content

---

**Last Updated**: January 2024
**Status**: Phase 1 - Documentation Phase
