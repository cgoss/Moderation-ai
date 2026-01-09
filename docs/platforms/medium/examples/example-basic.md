# Medium Basic Integration Example

This example demonstrates a basic integration with the Medium API to fetch articles and comments.

## Setup

1. Install required dependencies:
```bash
pip install requests python-dotenv
```

2. Create a `.env` file with your Medium credentials:
```bash
MEDIUM_ACCESS_TOKEN=your_access_token_here
```

## Basic Usage

### 1. Fetch User Information

```python
import os
from dotenv import load_dotenv
import requests

load_dotenv()

ACCESS_TOKEN = os.getenv("MEDIUM_ACCESS_TOKEN")

def get_user_info():
    """Get the authenticated user's information"""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        "https://api.medium.com/v1/me",
        headers=headers
    )
    
    if response.status_code == 200:
        user_data = response.json()['data']
        print(f"User: {user_data['name']}")
        print(f"Username: @{user_data['username']}")
        print(f"ID: {user_data['id']}")
        return user_data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Usage
user = get_user_info()
```

### 2. Fetch Articles

```python
def get_user_articles(user_id):
    """Get all articles by a user"""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"https://api.medium.com/v1/users/{user_id}/articles",
        headers=headers
    )
    
    if response.status_code == 200:
        articles = response.json()['data']
        print(f"Found {len(articles)} articles")
        return articles
    else:
        print(f"Error: {response.status_code}")
        return []

# Usage
if user:
    articles = get_user_articles(user['id'])
    for article in articles[:3]:  # Show first 3
        print(f"- {article['title']}")
```

### 3. Fetch Comments for an Article

```python
def get_article_comments(article_id):
    """Get all comments for an article"""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"https://api.medium.com/v1/posts/{article_id}/responses",
        headers=headers
    )
    
    if response.status_code == 200:
        comments = response.json()['data']
        print(f"Found {len(comments)} comments")
        return comments
    else:
        print(f"Error: {response.status_code}")
        return []

# Usage
if articles:
    article_id = articles[0]['id']
    comments = get_article_comments(article_id)
    for comment in comments[:3]:  # Show first 3
        print(f"- {comment['content'][:50]}...")
```

### 4. Simple Comment Analysis

```python
import re

def extract_text_from_html(html_content):
    """Extract plain text from HTML content"""
    text = re.sub(r'<[^>]+>', ' ', html_content)
    return ' '.join(text.split())

def analyze_comment(comment):
    """Simple comment analysis"""
    text = extract_text_from_html(comment['content'])
    word_count = len(text.split())
    
    analysis = {
        'comment_id': comment['id'],
        'text': text,
        'word_count': word_count,
        'has_links': bool(re.search(r'https?://\S+', text)),
        'creator_id': comment['creatorId']
    }
    
    return analysis

# Usage
if comments:
    for comment in comments[:3]:
        analysis = analyze_comment(comment)
        print(f"Comment ID: {analysis['comment_id']}")
        print(f"Text: {analysis['text'][:100]}...")
        print(f"Word count: {analysis['word_count']}")
        print(f"Has links: {analysis['has_links']}")
        print("---")
```

### 5. Complete Example

```python
import os
from dotenv import load_dotenv
import requests
import re

load_dotenv()

ACCESS_TOKEN = os.getenv("MEDIUM_ACCESS_TOKEN")

def main():
    # Get user info
    print("Fetching user information...")
    user = get_user_info()
    if not user:
        return
    
    # Get articles
    print(f"\nFetching articles for {user['name']}...")
    articles = get_user_articles(user['id'])
    if not articles:
        print("No articles found")
        return
    
    # Get comments for first article
    article = articles[0]
    print(f"\nFetching comments for article: {article['title']}")
    comments = get_article_comments(article['id'])
    
    if not comments:
        print("No comments found")
        return
    
    # Analyze comments
    print(f"\nAnalyzing {len(comments)} comments...")
    for comment in comments:
        analysis = analyze_comment(comment)
        print(f"\nComment by {analysis['creator_id']}:")
        print(f"  Text: {analysis['text'][:80]}...")
        print(f"  Words: {analysis['word_count']}")
        print(f"  Links: {'Yes' if analysis['has_links'] else 'No'}")

if __name__ == "__main__":
    main()
```

## Output Example

```
Fetching user information...
User: John Doe
Username: @johndoe
ID: 5303d74c64d66366f003d0fc

Fetching articles for John Doe...
Found 10 articles
- How to Build a Bot
- Understanding APIs
- Python Best Practices

Fetching comments for article: How to Build a Bot
Found 5 comments

Analyzing 5 comments...

Comment by 5303d74c64d66366f003d0fd:
  Text: Great article! This really helped me understand...
  Words: 15
  Links: No

Comment by 5303d74c64d66366f003d0fe:
  Text: Check out my guide at https://example.com/guide
  Words: 8
  Links: Yes
```

## Next Steps

- See [advanced integration example](./example-advanced.md) for more features
- Implement comment moderation rules
- Add automated comment processing
- Set up webhook notifications
