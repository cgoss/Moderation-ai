---
title: Reddit Authentication
category: platform
platform: reddit
related:
  - ./README.md
  - ./api-guide.md
  - ../../docs/api-reference/authentication.md
---

# Reddit Authentication

## Overview

Reddit API supports OAuth 2.0 for application-level access and Personal Use Script for simple script authentication. This document explains how to set up authentication for Reddit integration.

## Authentication Types

### 1. Personal Use Script (Recommended for Bots)

**Use Case**: Automated scripts, bots, simple applications

**Advantages**:
- Simple setup (username/password)
- No OAuth flow required
- Full access to user's account

**Limitations**:
- Tied to specific user account
- Cannot request user permissions
- Less flexible than OAuth

### 2. OAuth 2.0 Authorization Code

**Use Case**: Web applications requiring user login

**Advantages**:
- User-specific access
- Request permissions
- Refresh tokens
- Secure

**Limitations**:
- More complex setup
- Requires user approval
- User must log in

## Setup Instructions

### Step 1: Create Reddit Application

1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Click "Create Another App"
3. Fill in application details:
   - Name: "Moderation AI"
   - Description: "Comment moderation system"
   - About URL: Your website
   - Redirect URI: `http://localhost:8080/callback`
4. Click "Create App"

### Step 2: Generate Credentials

#### For Personal Use Script

1. Go to your app settings
2. Scroll to "Personal Use Script" section
3. Note:
   - Client ID
   - Client Secret
   - User Agent string

#### For OAuth 2.0

1. Note the Client ID and Client Secret
2. Configure redirect URI
3. Set up callback handler

### Step 3: Set Environment Variables

```bash
# For Personal Use Script
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export REDDIT_USER_AGENT="your_user_agent"
export REDDIT_USERNAME="your_username"
export REDDIT_PASSWORD="your_password"

# For OAuth 2.0
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export REDDIT_USER_AGENT="your_user_agent"
export REDDIT_ACCESS_TOKEN="your_access_token"
export REDDIT_REFRESH_TOKEN="your_refresh_token"
```

## Usage

### Personal Use Script Authentication

```python
from moderation_ai.platforms import RedditAPI

# From environment
reddit = RedditAPI.from_env()

# Explicit credentials
reddit = RedditAPI(
    client_id="your_client_id",
    client_secret="your_client_secret",
    user_agent="your_user_agent",
    username="your_username",
    password="your_password"
)

# Authenticate
await reddit.authenticate()
print("Authenticated successfully")
```

### OAuth 2.0 Authentication

```python
from moderation_ai.platforms import RedditAPI

# From environment
reddit = RedditAPI.from_env()

# With explicit tokens
reddit = RedditAPI(
    client_id="your_client_id",
    client_secret="your_client_secret",
    user_agent="your_user_agent",
    access_token="your_access_token",
    refresh_token="your_refresh_token"
)

await reddit.authenticate()
```

### Configuration File

Create `config.py`:

```python
# config.py
REDDIT_CONFIG = {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "user_agent": "your_user_agent",
    "username": "your_username",
    "password": "your_password"
}

# Usage
from moderation_ai.platforms import RedditAPI

reddit = RedditAPI(**REDDIT_CONFIG)
await reddit.authenticate()
```

## OAuth 2.0 Flow

### Authorization Code Flow

For applications requiring user authentication:

```python
from moderation_ai.utils import AuthManager

auth = AuthManager()

# Step 1: Get authorization URL
auth_url = await auth.get_reddit_auth_url(
    callback_url="http://localhost:8080/callback",
    scopes=["read", "moderate"]
)

print(f"Visit: {auth_url}")

# Step 2: Handle callback
async def handle_callback(auth_code):
    access_token = await auth.exchange_reddit_code(auth_code)
    return access_token

# Step 3: Use access token
reddit = RedditAPI(access_token=access_token)
await reddit.authenticate()
```

### Token Refresh

```python
# Refresh expired token
async def refresh_tokens():
    reddit = RedditAPI.from_env()
    await reddit.refresh_token()
    print("Tokens refreshed")
```

## User Agent String

Reddit requires a unique user agent string:

```python
# Format: platform:appname:version (by /u/username)
USER_AGENT = "python:moderation-ai:1.0 (by /u/your_username)"
```

## Required Scopes

| Scope | Description | Use Case |
|-------|-------------|-----------|
| `read` | Read posts and comments | Fetch content |
| `moderate` | Moderate content | Remove/approve comments |
| `submit` | Submit posts | Create posts |
| `subscribe` | Manage subscriptions | Track subreddits |
| `save` | Save posts | Bookmark posts |

For **comment moderation**:
```
read, moderate
```

## Token Management

### Token Validation

```python
# Validate current credentials
is_valid = await reddit.validate_credentials()

if is_valid:
    print("Credentials are valid")
else:
    print("Credentials are invalid")
```

### Token Refresh

```python
# Refresh OAuth tokens
await reddit.refresh_token()
```

### Session Management

```python
# Start session
await reddit.authenticate()

# Use session
comments = await reddit.fetch_comments(post_id)

# End session
await reddit.close_session()
```

## Error Handling

### Invalid Credentials

```python
from moderation_ai.utils import AuthenticationError

try:
    await reddit.authenticate()
except AuthenticationError as e:
    if e.code == 401:
        print("Invalid credentials")
        print("Please check your username/password or tokens")
    elif e.code == 403:
        print("Insufficient permissions")
        print("Please verify your OAuth scopes")
    else:
        print(f"Authentication error: {e.message}")
```

### Expired Token

```python
try:
    comments = await reddit.fetch_comments(post_id)
except AuthenticationError as e:
    if "expired" in e.message.lower():
        print("Token expired, refreshing...")
        await reddit.refresh_token()
        comments = await reddit.fetch_comments(post_id)
```

## Security Best Practices

### 1. Never Commit Credentials

```python
# Bad - hardcoded credentials
reddit = RedditAPI(username="user", password="pass", ...)

# Good - from environment
reddit = RedditAPI.from_env()
```

### 2. Use Environment Variables

```bash
# .env file (git-ignored)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=python:moderation-ai:1.0 (by /u/your_username)
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
```

### 3. Rotate Credentials Regularly

```python
# Rotate every 90 days
from datetime import datetime, timedelta

last_rotation = load_rotation_date()
if datetime.now() - last_rotation > timedelta(days=90):
    await rotate_credentials()
    save_rotation_date(datetime.now())
```

### 4. Use Minimum Required Scopes

```python
# Good - only needed scopes
reddit = RedditAPI(scopes=["read", "moderate"])

# Bad - excessive scopes
reddit = RedditAPI(scopes=["read", "moderate", "submit", ...])
```

### 5. Validate Tokens Before Use

```python
# Always validate
if await reddit.validate_credentials():
    await reddit.fetch_comments(post_id)
else:
    print("Invalid credentials, cannot proceed")
```

## Testing Authentication

### Test Personal Use Script

```python
import asyncio
from moderation_ai.platforms import RedditAPI

async def test_auth():
    reddit = RedditAPI.from_env()
    
    try:
        await reddit.authenticate()
        print("✓ Personal Use Script authentication successful")
        
        # Test API call
        post = await reddit.fetch_post("abc123")
        print(f"✓ Successfully fetched post: {post.title}")
        
    except AuthenticationError as e:
        print(f"✗ Authentication failed: {e.message}")

asyncio.run(test_auth())
```

### Test OAuth

```python
async def test_oauth():
    reddit = RedditAPI.from_env()
    
    try:
        await reddit.authenticate()
        print("✓ OAuth 2.0 authentication successful")
        
        # Test API call
        post = await reddit.fetch_post("abc123")
        print(f"✓ Successfully fetched post: {post.title}")
        
    except AuthenticationError as e:
        print(f"✗ Authentication failed: {e.message}")

asyncio.run(test_oauth())
```

## Troubleshooting

### Issue: 403 Forbidden

**Possible causes**:
- Insufficient OAuth scopes
- Not a moderator
- Private subreddit

**Solution**:
1. Verify OAuth scopes in app settings
2. Check if you're a moderator
3. Ensure subreddit is public

### Issue: 401 Unauthorized

**Possible causes**:
- Invalid credentials
- Expired access token
- Wrong auth method

**Solution**:
1. Verify credentials are correct
2. Refresh access token
3. Check token hasn't been revoked

### Issue: Rate Limit Errors

**Possible causes**:
- Exceeded rate limits
- Multiple requests

**Solution**:
1. Implement rate limiting
2. Upgrade API tier if needed
3. Check for duplicate requests

## Related Documentation

- **API Guide**: `./api-guide.md` - API usage
- **Rate Limits**: `./rate-limits.md` - Rate limit details
- **General Auth**: `../../docs/api-reference/authentication.md` - Cross-platform auth

---

**Last Updated**: January 2024
**Status**: Phase 2 - Documentation Complete
