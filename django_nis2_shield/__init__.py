__version__ = "0.3.1"

# Core exports
from .middleware import Nis2GuardMiddleware
from .loggers import Nis2JsonFormatter, PIIEncryptor
from .cef_formatter import Nis2CefFormatter, get_cef_logging_config
from .webhooks import WebhookNotifier, notify_security_event, get_webhook_notifier

# SIEM presets
from .siem_presets import (
    get_elastic_mapping,
    get_splunk_props,
    get_qradar_dsm,
    get_graylog_gelf_config,
    get_sumologic_config,
    get_datadog_config,
)

__all__ = [
    '__version__',
    'Nis2GuardMiddleware',
    'Nis2JsonFormatter',
    'Nis2CefFormatter',
    'PIIEncryptor',
    'WebhookNotifier',
    'notify_security_event',
    'get_webhook_notifier',
    'get_cef_logging_config',
    'get_elastic_mapping',
    'get_splunk_props',
    'get_qradar_dsm',
    'get_graylog_gelf_config',
    'get_sumologic_config',
    'get_datadog_config',
]
