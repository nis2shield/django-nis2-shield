"""
Tests for v0.3.0 features:
- Sliding window rate limiting
- Multi-SIEM presets
- Webhook notifications
"""
import unittest
from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase, override_settings


class TestSlidingWindowRateLimiter(SimpleTestCase):
    """Tests for the sliding window rate limiting algorithm."""
    
    @override_settings(NIS2_SHIELD={
        'ENABLE_RATE_LIMIT': True,
        'RATE_LIMIT_THRESHOLD': 5,
        'RATE_LIMIT_WINDOW': 60,
        'RATE_LIMIT_ALGORITHM': 'sliding_window'
    })
    def test_sliding_window_allows_under_threshold(self):
        """Test that requests under threshold are allowed."""
        from django_nis2_shield.enforcer import RateLimiter
        
        limiter = RateLimiter()
        self.assertEqual(limiter.algorithm, 'sliding_window')
        
        # Should allow 5 requests
        for i in range(5):
            self.assertTrue(limiter.is_allowed('192.168.1.1'))
    
    @override_settings(NIS2_SHIELD={
        'ENABLE_RATE_LIMIT': True,
        'RATE_LIMIT_THRESHOLD': 3,
        'RATE_LIMIT_WINDOW': 60,
        'RATE_LIMIT_ALGORITHM': 'sliding_window'
    })
    def test_sliding_window_blocks_over_threshold(self):
        """Test that requests over threshold are blocked."""
        from django_nis2_shield.enforcer import RateLimiter
        
        limiter = RateLimiter()
        
        # Allow first 3
        for _ in range(3):
            limiter.is_allowed('10.0.0.1')
        
        # Block the 4th
        self.assertFalse(limiter.is_allowed('10.0.0.1'))
    
    @override_settings(NIS2_SHIELD={
        'ENABLE_RATE_LIMIT': True,
        'RATE_LIMIT_THRESHOLD': 5,
        'RATE_LIMIT_ALGORITHM': 'fixed_window'
    })
    def test_fixed_window_fallback(self):
        """Test backward compatibility with fixed window algorithm."""
        from django_nis2_shield.enforcer import RateLimiter
        
        limiter = RateLimiter()
        self.assertEqual(limiter.algorithm, 'fixed_window')
    
    @override_settings(NIS2_SHIELD={
        'ENABLE_RATE_LIMIT': True,
        'RATE_LIMIT_THRESHOLD': 10,
        'RATE_LIMIT_ALGORITHM': 'sliding_window'
    })
    def test_get_remaining(self):
        """Test get_remaining method returns correct count."""
        from django_nis2_shield.enforcer import RateLimiter
        
        limiter = RateLimiter()
        
        # Initially should have full threshold
        self.assertEqual(limiter.get_remaining('10.10.10.10'), 10)
        
        # After 3 requests, should have 7 remaining
        for _ in range(3):
            limiter.is_allowed('10.10.10.10')
        
        self.assertEqual(limiter.get_remaining('10.10.10.10'), 7)


class TestMultiSIEMPresets(SimpleTestCase):
    """Tests for the new SIEM preset configurations."""
    
    def test_qradar_dsm_config(self):
        """Test QRadar DSM configuration structure."""
        from django_nis2_shield.siem_presets import get_qradar_dsm
        
        config = get_qradar_dsm()
        
        self.assertIn('log_source_type', config)
        self.assertIn('protocol', config)
        self.assertEqual(config['format'], 'CEF')
        self.assertIn('event_mappings', config)
        self.assertIn('100', config['event_mappings'])  # Audit log
    
    def test_graylog_gelf_config(self):
        """Test Graylog GELF configuration structure."""
        from django_nis2_shield.siem_presets import get_graylog_gelf_config
        
        config = get_graylog_gelf_config()
        
        self.assertEqual(config['version'], '1.1')
        self.assertIn('level_mapping', config)
        self.assertIn('additional_fields', config)
        self.assertIn('sample_gelf_message', config)
    
    def test_sumologic_config(self):
        """Test Sumo Logic configuration structure."""
        from django_nis2_shield.siem_presets import get_sumologic_config
        
        config = get_sumologic_config()
        
        self.assertIn('source_category', config)
        self.assertIn('field_extraction_query', config)
        self.assertIn('dashboard_query_examples', config)
    
    def test_datadog_config(self):
        """Test Datadog configuration structure."""
        from django_nis2_shield.siem_presets import get_datadog_config
        
        config = get_datadog_config()
        
        self.assertEqual(config['source'], 'django')
        self.assertIn('tags', config)
        self.assertIn('log_processing_rules', config)


class TestWebhookNotifier(SimpleTestCase):
    """Tests for the webhook notification system."""
    
    @override_settings(NIS2_SHIELD={
        'ENABLE_WEBHOOKS': False
    })
    def test_disabled_webhooks_dont_send(self):
        """Test that disabled webhooks don't attempt to send."""
        from django_nis2_shield.webhooks import WebhookNotifier
        
        notifier = WebhookNotifier()
        # Should not raise, just return early
        notifier.notify('test_event', {'data': 'test'})
    
    @override_settings(NIS2_SHIELD={
        'ENABLE_WEBHOOKS': True,
        'WEBHOOK_ASYNC': False,
        'WEBHOOKS': [{'url': 'https://example.com/webhook', 'format': 'json'}]
    })
    @patch('django_nis2_shield.webhooks.urlopen')
    def test_webhook_payload_structure(self, mock_urlopen):
        """Test that webhook payload has correct structure."""
        from django_nis2_shield.webhooks import WebhookNotifier
        
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=MagicMock(status=200))
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
        
        notifier = WebhookNotifier()
        notifier.notify('rate_limit_exceeded', {'ip': '1.2.3.4'})
        
        # Verify urlopen was called
        self.assertTrue(mock_urlopen.called)
    
    def test_slack_format(self):
        """Test Slack message formatting."""
        from django_nis2_shield.webhooks import WebhookNotifier
        
        notifier = WebhookNotifier()
        payload = {
            'event_type': 'rate_limit_exceeded',
            'severity': 'warning',
            'details': {'ip': '10.0.0.1', 'threshold': 100}
        }
        
        slack_msg = notifier._format_slack(payload)
        
        self.assertIn('text', slack_msg)
        self.assertIn('attachments', slack_msg)
        self.assertEqual(len(slack_msg['attachments']), 1)
    
    def test_teams_format(self):
        """Test Microsoft Teams message formatting."""
        from django_nis2_shield.webhooks import WebhookNotifier
        
        notifier = WebhookNotifier()
        payload = {
            'event_type': 'session_hijack_detected',
            'severity': 'critical',
            'details': {'ip': '10.0.0.1', 'user': 'testuser'}
        }
        
        teams_msg = notifier._format_teams(payload)
        
        self.assertEqual(teams_msg['@type'], 'MessageCard')
        self.assertIn('sections', teams_msg)
    
    def test_discord_format(self):
        """Test Discord message formatting."""
        from django_nis2_shield.webhooks import WebhookNotifier
        
        notifier = WebhookNotifier()
        payload = {
            'event_type': 'tor_node_blocked',
            'severity': 'warning',
            'timestamp': '2025-12-26T00:00:00Z',
            'details': {'ip': '10.0.0.1'}
        }
        
        discord_msg = notifier._format_discord(payload)
        
        self.assertIn('embeds', discord_msg)
        self.assertEqual(len(discord_msg['embeds']), 1)


class TestPackageExports(SimpleTestCase):
    """Test that all exports are available from package root."""
    
    def test_version(self):
        """Test version is correctly set."""
        import django_nis2_shield
        self.assertEqual(django_nis2_shield.__version__, '0.3.0')
    
    def test_core_exports(self):
        """Test core classes are exported."""
        from django_nis2_shield import (
            Nis2GuardMiddleware,
            Nis2JsonFormatter,
            Nis2CefFormatter,
            WebhookNotifier,
        )
        
        self.assertIsNotNone(Nis2GuardMiddleware)
        self.assertIsNotNone(Nis2JsonFormatter)
        self.assertIsNotNone(Nis2CefFormatter)
        self.assertIsNotNone(WebhookNotifier)
    
    def test_siem_preset_exports(self):
        """Test SIEM preset functions are exported."""
        from django_nis2_shield import (
            get_qradar_dsm,
            get_graylog_gelf_config,
            get_sumologic_config,
            get_datadog_config,
        )
        
        self.assertIsNotNone(get_qradar_dsm)
        self.assertIsNotNone(get_graylog_gelf_config)
        self.assertIsNotNone(get_sumologic_config)
        self.assertIsNotNone(get_datadog_config)


if __name__ == '__main__':
    unittest.main()
