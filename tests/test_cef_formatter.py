import unittest
import logging
import re
from django.conf import settings

# Configure minimal Django settings
if not settings.configured:
    settings.configure(
        NIS2_SHIELD={
            'INTEGRITY_KEY': 'test-secret',
        },
        DEBUG=True,
        ALLOWED_HOSTS=['*'],
        INSTALLED_APPS=['django_nis2_shield'],
    )

from django_nis2_shield.cef_formatter import (
    Nis2CefFormatter,
    escape_cef_value,
    escape_cef_header,
    SEVERITY_MAP,
    get_cef_logging_config
)


class TestCEFFormatter(unittest.TestCase):
    def setUp(self):
        self.formatter = Nis2CefFormatter()
        
    def test_cef_header_format(self):
        """Test that CEF header follows the specification."""
        record = logging.LogRecord(
            name='django_nis2_shield',
            level=logging.INFO,
            pathname='',
            lineno=1,
            msg='NIS2_AUDIT_LOG',
            args=(),
            exc_info=None
        )
        
        output = self.formatter.format(record)
        
        # CEF header should have 7 pipe-separated fields before extension
        parts = output.split('|')
        self.assertGreaterEqual(len(parts), 7)
        
        # Check CEF version
        self.assertTrue(parts[0].startswith('CEF:'))
        
        # Check vendor and product
        self.assertEqual(parts[1], 'DjangoNIS2Shield')
        self.assertEqual(parts[2], 'NIS2Shield')
        
    def test_cef_extension_mapping(self):
        """Test that NIS2 fields are correctly mapped to CEF extensions."""
        record = logging.LogRecord(
            name='django_nis2_shield',
            level=logging.INFO,
            pathname='',
            lineno=1,
            msg='NIS2_AUDIT_LOG',
            args=(),
            exc_info=None
        )
        record.nis2_data = {
            'who': {
                'ip': '192.168.1.100',
                'user_id': 'alice',
                'user_agent': 'Mozilla/5.0'
            },
            'what': {
                'url': '/api/login',
                'method': 'POST',
                'view': 'login_view'
            },
            'result': {
                'status': 200,
                'duration_seconds': 0.05
            }
        }
        
        output = self.formatter.format(record)
        
        # Check that extensions are present
        self.assertIn('src=192.168.1.100', output)
        self.assertIn('suser=alice', output)
        self.assertIn('request=/api/login', output)
        self.assertIn('requestMethod=POST', output)
        self.assertIn('act=login_view', output)
        self.assertIn('outcome=Success', output)
        self.assertIn('cn1=50', output)  # 0.05s = 50ms
        
    def test_cef_severity_mapping(self):
        """Test severity mapping from Python logging to CEF."""
        self.assertEqual(SEVERITY_MAP['DEBUG'], 0)
        self.assertEqual(SEVERITY_MAP['INFO'], 1)
        self.assertEqual(SEVERITY_MAP['WARNING'], 4)
        self.assertEqual(SEVERITY_MAP['ERROR'], 7)
        self.assertEqual(SEVERITY_MAP['CRITICAL'], 10)
        
    def test_cef_value_escaping(self):
        """Test that special characters are properly escaped."""
        # Test backslash
        self.assertEqual(escape_cef_value('a\\b'), 'a\\\\b')
        # Test equals sign
        self.assertEqual(escape_cef_value('a=b'), 'a\\=b')
        # Test newline
        self.assertEqual(escape_cef_value('a\nb'), 'a\\nb')
        
    def test_cef_header_escaping(self):
        """Test that header fields escape pipes."""
        self.assertEqual(escape_cef_header('a|b'), 'a\\|b')
        self.assertEqual(escape_cef_header('a\\b'), 'a\\\\b')
        
    def test_failure_outcome(self):
        """Test that HTTP errors are marked as Failure."""
        record = logging.LogRecord(
            name='django_nis2_shield',
            level=logging.WARNING,
            pathname='',
            lineno=1,
            msg='NIS2_AUDIT_LOG',
            args=(),
            exc_info=None
        )
        record.nis2_data = {
            'result': {'status': 404}
        }
        
        output = self.formatter.format(record)
        self.assertIn('outcome=Failure', output)
        
    def test_logging_config_helper(self):
        """Test the logging configuration helper."""
        config = get_cef_logging_config()
        
        self.assertIn('formatters', config)
        self.assertIn('cef', config['formatters'])
        self.assertIn('handlers', config)
        self.assertIn('loggers', config)
        
    def test_logging_config_with_file(self):
        """Test logging config with file handler."""
        config = get_cef_logging_config('/var/log/test.cef')
        
        self.assertIn('file', config['handlers'])
        self.assertEqual(config['handlers']['file']['filename'], '/var/log/test.cef')


if __name__ == '__main__':
    unittest.main()
