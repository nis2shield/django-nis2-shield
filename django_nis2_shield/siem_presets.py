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
