---
title: Moderate Twitter Comment Example
category: example
platform: twitter
related:
  - ../api-guide.md
  - ../comment-moderation.md
---

# Example: Moderate Twitter Comments

## Overview

This example demonstrates how to analyze and moderate Twitter comments (replies) using the Moderation AI library, including automated abuse detection and standards validation.

## Prerequisites

- Twitter API credentials with moderation permissions
- Python 3.9+ installed
- Moderation AI library installed

## Setup

### 1. Install Dependencies

```bash
pip install moderation-ai
```

### 2. Set Environment Variables

```bash
# For OAuth 1.0a (required for moderation)
export TWITTER_API_KEY="your_api_key"
export TWITTER_API_SECRET="your_api_secret"
export TWITTER_ACCESS_TOKEN="your_access_token"
export TWITTER_ACCESS_TOKEN_SECRET="your_access_token_secret"
```

Or create `.env` file:

```bash
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

## Example 1: Basic Moderation

```python
import asyncio
from moderation_ai.platforms import TwitterAPI
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector

async def moderate_single_comment():
    # Initialize components
    twitter = TwitterAPI.from_env()
    standards = StandardsEngine()
    abuse = AbuseDetector()
    
    # Comment to moderate
    comment_id = "9876543210"
    
    # Fetch comment
    print(f"Fetching comment {comment_id}...")
    comment = await twitter.fetch_comment(comment_id)
    
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
        await twitter.moderate_comment(comment_id, action)
        print(f"Comment {comment_id} has been moderated")
    else:
        print("Comment approved")

asyncio.run(moderate_single_comment())
```

## Example 2: Batch Moderation

```python
import asyncio
from moderation_ai.platforms import TwitterAPI
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector

async def moderate_tweet_replies():
    # Initialize components
    twitter = TwitterAPI.from_env()
    standards = StandardsEngine()
    abuse = AbuseDetector()
    
    # Tweet ID
    tweet_id = "1234567890"
    
    # Fetch all replies
    print(f"Fetching replies for tweet {tweet_id}...")
    comments = await twitter.fetch_comments(tweet_id)
    
    print(f"Found {len(comments)} replies\n")
    
    # Analyze in batch
    print("Analyzing comments...")
    abuse_results = abuse.batch_analyze(comments)
    
    # Moderate each comment
    moderation_summary = {
        "total": len(comments),
        "approved": 0,
        "hidden": 0,
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
            await twitter.moderate_comment(comment.id, action)
            
            # Log action
            print(f"@{comment.author_username}: {action}")
            print(f"  Reason: {abuse_result.abuse_type if abuse_result.is_abuse else decision.standard}")
            
            # Update summary
            if action == "hide":
                moderation_summary["hidden"] += 1
            elif action == "flag":
                moderation_summary["flagged"] += 1
        else:
            moderation_summary["approved"] += 1
    
    # Display summary
    print(f"\nModeration Summary:")
    print(f"  Total: {moderation_summary['total']}")
    print(f"  Approved: {moderation_summary['approved']}")
    print(f"  Hidden: {moderation_summary['hidden']}")
    print(f"  Flagged: {moderation_summary['flagged']}")

asyncio.run(moderate_tweet_replies())
```

## Example 3: Severity-Based Moderation

```python
import asyncio
from moderation_ai.platforms import TwitterAPI
from moderation_ai.analysis import AbuseDetector

async def severity_based_moderation():
    twitter = TwitterAPI.from_env()
    abuse = AbuseDetector()
    
    tweet_id = "1234567890"
    comments = await twitter.fetch_comments(tweet_id)
    
    # Define severity actions
    severity_actions = {
        "critical": "hide",
        "high": "hide",
        "medium": "flag",
        "low": "monitor"
    }
    
    results = abuse.batch_analyze(comments)
    
    for comment, result in zip(comments, results):
        if result.is_abuse:
            # Get action based on severity
            action = severity_actions.get(result.severity, "monitor")
            
            # Apply action
            if action in ["hide", "flag"]:
                await twitter.moderate_comment(comment.id, action)
            
            print(f"@{comment.author_username}")
            print(f"  Action: {action}")
            print(f"  Severity: {result.severity}")
            print(f"  Type: {result.abuse_type}")
            print(f"  Confidence: {result.confidence:.2f}")
            print()

asyncio.run(severity_based_moderation())
```

## Example 4: Real-Time Moderation Bot

```python
import asyncio
from moderation_ai.platforms import TwitterAPI
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector

async def moderation_bot():
    # Initialize components
    twitter = TwitterAPI.from_env()
    standards = StandardsEngine()
    abuse = AbuseDetector()
    
    # Track a tweet
    tweet_id = "1234567890"
    await twitter.track_post(tweet_id)
    
    print(f"Moderation bot started for tweet {tweet_id}")
    print("Waiting for comments...\n")
    
    # Define webhook handler
    async def on_comment_created(event):
        comment = event.data.comment
        
        print(f"New comment from @{comment.author_username}: {comment.text}")
        
        # Analyze for abuse
        abuse_result = abuse.analyze(comment)
        
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
            await twitter.moderate_comment(comment.id, action)
            
            print(f"  → Moderated: {action}")
            print(f"  → Reason: {abuse_result.abuse_type if abuse_result.is_abuse else decision.standard}")
        else:
            print("  → Approved")
        print()
    
    # Start webhook handler
    await twitter.start_webhook_handler(
        on_comment_created=on_comment_created
    )

asyncio.run(moderation_bot())
```

## Example 5: Logging and Audit Trail

```python
import asyncio
import json
from datetime import datetime
from moderation_ai.platforms import TwitterAPI
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector

async def moderated_with_logging():
    twitter = TwitterAPI.from_env()
    standards = StandardsEngine()
    abuse = AbuseDetector()
    
    tweet_id = "1234567890"
    comments = await twitter.fetch_comments(tweet_id)
    
    results = abuse.batch_analyze(comments)
    
    # Create audit log
    audit_log = []
    
    for comment, result in zip(comments, results):
        decision = standards.validate(comment.text)
        
        # Determine action
        action = "approve"
        
        if result.is_abuse:
            action = result.recommended_action
        elif decision.action != "approve":
            action = decision.action
        
        # Apply moderation
        if action != "approve":
            await twitter.moderate_comment(comment.id, action)
        
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

asyncio.run(moderated_with_logging())
```

## Running the Examples

### Run Basic Example

```bash
# Save as moderate_comment.py
python moderate_comment.py
```

### Run with Tweet ID

```python
# Modify example to accept tweet ID as argument
import sys

tweet_id = sys.argv[1] if len(sys.argv) > 1 else "1234567890"

# Use tweet_id in script
comments = await twitter.fetch_comments(tweet_id)
```

### Run with Webhook Server

```bash
# For real-time moderation bot
python moderate_comment.py
```

## Error Handling

### Handle Rate Limits

```python
from moderation_ai.utils import RateLimitExceeded

try:
    await twitter.moderate_comment(comment_id, "hide")
except RateLimitExceeded as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
```

### Handle Authentication Errors

```python
from moderation_ai.utils import AuthenticationError

try:
    await twitter.authenticate()
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print("Please verify your OAuth credentials")
```

## Tips

1. **Use OAuth 1.0a**: Required for moderation actions
2. **Handle edge cases**: Account for low confidence results
3. **Log all actions**: Maintain audit trail
4. **Review false positives**: Regularly check moderated content
5. **Update models**: Keep abuse detection models current

## Related Documentation

- **API Guide**: `../api-guide.md` - API usage
- **Comment Moderation**: `../comment-moderation.md` - Moderation guidelines
- **Standards**: `../../docs/standards-and-metrics.md` - Moderation rules
- **Abuse Detection**: `../../docs/comment-analysis/abuse-detection.md` - Abuse analysis

---

**Example Version**: 1.0
**Platform**: Twitter/X
**Status**: Working
