# TikTok API Guide

## API Overview

The Moderation Bot integrates with the TikTok for Business API to fetch videos, retrieve comments, and perform moderation actions. This guide details the API endpoints and interactions used by the bot.

## Base URL

```
https://open.tiktokapis.com/v2
```

## Authentication

All API requests require OAuth 2.0 authentication. Include the access token in the Authorization header:

```http
Authorization: Bearer {access_token}
```

## Endpoints

### 1. User Information

#### Get User Info
```http
GET https://open.tiktokapis.com/v2/user/info/
```

**Headers:**
```http
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "data": {
    "user": {
      "display_name": "John Doe",
      "avatar_url": "https://...",
      "username": "@johndoe",
      "is_verified": true,
      "union_id": "user_union_id",
      "avatar_url_100": "https://...",
      "avatar_large_url": "https://..."
    }
  }
}
```

### 2. Video Management

#### Get User Videos
```http
GET https://open.tiktokapis.com/v2/video/list/
```

**Headers:**
```http
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `cursor` (string, optional): Pagination cursor
- `max_count` (integer, optional): Max items per page (max 20)

**Response:**
```json
{
  "data": {
    "videos": [
      {
        "id": "video_id",
        "video_description": "Video caption",
        "create_time": 1234567890,
        "cover_image_url": "https://...",
        "share_url": "https://tiktok.com/@user/video/...",
        "duration": 15,
        "height": 1080,
        "width": 1920,
        "title": "Video Title",
        "embed_html": "<html>...</html>",
        "embed_link": "https://tiktok.com/embed/v2/..."
      }
    ],
    "has_more": false,
    "cursor": "next_cursor"
  }
}
```

#### Get Video Details
```http
GET https://open.tiktokapis.com/v2/video/query/
```

**Headers:**
```http
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `video_ids` (string, required): Comma-separated video IDs

**Response:**
```json
{
  "data": {
    "videos": [
      {
        "id": "video_id",
        "video_description": "Video caption",
        "create_time": 1234567890,
        "cover_image_url": "https://...",
        "share_url": "https://tiktok.com/@user/video/...",
        "duration": 15,
        "height": 1080,
        "width": 1920,
        "title": "Video Title"
      }
    ]
  }
}
```

### 3. Comment Management

#### Get Video Comments
```http
GET https://open.tiktokapis.com/v2/video/comment/list/
```

**Headers:**
```http
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `video_id` (string, required): Video ID
- `cursor` (string, optional): Pagination cursor
- `max_count` (integer, optional): Max comments (max 100)

**Response:**
```json
{
  "data": {
    "comments": [
      {
        "id": "comment_id",
        "video_id": "video_id",
        "text": "Comment text",
        "like_count": 10,
        "reply_count": 2,
        "create_time": 1234567890,
        "parent_comment_id": "parent_id",
        "user": {
          "display_name": "Jane Doe",
          "avatar_url": "https://...",
          "username": "@janedoe",
          "is_verified": false
        },
        "is_pinned": false,
        "reply_to_comment_id": "reply_to_id",
        "reply_to_user": {
          "display_name": "John Doe",
          "username": "@johndoe"
        }
      }
    ],
    "has_more": true,
    "cursor": "next_cursor"
  }
}
```

#### Create Comment
```http
POST https://open.tiktokapis.com/v2/video/comment/create/
```

**Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "video_id": "video_id",
  "text": "Comment text",
  "reply_to_comment_id": "comment_id"
}
```

**Response:**
```json
{
  "data": {
    "comment": {
      "id": "new_comment_id",
      "video_id": "video_id",
      "text": "Comment text",
      "like_count": 0,
      "reply_count": 0,
      "create_time": 1234567890
    }
  }
}
```

#### Delete Comment
```http
DELETE https://open.tiktokapis.com/v2/video/comment/delete/
```

**Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "comment_id": "comment_id"
}
```

**Response:**
```json
{
  "data": {}
}
```

#### Pin Comment
```http
POST https://open.tiktokapis.com/v2/video/comment/pin/
```

**Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "comment_id": "comment_id"
}
```

**Response:**
```json
{
  "data": {}
}
```

#### Unpin Comment
```http
POST https://open.tiktokapis.com/v2/video/comment/unpin/
```

**Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "comment_id": "comment_id"
}
```

**Response:**
```json
{
  "data": {}
}
```

### 4. Webhooks

#### Register Webhook
```http
POST https://open.tiktokapis.com/v2/webhook/register/
```

**Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "url": "https://your-domain.com/webhook",
  "secret": "your_webhook_secret",
  "events": [
    "video_comment_created",
    "video_comment_deleted"
  ]
}
```

**Response:**
```json
{
  "data": {
    "webhook_id": "webhook_id"
  }
}
```

## API Client Implementation

### Base Client

```python
import requests
from typing import Optional, Dict, List

class TikTokAPIClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://open.tiktokapis.com/v2"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, endpoint: str, method: str = "GET",
                     params: Optional[Dict] = None,
                     data: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        response = requests.request(
            method,
            url,
            headers=self.headers,
            params=params,
            json=data
        )
        response.raise_for_status()
        return response.json()
```

### Video Operations

```python
    def get_user_videos(self, cursor: str = None, max_count: int = 20) -> List[Dict]:
        """Get user's videos"""
        params = {"max_count": min(max_count, 20)}
        if cursor:
            params["cursor"] = cursor
        
        response = self._make_request("/video/list/", params=params)
        return response.get("data", {}).get("videos", [])
    
    def get_video_details(self, video_ids: List[str]) -> List[Dict]:
        """Get details for specific videos"""
        params = {"video_ids": ",".join(video_ids)}
        response = self._make_request("/video/query/", params=params)
        return response.get("data", {}).get("videos", [])
```

### Comment Operations

```python
    def get_video_comments(self, video_id: str, cursor: str = None, 
                        max_count: int = 100) -> List[Dict]:
        """Get comments for a video"""
        params = {
            "video_id": video_id,
            "max_count": min(max_count, 100)
        }
        if cursor:
            params["cursor"] = cursor
        
        response = self._make_request("/video/comment/list/", params=params)
        return response.get("data", {}).get("comments", [])
    
    def create_comment(self, video_id: str, text: str, 
                     reply_to_comment_id: str = None) -> Optional[Dict]:
        """Create a comment"""
        data = {"video_id": video_id, "text": text}
        if reply_to_comment_id:
            data["reply_to_comment_id"] = reply_to_comment_id
        
        response = self._make_request("/video/comment/create/", method="POST", data=data)
        return response.get("data", {}).get("comment")
    
    def delete_comment(self, comment_id: str) -> bool:
        """Delete a comment"""
        try:
            self._make_request("/video/comment/delete/", method="POST", 
                             data={"comment_id": comment_id})
            return True
        except Exception:
            return False
    
    def pin_comment(self, comment_id: str) -> bool:
        """Pin a comment"""
        try:
            self._make_request("/video/comment/pin/", method="POST",
                             data={"comment_id": comment_id})
            return True
        except Exception:
            return False
    
    def unpin_comment(self, comment_id: str) -> bool:
        """Unpin a comment"""
        try:
            self._make_request("/video/comment/unpin/", method="POST",
                             data={"comment_id": comment_id})
            return True
        except Exception:
            return False
```

## Error Handling

### Common Error Codes

- `200` - Success
- `401` - Unauthorized (invalid or expired token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

### Error Response Format

```json
{
  "error": {
    "code": "access_token_invalid",
    "message": "The access token provided is invalid",
    "log_id": "20250108100000000000000000000000"
  }
}
```

### Error Handling Example

```python
def safe_api_call(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print("Authentication failed. Please refresh access token.")
            elif e.response.status_code == 429:
                print("Rate limit exceeded. Please retry later.")
            else:
                print(f"API error: {e.response.status_code}")
            return None
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return None
    return wrapper
```

## Best Practices

1. **Pagination**: Always handle pagination for large datasets
2. **Rate Limiting**: Implement backoff strategies for rate limits
3. **Error Handling**: Robust error handling for all API calls
4. **Caching**: Cache responses to reduce API calls
5. **Token Refresh**: Implement OAuth token refresh mechanism
6. **Monitoring**: Track API usage and errors

## Limitations

1. **Comment Pagination**: Maximum 100 comments per request
2. **Video Pagination**: Maximum 20 videos per request
3. **Rate Limits**: Strict rate limits enforced
4. **Access**: Requires approved TikTok for Business API access
5. **Features**: Some features limited to business accounts

## Additional Resources

- [TikTok for Business API Documentation](https://developers.tiktok.com/doc/)
- [TikTok API Reference](https://developers.tiktok.com/doc/reference/)
- [TikTok Developer Portal](https://developers.tiktok.com/)
