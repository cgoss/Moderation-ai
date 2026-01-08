---
title: Fetch Twitter Comments Example
category: example
platform: twitter
related:
  - ../api-guide.md
  - ../data-models.md
---

# Example: Fetch Twitter Comments

## Overview

This example demonstrates how to fetch comments (replies) from a Twitter tweet using the Moderation AI library.

## Prerequisites

- Twitter API credentials set up
- Python 3.9+ installed
- Moderation AI library installed

## Setup

### 1. Install Dependencies

```bash
pip install moderation-ai
```

### 2. Set Environment Variables

```bash
export TWITTER_BEARER_TOKEN="your_bearer_token"
```

Or create `.env` file:

```bash
TWITTER_BEARER_TOKEN=your_bearer_token
```

## Basic Example: Fetch Single Tweet Comments

```python
import asyncio
from moderation_ai.platforms import TwitterAPI

async def main():
    # Initialize Twitter API
    twitter = TwitterAPI.from_env()
    
    # Tweet ID to fetch comments for
    tweet_id = "1234567890"
    
    # Fetch comments
    print(f"Fetching comments for tweet {tweet_id}...")
    comments = await twitter.fetch_comments(tweet_id)
    
    print(f"Found {len(comments)} comments:\n")
    
    for comment in comments:
        print(f"@{comment.author_username}: {comment.text}")
        print(f"  Created: {comment.created_at}")
        print(f"  Likes: {comment.public_metrics.like_count}")
        print()

asyncio.run(main())
```

## Example 2: Fetch with Metadata

```python
import asyncio
from moderation_ai.platforms import TwitterAPI

async def main():
    twitter = TwitterAPI.from_env()
    tweet_id = "1234567890"
    
    # Fetch comments with additional metadata
    comments = await twitter.fetch_comments(
        tweet_id,
        tweet_fields=["created_at", "public_metrics", "author_id"],
        user_fields=["username", "name", "verified"],
        expansions=["author_id"]
    )
    
    for comment in comments:
        print(f"@{comment.author_username} ({comment.author_name})")
        if comment.verified:
            print("  ✓ Verified")
        print(f"  {comment.text}")
        print(f"  Likes: {comment.public_metrics.like_count}")
        print(f"  Replies: {comment.public_metrics.reply_count}")
        print()

asyncio.run(main())
```

## Example 3: Fetch All Pages

```python
import asyncio
from moderation_ai.platforms import TwitterAPI

async def main():
    twitter = TwitterAPI.from_env()
    tweet_id = "1234567890"
    
    # Fetch all comments with pagination
    cursor = None
    all_comments = []
    
    while True:
        result = await twitter.fetch_comments(
            tweet_id,
            cursor=cursor,
            max_results=100
        )
        
        all_comments.extend(result.comments)
        print(f"Fetched {len(result.comments)} comments (total: {len(all_comments)})")
        
        if not result.has_more:
            break
        
        cursor = result.next_cursor
    
    print(f"\nTotal comments: {len(all_comments)}")

asyncio.run(main())
```

## Example 4: Analyze Comments

```python
import asyncio
from moderation_ai.platforms import TwitterAPI
from moderation_ai.analysis import SentimentAnalyzer

async def main():
    twitter = TwitterAPI.from_env()
    analyzer = SentimentAnalyzer()
    
    tweet_id = "1234567890"
    
    # Fetch comments
    comments = await twitter.fetch_comments(tweet_id)
    
    # Analyze sentiment
    results = analyzer.batch_analyze(comments)
    
    # Display results
    for comment, result in zip(comments, results):
        print(f"@{comment.author_username}: {result.sentiment} ({result.score:.2f})")
        print(f"  {comment.text[:50]}...")
        print()

asyncio.run(main())
```

## Example 5: Moderate Comments

```python
import asyncio
from moderation_ai.platforms import TwitterAPI
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector

async def main():
    twitter = TwitterAPI.from_env()
    standards = StandardsEngine()
    abuse = AbuseDetector()
    
    tweet_id = "1234567890"
    
    # Fetch comments
    comments = await twitter.fetch_comments(tweet_id)
    
    # Analyze and moderate
    for comment in comments:
        # Check against standards
        decision = standards.validate(comment.text)
        
        # Check for abuse
        abuse_result = abuse.analyze(comment)
        
        print(f"@{comment.author_username}")
        print(f"  {comment.text}")
        
        # Apply moderation action
        if abuse_result.is_abuse:
            action = abuse_result.recommended_action
            print(f"  Action: {action} (abuse: {abuse_result.abuse_type})")
            
            # Apply moderation
            await twitter.moderate_comment(comment.id, action)
        elif decision.action != "approve":
            print(f"  Action: {decision.action} (standard: {decision.standard})")
        else:
            print(f"  Action: approve")
        
        print()

asyncio.run(main())
```

## Example 6: Fetch Multiple Tweets

```python
import asyncio
from moderation_ai.platforms import TwitterAPI

async def main():
    twitter = TwitterAPI.from_env()
    
    # Multiple tweet IDs
    tweet_ids = ["1234567890", "0987654321", "5432109876"]
    
    # Fetch all tweets in parallel
    all_comments = []
    
    for tweet_id in tweet_ids:
        comments = await twitter.fetch_comments(tweet_id)
        all_comments.extend(comments)
        
        print(f"Tweet {tweet_id}: {len(comments)} comments")
    
    print(f"\nTotal comments across all tweets: {len(all_comments)}")

asyncio.run(main())
```

## Example 7: Stream Real-Time Comments

```python
import asyncio
from moderation_ai.platforms import TwitterAPI

async def main():
    twitter = TwitterAPI.from_env()
    
    # Track a specific tweet
    tweet_id = "1234567890"
    await twitter.track_post(tweet_id)
    
    # Handle incoming comments
    async def on_comment_created(event):
        comment = event.data.comment
        print(f"New comment from @{comment.author_username}: {comment.text}")
        
        # Analyze and moderate
        from moderation_ai.analysis import AbuseDetector
        abuse = AbuseDetector()
        result = abuse.analyze(comment)
        
        if result.is_abuse:
            await twitter.moderate_comment(comment.id, "hide")
            print("  → Comment hidden (abuse detected)")
    
    # Start streaming
    await twitter.start_webhook_handler(
        on_comment_created=on_comment_created
    )

asyncio.run(main())
```

## Running the Examples

### Run Basic Example

```bash
# Save as fetch_comments.py
python fetch_comments.py
```

### Run with Specific Tweet ID

```python
# Modify the example to accept tweet ID as argument
import sys

tweet_id = sys.argv[1] if len(sys.argv) > 1 else "1234567890"

comments = await twitter.fetch_comments(tweet_id)
```

## Error Handling

### Handle Rate Limits

```python
from moderation_ai.utils import RateLimitExceeded

try:
    comments = await twitter.fetch_comments(tweet_id)
except RateLimitExceeded as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
```

### Handle Authentication Errors

```python
from moderation_ai.utils import AuthenticationError

try:
    comments = await twitter.fetch_comments(tweet_id)
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
```

## Tips

1. **Always paginate**: Fetch all pages for complete results
2. **Use batch operations**: Reduce API calls
3. **Handle rate limits**: Implement proper rate limiting
4. **Cache user data**: Don't refetch user info
5. **Process in parallel**: Use asyncio for multiple requests

## Related Documentation

- **API Guide**: `../api-guide.md` - Detailed API usage
- **Data Models**: `../data-models.md` - Data structures
- **Moderation Example**: `./moderate-comment.md` - Moderation workflow
- **Tracking Example**: `./track-post.md` - Post tracking

---

**Example Version**: 1.0
**Platform**: Twitter/X
**Status**: Working
