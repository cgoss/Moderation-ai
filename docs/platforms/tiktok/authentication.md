# TikTok Authentication Guide

## Overview

TikTok uses OAuth 2.0 for authentication and authorization. This guide details how to set up and manage OAuth 2.0 authentication for the Moderation Bot.

## OAuth 2.0 Flow

TikTok supports the Authorization Code grant type for OAuth 2.0:

1. **Authorization Request**: User authorizes the application
2. **Authorization Code**: Receive authorization code from TikTok
3. **Access Token Exchange**: Exchange authorization code for access token
4. **Token Refresh**: Refresh expired tokens

## Setting Up OAuth

### 1. Create TikTok Application

1. Go to [TikTok Developer Portal](https://developers.tiktok.com/)
2. Log in with your TikTok account
3. Create a new application
4. Configure application settings:
   - Application Name
   - Application Description
   - Redirect URIs
   - Required Scopes
5. Record the following:
   - Client Key (app_id)
   - Client Secret
   - Redirect URIs

### 2. Configure Redirect URI

Set up a redirect URI for your application:
```
http://localhost:8080/callback
```

Or for production:
```
https://yourdomain.com/callback
```

## Required Scopes

For comment moderation, you need the following scopes:

| Scope | Description | Required for |
|-------|-------------|--------------|
| `user.info.basic` | Basic user information | Getting user profile |
| `video.list` | List user's videos | Getting videos |
| `video.read` | Read video details | Getting video info |
| `comment.read` | Read comments | Getting comments |
| `comment.manage` | Manage comments | Deleting/hiding comments |

**Note**: Not all scopes are available to all account types. Business accounts have the most access.

## Authorization Flow

### Step 1: Authorization Request

Construct the authorization URL:

```python
import urllib.parse

client_key = "your_client_key"
redirect_uri = "http://localhost:8080/callback"
state = "random_state_string"

scopes = [
    "user.info.basic",
    "video.list",
    "video.read",
    "comment.read",
    "comment.manage"
]

auth_url = (
    "https://www.tiktok.com/v2/auth/authorize?"
    f"client_key={client_key}&"
    f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
    f"scope={urllib.parse.quote('+'.join(scopes))}&"
    f"response_type=code&"
    f"state={state}"
)

print(f"Visit: {auth_url}")
```

### Step 2: Handle Callback

After user authorization, TikTok redirects to your redirect URI with an authorization code:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/callback')
def callback():
    auth_code = request.args.get('code')
    state = request.args.get('state')
    
    # Validate state to prevent CSRF
    if state != expected_state:
        return "Invalid state", 400
    
    # Exchange code for access token
    token_data = exchange_code_for_token(auth_code)
    
    return "Authentication successful!"
```

### Step 3: Exchange Code for Access Token

```python
import requests

def exchange_code_for_token(auth_code: str) -> dict:
    client_key = "your_client_key"
    client_secret = "your_client_secret"
    redirect_uri = "http://localhost:8080/callback"
    
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    
    data = {
        "client_key": client_key,
        "client_secret": client_secret,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    }
    
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    
    return response.json()
```

**Response:**
```json
{
  "access_token": "your_access_token",
  "token_type": "Bearer",
  "expires_in": 86400,
  "refresh_token": "your_refresh_token",
  "scope": "user.info.basic video.list video.read comment.read comment.manage",
  "refresh_expires_in": 31536000
}
```

## Token Management

### Store Tokens Securely

```python
import os
from typing import Optional
import json

class TokenManager:
    def __init__(self, storage_path: str = "tokens.json"):
        self.storage_path = storage_path
    
    def save_token(self, user_id: str, token_data: dict):
        """Save token data securely"""
        tokens = self.load_tokens()
        tokens[user_id] = {
            **token_data,
            'saved_at': int(time.time() * 1000)
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(tokens, f, indent=2)
    
    def load_tokens(self) -> dict:
        """Load all tokens"""
        if not os.path.exists(self.storage_path):
            return {}
        
        with open(self.storage_path, 'r') as f:
            return json.load(f)
    
    def get_token(self, user_id: str) -> Optional[str]:
        """Get access token for user"""
        tokens = self.load_tokens()
        return tokens.get(user_id, {}).get('access_token')
    
    def is_token_expired(self, user_id: str) -> bool:
        """Check if token is expired"""
        tokens = self.load_tokens()
        token_data = tokens.get(user_id)
        
        if not token_data:
            return True
        
        expires_at = token_data.get('saved_at', 0) + (token_data.get('expires_in', 0) * 1000)
        return int(time.time() * 1000) > expires_at
```

### Refresh Token

```python
import time

def refresh_token(refresh_token: str) -> dict:
    client_key = "your_client_key"
    client_secret = "your_client_secret"
    
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    
    data = {
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    
    return response.json()
```

## Using Access Token

Once you have an access token, include it in all API requests:

```python
def make_api_request(endpoint: str, access_token: str):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    url = f"https://open.tiktokapis.com/v2{endpoint}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()
```

## Environment Variables

Store credentials in environment variables:

```bash
TIKTOK_CLIENT_KEY=your_client_key
TIKTOK_CLIENT_SECRET=your_client_secret
TIKTOK_REDIRECT_URI=http://localhost:8080/callback
```

### Load Environment Variables

```python
from dotenv import load_dotenv
import os

load_dotenv()

client_key = os.getenv("TIKTOK_CLIENT_KEY")
client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
redirect_uri = os.getenv("TIKTOK_REDIRECT_URI")
```

## Error Handling

### Common Authentication Errors

```python
def handle_auth_error(response: requests.Response):
    if response.status_code == 401:
        print("Authentication failed - invalid or expired token")
    elif response.status_code == 403:
        print("Forbidden - insufficient permissions")
    elif response.status_code == 400:
        error_data = response.json()
        print(f"Bad request: {error_data.get('error', {})}")
    else:
        print(f"Unexpected error: {response.status_code}")
```

## Multi-User Authentication

If supporting multiple users/accounts:

```python
class MultiUserAuthManager:
    def __init__(self):
        self.token_manager = TokenManager()
    
    def authenticate_user(self, user_id: str, auth_code: str):
        """Authenticate a new user"""
        token_data = exchange_code_for_token(auth_code)
        self.token_manager.save_token(user_id, token_data)
        return token_data
    
    def get_valid_token(self, user_id: str) -> str:
        """Get valid access token, refresh if needed"""
        if self.token_manager.is_token_expired(user_id):
            tokens = self.token_manager.load_tokens()
            refresh_token = tokens[user_id]['refresh_token']
            new_token_data = refresh_token(refresh_token)
            self.token_manager.save_token(user_id, new_token_data)
        
        return self.token_manager.get_token(user_id)
```

## Testing Authentication

```python
def test_authentication(access_token: str) -> bool:
    """Test if the access token is valid"""
    try:
        user_info = make_api_request("/user/info/", access_token)
        print(f"Authenticated as: {user_info['data']['user']['display_name']}")
        return True
    except Exception as e:
        print(f"Authentication failed: {e}")
        return False
```

## Service Account Alternative

TikTok doesn't support service accounts. For automated bots:
1. Create a dedicated TikTok business account
2. Complete OAuth flow once
3. Store the access token securely
4. Use it for all API calls
5. Implement token refresh logic

## Security Best Practices

1. **Never commit tokens to version control**
2. **Encrypt tokens at rest**
3. **Use environment variables for secrets**
4. **Rotate tokens periodically**
5. **Monitor token usage**
6. **Validate state parameter** to prevent CSRF
7. **Use HTTPS** for all OAuth flows
8. **Implement token refresh logic**
9. **Monitor for unauthorized access**
10. **Use least privilege scopes**

## Troubleshooting

### Issue: "Access token invalid"
**Solution**: Ensure access token is included in Authorization header

### Issue: "Invalid redirect URI"
**Solution**: Verify redirect URI matches exactly with TikTok app settings

### Issue: "Insufficient permissions"
**Solution**: Request appropriate scopes during authorization

### Issue: "Expired token"
**Solution**: Implement token refresh mechanism

### Issue: "Scope not granted"
**Solution**: Some scopes require business account approval

## Security Checklist

- [ ] Store client secret securely
- [ ] Use HTTPS for all OAuth flows
- [ ] Validate state parameter to prevent CSRF
- [ ] Implement token refresh logic
- [ ] Never expose tokens in logs
- [ ] Rotate tokens periodically
- [ ] Monitor for unauthorized access
- [ ] Use least privilege scopes
- [ ] Encrypt tokens at rest
- [ ] Implement logout/revocation

## Additional Resources

- [TikTok OAuth 2.0 Documentation](https://developers.tiktok.com/doc/login-kit-manage/)
- [OAuth 2.0 Specification](https://tools.ietf.org/html/rfc6749)
- [TikTok Developer Portal](https://developers.tiktok.com/)
