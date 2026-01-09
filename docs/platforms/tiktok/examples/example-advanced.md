# TikTok Advanced Integration Example

This example demonstrates an advanced TikTok integration with comment tracking, automated moderation, and action execution.

## Features

- Track multiple videos for new comments
- Automated comment analysis
- Rule-based moderation
- Action execution (delete, pin, reply)
- Comprehensive logging

## Setup

1. Create a `.env` file:
```bash
TIKTOK_ACCESS_TOKEN=your_access_token
VIDEO_IDS=video_id_1,video_id_2
```

## Complete Implementation

```python
import os
from dotenv import load_dotenv
import requests
import re
import time
from datetime import datetime
from typing import List, Dict
import json

load_dotenv()

ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")

class TikTokModerator:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        self.action_log = []
        
        # Setup moderation rules
        self.setup_rules()
    
    def setup_rules(self):
        """Setup moderation rules"""
        self.spam_keywords = {
            'follow me', 'check my profile', 'click here', 'free money',
            'win big', 'limited time'
        }
        
        self.profanity_words = {
            'badword1', 'badword2', 'badword3'
        }
        
        self.harassment_patterns = [
            r'you.*stupid',
            r'you.*idiot',
            r'go.*kill.*yourself'
        ]
    
    def analyze_comment(self, comment: Dict) -> Dict:
        """Analyze comment for moderation"""
        text = comment.get('text', '').lower()
        words = text.split()
        user = comment.get('user', {})
        
        analysis = {
            'comment_id': comment['id'],
            'video_id': comment['video_id'],
            'text': text,
            'word_count': len(words),
            'char_count': len(text),
            'spam': False,
            'profanity': False,
            'harassment': False,
            'has_mentions': bool(re.search(r'@\w+', text)),
            'has_hashtags': bool(re.search(r'#\w+', text)),
            'like_count': comment.get('like_count', 0)
        }
        
        # Check for spam
        if any(keyword in text for keyword in self.spam_keywords):
            analysis['spam'] = True
        
        # Check for profanity
        if any(word in self.profanity_words for word in words):
            analysis['profanity'] = True
        
        # Check for harassment
        if any(re.search(pattern, text) for pattern in self.harassment_patterns):
            analysis['harassment'] = True
        
        # Determine severity
        if analysis['harassment']:
            analysis['severity'] = 'critical'
        elif analysis['spam']:
            analysis['severity'] = 'high'
        elif analysis['profanity']:
            analysis['severity'] = 'medium'
        elif analysis['word_count'] < 2:
            analysis['severity'] = 'low'
        else:
            analysis['severity'] = 'safe'
        
        return analysis
    
    def evaluate_rules(self, analysis: Dict) -> str:
        """Evaluate moderation rules"""
        severity = analysis['severity']
        
        if severity == 'critical':
            return 'delete'
        elif severity == 'high':
            return 'delete'
        elif severity == 'medium':
            return 'delete'
        elif severity == 'low':
            return 'review'
        else:
            return 'allow'
    
    def delete_comment(self, comment_id: str) -> bool:
        """Delete a comment"""
        try:
            url = "https://open.tiktokapis.com/v2/video/comment/delete/"
            data = {"comment_id": comment_id}
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            self.log_action(comment_id, 'delete', True)
            return True
        except Exception as e:
            self.log_action(comment_id, 'delete', False, str(e))
            return False
    
    def pin_comment(self, comment_id: str) -> bool:
        """Pin a comment"""
        try:
            url = "https://open.tiktokapis.com/v2/video/comment/pin/"
            data = {"comment_id": comment_id}
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            self.log_action(comment_id, 'pin', True)
            return True
        except Exception as e:
            self.log_action(comment_id, 'pin', False, str(e))
            return False
    
    def log_action(self, comment_id: str, action: str, 
                   success: bool, error: str = None):
        """Log moderation action"""
        log_entry = {
            'comment_id': comment_id,
            'action': action,
            'success': success,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        self.action_log.append(log_entry)
        print(f"Action: {action.upper()} comment {comment_id} - {'✓' if success else '✗'}")
    
    def get_video_comments(self, video_id: str) -> List[Dict]:
        """Get comments for a video"""
        try:
            url = "https://open.tiktokapis.com/v2/video/comment/list/"
            params = {"video_id": video_id, "max_count": 100}
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()['data'].get('comments', [])
        except Exception as e:
            print(f"Error fetching comments for {video_id}: {e}")
            return []
    
    def moderate_video(self, video_id: str) -> Dict:
        """Moderate all comments on a video"""
        print(f"\nModerating video: {video_id}")
        
        comments = self.get_video_comments(video_id)
        results = {
            'total': len(comments),
            'deleted': 0,
            'pinned': 0,
            'reviewed': 0,
            'allowed': 0
        }
        
        for comment in comments:
            analysis = self.analyze_comment(comment)
            action = self.evaluate_rules(analysis)
            
            if action == 'delete':
                if self.delete_comment(comment['id']):
                    results['deleted'] += 1
            elif action == 'pin':
                if self.pin_comment(comment['id']):
                    results['pinned'] += 1
            elif action == 'review':
                self.log_action(comment['id'], 'review', True)
                results['reviewed'] += 1
            else:
                results['allowed'] += 1
        
        return results
    
    def moderate_multiple_videos(self, video_ids: List[str]) -> Dict:
        """Moderate multiple videos"""
        print(f"Starting moderation for {len(video_ids)} videos")
        
        total_results = {
            'videos': len(video_ids),
            'total_comments': 0,
            'deleted': 0,
            'pinned': 0,
            'reviewed': 0,
            'allowed': 0
        }
        
        for i, video_id in enumerate(video_ids, 1):
            print(f"\n[{i}/{len(video_ids)}] Processing video {video_id}")
            results = self.moderate_video(video_id)
            
            total_results['total_comments'] += results['total']
            total_results['deleted'] += results['deleted']
            total_results['pinned'] += results['pinned']
            total_results['reviewed'] += results['reviewed']
            total_results['allowed'] += results['allowed']
            
            # Small delay between videos
            if i < len(video_ids):
                time.sleep(2)
        
        return total_results
    
    def generate_report(self) -> str:
        """Generate moderation report"""
        report = {
            'summary': {
                'total_actions': len(self.action_log),
                'successful': sum(1 for log in self.action_log if log['success']),
                'failed': sum(1 for log in self.action_log if not log['success'])
            },
            'by_action': {},
            'actions': self.action_log
        }
        
        for log in self.action_log:
            action = log['action']
            if action not in report['by_action']:
                report['by_action'][action] = 0
            report['by_action'][action] += 1
        
        return json.dumps(report, indent=2)
    
    def save_report(self, filename: str = "tiktok_moderation_report.json"):
        """Save moderation report to file"""
        report = self.generate_report()
        with open(filename, 'w') as f:
            f.write(report)
        print(f"\nReport saved to {filename}")

def main():
    # Initialize moderator
    access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
    if not access_token:
        print("Error: TIKTOK_ACCESS_TOKEN not found in .env file")
        return
    
    moderator = TikTokModerator(access_token)
    
    # Get video IDs from environment
    video_ids_str = os.getenv("VIDEO_IDS", "")
    video_ids = [vid.strip() for vid in video_ids_str.split(",") if vid.strip()]
    
    if not video_ids:
        print("Error: No video IDs provided in .env file")
        print("Add VIDEO_IDS=video_id_1,video_id_2 to .env")
        return
    
    # Moderate videos
    results = moderator.moderate_multiple_videos(video_ids)
    
    # Print summary
    print("\n" + "="*50)
    print("MODERATION SUMMARY")
    print("="*50)
    print(f"Videos processed: {results['videos']}")
    print(f"Total comments: {results['total_comments']}")
    print(f"Deleted: {results['deleted']}")
    print(f"Pinned: {results['pinned']}")
    print(f"Reviewed: {results['reviewed']}")
    print(f"Allowed: {results['allowed']}")
    print("="*50)
    
    # Save report
    moderator.save_report()

if __name__ == "__main__":
    main()
```

## Sample Output

```
Starting moderation for 3 videos

[1/3] Processing video video_id_1
Moderating video: video_id_1
Action: DELETE comment comment_id_1 - ✓
Action: PIN comment comment_id_2 - ✓
Action: REVIEW comment comment_id_3 - ✓
Action: ALLOW comment comment_id_4 - ✓

[2/3] Processing video video_id_2
Moderating video: video_id_2
Action: DELETE comment comment_id_5 - ✓
Action: ALLOW comment comment_id_6 - ✓

[3/3] Processing video video_id_3
Moderating video: video_id_3
Action: ALLOW comment comment_id_7 - ✓

==================================================
MODERATION SUMMARY
==================================================
Videos processed: 3
Total comments: 7
Deleted: 2
Pinned: 1
Reviewed: 1
Allowed: 3
==================================================

Report saved to tiktok_moderation_report.json
```

## Report Example

```json
{
  "summary": {
    "total_actions": 4,
    "successful": 4,
    "failed": 0
  },
  "by_action": {
    "delete": 2,
    "pin": 1,
    "review": 1
  },
  "actions": [
    {
      "comment_id": "comment_id_1",
      "action": "delete",
      "success": true,
      "error": null,
      "timestamp": "2025-01-08T10:30:00"
    },
    ...
  ]
}
```

## Next Steps

- Add webhook support for real-time moderation
- Implement more sophisticated analysis (sentiment, ML)
- Create a dashboard for monitoring moderation activity
- Add review queue for flagged comments
