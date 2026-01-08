---
title: Fetch YouTube Comments Example
category: example
platform: youtube
related:
  - ../api-guide.md
  - ../data-models.md
---

# Example: Fetch YouTube Comments

## Overview

This example demonstrates how to fetch comments from a YouTube video using Moderation AI library.

## Prerequisites

- YouTube API credentials
- Python 3.9+ installed
- Moderation AI library installed

## Setup

### 1. Install Dependencies

```bash
pip install moderation-ai
```

### 2. Set Environment Variables

```bash
export YOUTUBE_API_KEY=your_api_key
```

## Example 1: Basic Fetch

```python
import asyncio
from moderation_ai.platforms import YouTubeAPI

async def main():
    youtube = YouTubeAPI.from_env()
    
    video_id = "abc123"
    comments = await youtube.fetch_comments(video_id)
    
    print(f"Found {len(comments)} comments:")
    for comment in comments:
        print(f"{comment.author_display_name}: {comment.text}")

asyncio.run(main())
```

## Example 2: Fetch with Pagination

```python
async def main():
    youtube = YouTubeAPI.from_env()
    video_id = "abc123"
    
    page_token = None
    all_comments = []
    
    while True:
        result = await youtube.fetch_comments(
            video_id,
            page_token=page_token
        )
        
        all_comments.extend(result.comments)
        print(f"Fetched {len(result.comments)} comments (total: {len(all_comments)})")
        
        if not result.has_more:
            break
        
        page_token = result.next_page_token

asyncio.run(main())
```

## Example 3: Analyze Comments

```python
from moderation_ai.analysis import SentimentAnalyzer

async def main():
    youtube = YouTubeAPI.from_env()
    analyzer = SentimentAnalyzer()
    
    video_id = "abc123"
    comments = await youtube.fetch_comments(video_id)
    
    results = analyzer.batch_analyze(comments)
    
    for comment, result in zip(comments, results):
        print(f"{comment.author_display_name}: {result.sentiment} ({result.score:.2f})")

asyncio.run(main())
```

## Example 4: Moderate Comments

```python
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector

async def main():
    youtube = YouTubeAPI.from_env()
    standards = StandardsEngine()
    abuse = AbuseDetector()
    
    video_id = "abc123"
    comments = await youtube.fetch_comments(video_id)
    
    for comment in comments:
        # Check against standards
        decision = standards.validate(comment.text)
        
        # Check for abuse
        abuse_result = abuse.analyze(comment)
        
        # Apply moderation
        if abuse_result.is_abuse:
            action = "delete"
            await youtube.moderate_comment(comment.id, action)
        elif decision.action != "approve":
            action = decision.action

asyncio.run(main())
```

## Running Examples

### Run Basic Example

```bash
python fetch_comments.py
```

## Tips

1. Use pagination for many comments
2. Analyze in batches for efficiency
3. Respect rate limits (10,000 requests/day)
4. Cache video metadata to reduce API calls

## Related Documentation

- **API Guide**: `../api-guide.md` - API usage
- **Data Models**: `../data-models.md` - Data structures

---

**Example Version**: 1.0
**Platform**: YouTube
**Status**: Working
