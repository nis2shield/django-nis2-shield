"""
CEF (Common Event Format) Formatter for NIS2 Shield.

CEF Format: 
CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|Extension

Reference: https://www.microfocus.com/documentation/arcsight/arcsight-smartconnectors/
"""
import logging
import time
from datetime import datetime
from django.conf import settings


# CEF Severity mapping
# NIS2 events mapped to CEF severity levels (0-10)
SEVERITY_MAP = {
    'DEBUG': 0,
    'INFO': 1,
    'WARNING': 4,
    'ERROR': 7,
    'CRITICAL': 10
}

# Signature IDs for different event types
SIGNATURE_IDS = {
    'NIS2_AUDIT_LOG': '100',
    'NIS2_RATE_LIMIT': '200',
    'NIS2_SESSION_HIJACK': '201',
    'NIS2_TOR_BLOCK': '202',
    'NIS2_MFA_REQUIRED': '203',
    'DEFAULT': '999'
}


def escape_cef_value(value: str) -> str:
    """
    Escape special characters in CEF extension values.
    CEF requires escaping: backslash, equals, newline
    """
    if not isinstance(value, str):
        value = str(value)
    return value.replace('\\', '\\\\').replace('=', '\\=').replace('\n', '\\n').replace('\r', '\\r')


def escape_cef_header(value: str) -> str:
    """
    Escape special characters in CEF header fields.
    CEF headers require escaping: backslash, pipe
    """
    if not isinstance(value, str):
        value = str(value)
    return value.replace('\\', '\\\\').replace('|', '\\|')


class Nis2CefFormatter(logging.Formatter):
    """
    Formats log records as CEF (Common Event Format) for SIEM integration.
    
    CEF Extensions used:
    - src: Source IP address
    - suser: Source user
    - request: URL path
    - requestMethod: HTTP method
    - act: Action performed (view name)
    - outcome: Result status
    - rt: Receipt time (epoch ms)
    - cs1: Custom string 1 (user agent)
    - cn1: Custom number 1 (response time ms)
    """
    
    # CEF header constants
    CEF_VERSION = 0
    DEVICE_VENDOR = 'DjangoNIS2Shield'
    DEVICE_PRODUCT = 'NIS2Shield'
    DEVICE_VERSION = '0.3.0'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nis2_conf = getattr(settings, 'NIS2_SHIELD', {})
    
    def format(self, record):
        # Determine signature ID and name based on message
        message = record.getMessage()
        sig_id = SIGNATURE_IDS.get(message, SIGNATURE_IDS['DEFAULT'])
        
        # Get severity
        severity = SEVERITY_MAP.get(record.levelname, 3)
        
        # Build CEF header
        header = self._build_header(sig_id, message, severity)
        
        # Build CEF extension
        extension = self._build_extension(record)
        
        return f"{header}|{extension}"
    
    def _build_header(self, sig_id: str, name: str, severity: int) -> str:
        """Build the CEF header with proper escaping."""
        return (
            f"CEF:{self.CEF_VERSION}|"
            f"{escape_cef_header(self.DEVICE_VENDOR)}|"
            f"{escape_cef_header(self.DEVICE_PRODUCT)}|"
            f"{escape_cef_header(self.DEVICE_VERSION)}|"
            f"{escape_cef_header(sig_id)}|"
            f"{escape_cef_header(name)}|"
            f"{severity}"
        )
    
    def _build_extension(self, record) -> str:
        """Build the CEF extension key-value pairs."""
        extensions = []
        
        # Receipt time in epoch milliseconds
        rt = int(record.created * 1000)
        extensions.append(f"rt={rt}")
        
        # Add NIS2 data if present
        if hasattr(record, 'nis2_data'):
            nis2_data = record.nis2_data
            
            # WHO section
            who = nis2_data.get('who', {})
            if 'ip' in who:
                extensions.append(f"src={escape_cef_value(who['ip'])}")
            if 'user_id' in who:
                extensions.append(f"suser={escape_cef_value(who['user_id'])}")
            if 'user_agent' in who:
                extensions.append(f"cs1={escape_cef_value(who['user_agent'])}")
                extensions.append("cs1Label=UserAgent")
            
            # WHAT section
            what = nis2_data.get('what', {})
            if 'url' in what:
                extensions.append(f"request={escape_cef_value(what['url'])}")
            if 'method' in what:
                extensions.append(f"requestMethod={escape_cef_value(what['method'])}")
            if 'view' in what:
                extensions.append(f"act={escape_cef_value(what['view'])}")
            
            # RESULT section
            result = nis2_data.get('result', {})
            if 'status' in result:
                outcome = 'Success' if result['status'] < 400 else 'Failure'
                extensions.append(f"outcome={outcome}")
                extensions.append(f"cn2={result['status']}")
                extensions.append("cn2Label=HTTPStatusCode")
            if 'duration_seconds' in result:
                duration_ms = int(result['duration_seconds'] * 1000)
                extensions.append(f"cn1={duration_ms}")
                extensions.append("cn1Label=ResponseTimeMs")
        
        return ' '.join(extensions)


def get_cef_logging_config(log_file: str = None) -> dict:
    """
    Returns a Django LOGGING configuration dict for CEF output.
    
    Usage in settings.py:
        from django_nis2_shield.cef_formatter import get_cef_logging_config
        LOGGING = get_cef_logging_config('/var/log/django_nis2.cef')
    """
    handlers = {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'cef',
        }
    }
    
    if log_file:
        handlers['file'] = {
            'class': 'logging.FileHandler',
            'filename': log_file,
            'formatter': 'cef',
        }
    
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'cef': {
                '()': 'django_nis2_shield.cef_formatter.Nis2CefFormatter',
            },
        },
        'handlers': handlers,
        'loggers': {
            'django_nis2_shield': {
                'handlers': list(handlers.keys()),
                'level': 'INFO',
                'propagate': False,
            },
        },
    }
