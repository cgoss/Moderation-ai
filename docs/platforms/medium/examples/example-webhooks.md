# Medium Webhook Integration Example

This example demonstrates how to set up webhook integration with Medium for real-time comment moderation.

## Prerequisites

1. A publicly accessible server (or use ngrok for local development)
2. Medium API access with webhook permissions
3. SSL/TLS certificate (required for webhooks)

## Setup

1. Install dependencies:
```bash
pip install flask requests python-dotenv
```

2. Create `.env` file:
```bash
MEDIUM_ACCESS_TOKEN=your_access_token
WEBHOOK_SECRET=your_webhook_secret
```

## Webhook Server Implementation

```python
import os
from dotenv import load_dotenv
import hmac
import hashlib
import json
from flask import Flask, request, jsonify
from datetime import datetime
import requests

load_dotenv()

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("MEDIUM_ACCESS_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET").encode()

class WebhookModerator:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        self.setup_rules()
    
    def setup_rules(self):
        """Setup moderation rules"""
        self.spam_keywords = {'click here', 'free money', 'win big'}
        self.profanity_words = {'badword1', 'badword2'}
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature"""
        expected_signature = hmac.new(
            WEBHOOK_SECRET,
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def analyze_comment(self, text: str) -> dict:
        """Analyze comment"""
        text_lower = text.lower()
        words = text_lower.split()
        
        return {
            'spam': any(keyword in text_lower for keyword in self.spam_keywords),
            'profanity': any(word in self.profanity_words for word in words),
            'word_count': len(words)
        }
    
    def moderate_comment(self, comment_id: str, text: str) -> str:
        """Moderate comment and return action"""
        analysis = self.analyze_comment(text)
        
        if analysis['spam']:
            return 'delete'
        elif analysis['profanity']:
            return 'delete'
        elif analysis['word_count'] < 2:
            return 'flag'
        else:
            return 'allow'
    
    def delete_comment(self, comment_id: str) -> bool:
        """Delete a comment"""
        try:
            url = f"https://api.medium.com/v1/responses/{comment_id}"
            response = requests.delete(url, headers=self.headers)
            return response.status_code == 204
        except Exception as e:
            print(f"Error deleting comment: {e}")
            return False
    
    def log_event(self, event: dict, action: str):
        """Log webhook event"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event.get('type'),
            'comment_id': event.get('comment_id'),
            'action': action
        }
        print(f"Log: {log_entry}")
        
        # Save to log file
        with open('webhook_events.log', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

moderator = WebhookModerator()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle webhook events"""
    signature = request.headers.get('X-Medium-Signature')
    payload = request.get_data()
    
    # Verify signature
    if not moderator.verify_signature(payload, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    event = request.json
    event_type = event.get('type')
    
    print(f"Received event: {event_type}")
    
    # Handle comment events
    if event_type == 'response.created':
        handle_comment_created(event)
    elif event_type == 'response.updated':
        handle_comment_updated(event)
    
    return jsonify({'status': 'ok'}), 200

def handle_comment_created(event):
    """Handle new comment"""
    comment_id = event.get('response_id')
    article_id = event.get('post_id')
    text = event.get('content', '')
    
    print(f"New comment {comment_id} on article {article_id}")
    
    # Moderate comment
    action = moderator.moderate_comment(comment_id, text)
    
    # Execute action
    if action == 'delete':
        if moderator.delete_comment(comment_id):
            print(f"Deleted comment {comment_id}")
    elif action == 'flag':
        print(f"Flagged comment {comment_id} for review")
    
    # Log event
    moderator.log_event(event, action)

def handle_comment_updated(event):
    """Handle updated comment"""
    comment_id = event.get('response_id')
    print(f"Comment {comment_id} was updated")
    moderator.log_event(event, 'review')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
```

## Webhook Registration

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("MEDIUM_ACCESS_TOKEN")
WEBHOOK_URL = "https://your-domain.com/webhook"

def register_webhook():
    """Register webhook with Medium"""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": WEBHOOK_URL,
        "topics": ["response.created", "response.updated"],
        "secret": os.getenv("WEBHOOK_SECRET")
    }
    
    response = requests.post(
        "https://api.medium.com/v1/webhooks",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 201:
        print("Webhook registered successfully")
        return response.json()
    else:
        print(f"Failed to register webhook: {response.status_code}")
        print(response.text)
        return None

def list_webhooks():
    """List registered webhooks"""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    response = requests.get(
        "https://api.medium.com/v1/webhooks",
        headers=headers
    )
    
    if response.status_code == 200:
        webhooks = response.json()['data']
        print(f"Found {len(webhooks)} webhooks:")
        for webhook in webhooks:
            print(f"  - ID: {webhook['id']}")
            print(f"    URL: {webhook['url']}")
            print(f"    Topics: {webhook['topics']}")
        return webhooks
    else:
        print(f"Failed to list webhooks: {response.status_code}")
        return []

def delete_webhook(webhook_id):
    """Delete a webhook"""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    response = requests.delete(
        f"https://api.medium.com/v1/webhooks/{webhook_id}",
        headers=headers
    )
    
    if response.status_code == 204:
        print(f"Webhook {webhook_id} deleted successfully")
        return True
    else:
        print(f"Failed to delete webhook: {response.status_code}")
        return False

if __name__ == "__main__":
    # List existing webhooks
    print("Listing existing webhooks...")
    webhooks = list_webhooks()
    
    if webhooks:
        webhook_id = webhooks[0]['id']
        print(f"\nDeleting webhook {webhook_id}...")
        delete_webhook(webhook_id)
    
    # Register new webhook
    print("\nRegistering new webhook...")
    register_webhook()
```

## Testing with ngrok (Local Development)

```bash
# Start ngrok
ngrok http 8080

# Copy the https URL from ngrok output
# Update WEBHOOK_URL in webhook registration script
WEBHOOK_URL="https://your-ngrok-url.ngrok.io/webhook"
```

## Monitoring Webhook Events

```python
import json
from collections import defaultdict
from datetime import datetime, timedelta

def analyze_webhook_logs(log_file='webhook_events.log'):
    """Analyze webhook event logs"""
    if not os.path.exists(log_file):
        print("No webhook logs found")
        return
    
    events = []
    with open(log_file, 'r') as f:
        for line in f:
            events.append(json.loads(line.strip()))
    
    # Calculate statistics
    stats = {
        'total_events': len(events),
        'by_type': defaultdict(int),
        'by_action': defaultdict(int),
        'time_range': None
    }
    
    timestamps = []
    for event in events:
        stats['by_type'][event['event_type']] += 1
        stats['by_action'][event['action']] += 1
        timestamps.append(datetime.fromisoformat(event['timestamp']))
    
    if timestamps:
        stats['time_range'] = {
            'start': min(timestamps).isoformat(),
            'end': max(timestamps).isoformat()
        }
    
    # Print report
    print("\nWebhook Event Analysis")
    print("="*50)
    print(f"Total events: {stats['total_events']}")
    print(f"\nBy event type:")
    for event_type, count in stats['by_type'].items():
        print(f"  {event_type}: {count}")
    print(f"\nBy action:")
    for action, count in stats['by_action'].items():
        print(f"  {action}: {count}")
    if stats['time_range']:
        print(f"\nTime range:")
        print(f"  Start: {stats['time_range']['start']}")
        print(f"  End: {stats['time_range']['end']}")

if __name__ == "__main__":
    analyze_webhook_logs()
```

## Sample Webhook Event

```json
{
  "type": "response.created",
  "response_id": "comment_id_here",
  "post_id": "article_id_here",
  "content": "<p>This is a new comment</p>",
  "creator_id": "user_id_here",
  "created_at": 1234567890000
}
```

## Production Considerations

1. **Security**:
   - Always verify webhook signatures
   - Use HTTPS
   - Keep webhook secret secure

2. **Reliability**:
   - Implement retry logic for failed requests
   - Store events for replay if needed
   - Monitor webhook delivery status

3. **Performance**:
   - Process events asynchronously
   - Use message queues for high volume
   - Implement rate limiting

4. **Monitoring**:
   - Log all webhook events
   - Set up alerts for failures
   - Monitor response times

## Summary

This example provides:
- Flask webhook server with signature verification
- Real-time comment moderation
- Webhook registration and management
- Event logging and analysis
- Testing tools for local development
