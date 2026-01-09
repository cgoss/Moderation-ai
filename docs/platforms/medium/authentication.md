# Medium Authentication Guide

## Overview

Medium uses OAuth 2.0 for authentication and authorization. This guide details how to set up and manage OAuth 2.0 authentication for the Moderation Bot.

## OAuth 2.0 Flow

Medium uses the Authorization Code grant type for OAuth 2.0:

1. **Authorization Request**: User authorizes the application
2. **Authorization Code**: Receive authorization code from Medium
3. **Access Token Exchange**: Exchange authorization code for access token
4. **Token Refresh**: Refresh expired tokens

## Setting Up OAuth

### 1. Create Medium Application

1. Go to [Medium Settings](https://medium.com/me/settings)
2. Navigate to "Integration tokens" or "Developer apps"
3. Create a new application
4. Record the following:
   - Client ID
   - Client Secret
   - Redirect URI(s)

### 2. Configure Redirect URI

Set up a redirect URI for your application:
```
http://localhost:8080/callback
```

Or for production:
```
https://yourdomain.com/callback
```

## Authorization Flow

### Step 1: Authorization Request

Construct the authorization URL:

```python
import urllib.parse

client_id = "your_client_id"
redirect_uri = "http://localhost:8080/callback"
state = "random_state_string"

scopes = "basicProfile,publishPost,listPublications"

auth_url = (
    "https://medium.com/m/oauth/authorize?"
    f"client_id={client_id}&"
    f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
    f"scope={scopes}&"
    f"state={state}"
)

print(f"Visit: {auth_url}")
```

### Step 2: Handle Callback

After user authorization, Medium redirects to your redirect URI with an authorization code:

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
import urllib.parse

def exchange_code_for_token(auth_code: str) -> dict:
    client_id = "your_client_id"
    client_secret = "your_client_secret"
    redirect_uri = "http://localhost:8080/callback"
    
    token_url = "https://api.medium.com/v1/tokens"
    
    data = {
        "code": auth_code,
        "client_id": client_id,
        "client_secret": client_secret,
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
  "access_token": "0123456789abcdef0123456789abcdef",
  "refresh_token": "0123456789abcdef0123456789abcdef",
  "expires_at": 1452763256056,
  "scope": "basicProfile,publishPost,listPublications"
}
```

## Token Management

### Store Tokens Securely

```python
import os
from typing import Optional

class TokenManager:
    def __init__(self, storage_path: str = "tokens.json"):
        self.storage_path = storage_path
    
    def save_token(self, user_id: str, token_data: dict):
        """Save token data securely"""
        tokens = self.load_tokens()
        tokens[user_id] = token_data
        
        with open(self.storage_path, 'w') as f:
            import json
            json.dump(tokens, f)
    
    def load_tokens(self) -> dict:
        """Load all tokens"""
        if not os.path.exists(self.storage_path):
            return {}
        
        with open(self.storage_path, 'r') as f:
            import json
            return json.load(f)
    
    def get_token(self, user_id: str) -> Optional[str]:
        """Get access token for user"""
        tokens = self.load_tokens()
        return tokens.get(user_id, {}).get('access_token')
    
    def is_token_expired(self, user_id: str) -> bool:
        """Check if token is expired"""
        tokens = self.load_tokens()
        expires_at = tokens.get(user_id, {}).get('expires_at')
        
        if not expires_at:
            return True
        
        return expires_at < (int(time.time() * 1000))
```

### Refresh Token

```python
import time

def refresh_token(refresh_token: str) -> dict:
    client_id = "your_client_id"
    client_secret = "your_client_secret"
    
    token_url = "https://api.medium.com/v1/tokens"
    
    data = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
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
    
    url = f"https://api.medium.com/v1{endpoint}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()
```

## Scopes

Medium supports the following scopes:

| Scope | Description | Required for |
|-------|-------------|--------------|
| `basicProfile` | Basic user information | Getting user profile |
| `listPublications` | List user's publications | Getting publications |
| `publishPost` | Create and manage posts | Publishing articles |
| `uploadImage` | Upload images | Image uploads |

For comment moderation, you typically need:
- `basicProfile`
- `listPublications`

## Token Storage Best Practices

1. **Never commit tokens to version control**
2. **Encrypt tokens at rest**
3. **Use environment variables for secrets**
4. **Rotate tokens periodically**
5. **Monitor token usage**

### Environment Variables

```bash
MEDIUM_CLIENT_ID=your_client_id
MEDIUM_CLIENT_SECRET=your_client_secret
MEDIUM_REDIRECT_URI=http://localhost:8080/callback
```

### Load Environment Variables

```python
from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.getenv("MEDIUM_CLIENT_ID")
client_secret = os.getenv("MEDIUM_CLIENT_SECRET")
redirect_uri = os.getenv("MEDIUM_REDIRECT_URI")
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
        print(f"Bad request: {error_data.get('errors', [])}")
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

## Service Account Alternative

Medium doesn't support service accounts. For automated bots:
1. Create a dedicated Medium account
2. Complete OAuth flow once
3. Store the access token securely
4. Use it for all API calls

## Testing Authentication

```python
def test_authentication(access_token: str) -> bool:
    """Test if the access token is valid"""
    try:
        user_info = make_api_request("/me", access_token)
        print(f"Authenticated as: {user_info['data']['name']}")
        return True
    except Exception as e:
        print(f"Authentication failed: {e}")
        return False
```

## Troubleshooting

### Issue: "Access token not found"
**Solution**: Ensure access token is included in Authorization header

### Issue: "Invalid redirect URI"
**Solution**: Verify redirect URI matches exactly with Medium app settings

### Issue: "Expired token"
**Solution**: Implement token refresh mechanism

### Issue: "Insufficient permissions"
**Solution**: Request appropriate scopes during authorization

## Security Checklist

- [ ] Store client secret securely
- [ ] Use HTTPS for all OAuth flows
- [ ] Validate state parameter to prevent CSRF
- [ ] Implement token refresh logic
- [ ] Never expose tokens in logs
- [ ] Rotate tokens periodically
- [ ] Monitor for unauthorized access
- [ ] Use least privilege scopes

## Additional Resources

- [Medium OAuth 2.0 Documentation](https://github.com/Medium/medium-api-docs/blob/master/README.md#21-identity)
- [OAuth 2.0 Specification](https://tools.ietf.org/html/rfc6749)
