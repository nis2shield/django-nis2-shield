def get_elastic_mapping():
    """
    Returns a JSON schema mapping for Elasticsearch suitable for NIS2 logs.
    """
    return {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "level": {"type": "keyword"},
                "logger": {"type": "keyword"},
                "message": {"type": "text"},
                "log": {
                    "properties": {
                        "who": {
                            "properties": {
                                "ip": {"type": "ip"},
                                "user_id": {"type": "keyword"},
                                "user_agent": {"type": "text"}
                            }
                        },
                        "what": {
                            "properties": {
                                "url": {"type": "keyword"},
                                "method": {"type": "keyword"},
                                "view": {"type": "keyword"}
                            }
                        },
                        "result": {
                            "properties": {
                                "status": {"type": "integer"},
                                "duration_seconds": {"type": "float"}
                            }
                        }
                    }
                },
                "integrity_hash": {"type": "keyword"}
            }
        }
    }

def get_splunk_props():
    """
    Returns a sample props.conf configuration for Splunk.
    """
    return """
[django_nis2_shield]
DATETIME_CONFIG = CURRENT
KV_MODE = json
category = Custom
description = NIS2 Audit Logs
disabled = false
pulldown_type = true
"""


def get_qradar_dsm():
    """
    Returns QRadar DSM (Device Support Module) configuration for NIS2 logs.
    
    QRadar natively supports CEF format, so use the CEF formatter
    with a syslog forwarder pointing to your QRadar instance.
    
    Usage:
        1. Configure CEF logging in Django
        2. Set up rsyslog/syslog-ng to forward to QRadar
        3. Create a log source in QRadar with these settings
    """
    return {
        'log_source_type': 'Universal DSM',
        'log_source_identifier': 'DjangoNIS2Shield',
        'protocol': 'syslog',
        'format': 'CEF',
        'coalesce_events': False,
        'event_mappings': {
            '100': {'name': 'Audit Log', 'category': 'Audit'},
            '200': {'name': 'Rate Limit Exceeded', 'category': 'DoS'},
            '201': {'name': 'Session Hijack Attempt', 'category': 'Authentication'},
            '202': {'name': 'Tor Exit Node Blocked', 'category': 'Access'},
            '203': {'name': 'MFA Required', 'category': 'Authentication'},
        },
        'severity_mapping': {
            'INFO': 1,
            'WARNING': 4,
            'ERROR': 7,
            'CRITICAL': 10
        }
    }


def get_graylog_gelf_config():
    """
    Returns GELF (Graylog Extended Log Format) configuration.
    
    GELF is Graylog's native format and provides better performance
    than parsing JSON logs.
    
    Usage:
        Configure a GELF UDP/TCP input in Graylog, then use a 
        GELF handler in Python logging.
    """
    return {
        'version': '1.1',
        'host': 'django-nis2-shield',
        'facility': 'nis2_audit',
        'level_mapping': {
            'DEBUG': 7,    # Debug
            'INFO': 6,     # Informational
            'WARNING': 4,  # Warning
            'ERROR': 3,    # Error
            'CRITICAL': 2  # Critical
        },
        'additional_fields': {
            '_application': 'django-nis2-shield',
            '_environment': 'production',
            '_compliance': 'NIS2'
        },
        'sample_gelf_message': {
            'version': '1.1',
            'host': 'django-app',
            'short_message': 'NIS2_AUDIT_LOG',
            'level': 6,
            '_user_id': 'anonymous',
            '_src_ip': '192.168.1.100',
            '_url': '/api/endpoint',
            '_method': 'POST',
            '_status': 200,
            '_duration_ms': 45
        }
    }


def get_sumologic_config():
    """
    Returns Sumo Logic configuration for NIS2 logs.
    
    Sumo Logic works best with JSON logs sent via HTTP collector.
    
    Usage:
        1. Create an HTTP Logs and Metrics Source in Sumo Logic
        2. Configure Python logging to send JSON to the provided URL
        3. Use these field extraction rules in Sumo Logic
    """
    return {
        'source_category': 'nis2/audit',
        'source_name': 'django-nis2-shield',
        'content_type': 'application/json',
        'field_extraction_query': '''
| json auto
| where !isNull(log.who.ip)
| fields _messagetime as timestamp, 
         log.who.ip as src_ip, 
         log.who.user_id as user,
         log.who.user_agent as user_agent,
         log.what.url as url,
         log.what.method as method,
         log.what.view as view_name,
         log.result.status as status_code,
         log.result.duration_seconds as duration,
         integrity_hash
''',
        'dashboard_query_examples': {
            'requests_by_status': '''
_sourceCategory=nis2/audit
| json auto
| timeslice 1m
| count by _timeslice, log.result.status
| transpose row _timeslice column log.result.status
''',
            'top_users': '''
_sourceCategory=nis2/audit
| json auto
| count by log.who.user_id
| top 10 log.who.user_id by _count
''',
            'security_events': '''
_sourceCategory=nis2/audit
| json auto
| where log.result.status >= 400
| count by log.what.url, log.result.status
'''
        }
    }


def get_datadog_config():
    """
    Returns Datadog configuration for NIS2 logs.
    
    Datadog can ingest logs via their agent or HTTP API.
    """
    return {
        'source': 'django',
        'service': 'nis2-shield',
        'tags': ['env:production', 'compliance:nis2', 'framework:django'],
        'log_processing_rules': [
            {
                'type': 'attribute_remapper',
                'name': 'Map IP to network.client.ip',
                'sources': ['log.who.ip'],
                'target': 'network.client.ip'
            },
            {
                'type': 'attribute_remapper', 
                'name': 'Map user_id to usr.id',
                'sources': ['log.who.user_id'],
                'target': 'usr.id'
            },
            {
                'type': 'attribute_remapper',
                'name': 'Map status to http.status_code',
                'sources': ['log.result.status'],
                'target': 'http.status_code'
            }
        ]
    }

