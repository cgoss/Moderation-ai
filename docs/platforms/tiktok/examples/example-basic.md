# TikTok Basic Integration Example

This example demonstrates a basic integration with TikTok API to fetch videos and comments.

## Setup

1. Install required dependencies:
```bash
pip install requests python-dotenv
```

2. Create a `.env` file with your TikTok credentials:
```bash
TIKTOK_ACCESS_TOKEN=your_access_token_here
```

## Basic Usage

### 1. Get User Info

```python
import os
from dotenv import load_dotenv
import requests

load_dotenv()

ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")

def get_user_info():
    """Get authenticated user's information"""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        "https://open.tiktokapis.com/v2/user/info/",
        headers=headers
    )
    
    if response.status_code == 200:
        user_data = response.json()['data']['user']
        print(f"Display Name: {user_data['display_name']}")
        print(f"Username: {user_data['username']}")
        print(f"ID: {user_data['union_id']}")
        return user_data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Usage
user = get_user_info()
```

### 2. Get User Videos

```python
def get_user_videos(cursor=None):
    """Get videos from authenticated user"""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    params = {"max_count": 10}
    if cursor:
        params["cursor"] = cursor
    
    response = requests.get(
        "https://open.tiktokapis.com/v2/video/list/",
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        data = response.json()['data']
        videos = data.get('videos', [])
        has_more = data.get('has_more', False)
        next_cursor = data.get('cursor')
        
        print(f"Found {len(videos)} videos")
        return videos, has_more, next_cursor
    else:
        print(f"Error: {response.status_code}")
        return [], False, None

# Usage
videos, has_more, cursor = get_user_videos()
for video in videos[:3]:
    print(f"- {video.get('title', 'No title')}")
```

### 3. Get Video Comments

```python
def get_video_comments(video_id, cursor=None):
    """Get comments for a specific video"""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    params = {
        "video_id": video_id,
        "max_count": 50
    }
    if cursor:
        params["cursor"] = cursor
    
    response = requests.get(
        "https://open.tiktokapis.com/v2/video/comment/list/",
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        data = response.json()['data']
        comments = data.get('comments', [])
        has_more = data.get('has_more', False)
        next_cursor = data.get('cursor')
        
        print(f"Found {len(comments)} comments")
        return comments, has_more, next_cursor
    else:
        print(f"Error: {response.status_code}")
        return [], False, None

# Usage
if videos:
    video_id = videos[0]['id']
    comments, has_more, cursor = get_video_comments(video_id)
    for comment in comments[:3]:
        user = comment.get('user', {})
        print(f"- @{user.get('username', 'Unknown')}: {comment.get('text', '')[:50]}...")
```

### 4. Simple Comment Analysis

```python
import re

def analyze_comment(comment):
    """Simple comment analysis"""
    text = comment.get('text', '')
    user = comment.get('user', {})
    
    analysis = {
        'comment_id': comment['id'],
        'text': text,
        'username': user.get('username'),
        'word_count': len(text.split()),
        'has_mentions': bool(re.search(r'@\w+', text)),
        'has_hashtags': bool(re.search(r'#\w+', text)),
        'like_count': comment.get('like_count', 0)
    }
    
    return analysis

# Usage
if comments:
    for comment in comments[:3]:
        analysis = analyze_comment(comment)
        print(f"\nComment ID: {analysis['comment_id']}")
        print(f"User: @{analysis['username']}")
        print(f"Text: {analysis['text'][:100]}...")
        print(f"Words: {analysis['word_count']}")
        print(f"Mentions: {analysis['has_mentions']}")
        print(f"Hashtags: {analysis['has_hashtags']}")
        print(f"Likes: {analysis['like_count']}")
```

### 5. Complete Example

```python
import os
from dotenv import load_dotenv
import requests
import re

load_dotenv()

ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")

def main():
    # Get user info
    print("Fetching user information...")
    user = get_user_info()
    if not user:
        return
    
    # Get videos
    print(f"\nFetching videos for {user['display_name']}...")
    videos, has_more, cursor = get_user_videos()
    if not videos:
        print("No videos found")
        return
    
    # Get comments for first video
    video = videos[0]
    print(f"\nFetching comments for video: {video.get('title', 'No title')}")
    comments, has_more, cursor = get_video_comments(video['id'])
    
    if not comments:
        print("No comments found")
        return
    
    # Analyze comments
    print(f"\nAnalyzing {len(comments)} comments...")
    for comment in comments[:5]:
        analysis = analyze_comment(comment)
        print(f"\nComment by @{analysis['username']}:")
        print(f"  Text: {analysis['text'][:80]}...")
        print(f"  Words: {analysis['word_count']}")
        print(f"  Mentions: {'Yes' if analysis['has_mentions'] else 'No'}")
        print(f"  Hashtags: {'Yes' if analysis['has_hashtags'] else 'No'}")
        print(f"  Likes: {analysis['like_count']}")

if __name__ == "__main__":
    main()
```

## Output Example

```
Fetching user information...
Display Name: John Doe
Username: @johndoe
ID: 123456789

Fetching videos for John Doe...
Found 10 videos
- My First Video
- How to Code
- Tutorial Video

Fetching comments for video: My First Video
Found 25 comments

Analyzing 25 comments...

Comment by @janedoe:
  Text: This is a great video! Really enjoyed it...
  Words: 8
  Mentions: No
  Hashtags: No
  Likes: 15

Comment by @bobsmith:
  Text: Thanks for sharing this tutorial...
  Words: 6
  Mentions: No
  Hashtags: No
  Likes: 8
```

## Next Steps

- See [advanced integration example](./example-advanced.md) for more features
- Implement comment moderation rules
- Add automated comment processing
- Set up webhook notifications
