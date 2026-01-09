# Moderation Bot API Reference

Complete API documentation for all endpoints.

## Table of Contents

- [Authentication](#authentication)
- [Moderation Endpoints](#moderation-endpoints)
- [Platform Management](#platform-management)
- [Analytics & Reporting](#analytics--reporting)
- [Webhooks](#webhooks)
- [Rate Limiting](#rate-limiting)
- [Health & Status](#health--status)
- [Error Codes](#error-codes)

---

## Authentication

### POST /api/v1/auth/authorize

Initiates OAuth 2.0 authorization flow.

**Request Body:**
```json
{
  "platform": "instagram",
  "redirect_uri": "https://your-domain.com/callback"
  "scopes": ["user_profile", "comments", "likes"]
}
```

**Response:**
```json
{
  "authorization_url": "https://api.instagram.com/oauth/authorize?client_id=...",
  "state": "random_state_string",
  "expires_at": "2026-01-08T10:00:00Z"
}
```

### POST /api/v1/auth/token

Exchanges authorization code for access token.

**Request Body:**
```json
{
  "code": "auth_code_from_callback",
  "state": "random_state_string"
}
```

**Response:**
```json
{
  "access_token": "insta_...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "refresh_token...",
  "scope": "user_profile,comments,likes"
}
```

### POST /api/v1/auth/refresh

Refreshes expired access token.

**Request Body:**
```json
{
  "refresh_token": "your_refresh_token"
}
```

**Response:**
```json
{
  "access_token": "new_access_token",
  "expires_in": 3600,
  "refresh_token": "new_refresh_token"
}
```

### POST /api/v1/auth/logout

Invalidates current session.

**Response:**
```json
{
  "success": true
}
```

---

## Moderation Endpoints

### POST /api/v1/moderate/comment

Moderates a comment using AI analysis.

**Request Body:**
```json
{
  "platform": "instagram",
  "comment_id": "comment_123",
  "comment_text": "This comment contains profanity",
  "user_id": "user_456",
  "user_username": "testuser",
  "context": {
    "media_id": "media_789",
    "media_caption": "Post caption",
    "user_followers": 1000
  }
}
```

**Response:**
```json
{
  "comment_id": "comment_123",
  "action": "delete",
  "confidence": 0.95,
  "reasoning": {
    "profanity": {
      "detected": true,
      "confidence": 0.97,
      "severity": "high"
    },
    "spam": {
      "detected": false,
      "confidence": 0.05,
      "severity": "low"
    },
    "harassment": {
      "detected": false,
      "confidence": 0.02,
      "severity": "low"
    },
    "abuse": {
      "detected": false,
      "confidence": 0.10,
      "severity": "low"
    }
  },
  "suggested_action": "delete",
  "llm_provider": "openai",
  "llm_model": "gpt-4",
  "analysis_time_ms": 150
}
```

### POST /api/v1/moderate/batch

Moderates multiple comments in a single request.

**Request Body:**
```json
{
  "comments": [
    {
      "platform": "instagram",
      "comment_id": "comment_1",
      "comment_text": "Comment 1 text"
    },
    {
      "platform": "instagram",
      "comment_id": "comment_2",
      "comment_text": "Comment 2 text"
    }
  ]
}
```

**Response:**
```json
{
  "total_processed": 2,
  "results": [
    {
      "comment_id": "comment_1",
      "action": "allow"
    },
    {
      "comment_id": "comment_2",
      "action": "delete",
      "reasoning": {
        "profanity": {"detected": true}
      }
    }
  ]
}
```

### GET /api/v1/moderate/status/:id

Gets moderation status of a comment.

**Response:**
```json
{
  "comment_id": "comment_123",
  "current_status": "deleted",
  "original_action": "delete",
  "action_timestamp": "2026-01-08T10:30:00Z",
  "performed_by": "system",
  "history": [
    {
      "action": "delete",
      "performed_at": "2026-01-08T10:30:00Z",
      "performed_by": "system"
    }
  ]
}
```

---

## Platform Management

### POST /api/v1/instagram/connect

Connects Instagram account.

**Request Body:**
```json
{
  "access_token": "your_access_token",
  "webhook_url": "https://your-domain.com/webhooks/instagram"
}
```

**Response:**
```json
{
  "success": true,
  "platform": "instagram",
  "connected_user": {
    "id": "17841403",
    "username": "testuser"
    "profile_picture": "https://..."
  }
}
```

### POST /api/v1/instagram/disconnect

Disconnects Instagram account.

**Response:**
```json
{
  "success": true
}
```

### POST /api/v1/medium/connect

Connects Medium account.

**Request Body:**
```json
{
  "access_token": "your_access_token"
}
```

**Response:**
```json
{
  "success": true,
  "platform": "medium",
  "connected_user": {
    "id": "user_id",
    "username": "testuser"
  }
}
```

### POST /api/v1/tiktok/connect

Connects TikTok account.

**Request Body:**
```json
{
  "client_key": "your_client_key",
  "client_secret": "your_client_secret",
  "webhook_url": "https://your-domain.com/webhooks/tiktok"
}
```

**Response:**
```json
{
  "success": true,
  "platform": "tiktok",
  "connected_user": {
    "open_id": "user_open_id",
    "username": "testuser",
    "display_name": "Test User"
  }
}
```

---

## Analytics & Reporting

### GET /api/v1/analytics/overview

Get system-wide analytics overview.

**Response:**
```json
{
  "period": "24h",
  "comments_moderated": 1523,
  "actions_taken": {
    "delete": 120,
    "hide": 45,
    "flag": 23,
    "allow": 1235
  },
  "platform_breakdown": {
    "instagram": {
      "comments_moderated": 650,
      "success_rate": 0.98
    },
    "medium": {
      "comments_moderated": 320,
      "success_rate": 0.97
    },
    "tiktok": {
      "comments_moderated": 553,
      "success_rate": 0.96
    }
  },
  "llm_stats": {
    "openai": {
      "requests": 1250,
      "success_rate": 0.99
    },
    "anthropic": {
      "requests": 890,
      "success_rate": 0.97
    }
  }
}
```

### GET /api/v1/analytics/platform/:platform

Get platform-specific analytics.

**Response:**
```json
{
  "platform": "instagram",
  "period": "24h",
  "api_calls": 1250,
  "rate_limit_hits": 15,
  "average_response_time_ms": 150,
  "success_rate": 0.99
}
```

### GET /api/v1/analytics/rules/performance

Get moderation rule performance.

**Response:**
```json
{
  "rules_evaluated": 1523,
  "rule_performance": [
    {
      "rule_id": "profanity_rule",
      "triggered_count": 120,
      "false_positive_rate": 0.02,
      "false_negative_rate": 0.05
    },
    {
      "rule_id": "spam_rule",
      "triggered_count": 45,
      "false_positive_rate": 0.01,
      "false_negative_rate": 0.03
    }
  ]
}
```

---

## Webhooks

### POST /api/v1/webhooks/instagram

Registers Instagram webhook.

**Request Body:**
```json
{
  "webhook_url": "https://your-domain.com/webhooks/instagram",
  "events": ["comment.created", "comment.deleted"],
  "secret": "webhook_secret"
}
```

**Response:**
```json
{
  "webhook_id": "webhook_123",
  "status": "active",
  "verified": false
  "verification_url": "https://your-domain.com/webhooks/instagram/verify"
}
```

### POST /api/v1/webhooks/verify/:id

Verifies webhook endpoint.

**Response:**
```json
{
  "webhook_id": "webhook_123",
  "status": "verified",
  "challenge": "test_challenge_token"
}
```

---

## Rate Limiting

### GET /api/v1/rate-limit/status

Get current rate limit status.

**Response:**
```json
{
  "platform": "instagram",
  "limit": 200,
  "remaining": 185,
  "reset": "1234567890",
  "reset_time": "2026-01-08T12:00:00Z"
}
```

### GET /api/v1/rate-limit/history

Get rate limit usage history.

**Response:**
```json
{
  "platform": "instagram",
  "period": "24h",
  "usage": [
    {
      "hour": "2026-01-08T10:00:00Z",
      "requests": 180,
      "limited": 0,
      "remaining": 20
    }
  ]
}
```

---

## Health & Status

### GET /api/v1/health

System health check.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "web": "ok",
    "database": "ok",
    "redis": "ok",
    "llm_providers": {
      "openai": "ok",
      "anthropic": "ok"
    }
  },
  "timestamp": "2026-01-08T11:30:00Z"
}
```

### GET /api/v1/health/database

Database health check.

**Response:**
```json
{
  "status": "healthy",
  "connection_count": 5,
  "active_connections": 3,
  "max_connections": 20,
  "query_time_avg_ms": 50
}
```

### GET /api/v1/health/cache

Cache health check.

**Response:**
```json
{
  "status": "healthy",
  "cache_type": "redis",
  "memory_usage_mb": 125,
  "hit_rate": 0.85,
  "keys_count": 1523
}
```

---

## Error Codes

### HTTP Status Codes

| Code | Description | Solution |
|-------|-------------|----------|
| 200 | Success | - |
| 201 | Created | - |
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Refresh token |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Check resource ID |
| 429 | Rate Limit | Wait and retry |
| 500 | Server Error | Try again later |

### Error Response Format

```json
{
  "error": {
    "code": "invalid_token",
    "message": "The provided access token is invalid or has expired",
    "details": {
      "platform": "instagram",
      "token_expires_at": "2026-01-08T09:00:00Z"
    }
  }
}
```

### Common Error Codes

| Code | Message | HTTP Status | Solution |
|-------|---------|--------------|----------|
| `INVALID_TOKEN` | Invalid or expired token | 401 | Refresh token |
| `INVALID_PLATFORM` | Unsupported platform | 400 | Check platform value |
| `INVALID_COMMENT` | Comment not found | 404 | Check comment ID |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 | Wait and retry |
| `MODERATION_FAILED` | Moderation error | 500 | Check logs |
| `PLATFORM_ERROR` | Platform API error | 502 | Check platform status |
| `LLM_ERROR` | AI provider error | 502 | Check LLM status |
| `DATABASE_ERROR` | Database error | 500 | Check database |

---

## Rate Limiting

All API endpoints are rate-limited:

- **Per Platform**: 200 requests/minute
- **Per User**: 60 requests/minute
- **Per IP**: 500 requests/minute
- **Burst**: 10 requests/second

Rate limit headers:
```http
X-RateLimit-Limit: 200
X-RateLimit-Remaining: 185
X-RateLimit-Reset: 1234567890
```

---

## Authentication

All endpoints except `/health` require authentication:

**Header:**
```http
Authorization: Bearer your_access_token
```

**OAuth 2.0 Flow:**
1. Client redirects user to platform
2. User approves authorization
3. Platform redirects back with code
4. Client exchanges code for token
5. Client stores token for future requests

**Token Management:**
- Access tokens expire in 1 hour
- Refresh tokens valid for 30 days
- Automatic refresh in background
- Token storage encrypted at rest

---

## Pagination

List endpoints support pagination:

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 1523,
    "total_pages": 77,
    "has_next": true,
    "next_cursor": "abc123..."
  }
}
```

---

## WebSocket

Real-time updates via WebSocket:

**Connection URL:**
```
wss://your-domain.com/ws
```

**Event Types:**
- `comment.moderated`
- `action.executed`
- `webhook.received`
- `platform.connected`
- `rate.limit.hit`
- `alert.fired`

**Message Format:**
```json
{
  "type": "comment.moderated",
  "data": {
    "comment_id": "comment_123",
    "action": "delete"
    "timestamp": "2026-01-08T10:30:00Z"
  }
}
```

---

**API Reference v1.0** - Last Updated: January 8, 2026
