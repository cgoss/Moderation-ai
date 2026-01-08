---
title: Fetch Reddit Comments Example
category: example
platform: reddit
related:
  - ../api-guide.md
  - ../data-models.md
---

# Example: Fetch Reddit Comments

## Overview

This example demonstrates how to fetch comments from a Reddit post using Moderation AI library.

## Prerequisites

- Reddit API credentials set up
- Python 3.9+ installed
- Moderation AI library installed

## Setup

### 1. Install Dependencies

```bash
pip install moderation-ai
```

### 2. Set Environment Variables

```bash
# Reddit credentials
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export REDDIT_USER_AGENT="python:moderation-ai:1.0 (by /u/your_username)"
export REDDIT_USERNAME="your_username"
export REDDIT_PASSWORD="your_password"
```

Or create `.env` file:

```bash
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=python:moderation-ai:1.0 (by /u/your_username)
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
```

## Example 1: Basic Fetch

```python
import asyncio
from moderation_ai.platforms import RedditAPI

async def main():
    # Initialize Reddit API
    reddit = RedditAPI.from_env()
    
    # Post ID to fetch comments for
    post_id = "abc123"
    
    # Fetch comments
    print(f"Fetching comments for post {post_id}...")
    comments = await reddit.fetch_comments(post_id)
    
    print(f"Found {len(comments)} comments:\n")
    
    for comment in comments:
        print(f"{comment.author_username}: {comment.text}")
        print(f"  Score: {comment.score}")
        print(f"  Depth: {comment.depth}")
        print()

asyncio.run(main())
```

## Example 2: Fetch with Metadata

```python
import asyncio
from moderation_ai.platforms import RedditAPI

async def main():
    reddit = RedditAPI.from_env()
    post_id = "abc123"
    
    # Fetch comments with additional metadata
    comments = await reddit.fetch_comments(
        post_id,
        include_threaded=True,
        include_depth=True
    )
    
    for comment in comments:
        print(f"@{comment.author_username}: {comment.text}")
        print(f"  Score: {comment.score}")
        print(f"  Depth: {comment.depth}")
        print(f"  Replies: {len(comment.replies)}")
        print()

asyncio.run(main())
```

## Example 3: Fetch All Pages

```python
import asyncio
from moderation_ai.platforms import RedditAPI

async def main():
    reddit = RedditAPI.from_env()
    post_id = "abc123"
    
    # Fetch all comments with pagination
    after = None
    all_comments = []
    
    while True:
        result = await reddit.fetch_comments(
            post_id,
            after=after,
            limit=100
        )
        
        all_comments.extend(result.comments)
        print(f"Fetched {len(result.comments)} comments (total: {len(all_comments)})")
        
        if not result.has_more:
            break
        
        after = result.after
    
    print(f"\nTotal comments: {len(all_comments)}")

asyncio.run(main())
```

## Example 4: Analyze Comments

```python
import asyncio
from moderation_ai.platforms import RedditAPI
from moderation_ai.analysis import SentimentAnalyzer

async def main():
    reddit = RedditAPI.from_env()
    analyzer = SentimentAnalyzer()
    
    post_id = "abc123"
    
    # Fetch comments
    comments = await reddit.fetch_comments(post_id)
    
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
from moderation_ai.platforms import RedditAPI
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector

async def main():
    reddit = RedditAPI.from_env()
    standards = StandardsEngine()
    abuse = AbuseDetector()
    
    post_id = "abc123"
    
    # Fetch comments
    comments = await reddit.fetch_comments(post_id)
    
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
            await reddit.moderate_comment(comment.id, action)
        elif decision.action != "approve":
            print(f"  Action: {decision.action} (standard: {decision.standard})")
        else:
            print(f"  Action: approve")
        
        print()

asyncio.run(main())
```

## Example 6: Fetch User Comments

```python
import asyncio
from moderation_ai.platforms import RedditAPI

async def main():
    reddit = RedditAPI.from_env()
    
    # Fetch user's comments
    username = "reddit_user"
    comments = await reddit.fetch_user_comments(username, limit=100)
    
    print(f"Found {len(comments)} comments by {username}:\n")
    
    for comment in comments:
        print(f"{comment.text[:80]}...")
        print(f"  Subreddit: {comment.subreddit_name}")
        print(f"  Score: {comment.score}")
        print()

asyncio.run(main())
```

## Example 7: Process Nested Comments

```python
import asyncio
from moderation_ai.platforms import RedditAPI

async def main():
    reddit = RedditAPI.from_env()
    
    post_id = "abc123"
    
    # Fetch comments
    comments = await reddit.fetch_comments(post_id)
    
    # Process nested structure
    def process_comment_tree(comment_list, depth=0):
        for comment in comment_list:
            indent = "  " * depth
            print(f"{indent}{comment.author_username}: {comment.text[:60]}...")
            print(f"{indent}  Score: {comment.score}, Depth: {depth}")
            
            # Recursively process replies
            if comment.replies:
                process_comment_tree(comment.replies, depth + 1)
    
    # Start processing from root comments
    root_comments = [c for c in comments if c.is_root]
    process_comment_tree(root_comments)

asyncio.run(main())
```

## Running Examples

### Run Basic Example

```bash
# Save as fetch_comments.py
python fetch_comments.py
```

### Run with Specific Post ID

```python
# Modify example to accept post ID as argument
import sys

post_id = sys.argv[1] if len(sys.argv) > 1 else "abc123"

# Use post_id in script
comments = await reddit.fetch_comments(post_id)
```

## Error Handling

### Handle Rate Limits

```python
from moderation_ai.utils import RateLimitExceeded

try:
    comments = await reddit.fetch_comments(post_id)
except RateLimitExceeded as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
```

### Handle Authentication Errors

```python
from moderation_ai.utils import AuthenticationError

try:
    comments = await reddit.fetch_comments(post_id)
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
```

## Tips

1. **Always paginate**: Fetch all pages for complete results
2. **Use batch operations**: Reduce API calls
3. **Handle nested comments**: Process comment tree structure
4. **Cache user data**: Don't refetch user info
5. **Process in parallel**: Use asyncio for multiple requests

## Related Documentation

- **API Guide**: `../api-guide.md` - Detailed API usage
- **Data Models**: `../data-models.md` - Data structures
- **Moderation Example**: `./moderate-comment.md` - Moderation workflow
- **Tracking Example**: `./track-post.md` - Post monitoring

---

**Example Version**: 1.0
**Platform**: Reddit
**Status**: Working
