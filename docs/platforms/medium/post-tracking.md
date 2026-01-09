# Medium Post Tracking

## Overview

Post tracking in Medium involves monitoring articles for new comments and managing comment moderation. This guide details how to track Medium articles and their associated comments.

## Tracking Strategy

Medium articles can be tracked by:
1. **Author-based**: Track all articles by specific authors
2. **Publication-based**: Track all articles in specific publications
3. **Individual articles**: Track specific article IDs

## Article Discovery

### Author Articles

Fetch articles published by a specific author:

```python
import requests
from typing import List, Dict

class MediumArticleTracker:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def get_author_articles(self, author_id: str) -> List[Dict]:
        """Get all articles by an author"""
        url = f"https://api.medium.com/v1/users/{author_id}/articles"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json().get('data', [])
```

### Publication Articles

Fetch articles from a publication:

```python
    def get_publication_articles(self, publication_id: str) -> List[Dict]:
        """Get all articles in a publication"""
        url = f"https://api.medium.com/v1/publications/{publication_id}/posts"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json().get('data', [])
```

## Article Storage

Store tracked articles for efficient access:

```python
import json
import os
from datetime import datetime
from typing import Dict, List

class ArticleStorage:
    def __init__(self, storage_path: str = "articles.json"):
        self.storage_path = storage_path
    
    def load_articles(self) -> Dict[str, Dict]:
        """Load all tracked articles"""
        if not os.path.exists(self.storage_path):
            return {}
        
        with open(self.storage_path, 'r') as f:
            return json.load(f)
    
    def save_article(self, article: Dict):
        """Save or update an article"""
        articles = self.load_articles()
        articles[article['id']] = {
            **article,
            'last_updated': datetime.now().isoformat(),
            'last_comment_check': None
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(articles, f, indent=2)
    
    def get_article(self, article_id: str) -> Dict:
        """Get a specific article"""
        articles = self.load_articles()
        return articles.get(article_id)
    
    def update_comment_check(self, article_id: str):
        """Update last comment check timestamp"""
        articles = self.load_articles()
        if article_id in articles:
            articles[article_id]['last_comment_check'] = datetime.now().isoformat()
            
            with open(self.storage_path, 'w') as f:
                json.dump(articles, f, indent=2)
```

## Comment Tracking

### Fetch Comments

Retrieve comments for an article:

```python
    def get_article_comments(self, article_id: str) -> List[Dict]:
        """Get all comments for an article"""
        url = f"https://api.medium.com/v1/posts/{article_id}/responses"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json().get('data', [])
```

### Track New Comments

Identify new comments since last check:

```python
from datetime import datetime

class CommentTracker:
    def __init__(self, article_storage: ArticleStorage):
        self.article_storage = article_storage
    
    def get_new_comments(self, article_id: str) -> List[Dict]:
        """Get new comments since last check"""
        article = self.article_storage.get_article(article_id)
        
        if not article:
            return []
        
        last_check = article.get('last_comment_check')
        if not last_check:
            last_check = datetime(1970, 1, 1).isoformat()
        
        # Fetch all comments
        tracker = MediumArticleTracker(self.access_token)
        all_comments = tracker.get_article_comments(article_id)
        
        # Filter new comments
        new_comments = [
            comment for comment in all_comments
            if comment['createdAt'] > last_check
        ]
        
        # Update last check time
        self.article_storage.update_comment_check(article_id)
        
        return new_comments
```

## Polling Strategy

Implement polling to check for new comments:

```python
import time
import threading
from typing import Callable

class ArticlePoller:
    def __init__(self, article_ids: List[str], 
                 comment_tracker: CommentTracker,
                 poll_interval: int = 300):
        self.article_ids = article_ids
        self.comment_tracker = comment_tracker
        self.poll_interval = poll_interval
        self.running = False
        self.thread = None
    
    def on_new_comment(self, callback: Callable[[str, List[Dict]], None]):
        """Set callback for new comments"""
        self.callback = callback
    
    def poll(self):
        """Poll for new comments"""
        while self.running:
            for article_id in self.article_ids:
                try:
                    new_comments = self.comment_tracker.get_new_comments(article_id)
                    
                    if new_comments and hasattr(self, 'callback'):
                        self.callback(article_id, new_comments)
                
                except Exception as e:
                    print(f"Error polling article {article_id}: {e}")
            
            time.sleep(self.poll_interval)
    
    def start(self):
        """Start polling"""
        self.running = True
        self.thread = threading.Thread(target=self.poll)
        self.thread.start()
    
    def stop(self):
        """Stop polling"""
        self.running = False
        if self.thread:
            self.thread.join()
```

## Article Registration

Register new articles for tracking:

```python
class ArticleRegistry:
    def __init__(self, article_storage: ArticleStorage):
        self.article_storage = article_storage
        self.pollers = {}
    
    def register_article(self, article_id: str, article_data: Dict):
        """Register a new article for tracking"""
        self.article_storage.save_article(article_data)
    
    def register_author_articles(self, author_id: str):
        """Register all articles by an author"""
        tracker = MediumArticleTracker(self.access_token)
        articles = tracker.get_author_articles(author_id)
        
        for article in articles:
            self.register_article(article['id'], article)
    
    def register_publication_articles(self, publication_id: str):
        """Register all articles in a publication"""
        tracker = MediumArticleTracker(self.access_token)
        articles = tracker.get_publication_articles(publication_id)
        
        for article in articles:
            self.register_article(article['id'], article)
    
    def start_tracking(self, article_id: str, comment_tracker: CommentTracker):
        """Start tracking a specific article"""
        if article_id not in self.pollers:
            poller = ArticlePoller([article_id], comment_tracker)
            self.pollers[article_id] = poller
            poller.start()
    
    def stop_tracking(self, article_id: str):
        """Stop tracking a specific article"""
        if article_id in self.pollers:
            self.pollers[article_id].stop()
            del self.pollers[article_id]
```

## Webhook Integration

Medium has limited webhook support. Webhooks are primarily available for publications:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

class WebhookHandler:
    def __init__(self, secret: str):
        self.secret = secret
        self.handlers = {}
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register a handler for a specific event type"""
        self.handlers[event_type] = handler
    
    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verify webhook signature"""
        import hmac
        import hashlib
        
        expected_signature = hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def handle_event(self, event_type: str, data: Dict):
        """Handle webhook event"""
        if event_type in self.handlers:
            self.handlers[event_type](data)

webhook_handler = WebhookHandler("your_webhook_secret")

@app.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers.get('X-Medium-Signature')
    payload = request.get_data(as_text=True)
    
    if not webhook_handler.verify_signature(payload, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    event_data = request.json
    event_type = event_data.get('type')
    
    webhook_handler.handle_event(event_type, event_data)
    
    return jsonify({'status': 'ok'}), 200
```

## Article Metadata

Track additional article metadata:

```python
class ArticleMetadata:
    def __init__(self, article_storage: ArticleStorage):
        self.article_storage = article_storage
    
    def add_metadata(self, article_id: str, key: str, value: any):
        """Add metadata to an article"""
        articles = self.article_storage.load_articles()
        
        if article_id in articles:
            if 'metadata' not in articles[article_id]:
                articles[article_id]['metadata'] = {}
            
            articles[article_id]['metadata'][key] = value
            
            with open(self.article_storage.storage_path, 'w') as f:
                json.dump(articles, f, indent=2)
    
    def get_metadata(self, article_id: str, key: str) -> any:
        """Get metadata from an article"""
        articles = self.article_storage.load_articles()
        
        if article_id in articles and 'metadata' in articles[article_id]:
            return articles[article_id]['metadata'].get(key)
        
        return None
```

## Batch Operations

Process multiple articles efficiently:

```python
class BatchProcessor:
    def __init__(self, article_storage: ArticleStorage):
        self.article_storage = article_storage
    
    def process_batch(self, article_ids: List[str], 
                      processor: Callable[[str], None]):
        """Process a batch of articles"""
        for article_id in article_ids:
            try:
                processor(article_id)
            except Exception as e:
                print(f"Error processing article {article_id}: {e}")
    
    def update_last_check(self, article_ids: List[str]):
        """Update last check for multiple articles"""
        processor = lambda aid: self.article_storage.update_comment_check(aid)
        self.process_batch(article_ids, processor)
```

## Error Handling

Handle tracking errors gracefully:

```python
def safe_track_article(article_id: str, tracker: CommentTracker) -> bool:
    """Safely track an article"""
    try:
        new_comments = tracker.get_new_comments(article_id)
        
        if new_comments:
            print(f"Found {len(new_comments)} new comments on article {article_id}")
            # Process new comments
        
        return True
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error tracking article {article_id}: {e}")
        return False
    except Exception as e:
        print(f"Error tracking article {article_id}: {e}")
        return False
```

## Monitoring

Monitor tracking performance:

```python
class TrackingMonitor:
    def __init__(self):
        self.tracking_stats = {}
    
    def record_check(self, article_id: str, new_comments_count: int):
        """Record a tracking check"""
        if article_id not in self.tracking_stats:
            self.tracking_stats[article_id] = {
                'checks': 0,
                'new_comments': 0,
                'last_check': None
            }
        
        self.tracking_stats[article_id]['checks'] += 1
        self.tracking_stats[article_id]['new_comments'] += new_comments_count
        self.tracking_stats[article_id]['last_check'] = datetime.now().isoformat()
    
    def get_stats(self) -> Dict:
        """Get tracking statistics"""
        return self.tracking_stats
```

## Summary

1. **Discover articles** by author or publication
2. **Store articles** for tracking
3. **Fetch comments** periodically
4. **Identify new comments** since last check
5. **Implement polling** for regular checks
6. **Handle errors** gracefully
7. **Monitor performance** of tracking

By following this approach, you can effectively track Medium articles and their comments for moderation.
