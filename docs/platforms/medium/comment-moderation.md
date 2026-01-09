# Medium Comment Moderation

## Overview

This guide details the comment moderation workflow for Medium articles, including analyzing comments, applying rules, and taking moderation actions.

## Moderation Workflow

```
New Comment → Content Analysis → Rule Evaluation → Action Decision → Execute Action
```

## Comment Analysis

### 1. Content Extraction

Extract text content from Medium comments:

```python
import re
from html import unescape
from typing import Dict, List

class CommentAnalyzer:
    @staticmethod
    def extract_text(comment: Dict) -> str:
        """Extract plain text from comment"""
        content = comment.get('content', '')
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', content)
        
        # Unescape HTML entities
        text = unescape(text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def extract_metadata(comment: Dict) -> Dict:
        """Extract metadata from comment"""
        return {
            'id': comment.get('id'),
            'author_id': comment.get('creatorId'),
            'parent_id': comment.get('parentId'),
            'created_at': comment.get('createdAt'),
            'vote_count': comment.get('voteCount', 0),
            'content_format': comment.get('contentFormat', 'html')
        }
```

### 2. Content Analysis

Analyze comment for various attributes:

```python
class ContentAnalysis:
    def __init__(self):
        self.profanity_list = self.load_profanity_list()
        self.spam_keywords = self.load_spam_keywords()
    
    def load_profanity_list(self) -> set:
        """Load list of profane words"""
        return {"badword1", "badword2", "badword3"}
    
    def load_spam_keywords(self) -> set:
        """Load spam detection keywords"""
        return {"click here", "free money", "win big", "subscribe"}
    
    def detect_profanity(self, text: str) -> bool:
        """Detect profanity in text"""
        words = text.lower().split()
        return any(word in self.profanity_list for word in words)
    
    def detect_spam(self, text: str) -> bool:
        """Detect spam patterns"""
        # Check for spam keywords
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in self.spam_keywords):
            return True
        
        # Check for excessive links
        links = re.findall(r'https?://\S+', text)
        if len(links) > 3:
            return True
        
        # Check for excessive caps
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.7:
            return True
        
        return False
    
    def detect_harassment(self, text: str) -> bool:
        """Detect harassment patterns"""
        harassment_patterns = [
            r'you.*stupid',
            r'you.*idiot',
            r'go.*kill.*yourself',
            r'you.*are.*awful'
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in harassment_patterns)
    
    def analyze(self, text: str) -> Dict:
        """Perform comprehensive analysis"""
        return {
            'profanity': self.detect_profanity(text),
            'spam': self.detect_spam(text),
            'harassment': self.detect_harassment(text),
            'word_count': len(text.split()),
            'char_count': len(text),
            'contains_link': bool(re.search(r'https?://\S+', text))
        }
```

## Rule Engine

### 1. Rule Definition

Define moderation rules:

```python
from enum import Enum, auto

class ModerationAction(Enum):
    ALLOW = auto()
    FLAG = auto()
    DELETE = auto()
    HIDE = auto()

class Rule:
    def __init__(self, name: str, priority: int, condition: callable, action: ModerationAction):
        self.name = name
        self.priority = priority
        self.condition = condition
        self.action = action
    
    def evaluate(self, comment: Dict, analysis: Dict) -> tuple[bool, ModerationAction]:
        """Evaluate rule against comment"""
        if self.condition(comment, analysis):
            return True, self.action
        return False, None

class RuleEngine:
    def __init__(self):
        self.rules = []
    
    def add_rule(self, rule: Rule):
        """Add a rule to the engine"""
        self.rules.append(rule)
    
    def evaluate_comment(self, comment: Dict, analysis: Dict) -> ModerationAction:
        """Evaluate all rules against a comment"""
        # Sort rules by priority (higher priority first)
        sorted_rules = sorted(self.rules, key=lambda r: -r.priority)
        
        for rule in sorted_rules:
            triggered, action = rule.evaluate(comment, analysis)
            if triggered:
                print(f"Rule '{rule.name}' triggered")
                return action
        
        return ModerationAction.ALLOW
```

### 2. Predefined Rules

Create common moderation rules:

```python
class PredefinedRules:
    @staticmethod
    def create_harassment_rule() -> Rule:
        """Rule for harassment detection"""
        return Rule(
            name="Harassment Detection",
            priority=100,
            condition=lambda comment, analysis: analysis['harassment'],
            action=ModerationAction.DELETE
        )
    
    @staticmethod
    def create_spam_rule() -> Rule:
        """Rule for spam detection"""
        return Rule(
            name="Spam Detection",
            priority=90,
            condition=lambda comment, analysis: analysis['spam'],
            action=ModerationAction.DELETE
        )
    
    @staticmethod
    def create_profanity_rule() -> Rule:
        """Rule for profanity detection"""
        return Rule(
            name="Profanity Detection",
            priority=80,
            condition=lambda comment, analysis: analysis['profanity'],
            action=ModerationAction.FLAG
        )
    
    @staticmethod
    def create_short_comment_rule() -> Rule:
        """Rule for very short comments"""
        return Rule(
            name="Short Comment Filter",
            priority=30,
            condition=lambda comment, analysis: analysis['word_count'] < 2,
            action=ModerationAction.FLAG
        )
    
    @staticmethod
    def setup_default_rules(engine: RuleEngine):
        """Setup default moderation rules"""
        engine.add_rule(PredefinedRules.create_harassment_rule())
        engine.add_rule(PredefinedRules.create_spam_rule())
        engine.add_rule(PredefinedRules.create_profanity_rule())
        engine.add_rule(PredefinedRules.create_short_comment_rule())
```

## Moderation Actions

### 1. Action Executor

Execute moderation actions on Medium:

```python
import requests

class ActionExecutor:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        self.action_log = []
    
    def delete_comment(self, comment_id: str) -> bool:
        """Delete a comment"""
        url = f"https://api.medium.com/v1/responses/{comment_id}"
        
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            
            self.log_action(comment_id, ModerationAction.DELETE, True)
            return True
        
        except Exception as e:
            print(f"Error deleting comment {comment_id}: {e}")
            self.log_action(comment_id, ModerationAction.DELETE, False, str(e))
            return False
    
    def flag_comment(self, comment_id: str) -> bool:
        """Flag a comment for review"""
        # Medium doesn't have a native flag API
        # Log for manual review
        self.log_action(comment_id, ModerationAction.FLAG, True)
        return True
    
    def log_action(self, comment_id: str, action: ModerationAction, 
                   success: bool, error: str = None):
        """Log moderation action"""
        log_entry = {
            'comment_id': comment_id,
            'action': action.name,
            'success': success,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        self.action_log.append(log_entry)
    
    def get_action_log(self) -> List[Dict]:
        """Get all action logs"""
        return self.action_log
```

### 2. Action Queue

Queue actions for batch processing:

```python
import queue
import threading

class ActionQueue:
    def __init__(self, executor: ActionExecutor):
        self.executor = executor
        self.queue = queue.Queue()
        self.workers = []
        self.running = False
    
    def add_action(self, comment_id: str, action: ModerationAction):
        """Add action to queue"""
        self.queue.put((comment_id, action))
    
    def process_queue(self):
        """Process actions from queue"""
        while self.running:
            try:
                comment_id, action = self.queue.get(timeout=1)
                
                if action == ModerationAction.DELETE:
                    self.executor.delete_comment(comment_id)
                elif action == ModerationAction.FLAG:
                    self.executor.flag_comment(comment_id)
                
                self.queue.task_done()
            
            except queue.Empty:
                continue
    
    def start(self, num_workers: int = 2):
        """Start processing queue"""
        self.running = True
        for _ in range(num_workers):
            worker = threading.Thread(target=self.process_queue)
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """Stop processing queue"""
        self.running = False
        for worker in self.workers:
            worker.join()
```

## Integration

### 1. Full Moderation Pipeline

Combine all components:

```python
class CommentModerator:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.analyzer = CommentAnalyzer()
        self.content_analysis = ContentAnalysis()
        self.rule_engine = RuleEngine()
        self.executor = ActionExecutor(access_token)
        self.action_queue = ActionQueue(self.executor)
        
        # Setup default rules
        PredefinedRules.setup_default_rules(self.rule_engine)
    
    def moderate_comment(self, comment: Dict) -> ModerationAction:
        """Moderate a single comment"""
        # Extract text
        text = self.analyzer.extract_text(comment)
        
        # Analyze content
        analysis = self.content_analysis.analyze(text)
        
        # Evaluate rules
        action = self.rule_engine.evaluate_comment(comment, analysis)
        
        # Execute action
        comment_id = comment.get('id')
        if action != ModerationAction.ALLOW:
            self.action_queue.add_action(comment_id, action)
        
        return action
    
    def moderate_comments(self, comments: List[Dict]) -> Dict[str, ModerationAction]:
        """Moderate multiple comments"""
        results = {}
        
        for comment in comments:
            action = self.moderate_comment(comment)
            results[comment['id']] = action
        
        return results
```

### 2. Real-time Moderation

Moderate comments in real-time:

```python
class RealtimeModerator:
    def __init__(self, moderator: CommentModerator):
        self.moderator = moderator
        self.action_queue = moderator.action_queue
    
    def on_new_comment(self, article_id: str, comments: List[Dict]):
        """Handle new comments"""
        print(f"Moderating {len(comments)} new comments on article {article_id}")
        
        actions = self.moderator.moderate_comments(comments)
        
        # Start action queue if not running
        if not self.action_queue.running:
            self.action_queue.start()
```

## Audit Trail

Maintain audit trail of all moderation actions:

```python
import json

class AuditLogger:
    def __init__(self, log_path: str = "audit_log.json"):
        self.log_path = log_path
    
    def log_moderation(self, comment: Dict, action: ModerationAction, 
                       analysis: Dict = None):
        """Log moderation action"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'comment_id': comment.get('id'),
            'article_id': comment.get('parentId'),
            'author_id': comment.get('creatorId'),
            'content': self.analyzer.extract_text(comment),
            'action': action.name,
            'analysis': analysis
        }
        
        # Append to log file
        logs = self.load_logs()
        logs.append(log_entry)
        
        with open(self.log_path, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def load_logs(self) -> List[Dict]:
        """Load all logs"""
        if not os.path.exists(self.log_path):
            return []
        
        with open(self.log_path, 'r') as f:
            return json.load(f)
    
    def get_logs_by_article(self, article_id: str) -> List[Dict]:
        """Get logs for a specific article"""
        logs = self.load_logs()
        return [log for log in logs if log['article_id'] == article_id]
```

## Reporting

Generate moderation reports:

```python
class ModerationReporter:
    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
    
    def generate_report(self, start_date: str = None, end_date: str = None) -> Dict:
        """Generate moderation report"""
        logs = self.audit_logger.load_logs()
        
        # Filter by date range if provided
        if start_date:
            logs = [log for log in logs if log['timestamp'] >= start_date]
        if end_date:
            logs = [log for log in logs if log['timestamp'] <= end_date]
        
        # Calculate statistics
        total_comments = len(logs)
        deleted = sum(1 for log in logs if log['action'] == 'DELETE')
        flagged = sum(1 for log in logs if log['action'] == 'FLAG')
        allowed = sum(1 for log in logs if log['action'] == 'ALLOW')
        
        return {
            'total_comments': total_comments,
            'deleted': deleted,
            'flagged': flagged,
            'allowed': allowed,
            'delete_rate': deleted / total_comments if total_comments > 0 else 0,
            'flag_rate': flagged / total_comments if total_comments > 0 else 0
        }
```

## Best Practices

1. **Start conservative**: Begin with permissive rules, tighten gradually
2. **Review flagged content**: Regularly review flagged comments
3. **Monitor false positives**: Track and adjust for false positives
4. **Maintain audit trail**: Keep detailed logs of all actions
5. **Test rules**: Test rules on historical data before deployment
6. **Escalate edge cases**: Have a process for ambiguous cases

## Summary

The Medium comment moderation system provides:
- Content analysis (profanity, spam, harassment detection)
- Rule-based moderation engine
- Action execution (delete, flag, allow)
- Queued action processing
- Comprehensive audit trail
- Reporting and analytics
