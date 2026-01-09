# Medium API Guide

## API Overview

The Moderation Bot integrates with the Medium API to fetch articles, retrieve comments, and perform moderation actions. This guide details the API endpoints and interactions used by the bot.

## Base URL

```
https://api.medium.com/v1
```

## Authentication

All API requests require OAuth 2.0 authentication. Include the access token in the Authorization header:

```http
Authorization: Bearer {access_token}
```

## Endpoints

### 1. User Information

#### Get Current User
```http
GET /me
```

**Response:**
```json
{
  "data": {
    "id": "5303d74c64d66366f003d0fc",
    "username": "jordan",
    "name": "Jordan Lewis",
    "url": "https://medium.com/@jordan",
    "imageUrl": "https://cdn-images-1.medium.com/fit/c/200/200/1*QVp..."
  }
}
```

### 2. Publications

#### Get Publications by User
```http
GET /users/{userId}/publications
```

**Parameters:**
- `userId` (string): The user's ID

**Response:**
```json
{
  "data": [
    {
      "id": "b969ac62a46b",
      "name": "The Startup",
      "description": "The best advice from the best people in the startup world.",
      "url": "https://medium.com/the-startup",
      "imageUrl": "https://cdn-images-1.medium.com/fit/c/200/200/0*U..."
    }
  ]
}
```

#### Get Publication Contributors
```http
GET /publications/{publicationId}/contributors
```

**Parameters:**
- `publicationId` (string): The publication's ID

**Response:**
```json
{
  "data": [
    {
      "publicationId": "b969ac62a46b",
      "userId": "5303d74c64d66366f003d0fc",
      "role": "editor"
    }
  ]
}
```

### 3. Articles

#### Get Articles by Author
```http
GET /users/{authorId}/articles
```

**Parameters:**
- `authorId` (string): The author's user ID

**Response:**
```json
{
  "data": [
    {
      "id": "68bb8f8f5c1",
      "title": "Hello World",
      "authorId": "5303d74c64d66366f003d0fc",
      "tags": ["hello", "world"],
      "url": "https://medium.com/@jordan/hello-world-68bb8f8f5c1",
      "imageUrl": "https://cdn-images-1.medium.com/fit/c/700/700/0*5...",
      "publishedAt": 1452763256056
    }
  ]
}
```

#### Get Articles by Publication
```http
GET /publications/{publicationId}/posts
```

**Parameters:**
- `publicationId` (string): The publication's ID

**Response:**
```json
{
  "data": [
    {
      "id": "68bb8f8f5c1",
      "title": "Hello World",
      "authorId": "5303d74c64d66366f003d0fc",
      "tags": ["hello", "world"],
      "url": "https://medium.com/@jordan/hello-world-68bb8f8f5c1",
      "publishedAt": 1452763256056
    }
  ]
}
```

#### Get Article Content
```http
GET /posts/{postId}
```

**Parameters:**
- `postId` (string): The article's ID

**Response:**
```json
{
  "data": {
    "id": "68bb8f8f5c1",
    "title": "Hello World",
    "authorId": "5303d74c64d66366f003d0fc",
    "content": "<p>Hello World!</p>",
    "contentFormat": "html",
    "publishStatus": "public",
    "publishedAt": 1452763256056,
    "url": "https://medium.com/@jordan/hello-world-68bb8f8f5c1",
    "virtuals": {
      "wordCount": 2,
      "readingTime": 0.01
    }
  }
}
```

### 4. Comments

#### Get Comments on Article
```http
GET /posts/{postId}/responses
```

**Parameters:**
- `postId` (string): The article's ID

**Note**: The Medium API does not provide a direct endpoint for comments. Comments are called "responses" on Medium.

**Response:**
```json
{
  "data": [
    {
      "id": "68bb8f8f5c1d",
      "creatorId": "5303d74c64d66366f003d0fd",
      "content": "<p>Great article!</p>",
      "contentFormat": "html",
      "parentId": "68bb8f8f5c1",
      "createdAt": 1452763256057,
      "voteCount": 10
    }
  ]
}
```

#### Get Comments by User
```http
GET /users/{userId}/responses
```

**Parameters:**
- `userId` (string): The user's ID

**Response:**
```json
{
  "data": [
    {
      "id": "68bb8f8f5c1d",
      "creatorId": "5303d74c64d66366f003d0fd",
      "content": "<p>Great article!</p>",
      "contentFormat": "html",
      "parentId": "68bb8f8f5c1",
      "createdAt": 1452763256057
    }
  ]
}
```

### 5. Moderation Actions

**Important**: Medium's API has very limited moderation endpoints. Most moderation actions require:
- Being the article author
- Being a publication admin/editor
- Using alternative methods (e.g., direct API calls with additional permissions)

#### Delete Comment
```http
DELETE /responses/{responseId}
```

**Parameters:**
- `responseId` (string): The comment's ID

**Response:**
```
204 No Content
```

**Note**: This requires the authenticated user to be the comment author or have appropriate permissions.

## API Client Implementation

### Base Client

```python
import requests
from typing import Optional, Dict, List

class MediumAPIClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.medium.com/v1"
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

### Article Operations

```python
    def get_user_articles(self, user_id: str) -> List[Dict]:
        """Get articles by user"""
        response = self._make_request(f"/users/{user_id}/articles")
        return response.get("data", [])

    def get_publication_articles(self, publication_id: str) -> List[Dict]:
        """Get articles by publication"""
        response = self._make_request(
            f"/publications/{publication_id}/posts"
        )
        return response.get("data", [])

    def get_article(self, post_id: str) -> Optional[Dict]:
        """Get specific article"""
        response = self._make_request(f"/posts/{post_id}")
        return response.get("data")
```

### Comment Operations

```python
    def get_article_comments(self, post_id: str) -> List[Dict]:
        """Get comments on an article"""
        response = self._make_request(f"/posts/{post_id}/responses")
        return response.get("data", [])

    def get_user_comments(self, user_id: str) -> List[Dict]:
        """Get comments by user"""
        response = self._make_request(f"/users/{user_id}/responses")
        return response.get("data", [])

    def delete_comment(self, comment_id: str) -> bool:
        """Delete a comment"""
        try:
            self._make_request(
                f"/responses/{comment_id}",
                method="DELETE"
            )
            return True
        except Exception:
            return False
```

### Publication Operations

```python
    def get_publications(self, user_id: str) -> List[Dict]:
        """Get publications for a user"""
        response = self._make_request(f"/users/{user_id}/publications")
        return response.get("data", [])

    def get_publication_contributors(self, publication_id: str) -> List[Dict]:
        """Get contributors to a publication"""
        response = self._make_request(
            f"/publications/{publication_id}/contributors"
        )
        return response.get("data", [])
```

## Error Handling

### Common Error Codes

- `401 Unauthorized`: Invalid or expired access token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource doesn't exist
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Medium API error

### Error Response Format

```json
{
  "errors": [
    {
      "message": "Access token not found",
      "code": 6001
    }
  ]
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

1. **Comment Management**: Limited comment moderation endpoints
2. **Real-time Updates**: No real-time comment notifications (webhooks limited)
3. **Bulk Operations**: No bulk delete or moderation operations
4. **Search**: Limited search capabilities
5. **Filtering**: Limited filtering options for articles and comments

## Additional Resources

- [Medium API Documentation](https://github.com/Medium/medium-api-docs)
- [Medium API Issues](https://github.com/Medium/medium-api-docs/issues)
- [OAuth 2.0 Guide](https://medium.com/developers)
