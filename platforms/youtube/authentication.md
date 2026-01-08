---
title: YouTube Authentication
category: platform
platform: youtube
related:
  - ./README.md
  - ./api-guide.md
  - ../../docs/api-reference/authentication.md
---

# YouTube Authentication

## Overview

YouTube Data API v3 supports API Key and OAuth 2.0 for authentication. This document explains how to set up authentication for YouTube integration.

## Authentication Types

### API Key (Recommended)

**Use Case**: Read-only access, simple setup

**Advantages**:
- Simple setup
- No OAuth flow required
- Higher quota (10,000 requests/day)
- No user authentication needed

**Limitations**:
- Read-only access
- Cannot moderate comments
- Cannot write data

### OAuth 2.0 (Required for Moderation)

**Use Case**: Read + write access, moderation

**Advantages**:
- Full API access
- Can moderate comments
- User-specific actions

**Limitations**:
- Complex OAuth flow
- Requires user approval
- Lower quota (free tier)

## Setup

### Step 1: Get API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Select YouTube Data API v3
4. Generate API key

### Step 2: Set Environment Variables

```bash
# For API Key
export YOUTUBE_API_KEY="your_api_key"

# For OAuth 2.0
export YOUTUBE_CLIENT_ID="your_client_id"
export YOUTUBE_CLIENT_SECRET="your_client_secret"
export YOUTUBE_ACCESS_TOKEN="your_access_token"
export YOUTUBE_REFRESH_TOKEN="your_refresh_token"
```

### Step 3: Initialize YouTubeAPI

```python
from moderation_ai.platforms import YouTubeAPI

# API Key
youtube = YouTubeAPI.from_env()

# OAuth 2.0
youtube = YouTubeAPI(
    client_id="your_client_id",
    client_secret="your_client_secret",
    access_token="your_access_token"
)
```

## Usage

### API Key Authentication

```python
youtube = YouTubeAPI.from_env()

# Authenticate
await youtube.authenticate()
```

### OAuth 2.0 Authentication

```python
youtube = YouTubeAPI(
    client_id="your_client_id",
    client_secret="your_client_secret",
    access_token="your_access_token"
)

await youtube.authenticate()
```

### Token Refresh

```python
# Refresh OAuth token
await youtube.refresh_token()
```

## Required Scopes

| Scope | Description | Use Case |
|-------|-------------|-----------|
| `https://www.googleapis.com/auth/youtube.readonly` | Read access | Fetch videos and comments |
| `https://www.googleapis.com/auth/youtube.force-ssl` | SSL requirement | Force HTTPS |
| `https://www.googleapis.com/auth/youtube` | Full access | All operations |

## Error Handling

### Invalid API Key

```python
from moderation_ai.utils import AuthenticationError

try:
    await youtube.authenticate()
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
```

## Security

### Never Commit Credentials

```python
# Good - from environment
youtube = YouTubeAPI.from_env()

# Bad - hardcoded
youtube = YouTubeAPI(api_key="your_key")
```

## Related Documentation

- **API Guide**: `./api-guide.md`
- **Rate Limits**: `./rate-limits.md`

---

**Last Updated**: January 2024
**Status**: Phase 2 - Documentation Complete