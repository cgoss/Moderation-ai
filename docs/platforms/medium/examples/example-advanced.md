# Medium Advanced Integration Example

This example demonstrates an advanced Medium integration with comment tracking, automated moderation, and action execution.

## Features

- Track multiple articles for new comments
- Automated comment analysis
- Rule-based moderation
- Action execution (delete, flag)
- Comprehensive logging

## Setup

1. Create a `.env` file:
```bash
MEDIUM_ACCESS_TOKEN=your_access_token_here
ARTICLE_IDS=article_id_1,article_id_2
```

## Complete Implementation

```python
import os
from dotenv import load_dotenv
import requests
import re
import time
from datetime import datetime
from typing import List, Dict, Optional
import json

load_dotenv()

class MediumModerator:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        self.article_cache = {}
        self.action_log = []
        
        # Setup moderation rules
        self.setup_rules()
    
    def setup_rules(self):
        """Setup moderation rules"""
        self.spam_keywords = {
            'click here', 'free money', 'win big', 'subscribe now',
            'limited time', 'act now', 'amazing offer'
        }
        
        self.profanity_words = {
            'badword1', 'badword2', 'badword3'
        }
        
        self.harassment_patterns = [
            r'you.*stupid',
            r'you.*idiot',
            r'go.*kill.*yourself'
        ]
    
    def extract_text(self, content: str) -> str:
        """Extract plain text from HTML content"""
        text = re.sub(r'<[^>]+>', ' ', content)
        return ' '.join(text.split())
    
    def analyze_comment(self, comment: Dict) -> Dict:
        """Analyze comment for moderation"""
        text = self.extract_text(comment['content']).lower()
        words = text.split()
        
        analysis = {
            'comment_id': comment['id'],
            'article_id': comment['parentId'],
            'text': text,
            'word_count': len(words),
            'char_count': len(text),
            'spam': False,
            'profanity': False,
            'harassment': False,
            'has_links': False,
            'excessive_caps': False,
            'severity': 'low'
        }
        
        # Check for spam
        if any(keyword in text for keyword in self.spam_keywords):
            analysis['spam'] = True
            analysis['severity'] = 'high'
        
        # Check for profanity
        if any(word in self.profanity_words for word in words):
            analysis['profanity'] = True
            analysis['severity'] = 'medium'
        
        # Check for harassment
        if any(re.search(pattern, text) for pattern in self.harassment_patterns):
            analysis['harassment'] = True
            analysis['severity'] = 'critical'
        
        # Check for links
        if re.search(r'https?://\S+', text):
            analysis['has_links'] = True
        
        # Check for excessive caps
        if words and sum(1 for c in text if c.isupper()) / len(text) > 0.7:
            analysis['excessive_caps'] = True
            analysis['severity'] = 'medium'
        
        # Check for very short comments
        if analysis['word_count'] < 2:
            analysis['severity'] = 'low'
        
        return analysis
    
    def evaluate_rules(self, analysis: Dict) -> str:
        """Evaluate moderation rules"""
        severity = analysis['severity']
        
        if severity == 'critical':
            return 'delete'
        elif severity == 'high':
            return 'delete'
        elif severity == 'medium':
            return 'flag'
        elif analysis['word_count'] < 2:
            return 'flag'
        else:
            return 'allow'
    
    def delete_comment(self, comment_id: str) -> bool:
        """Delete a comment"""
        try:
            url = f"https://api.medium.com/v1/responses/{comment_id}"
            response = requests.delete(url, headers=self.headers)
            
            success = response.status_code == 204
            self.log_action(comment_id, 'delete', success)
            
            return success
        except Exception as e:
            self.log_action(comment_id, 'delete', False, str(e))
            return False
    
    def flag_comment(self, comment_id: str) -> bool:
        """Flag a comment for review"""
        # Medium doesn't have native flag API
        # Log for manual review
        self.log_action(comment_id, 'flag', True)
        return True
    
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
    
    def get_article_comments(self, article_id: str) -> List[Dict]:
        """Get comments for an article"""
        try:
            url = f"https://api.medium.com/v1/posts/{article_id}/responses"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            print(f"Error fetching comments for {article_id}: {e}")
            return []
    
    def moderate_article(self, article_id: str) -> Dict:
        """Moderate all comments on an article"""
        print(f"\nModerating article: {article_id}")
        
        comments = self.get_article_comments(article_id)
        results = {
            'total': len(comments),
            'deleted': 0,
            'flagged': 0,
            'allowed': 0
        }
        
        for comment in comments:
            analysis = self.analyze_comment(comment)
            action = self.evaluate_rules(analysis)
            
            if action == 'delete':
                if self.delete_comment(comment['id']):
                    results['deleted'] += 1
            elif action == 'flag':
                self.flag_comment(comment['id'])
                results['flagged'] += 1
            else:
                results['allowed'] += 1
        
        return results
    
    def moderate_multiple_articles(self, article_ids: List[str]) -> Dict:
        """Moderate multiple articles"""
        print(f"Starting moderation for {len(article_ids)} articles")
        
        total_results = {
            'articles': len(article_ids),
            'total_comments': 0,
            'deleted': 0,
            'flagged': 0,
            'allowed': 0
        }
        
        for i, article_id in enumerate(article_ids, 1):
            print(f"\n[{i}/{len(article_ids)}] Processing article {article_id}")
            results = self.moderate_article(article_id)
            
            total_results['total_comments'] += results['total']
            total_results['deleted'] += results['deleted']
            total_results['flagged'] += results['flagged']
            total_results['allowed'] += results['allowed']
            
            # Small delay between articles
            if i < len(article_ids):
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
    
    def save_report(self, filename: str = "moderation_report.json"):
        """Save moderation report to file"""
        report = self.generate_report()
        with open(filename, 'w') as f:
            f.write(report)
        print(f"\nReport saved to {filename}")

def main():
    # Initialize moderator
    access_token = os.getenv("MEDIUM_ACCESS_TOKEN")
    if not access_token:
        print("Error: MEDIUM_ACCESS_TOKEN not found in .env file")
        return
    
    moderator = MediumModerator(access_token)
    
    # Get article IDs from environment
    article_ids_str = os.getenv("ARTICLE_IDS", "")
    article_ids = [aid.strip() for aid in article_ids_str.split(",") if aid.strip()]
    
    if not article_ids:
        print("Error: No article IDs provided in .env file")
        print("Add ARTICLE_IDS=article_id_1,article_id_2 to .env")
        return
    
    # Moderate articles
    results = moderator.moderate_multiple_articles(article_ids)
    
    # Print summary
    print("\n" + "="*50)
    print("MODERATION SUMMARY")
    print("="*50)
    print(f"Articles processed: {results['articles']}")
    print(f"Total comments: {results['total_comments']}")
    print(f"Deleted: {results['deleted']}")
    print(f"Flagged: {results['flagged']}")
    print(f"Allowed: {results['allowed']}")
    print("="*50)
    
    # Save report
    moderator.save_report()

if __name__ == "__main__":
    main()
```

## Sample Output

```
Starting moderation for 3 articles

[1/3] Processing article article_id_1
Moderating article: article_id_1
Action: DELETE comment comment_id_1 - ✓
Action: DELETE comment comment_id_2 - ✓
Action: FLAG comment comment_id_3 - ✓
Action: ALLOW comment comment_id_4 - ✓

[2/3] Processing article article_id_2
Moderating article: article_id_2
Action: FLAG comment comment_id_5 - ✓
Action: ALLOW comment comment_id_6 - ✓

[3/3] Processing article article_id_3
Moderating article: article_id_3
Action: ALLOW comment comment_id_7 - ✓

==================================================
MODERATION SUMMARY
==================================================
Articles processed: 3
Total comments: 7
Deleted: 2
Flagged: 2
Allowed: 3
==================================================

Report saved to moderation_report.json
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
    "flag": 2
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
