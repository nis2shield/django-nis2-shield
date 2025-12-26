"""
Webhook notifications for real-time security alerting.

Supports multiple webhook formats:
- Slack (Incoming Webhooks)
- Microsoft Teams (Incoming Webhooks)  
- Discord (Webhooks)
- Generic HTTP POST (JSON payload)

Usage in settings.py:
    NIS2_SHIELD = {
        'ENABLE_WEBHOOKS': True,
        'WEBHOOK_ASYNC': True,  # Non-blocking (recommended)
        'WEBHOOKS': [
            {'url': 'https://hooks.slack.com/services/...', 'format': 'slack'},
            {'url': 'https://outlook.office.com/webhook/...', 'format': 'teams'},
            {'url': 'https://discord.com/api/webhooks/...', 'format': 'discord'},
            {'url': 'https://your-siem.com/api/alerts', 'format': 'json'},
        ]
    }
"""
import json
import logging
import threading
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from django.conf import settings

logger = logging.getLogger('django_nis2_shield')


# Event severity levels
SEVERITY_LEVELS = {
    'info': {'color': '#36a64f', 'teams_color': '00FF00', 'discord_color': 3066993},
    'warning': {'color': '#ff9800', 'teams_color': 'FFA500', 'discord_color': 16750848},
    'critical': {'color': '#f44336', 'teams_color': 'FF0000', 'discord_color': 15158332},
}

# Default severity for event types
EVENT_SEVERITY = {
    'rate_limit_exceeded': 'warning',
    'session_hijack_detected': 'critical',
    'tor_node_blocked': 'warning',
    'mfa_required': 'info',
    'audit_log': 'info',
}


class WebhookNotifier:
    """
    Sends real-time notifications to configured webhooks when security events occur.
    
    By default, notifications are sent asynchronously to avoid blocking request processing.
    """
    
    def __init__(self):
        nis2_conf = getattr(settings, 'NIS2_SHIELD', {})
        self.webhooks = nis2_conf.get('WEBHOOKS', [])
        self.enabled = nis2_conf.get('ENABLE_WEBHOOKS', False)
        self.async_send = nis2_conf.get('WEBHOOK_ASYNC', True)
        self.timeout = nis2_conf.get('WEBHOOK_TIMEOUT', 5)
    
    def notify(self, event_type: str, data: dict):
        """
        Send notification to all configured webhooks.
        
        Args:
            event_type: Type of event (e.g., 'rate_limit_exceeded', 'session_hijack_detected')
            data: Event data dict containing relevant information
        """
        if not self.enabled or not self.webhooks:
            return
        
        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        payload = self._build_payload(event_type, data)
        
        for webhook in self.webhooks:
            if self.async_send:
                thread = threading.Thread(
                    target=self._send_webhook,
                    args=(webhook, payload),
                    daemon=True
                )
                thread.start()
            else:
                self._send_webhook(webhook, payload)
    
    def _build_payload(self, event_type: str, data: dict) -> dict:
        """Build the base payload for notifications."""
        severity = EVENT_SEVERITY.get(event_type, 'info')
        
        return {
            'event_type': event_type,
            'source': 'django-nis2-shield',
            'timestamp': data.get('timestamp'),
            'severity': severity,
            'details': data
        }
    
    def _send_webhook(self, webhook: dict, payload: dict):
        """Send payload to a specific webhook."""
        try:
            url = webhook.get('url')
            format_type = webhook.get('format', 'json')
            
            # Format payload based on webhook type
            if format_type == 'slack':
                body = self._format_slack(payload)
            elif format_type == 'teams':
                body = self._format_teams(payload)
            elif format_type == 'discord':
                body = self._format_discord(payload)
            else:
                body = payload
            
            # Send HTTP request
            data = json.dumps(body).encode('utf-8')
            req = Request(url, data=data)
            req.add_header('Content-Type', 'application/json')
            req.add_header('User-Agent', 'DjangoNIS2Shield/0.3.0')
            
            with urlopen(req, timeout=self.timeout) as response:
                if response.status >= 400:
                    logger.error(f"Webhook returned status {response.status}: {url}")
                    
        except HTTPError as e:
            logger.error(f"Webhook HTTP error {e.code}: {url}")
        except URLError as e:
            logger.error(f"Webhook connection error: {url} - {e.reason}")
        except Exception as e:
            logger.error(f"Webhook notification failed: {url} - {str(e)}")
    
    def _format_slack(self, payload: dict) -> dict:
        """Format payload for Slack Incoming Webhook."""
        severity = payload['severity']
        color = SEVERITY_LEVELS.get(severity, SEVERITY_LEVELS['info'])['color']
        
        # Build attachment fields from details
        fields = []
        details = payload.get('details', {})
        for key, value in details.items():
            if key != 'timestamp' and value:
                fields.append({
                    'title': key.replace('_', ' ').title(),
                    'value': str(value),
                    'short': len(str(value)) < 30
                })
        
        return {
            'text': f"🛡️ NIS2 Security Alert",
            'attachments': [{
                'color': color,
                'title': payload['event_type'].replace('_', ' ').title(),
                'fields': fields,
                'footer': 'Django NIS2 Shield',
                'ts': int(datetime.utcnow().timestamp())
            }]
        }
    
    def _format_teams(self, payload: dict) -> dict:
        """Format payload for Microsoft Teams Incoming Webhook."""
        severity = payload['severity']
        color = SEVERITY_LEVELS.get(severity, SEVERITY_LEVELS['info'])['teams_color']
        
        # Build facts from details
        facts = []
        details = payload.get('details', {})
        for key, value in details.items():
            if key != 'timestamp' and value:
                facts.append({
                    'name': key.replace('_', ' ').title(),
                    'value': str(value)
                })
        
        return {
            '@type': 'MessageCard',
            '@context': 'http://schema.org/extensions',
            'themeColor': color,
            'summary': f"NIS2 Alert: {payload['event_type']}",
            'sections': [{
                'activityTitle': f"🛡️ {payload['event_type'].replace('_', ' ').title()}",
                'activitySubtitle': f"Severity: {severity.upper()}",
                'facts': facts,
                'markdown': True
            }]
        }
    
    def _format_discord(self, payload: dict) -> dict:
        """Format payload for Discord Webhook."""
        severity = payload['severity']
        color = SEVERITY_LEVELS.get(severity, SEVERITY_LEVELS['info'])['discord_color']
        
        # Build fields from details
        fields = []
        details = payload.get('details', {})
        for key, value in details.items():
            if key != 'timestamp' and value:
                fields.append({
                    'name': key.replace('_', ' ').title(),
                    'value': str(value),
                    'inline': len(str(value)) < 30
                })
        
        return {
            'embeds': [{
                'title': f"🛡️ NIS2 Security Alert",
                'description': payload['event_type'].replace('_', ' ').title(),
                'color': color,
                'fields': fields,
                'footer': {'text': 'Django NIS2 Shield'},
                'timestamp': payload.get('timestamp')
            }]
        }


# Singleton instance for easy import
_notifier_instance = None


def get_webhook_notifier() -> WebhookNotifier:
    """Get the singleton WebhookNotifier instance."""
    global _notifier_instance
    if _notifier_instance is None:
        _notifier_instance = WebhookNotifier()
    return _notifier_instance


def notify_security_event(event_type: str, **kwargs):
    """
    Convenience function to send a security event notification.
    
    Usage:
        from django_nis2_shield.webhooks import notify_security_event
        notify_security_event('rate_limit_exceeded', ip='1.2.3.4', threshold=100)
    """
    notifier = get_webhook_notifier()
    notifier.notify(event_type, kwargs)
