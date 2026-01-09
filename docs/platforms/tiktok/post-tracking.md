# TikTok Post Tracking

## Overview

Post tracking in TikTok involves monitoring videos for new comments and managing comment moderation. This guide details how to track TikTok videos and their associated comments.

## Tracking Strategy

TikTok videos can be tracked by:
1. **User-based**: Track all videos from specific users
2. **Individual videos**: Track specific video IDs
3. **Hashtag-based**: Track videos with specific hashtags (limited API support)

## Video Discovery

### User Videos

Fetch videos from a specific user:

```python
import requests
from typing import List, Dict

class TikTokVideoTracker:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def get_user_videos(self, cursor: str = None, max_count: int = 20) -> List[Dict]:
        """Get videos from authenticated user"""
        url = "https://open.tiktokapis.com/v2/video/list/"
        params = {"max_count": min(max_count, 20)}
        if cursor:
            params["cursor"] = cursor
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json().get('data', {})
        return data.get('videos', [])
    
    def get_all_user_videos(self) -> List[Dict]:
        """Get all videos with pagination"""
        all_videos = []
        cursor = None
        
        while True:
            videos = self.get_user_videos(cursor=cursor)
            all_videos.extend(videos)
            
            if len(videos) < 20:
                break
            
            cursor = videos[-1].get('cursor')
            if not cursor:
                break
        
        return all_videos
```

## Video Storage

Store tracked videos for efficient access:

```python
import json
import os
from datetime import datetime
from typing import Dict, List

class VideoStorage:
    def __init__(self, storage_path: str = "videos.json"):
        self.storage_path = storage_path
    
    def load_videos(self) -> Dict[str, Dict]:
        """Load all tracked videos"""
        if not os.path.exists(self.storage_path):
            return {}
        
        with open(self.storage_path, 'r') as f:
            return json.load(f)
    
    def save_video(self, video: Dict):
        """Save or update a video"""
        videos = self.load_videos()
        videos[video['id']] = {
            'id': video['id'],
            'title': video.get('title', ''),
            'description': video.get('video_description', ''),
            'create_time': video['create_time'],
            'share_url': video.get('share_url', ''),
            'cover_image_url': video.get('cover_image_url', ''),
            'duration': video.get('duration', 0),
            'tracked_at': datetime.now().isoformat(),
            'last_comment_check': None,
            'total_comments': 0
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(videos, f, indent=2)
    
    def get_video(self, video_id: str) -> Dict:
        """Get a specific video"""
        videos = self.load_videos()
        return videos.get(video_id)
    
    def update_comment_check(self, video_id: str, comment_count: int = 0):
        """Update last comment check timestamp"""
        videos = self.load_videos()
        if video_id in videos:
            videos[video_id]['last_comment_check'] = datetime.now().isoformat()
            videos[video_id]['total_comments'] = comment_count
            
            with open(self.storage_path, 'w') as f:
                json.dump(videos, f, indent=2)
```

## Comment Tracking

### Fetch Comments

Retrieve comments for a video:

```python
    def get_video_comments(self, video_id: str, cursor: str = None, 
                        max_count: int = 100) -> List[Dict]:
        """Get comments for a video"""
        url = "https://open.tiktokapis.com/v2/video/comment/list/"
        params = {
            "video_id": video_id,
            "max_count": min(max_count, 100)
        }
        if cursor:
            params["cursor"] = cursor
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json().get('data', {})
        return data.get('comments', [])
    
    def get_all_video_comments(self, video_id: str) -> List[Dict]:
        """Get all comments with pagination"""
        all_comments = []
        cursor = None
        
        while True:
            comments = self.get_video_comments(video_id, cursor=cursor)
            all_comments.extend(comments)
            
            if len(comments) < 100:
                break
            
            cursor = comments[-1].get('cursor')
            if not cursor:
                break
        
        return all_comments
```

### Track New Comments

Identify new comments since last check:

```python
from datetime import datetime

class CommentTracker:
    def __init__(self, video_storage: VideoStorage):
        self.video_storage = video_storage
    
    def get_new_comments(self, video_id: str) -> List[Dict]:
        """Get new comments since last check"""
        video = self.video_storage.get_video(video_id)
        
        if not video:
            return []
        
        last_check = video.get('last_comment_check')
        if not last_check:
            last_check = datetime(1970, 1, 1).timestamp()
        
        tracker = TikTokVideoTracker(self.access_token)
        all_comments = tracker.get_all_video_comments(video_id)
        
        new_comments = [
            comment for comment in all_comments
            if comment['create_time'] > last_check
        ]
        
        self.video_storage.update_comment_check(video_id, len(all_comments))
        
        return new_comments
```

## Polling Strategy

Implement polling to check for new comments:

```python
import time
import threading
from typing import Callable

class VideoPoller:
    def __init__(self, video_ids: List[str], 
                 comment_tracker: CommentTracker,
                 poll_interval: int = 300):
        self.video_ids = video_ids
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
            for video_id in self.video_ids:
                try:
                    new_comments = self.comment_tracker.get_new_comments(video_id)
                    
                    if new_comments and hasattr(self, 'callback'):
                        self.callback(video_id, new_comments)
                
                except Exception as e:
                    print(f"Error polling video {video_id}: {e}")
            
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

## Video Registration

Register new videos for tracking:

```python
class VideoRegistry:
    def __init__(self, video_storage: VideoStorage):
        self.video_storage = video_storage
        self.pollers = {}
    
    def register_video(self, video_id: str, video_data: Dict):
        """Register a new video for tracking"""
        self.video_storage.save_video(video_data)
    
    def register_user_videos(self):
        """Register all videos from authenticated user"""
        tracker = TikTokVideoTracker(self.access_token)
        videos = tracker.get_all_user_videos()
        
        for video in videos:
            self.register_video(video['id'], video)
    
    def start_tracking(self, video_id: str, comment_tracker: CommentTracker):
        """Start tracking a specific video"""
        if video_id not in self.pollers:
            poller = VideoPoller([video_id], comment_tracker)
            self.pollers[video_id] = poller
            poller.start()
    
    def stop_tracking(self, video_id: str):
        """Stop tracking a specific video"""
        if video_id in self.pollers:
            self.pollers[video_id].stop()
            del self.pollers[video_id]
```

## Webhook Integration

TikTok supports webhooks for real-time notifications:

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
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature"""
        import hmac
        import hashlib
        
        expected_signature = hmac.new(
            self.secret.encode(),
            payload,
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
    signature = request.headers.get('X-TikTok-Signature')
    payload = request.get_data(as_text=True)
    
    if not webhook_handler.verify_signature(payload, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    event_data = request.json
    event_type = event_data.get('type')
    
    webhook_handler.handle_event(event_type, event_data)
    
    return jsonify({'status': 'ok'}), 200
```

## Video Metadata

Track additional video metadata:

```python
class VideoMetadata:
    def __init__(self, video_storage: VideoStorage):
        self.video_storage = video_storage
    
    def add_metadata(self, video_id: str, key: str, value: any):
        """Add metadata to a video"""
        videos = self.video_storage.load_videos()
        
        if video_id in videos:
            if 'metadata' not in videos[video_id]:
                videos[video_id]['metadata'] = {}
            
            videos[video_id]['metadata'][key] = value
            
            with open(self.video_storage.storage_path, 'w') as f:
                json.dump(videos, f, indent=2)
    
    def get_metadata(self, video_id: str, key: str) -> any:
        """Get metadata from a video"""
        videos = self.video_storage.load_videos()
        
        if video_id in videos and 'metadata' in videos[video_id]:
            return videos[video_id]['metadata'].get(key)
        
        return None
```

## Batch Operations

Process multiple videos efficiently:

```python
class BatchProcessor:
    def __init__(self, video_storage: VideoStorage):
        self.video_storage = video_storage
    
    def process_batch(self, video_ids: List[str], 
                      processor: Callable[[str], None]):
        """Process a batch of videos"""
        for video_id in video_ids:
            try:
                processor(video_id)
            except Exception as e:
                print(f"Error processing video {video_id}: {e}")
    
    def update_last_check(self, video_ids: List[str]):
        """Update last check for multiple videos"""
        tracker = TikTokVideoTracker(self.access_token)
        processor = lambda vid: self.video_storage.update_comment_check(
            vid, 
            len(tracker.get_all_video_comments(vid))
        )
        self.process_batch(video_ids, processor)
```

## Error Handling

Handle tracking errors gracefully:

```python
def safe_track_video(video_id: str, tracker: CommentTracker) -> bool:
    """Safely track a video"""
    try:
        new_comments = tracker.get_new_comments(video_id)
        
        if new_comments:
            print(f"Found {len(new_comments)} new comments on video {video_id}")
        
        return True
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error tracking video {video_id}: {e}")
        return False
    except Exception as e:
        print(f"Error tracking video {video_id}: {e}")
        return False
```

## Monitoring

Monitor tracking performance:

```python
class TrackingMonitor:
    def __init__(self):
        self.tracking_stats = {}
    
    def record_check(self, video_id: str, new_comments_count: int):
        """Record a tracking check"""
        if video_id not in self.tracking_stats:
            self.tracking_stats[video_id] = {
                'checks': 0,
                'new_comments': 0,
                'last_check': None
            }
        
        self.tracking_stats[video_id]['checks'] += 1
        self.tracking_stats[video_id]['new_comments'] += new_comments_count
        self.tracking_stats[video_id]['last_check'] = datetime.now().isoformat()
    
    def get_stats(self) -> Dict:
        """Get tracking statistics"""
        return self.tracking_stats
```

## Summary

1. **Discover videos** by user
2. **Store videos** for tracking
3. **Fetch comments** periodically
4. **Identify new comments** since last check
5. **Implement polling** for regular checks
6. **Handle errors** gracefully
7. **Monitor performance** of tracking

By following this approach, you can effectively track TikTok videos and their comments for moderation.
