---
title: Authentication Patterns
category: core
related:
  - ./README.md
  - ./error-handling.md
  - ../platforms/twitter/authentication.md
  - ../platforms/reddit/authentication.md
---

# Authentication Patterns

## Overview

All platform integrations in Moderation AI use a unified authentication interface through the `AuthManager` utility. This document describes cross-platform authentication patterns, credential management, and best practices.

## Authentication Architecture

```
Application
    ↓
AuthManager (Unified Interface)
    ↓
┌─────────────┬─────────────┬──────────────┐
│  Twitter    │   Reddit    │   YouTube    │
│  OAuth 2.0  │  OAuth 2.0  │  OAuth/API   │
└─────────────┴─────────────┴──────────────┘
```

## AuthManager Interface

The `AuthManager` provides a unified interface for all authentication operations:

```python
from moderation_ai.utils import AuthManager

auth = AuthManager()

# Get credentials for a platform
credentials = await auth.get_credentials("twitter")

# Refresh access token
await auth.refresh_token("twitter")

# Validate credentials
is_valid = await auth.validate("twitter")

# Revoke credentials
await auth.revoke("twitter")
```

## Credential Storage Strategies

### 1. Environment Variables (Recommended)

Store credentials in environment variables:

```bash
# .env file (git-ignored)
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_BEARER_TOKEN=your_token

REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=your_user_agent

YOUTUBE_API_KEY=your_key
```

Usage:

```python
import os
from moderation_ai.platforms import TwitterAPI

# Load from environment
api_key = os.getenv("TWITTER_API_KEY")
twitter = TwitterAPI(api_key=api_key, ...)

# Or use convenience method
twitter = TwitterAPI.from_env()
```

### 2. Configuration File

Store credentials in a secure configuration file:

```python
# config.json
{
  "twitter": {
    "api_key": "your_key",
    "api_secret": "your_secret",
    "bearer_token": "your_token"
  },
  "reddit": {
    "client_id": "your_client_id",
    "client_secret": "your_secret",
    "user_agent": "your_user_agent"
  }
}
```

Usage:

```python
from moderation_ai.utils import Config

config = Config.from_file("config.json")
twitter = TwitterAPI(**config.twitter)
```

### 3. Secret Management Service

For production, use a secret management service:

```python
from moderation_ai.utils import SecretManager

# AWS Secrets Manager
secrets = SecretManager(provider="aws", region="us-east-1")
twitter_creds = await secrets.get("twitter")
```

## Platform-Specific Authentication

### Twitter/X

**Auth Type**: OAuth 2.0 Bearer Token

```python
from moderation_ai.platforms import TwitterAPI

# Method 1: Bearer Token (read-only, common for moderation)
twitter = TwitterAPI(
    bearer_token="your_bearer_token"
)

# Method 2: OAuth 1.0a (user context, read/write)
twitter = TwitterAPI(
    api_key="your_api_key",
    api_secret="your_api_secret",
    access_token="your_access_token",
    access_token_secret="your_access_token_secret"
)

# Method 3: From environment
twitter = TwitterAPI.from_env()
```

**Required Scopes for Moderation**:
- `tweet.read` - Read tweets
- `users.read` - Read user information
- `mute.read` - Read mute lists (if applicable)

**Credential Setup**:
1. Create Twitter Developer account
2. Create a new app
3. Generate API key and secret
4. Generate Bearer Token
5. Set environment variables

### Reddit

**Auth Type**: OAuth 2.0 Authorization Code Flow

```python
from moderation_ai.platforms import RedditAPI

# Method 1: Client credentials (script app)
reddit = RedditAPI(
    client_id="your_client_id",
    client_secret="your_client_secret",
    user_agent="your_user_agent"
)

# Method 2: OAuth with user context
reddit = RedditAPI(
    client_id="your_client_id",
    client_secret="your_client_secret",
    user_agent="your_user_agent",
    username="your_username",
    password="your_password"
)

# Method 3: From environment
reddit = RedditAPI.from_env()
```

**Required Scopes for Moderation**:
- `read` - Read posts and comments
- `modconfig` - Access subreddit configuration (if moderator)

**Credential Setup**:
1. Create Reddit account
2. Go to reddit.com/prefs/apps
3. Create script application
4. Get client ID and secret
5. Set environment variables

### YouTube

**Auth Type**: OAuth 2.0 or API Key

```python
from moderation_ai.platforms import YouTubeAPI

# Method 1: API Key (read-only)
youtube = YouTubeAPI(api_key="your_api_key")

# Method 2: OAuth 2.0 (user context)
youtube = YouTubeAPI(
    client_id="your_client_id",
    client_secret="your_client_secret",
    refresh_token="your_refresh_token"
)

# Method 3: From environment
youtube = YouTubeAPI.from_env()
```

**Required Scopes for Moderation**:
- `https://www.googleapis.com/auth/youtube.readonly` - Read comments

**Credential Setup**:
1. Create Google Cloud project
2. Enable YouTube Data API v3
3. Create OAuth 2.0 credentials
4. Or create API key for read-only access
5. Set environment variables

### Instagram

**Auth Type**: OAuth 2.0 (Instagram Graph API)

```python
from moderation_ai.platforms import InstagramAPI

instagram = InstagramAPI(
    client_id="your_client_id",
    client_secret="your_client_secret",
    access_token="your_access_token"
)

# From environment
instagram = InstagramAPI.from_env()
```

**Required Permissions for Moderation**:
- `instagram_basic` - Basic read access
- `instagram_manage_comments` - Read and moderate comments

### Medium

**Auth Type**: OAuth 2.0 or API Token

```python
from moderation_ai.platforms import MediumAPI

# Method 1: API Token
medium = MediumAPI(token="your_token")

# Method 2: OAuth 2.0
medium = MediumAPI(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# From environment
medium = MediumAPI.from_env()
```

### TikTok

**Auth Type**: OAuth 2.0

```python
from moderation_ai.platforms import TikTokAPI

tiktok = TikTokAPI(
    client_key="your_client_key",
    client_secret="your_client_secret"
)

# From environment
tiktok = TikTokAPI.from_env()
```

## OAuth 2.0 Flow Patterns

### Authorization Code Flow

Used when user-specific permissions are required:

```python
from moderation_ai.utils import AuthManager

auth = AuthManager()

# Step 1: Get authorization URL
auth_url = auth.get_authorization_url(
    platform="twitter",
    redirect_uri="http://localhost:8080/callback",
    scopes=["tweet.read", "users.read"]
)

# Step 2: User visits auth_url and authorizes
# Step 3: Handle callback
access_token = await auth.handle_callback(
    platform="twitter",
    code="authorization_code_from_callback",
    redirect_uri="http://localhost:8080/callback"
)
```

### Client Credentials Flow

Used for application-level access (no user context):

```python
from moderation_ai.utils import AuthManager

auth = AuthManager()

# Get access token using client credentials
access_token = await auth.get_access_token(
    platform="twitter",
    client_id="your_client_id",
    client_secret="your_client_secret"
)
```

### Token Refresh

Automatically refresh expired tokens:

```python
from moderation_ai.utils import AuthManager

auth = AuthManager()

# Check if token needs refresh
if await auth.needs_refresh("twitter"):
    await auth.refresh_token("twitter")

# Get fresh access token
access_token = await auth.get_credentials("twitter").access_token
```

## Token Management

### Token Storage

Tokens are cached in memory and optionally persisted:

```python
from moderation_ai.utils import AuthManager

auth = AuthManager(cache_enabled=True, cache_file=".auth_cache.json")

# Tokens are automatically cached
credentials = await auth.get_credentials("twitter")

# Clear cache if needed
auth.clear_cache()
```

### Token Rotation

For security, rotate tokens periodically:

```python
from moderation_ai.utils import AuthManager

auth = AuthManager()

# Force token refresh
await auth.refresh_token("twitter", force=True)

# Revoke old token
await auth.revoke("twitter")
```

## Multi-Tenant Authentication

For applications serving multiple users:

```python
from moderation_ai.utils import AuthManager

auth = AuthManager()

# Store credentials per user
await auth.set_credentials("twitter", user_id="user123", credentials={
    "access_token": "...",
    "refresh_token": "..."
})

# Get credentials for specific user
credentials = await auth.get_credentials("twitter", user_id="user123")
```

## Authentication Errors

### Common Error Codes

| Error Code | Meaning | Resolution |
|------------|---------|------------|
| 401 | Invalid credentials | Verify credentials are correct |
| 403 | Insufficient permissions | Check OAuth scopes |
| 429 | Rate limit exceeded | Wait and retry |
| 500 | Platform error | Retry with backoff |

### Error Handling Example

```python
from moderation_ai.utils import AuthManager, AuthenticationError

auth = AuthManager()

try:
    credentials = await auth.get_credentials("twitter")
except AuthenticationError as e:
    if e.code == 401:
        print("Invalid credentials - please check API key")
    elif e.code == 403:
        print("Insufficient permissions - check OAuth scopes")
    else:
        print(f"Authentication error: {e}")
```

## Security Best Practices

### 1. Never Commit Credentials
```python
# Bad - hardcoded credentials
api = TwitterAPI(api_key="abc123", ...)

# Good - from environment
api = TwitterAPI.from_env()
```

### 2. Use Least Privilege
```python
# Request only necessary scopes
scopes = ["tweet.read"]  # Only read tweets, not write
```

### 3. Validate Credentials
```python
from moderation_ai.utils import AuthManager

auth = AuthManager()

# Validate before use
if not await auth.validate("twitter"):
    raise Exception("Invalid credentials")
```

### 4. Rotate Tokens
```python
# Rotate tokens periodically
await auth.refresh_token("twitter", force=True)
```

### 5. Secure Storage
```python
# Use encryption for stored tokens
auth = AuthManager(encryption_key=os.getenv("ENCRYPTION_KEY"))
```

## Testing Authentication

### Mock Authentication (Testing)

```python
from unittest.mock import Mock
from moderation_ai.platforms import TwitterAPI

# Mock authentication for tests
twitter = TwitterAPI.from_env()
twitter.authenticate = Mock(return_value=True)

# Test with mock
await twitter.authenticate()
```

### Validation Tests

```python
from moderation_ai.utils import AuthManager

auth = AuthManager()

# Test all platform credentials
platforms = ["twitter", "reddit", "youtube"]
for platform in platforms:
    if await auth.validate(platform):
        print(f"{platform}: ✓ Valid")
    else:
        print(f"{platform}: ✗ Invalid")
```

## Troubleshooting

### Issue: "Invalid credentials"

**Possible causes**:
- Typo in API key/secret
- Expired access token
- Wrong environment variable name

**Resolution**:
- Verify credentials match platform dashboard
- Check token hasn't expired
- Verify environment variable names

### Issue: "Insufficient permissions"

**Possible causes**:
- Missing OAuth scopes
- App not approved for scopes
- Wrong app type

**Resolution**:
- Check OAuth scopes in app configuration
- Ensure app is approved for required permissions
- Use correct app type (script vs. installed)

### Issue: "Rate limit exceeded"

**Possible causes**:
- Too many authentication attempts
- Token refresh too frequent

**Resolution**:
- Implement exponential backoff
- Cache tokens to reduce refresh frequency
- Use rate limiting

## Related Documentation

- **Platform-specific auth**: `../platforms/{platform}/authentication.md`
- **Error handling**: `./error-handling.md`
- **Configuration**: `../ARCHITECTURE.md#configuration-management`

---

**Last Updated**: January 2024
**Status**: Phase 1 - Documentation Phase
