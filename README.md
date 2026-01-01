# Django NIS2 Shield

[![PyPI version](https://badge.fury.io/py/django-nis2-shield.svg)](https://badge.fury.io/py/django-nis2-shield)
[![Python](https://img.shields.io/pypi/pyversions/django-nis2-shield.svg)](https://pypi.org/project/django-nis2-shield/)
[![Django](https://img.shields.io/badge/django-3.2%20%7C%204.x%20%7C%205.x-blue.svg)](https://www.djangoproject.com/)
[![Safety: Passing](https://pyup.io/repos/github/nis2shield/django-nis2-shield/shield.svg)](https://pyup.io/repos/github/nis2shield/django-nis2-shield/)
[![PiWheels](https://img.shields.io/badge/piwheels-available-orange.svg)](https://piwheels.org/project/django-nis2-shield/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

### The "Security-First" Middleware for NIS2 Compliance.

Companies subject to NIS2 Directive need **demonstrable compliance**. This middleware provides:

1.  **Forensic logging** with HMAC-SHA256 integrity and PII encryption (Art. 21.2.h)
2.  **Rate limiting** to prevent DoS/Brute Force attacks (Art. 21.2.e)
3.  **Session Guard** to detect hijacking via IP/User-Agent validation (Art. 21.2.a)
4.  **MFA Gatekeeper** for sensitive routes (Art. 21.2.j)
5.  **Multi-SIEM Presets**: Ready-to-use configs for Splunk, Datadog, QRadar.

> **Part of the NIS2 Shield Ecosystem**: Use with [`@nis2shield/react-guard`](https://github.com/nis2shield/react-guard) for client-side protection and [`nis2shield/infrastructure`](https://github.com/nis2shield/infrastructure) for a full-stack, audited implementation.

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│  @nis2shield/react-guard                                    │
│  ├── SessionWatchdog (idle detection)                       │
│  ├── AuditBoundary (crash reports)                         │
│  └── → POST /api/nis2/telemetry/                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend (NIS2 Adapter)                      │
│  **django-nis2-shield**                                     │
│  ├── ForensicLogger (HMAC signed logs)                     │
│  ├── RateLimiter, SessionGuard, TorBlocker                 │
│  └── → SIEM (Elasticsearch, Splunk, QRadar, etc.)          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure                            │
│  nis2shield/infrastructure                                  │
│  ├── Centralized Logging (ELK/Splunk)                       │
│  └── Audited Deployment (Terraform/Helm)                    │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Key Features

### 🔒 Forensic Logger
- Structured logs (JSON or CEF) signed with HMAC-SHA256
- Automatic PII field encryption (GDPR compliant)
- Configurable IP anonymization

### 🛡️ Active Defense
- **Rate Limiting**: Protection against application-level DoS attacks (sliding window algorithm)
- **Session Guard**: Session hijacking prevention with mobile network tolerance
- **Tor Blocker**: Automatic blocking of Tor exit nodes
- **MFA Gatekeeper**: 2FA redirect for sensitive paths

### 📊 Compliance & Reporting
- `check_nis2` command for configuration auditing
- Incident report generation for CSIRT (24h deadline)
- SIEM presets for Elasticsearch, Splunk, QRadar, Graylog, Sumo Logic, and Datadog

### 🔔 Real-time Alerting (v0.3.0+)
- Webhook notifications for security events
- Supports Slack, Microsoft Teams, Discord, and generic HTTP

## 📦 Installation

```bash
pip install django-nis2-shield
```

For development:
```bash
pip install django-nis2-shield[dev]
```

## ⚙️ Configuration

### settings.py

```python
INSTALLED_APPS = [
    ...,
    'django_nis2_shield',
]

MIDDLEWARE = [
    ...,
    # Add after SessionMiddleware and before CommonMiddleware
    'django_nis2_shield.middleware.Nis2GuardMiddleware', 
    ...,
]

# NIS2 Shield Configuration
NIS2_SHIELD = {
    # Security Keys
    'INTEGRITY_KEY': 'change-me-to-a-secure-secret',
    'ENCRYPTION_KEY': b'your-32-byte-fernet-key-here=',  # Fernet.generate_key()
    
    # Privacy (GDPR)
    'ANONYMIZE_IPS': True,
    'ENCRYPT_PII': True,
    'PII_FIELDS': ['user_id', 'email', 'ip', 'user_agent'],
    
    # Active Defense
    'ENABLE_RATE_LIMIT': True,
    'RATE_LIMIT_THRESHOLD': 100,  # requests per window
    'RATE_LIMIT_WINDOW': 60,  # seconds
    'RATE_LIMIT_ALGORITHM': 'sliding_window',  # or 'fixed_window'
    'ENABLE_SESSION_GUARD': True,
    'SESSION_IP_TOLERANCE': 'subnet',  # 'exact', 'subnet', 'none'
    'BLOCK_TOR_EXIT_NODES': True,
    
    # MFA
    'ENFORCE_MFA_ROUTES': ['/admin/', '/finance/'],
    'MFA_SESSION_FLAG': 'is_verified_mfa',
    'MFA_REDIRECT_URL': '/accounts/login/mfa/',
    
    # Webhooks (v0.3.0+)
    'ENABLE_WEBHOOKS': True,
    'WEBHOOKS': [
        {'url': 'https://hooks.slack.com/...', 'format': 'slack'},
    ]
}
```

### Log Format: CEF (Enterprise SIEM)

For CEF output instead of JSON:

```python
from django_nis2_shield.cef_formatter import get_cef_logging_config

LOGGING = get_cef_logging_config('/var/log/django_nis2.cef')
```

## 🚀 Usage

### Configuration Audit
```bash
python manage.py check_nis2
```

### Threat Intelligence Update
```bash
python manage.py update_threat_list
```

### Incident Report Generation
```bash
python manage.py generate_incident_report --hours=24 --output=incident.json
```

## 📈 Dashboard Monitoring

The project includes a Docker stack for log visualization:

```bash
cd dashboard
docker compose up -d

# Access:
# - Kibana: http://localhost:5601
# - Grafana: http://localhost:3000 (admin/admin)
```

See [dashboard/README.md](dashboard/README.md) for details.

## 🧪 Testing

```bash
# With pytest
pip install pytest pytest-django
PYTHONPATH=. pytest tests/ -v
```

## 📖 Recipes

### Banking App with MFA & Rate Limiting

```python
# settings.py
NIS2_SHIELD = {
    'INTEGRITY_KEY': os.environ['NIS2_HMAC_KEY'],
    'ENCRYPTION_KEY': os.environ['NIS2_AES_KEY'],
    
    # Rate Limit: 50 requests per minute
    'ENABLE_RATE_LIMIT': True,
    'RATE_LIMIT_THRESHOLD': 50,
    'RATE_LIMIT_WINDOW': 60,
    
    # MFA for admin and finance
    'ENFORCE_MFA_ROUTES': ['/admin/', '/finance/', '/transfers/'],
    'MFA_REDIRECT_URL': '/accounts/mfa/verify/',
}
```

### E-commerce with Splunk SIEM

```python
# settings.py
import os

NIS2_SHIELD = {
    'INTEGRITY_KEY': os.environ['NIS2_HMAC_KEY'],
    'ANONYMIZE_IPS': True,
    'ENCRYPT_PII': True,
    
    # Webhooks for real-time alerts
    'ENABLE_WEBHOOKS': True,
    'WEBHOOKS': [
        {'url': 'https://hooks.slack.com/...', 'format': 'slack'},
    ]
}

# Splunk SIEM Output
from django_nis2_shield.siem import get_splunk_logging_config
LOGGING = get_splunk_logging_config(
    splunk_url='https://splunk.example.com:8088',
    token=os.environ['SPLUNK_HEC_TOKEN']
)
```

### Healthcare API with Session Guard

```python
# Block session hijacking attempts with IP tolerance for mobile networks
NIS2_SHIELD = {
    'ENABLE_SESSION_GUARD': True,
    'SESSION_IP_TOLERANCE': 'subnet',  # 'exact', 'subnet', or 'none'
    'BLOCK_TOR_EXIT_NODES': True,
}
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions are welcome! Open an issue or PR on GitHub.

---

**[Documentation](https://nis2shield.com)** · **[PyPI](https://pypi.org/project/django-nis2-shield/)** · **[Changelog](CHANGELOG.md)**
