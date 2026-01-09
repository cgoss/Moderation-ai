# TikTok Webhook Integration Example

This example demonstrates how to set up webhook integration with TikTok for real-time comment moderation.

## Prerequisites

1. A publicly accessible server (or use ngrok for local development)
2. TikTok API access with webhook permissions
3. SSL/TLS certificate (required for webhooks)

## Setup

1. Install dependencies:
```bash
pip install flask requests python-dotenv
```

2. Create `.env` file:
```bash
TIKTOK_ACCESS_TOKEN=your_access_token
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

ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")
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
        self.spam_keywords = {'follow me', 'click here', 'free money'}
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
    
    def moderate_comment(self, comment_id: str, text: str, video_id: str) -> str:
        """Moderate comment and return action"""
        analysis = self.analyze_comment(text)
        
        if analysis['spam'] or analysis['profanity']:
            return 'delete'
        elif analysis['word_count'] < 2:
            return 'review'
        else:
            return 'allow'
    
    def delete_comment(self, comment_id: str) -> bool:
        """Delete a comment"""
        try:
            url = "https://open.tiktokapis.com/v2/video/comment/delete/"
            data = {"comment_id": comment_id}
            response = requests.post(url, headers=self.headers, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error deleting comment: {e}")
            return False
    
    def log_event(self, event: dict, action: str):
        """Log webhook event"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event.get('type'),
            'comment_id': event.get('comment_id'),
            'video_id': event.get('video_id'),
            'action': action
        }
        print(f"Log: {log_entry}")
        
        # Save to log file
        with open('tiktok_webhook_events.log', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

moderator = WebhookModerator()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle webhook events"""
    signature = request.headers.get('X-TikTok-Signature')
    payload = request.get_data(as_text=True)
    
    # Verify signature
    if not moderator.verify_signature(payload, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    event = request.json
    event_type = event.get('type')
    
    print(f"Received event: {event_type}")
    
    # Handle comment events
    if event_type == 'video_comment_created':
        handle_comment_created(event)
    elif event_type == 'video_comment_deleted':
        handle_comment_deleted(event)
    
    return jsonify({'status': 'ok'}), 200

def handle_comment_created(event):
    """Handle new comment"""
    comment_id = event.get('comment_id')
    video_id = event.get('video_id')
    text = event.get('text', '')
    
    print(f"New comment {comment_id} on video {video_id}")
    
    # Moderate comment
    action = moderator.moderate_comment(comment_id, text, video_id)
    
    # Execute action
    if action == 'delete':
        if moderator.delete_comment(comment_id):
            print(f"Deleted comment {comment_id}")
    elif action == 'review':
        print(f"Flagged comment {comment_id} for review")
    
    # Log event
    moderator.log_event(event, action)

def handle_comment_deleted(event):
    """Handle deleted comment"""
    comment_id = event.get('comment_id')
    print(f"Comment {comment_id} was deleted")
    moderator.log_event(event, 'deleted')

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

ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")
WEBHOOK_URL = "https://your-domain.com/webhook"

def register_webhook():
    """Register webhook with TikTok"""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": WEBHOOK_URL,
        "secret": os.getenv("WEBHOOK_SECRET"),
        "events": [
            "video_comment_created",
            "video_comment_deleted"
        ]
    }
    
    response = requests.post(
        "https://open.tiktokapis.com/v2/webhook/register/",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
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
        "https://open.tiktokapis.com/v2/webhook/list/",
        headers=headers
    )
    
    if response.status_code == 200:
        webhooks = response.json()['data']
        print(f"Found {len(webhooks)} webhooks:")
        for webhook in webhooks:
            print(f"  - ID: {webhook['id']}")
            print(f"    URL: {webhook['url']}")
            print(f"    Events: {webhook['events']}")
        return webhooks
    else:
        print(f"Failed to list webhooks: {response.status_code}")
        return []

def delete_webhook(webhook_id):
    """Delete a webhook"""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.delete(
        f"https://open.tiktokapis.com/v2/webhook/delete/",
        headers=headers,
        json={"webhook_id": webhook_id}
    )
    
    if response.status_code == 200:
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

# Copy https URL from ngrok output
# Update WEBHOOK_URL in webhook registration script
WEBHOOK_URL="https://your-ngrok-url.ngrok.io/webhook"
```

## Monitoring Webhook Events

```python
import json
from collections import defaultdict
from datetime import datetime, timedelta

def analyze_webhook_logs(log_file='tiktok_webhook_events.log'):
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
  "type": "video_comment_created",
  "comment_id": "comment_id_here",
  "video_id": "video_id_here",
  "text": "This is a new comment",
  "user_id": "user_id_here",
  "username": "@username",
  "created_at": 1234567890
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
