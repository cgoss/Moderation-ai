---
title: Twitter Authentication
category: platform
platform: twitter
related:
  - ./README.md
  - ./api-guide.md
  - ../../docs/api-reference/authentication.md
---

# Twitter Authentication

## Overview

Twitter API v2 supports OAuth 2.0 for both read-only access and full read/write capabilities. This document explains how to set up authentication for the Moderation AI Twitter integration.

## Authentication Types

### 1. OAuth 2.0 Bearer Token (Read-Only)

**Use Case**: Fetching tweets, reading comments, analyzing content

**Advantages**:
- Simple setup
- Higher rate limits
- No user context required

**Limitations**:
- Read-only access
- Cannot moderate content
- Cannot post tweets

### 2. OAuth 1.0a User Context (Read/Write)

**Use Case**: Moderate comments, hide replies, delete tweets

**Advantages**:
- Full read/write access
- Can moderate user's own content
- Can post comments

**Limitations**:
- More complex setup
- Lower rate limits
- Requires user authentication

## Setup Instructions

### Prerequisites

1. Twitter Developer account
2. Created a project and app
3. Generated API keys and secrets

### Step 1: Create Twitter Developer Account

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Sign up for a developer account
3. Complete application process

### Step 2: Create Project and App

1. Navigate to Developer Portal
2. Click "Create Project"
3. Enter project details:
   - Name: "Moderation AI"
   - Description: "Comment moderation system"
4. Create an app within the project

### Step 3: Generate Credentials

#### For Bearer Token (Read-Only)

1. Go to App Settings
2. Navigate to "Keys and Tokens"
3. Generate Bearer Token
4. Copy and save the token

#### For OAuth 1.0a (User Context)

1. Go to App Settings
2. Navigate to "Keys and Tokens"
3. Generate Consumer Keys (API Key and Secret)
4. Generate Access Token and Token Secret

### Step 4: Configure App Permissions

1. Go to App Settings → Permissions
2. Set appropriate permissions:
   - **Read-only**: `tweet.read`, `users.read`
   - **Read and Write**: `tweet.read`, `tweet.write`, `tweet.moderate.write`
3. Save changes

### Step 5: Set Environment Variables

```bash
# For Bearer Token
export TWITTER_BEARER_TOKEN="your_bearer_token_here"

# For OAuth 1.0a
export TWITTER_API_KEY="your_api_key"
export TWITTER_API_SECRET="your_api_secret"
export TWITTER_ACCESS_TOKEN="your_access_token"
export TWITTER_ACCESS_TOKEN_SECRET="your_access_token_secret"
```

## Usage

### Bearer Token Authentication

```python
from moderation_ai.platforms import TwitterAPI

# From environment
twitter = TwitterAPI.from_env()

# Explicit credentials
twitter = TwitterAPI(
    bearer_token="your_bearer_token"
)

# Authenticate
await twitter.authenticate()
print("Authenticated successfully")
```

### OAuth 1.0a Authentication

```python
from moderation_ai.platforms import TwitterAPI

# From environment
twitter = TwitterAPI.from_env()

# Explicit credentials
twitter = TwitterAPI(
    api_key="your_api_key",
    api_secret="your_api_secret",
    access_token="your_access_token",
    access_token_secret="your_access_token_secret"
)

# Authenticate
await twitter.authenticate()
print("Authenticated successfully")
```

### Configuration File

Create `config.py`:

```python
# config.py
TWITTER_CONFIG = {
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "bearer_token": "your_bearer_token",
    "access_token": "your_access_token",
    "access_token_secret": "your_access_token_secret"
}

# Usage
from moderation_ai.platforms import TwitterAPI

twitter = TwitterAPI(**TWITTER_CONFIG)
await twitter.authenticate()
```

## OAuth 2.0 Flows

### Authorization Code Flow (User Context)

For applications requiring user authentication:

```python
from moderation_ai.utils import AuthManager

auth = AuthManager()

# Step 1: Get authorization URL
auth_url = await auth.get_twitter_auth_url(
    callback_url="http://localhost:8080/callback",
    scopes=["tweet.read", "tweet.write"]
)

print(f"Visit: {auth_url}")

# Step 2: Handle callback
async def handle_callback(auth_code):
    access_token = await auth.exchange_twitter_code(auth_code)
    return access_token

# Step 3: Use access token
twitter = TwitterAPI(access_token=access_token)
await twitter.authenticate()
```

### Client Credentials Flow (App-Only)

For read-only access without user context:

```python
from moderation_ai.utils import AuthManager

auth = AuthManager()

# Get bearer token
bearer_token = await auth.get_twitter_bearer_token(
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# Use bearer token
twitter = TwitterAPI(bearer_token=bearer_token)
await twitter.authenticate()
```

## Required Scopes

| Scope | Description | Use Case |
|-------|-------------|-----------|
| `tweet.read` | Read tweets | Fetch tweets and replies |
| `tweet.write` | Write tweets | Post comments |
| `tweet.moderate.write` | Moderate tweets | Hide replies |
| `users.read` | Read users | Get user information |
| `follows.read` | Read follows | Check followers |

For **read-only moderation analysis**:
```
tweet.read, users.read
```

For **full moderation capabilities**:
```
tweet.read, tweet.write, tweet.moderate.write, users.read
```

## Token Management

### Token Validation

```python
# Validate current credentials
is_valid = await twitter.validate_credentials()

if is_valid:
    print("Credentials are valid")
else:
    print("Credentials are invalid")
```

### Token Refresh

```python
# Refresh OAuth tokens
await twitter.refresh_token()
```

### Token Revocation

```python
# Revoke access
await twitter.revoke_token()
```

## Error Handling

### Invalid Credentials

```python
from moderation_ai.utils import AuthenticationError

try:
    await twitter.authenticate()
except AuthenticationError as e:
    if e.code == 401:
        print("Invalid credentials")
        print("Please check your API keys and secrets")
    elif e.code == 403:
        print("Insufficient permissions")
        print("Please verify your OAuth scopes")
    else:
        print(f"Authentication error: {e.message}")
```

### Expired Token

```python
try:
    comments = await twitter.fetch_comments(tweet_id)
except AuthenticationError as e:
    if "expired" in e.message.lower():
        print("Token expired, refreshing...")
        await twitter.refresh_token()
        comments = await twitter.fetch_comments(tweet_id)
```

## Security Best Practices

### 1. Never Commit Credentials

```python
# Bad - hardcoded credentials
twitter = TwitterAPI(api_key="abc123", ...)

# Good - from environment
twitter = TwitterAPI.from_env()
```

### 2. Use Environment Variables

```bash
# .env file (git-ignored)
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_BEARER_TOKEN=your_bearer_token
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
twitter = TwitterAPI(scopes=["tweet.read"])

# Bad - excessive scopes
twitter = TwitterAPI(scopes=["tweet.read", "tweet.write", "users.read", ...])
```

### 5. Validate Tokens Before Use

```python
# Always validate
if await twitter.validate_credentials():
    await twitter.fetch_comments(tweet_id)
else:
    print("Invalid credentials, cannot proceed")
```

## Testing Authentication

### Test Bearer Token

```python
import asyncio
from moderation_ai.platforms import TwitterAPI

async def test_bearer_token():
    twitter = TwitterAPI.from_env()
    
    try:
        await twitter.authenticate()
        print("✓ Bearer token authentication successful")
        
        # Test API call
        tweet = await twitter.fetch_tweet("1234567890")
        print(f"✓ Successfully fetched tweet: {tweet.text}")
        
    except AuthenticationError as e:
        print(f"✗ Authentication failed: {e.message}")

asyncio.run(test_bearer_token())
```

### Test OAuth 1.0a

```python
async def test_oauth():
    twitter = TwitterAPI.from_env()
    
    try:
        await twitter.authenticate()
        print("✓ OAuth 1.0a authentication successful")
        
        # Test moderation action
        await twitter.moderate_comment("9876543210", "hide")
        print("✓ Successfully moderated comment")
        
    except AuthenticationError as e:
        print(f"✗ Authentication failed: {e.message}")

asyncio.run(test_oauth())
```

## Troubleshooting

### Issue: 403 Forbidden

**Possible causes**:
- Insufficient OAuth scopes
- App not approved for requested scopes
- Wrong API tier

**Solution**:
1. Verify OAuth scopes in app settings
2. Check app is approved for required permissions
3. Verify API access level

### Issue: 401 Unauthorized

**Possible causes**:
- Invalid API key or secret
- Expired bearer token
- Wrong access token

**Solution**:
1. Verify credentials are correct
2. Regenerate bearer token if expired
3. Check token hasn't been revoked

### Issue: 429 Rate Limit Exceeded

**Possible causes**:
- Exceeded rate limits
- Multiple tokens being used

**Solution**:
1. Implement rate limiting
2. Upgrade API tier if needed
3. Check for duplicate requests

### Issue: Insufficient Permissions

**Possible causes**:
- Missing OAuth scopes
- App permissions not updated

**Solution**:
1. Add required OAuth scopes
2. Update app permissions
3. Regenerate tokens after permissions change

## Multi-Tenant Setup

For applications serving multiple users:

```python
from moderation_ai.utils import TenantManager

manager = TenantManager()

# Register tenant
await manager.register_tenant(
    tenant_id="tenant1",
    platform="twitter",
    credentials={
        "api_key": "tenant1_key",
        "api_secret": "tenant1_secret",
        "access_token": "tenant1_token"
    }
)

# Get tenant-specific API
twitter = await manager.get_twitter_api("tenant1")
await twitter.authenticate()
```

## Related Documentation

- **API Guide**: `./api-guide.md` - API usage
- **Rate Limits**: `./rate-limits.md` - Rate limit details
- **General Auth**: `../../docs/api-reference/authentication.md` - Cross-platform auth

---

**Last Updated**: January 2024
**Status**: Phase 2 - Documentation Complete
