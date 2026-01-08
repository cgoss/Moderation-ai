---
title: Moderate Reddit Comment Example
category: example
platform: reddit
related:
  - ../api-guide.md
  - ../comment-moderation.md
---

# Example: Moderate Reddit Comments

## Overview

This example demonstrates how to analyze and moderate Reddit comments using Moderation AI library, including automated abuse detection and standards validation.

## Prerequisites

- Reddit API credentials with moderator permissions
- Python 3.9+ installed
- Moderation AI library installed

## Setup

### 1. Install Dependencies

```bash
pip install moderation-ai
```

### 2. Set Environment Variables

```bash
# Reddit credentials (requires mod permissions)
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

## Example 1: Basic Moderation

```python
import asyncio
from moderation_ai.platforms import RedditAPI
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector

async def moderate_single_comment():
    # Initialize components
    reddit = RedditAPI.from_env()
    standards = StandardsEngine()
    abuse = AbuseDetector()
    
    # Comment to moderate
    comment_id = "def456"
    
    # Fetch comment
    print(f"Fetching comment {comment_id}...")
    comment = await reddit.fetch_comment(comment_id)
    
    # Analyze for abuse
    print("Analyzing for abuse...")
    abuse_result = abuse.analyze(comment)
    
    # Validate against standards
    print("Validating against standards...")
    decision = standards.validate(comment.text)
    
    # Display results
    print(f"\n@{comment.author_username}: {comment.text}")
    print(f"\nAbuse Detection:")
    print(f"  Abuse detected: {abuse_result.is_abuse}")
    if abuse_result.is_abuse:
        print(f"  Type: {abuse_result.abuse_type}")
        print(f"  Severity: {abuse_result.severity}")
        print(f"  Confidence: {abuse_result.confidence:.2f}")
    
    print(f"\nStandards Validation:")
    print(f"  Action: {decision.action}")
    if decision.standards_violated:
        print(f"  Violated standards: {decision.standards_violated}")
        print(f"  Reasoning: {decision.reasoning}")
    
    # Apply moderation action
    action = "approve"
    
    if abuse_result.is_abuse:
        action = abuse_result.recommended_action
    elif decision.action != "approve":
        action = decision.action
    
    print(f"\nApplying action: {action}")
    
    if action != "approve":
        success = await reddit.moderate_comment(comment_id, action)
        if success:
            print(f"Comment {comment_id} has been moderated")
        else:
            print(f"Failed to moderate comment")
    else:
        print("Comment approved")

asyncio.run(moderate_single_comment())
```

## Example 2: Batch Moderation

```python
import asyncio
from moderation_ai.platforms import RedditAPI
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector

async def moderate_post_comments():
    # Initialize components
    reddit = RedditAPI.from_env()
    standards = StandardsEngine()
    abuse = AbuseDetector()
    
    # Post ID
    post_id = "abc123"
    
    # Fetch comments
    print(f"Fetching comments for post {post_id}...")
    comments = await reddit.fetch_comments(post_id)
    
    print(f"Found {len(comments)} comments\n")
    
    # Analyze in batch
    print("Analyzing comments...")
    abuse_results = abuse.batch_analyze(comments)
    
    # Moderate each comment
    moderation_summary = {
        "total": len(comments),
        "approved": 0,
        "removed": 0,
        "flagged": 0
    }
    
    for comment, abuse_result in zip(comments, abuse_results):
        # Validate against standards
        decision = standards.validate(comment.text)
        
        # Determine action
        action = "approve"
        
        if abuse_result.is_abuse:
            action = abuse_result.recommended_action
        elif decision.action != "approve":
            action = decision.action
        
        # Apply moderation
        if action != "approve":
            success = await reddit.moderate_comment(comment.id, action)
            
            # Log action
            print(f"@{comment.author_username}: {action}")
            print(f"  Reason: {abuse_result.abuse_type if abuse_result.is_abuse else decision.standard}")
            
            # Update summary
            if action == "remove":
                moderation_summary["removed"] += 1
            elif action == "flag":
                moderation_summary["flagged"] += 1
        else:
            moderation_summary["approved"] += 1
    
    # Display summary
    print(f"\nModeration Summary:")
    print(f"  Total comments: {moderation_summary['total']}")
    print(f"  Approved: {moderation_summary['approved']}")
    print(f"  Removed: {moderation_summary['removed']}")
    print(f"  Flagged: {moderation_summary['flagged']}")

asyncio.run(moderate_post_comments())
```

## Example 3: Severity-Based Moderation

```python
import asyncio
from moderation_ai.platforms import RedditAPI
from moderation_ai.analysis import AbuseDetector

async def severity_based_moderation():
    reddit = RedditAPI.from_env()
    abuse = AbuseDetector()
    
    post_id = "abc123"
    comments = await reddit.fetch_comments(post_id)
    
    # Define severity actions
    severity_actions = {
        "critical": "remove",
        "high": "remove",
        "medium": "remove",
        "low": "flag"
    }
    
    # Analyze
    results = abuse.batch_analyze(comments)
    
    print("Applying severity-based moderation...")
    for comment, result in zip(comments, results):
        if result.is_abuse:
            action = severity_actions.get(result.severity, "flag")
            print(f"@{comment.author_username}: {action}")
            print(f"  Severity: {result.severity}")
            print(f"  Type: {result.abuse_type}")
            print(f"  Confidence: {result.confidence:.2f}")
            
            # Apply action
            await reddit.moderate_comment(comment.id, action)
            print(f"  → Moderated")
        print()

asyncio.run(severity_based_moderation())
```

## Example 4: Multi-Comment Moderation

```python
import asyncio
from moderation_ai.platforms import RedditAPI

async def moderate_multiple_comments():
    reddit = RedditAPI.from_env()
    abuse = AbuseDetector()
    
    # Multiple comment IDs to moderate
    comment_ids = [
        "def456",
        "ghi789",
        "jkl012"
    ]
    
    print(f"Moderating {len(comment_ids)} comments...")
    
    for comment_id in comment_ids:
        try:
            # Fetch and analyze
            comment = await reddit.fetch_comment(comment_id)
            result = abuse.analyze(comment)
            
            # Display
            print(f"@{comment.author_username}: {comment.text[:50]}...")
            print(f"  Abuse: {result.is_abuse}")
            
            # Moderate if needed
            if result.is_abuse:
                await reddit.moderate_comment(comment_id, result.recommended_action)
                print(f"  → {result.recommended_action}")
            else:
                print(f"  → Approve")
            print()
        
        except Exception as e:
            print(f"Error moderating {comment_id}: {e}")
    
    print("Moderation complete")

asyncio.run(moderate_multiple_comments())
```

## Example 5: Real-Time Moderation Bot

```python
import asyncio
from moderation_ai.platforms import RedditAPI
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector

async def moderation_bot():
    # Initialize components
    reddit = RedditAPI.from_env()
    standards = StandardsEngine()
    abuse = AbuseDetector()
    
    # Monitor subreddit
    subreddit_name = "moderation_ai"
    
    print(f"Starting moderation bot for r/{subreddit_name}...")
    
    # Track new posts
    while True:
        # Get new posts
        posts = await reddit.fetch_subreddit_posts(
            subreddit=subreddit_name,
            sort="new",
            limit=10
        )
        
        for post in posts:
            # Get comments for post
            comments = await reddit.fetch_comments(post.id)
            
            # Analyze and moderate
            results = abuse.batch_analyze(comments)
            
            for comment, result in zip(comments, results):
                # Check against standards
                decision = standards.validate(comment.text)
                
                # Apply action
                if result.is_abuse:
                    await reddit.moderate_comment(comment.id, "remove")
                    print(f"Removed: @{comment.author_username} ({result.abuse_type})")
                elif decision.action != "approve":
                    await reddit.moderate_comment(comment.id, decision.action)
                    print(f"Action taken: @{comment.author_username} ({decision.action})")
        
        # Wait before next check
        await asyncio.sleep(300)  # Check every 5 minutes

asyncio.run(moderation_bot())
```

## Example 6: Logging and Audit Trail

```python
import asyncio
import json
from datetime import datetime
from moderation_ai.platforms import RedditAPI
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector

async def moderate_with_logging():
    reddit = RedditAPI.from_env()
    standards = StandardsEngine()
    abuse = AbuseDetector()
    
    post_id = "abc123"
    comments = await reddit.fetch_comments(post_id)
    results = abuse.batch_analyze(comments)
    
    # Create audit log
    audit_log = []
    
    print("Moderating with logging...")
    for comment, result in zip(comments, results):
        # Validate
        decision = standards.validate(comment.text)
        
        # Determine action
        action = "approve"
        if result.is_abuse:
            action = result.recommended_action
        elif decision.action != "approve":
            action = decision.action
        
        # Apply moderation
        if action != "approve":
            await reddit.moderate_comment(comment.id, action)
        
        # Log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "comment_id": comment.id,
            "author_username": comment.author_username,
            "comment_text": comment.text,
            "abuse_detected": result.is_abuse,
            "abuse_type": result.abuse_type if result.is_abuse else None,
            "severity": result.severity if result.is_abuse else None,
            "confidence": result.confidence,
            "standards_violated": decision.standards_violated,
            "violated_standards": decision.standards_violated if decision.standards_violated else None,
            "action_taken": action,
            "moderated_by": "automated"
        }
        
        audit_log.append(log_entry)
    
    # Save audit log
    with open("moderation_audit.json", "w") as f:
        json.dump(audit_log, f, indent=2)
    
    print(f"Moderated {len(comments)} comments")
    print(f"Audit log saved to moderation_audit.json")

asyncio.run(moderate_with_logging())
```

## Running Examples

### Run Basic Example

```bash
# Save as moderate_comment.py
python moderate_comment.py
```

### Run with Specific Comment

```python
# Modify example to accept comment ID as argument
import sys

comment_id = sys.argv[1] if len(sys.argv) > 1 else "def456"

# Use comment_id in script
comment = await reddit.fetch_comment(comment_id)
```

### Run Moderation Bot

```bash
# Save as moderation_bot.py
python moderation_bot.py
```

## Error Handling

### Handle Rate Limits

```python
from moderation_ai.utils import RateLimitExceeded

try:
    await reddit.moderate_comment(comment_id, "remove")
except RateLimitExceeded as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
```

### Handle Authentication Errors

```python
from moderation_ai.utils import AuthenticationError

try:
    await reddit.authenticate()
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print("Please verify your Reddit credentials and moderator permissions")
```

### Handle Permission Errors

```python
try:
    await reddit.moderate_comment(comment_id, "remove")
except Exception as e:
    if "moderator" in str(e).lower():
        print(f"Permission denied: Not a moderator")
        print("Please verify you have moderator permissions")
    else:
        raise e
```

## Tips

1. **Verify Mod Permissions**: You must be a moderator to remove comments
2. **Use Appropriate Actions**: Remove for abuse, flag for review
3. **Log All Actions**: Maintain audit trail
4. **Review False Positives**: Regularly check moderated content
5. **Update Standards**: Keep standards current and relevant

## Related Documentation

- **API Guide**: `../api-guide.md` - API usage
- **Comment Moderation**: `../comment-moderation.md` - Moderation guidelines
- **Standards**: `../../docs/standards-and-metrics.md` - Moderation rules
- **Abuse Detection**: `../../docs/comment-analysis/abuse-detection.md` - Abuse analysis

---

**Example Version**: 1.0
**Platform**: Reddit
**Status**: Working
