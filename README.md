# Django NIS2 Shield

[![PyPI version](https://badge.fury.io/py/django-nis2-shield.svg)](https://badge.fury.io/py/django-nis2-shield)
[![Python](https://img.shields.io/pypi/pyversions/django-nis2-shield.svg)](https://pypi.org/project/django-nis2-shield/)
[![Django](https://img.shields.io/badge/django-3.2%20%7C%204.x%20%7C%205.x-blue.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Il Middleware "Security-First" per la conformità NIS2.**

`django-nis2-shield` è una libreria plug-and-play progettata per aiutare le applicazioni Django a soddisfare i requisiti tecnici della Direttiva NIS2 (Network and Information Security 2), con un focus su Logging Forense, Active Defense e SIEM Integration.

## ✨ Caratteristiche Principali

### 🔒 Forensic Logger
- Log strutturati (JSON o CEF) firmati con HMAC-SHA256
- Cifratura automatica dei campi PII (GDPR compliant)
- IP Anonymization configurabile

### 🛡️ Active Defense
- **Rate Limiting**: Protezione contro attacchi DoS applicativi
- **Session Guard**: Prevenzione Session Hijacking con tolleranza mobile
- **Tor Blocker**: Blocco automatico dei nodi di uscita Tor
- **MFA Gatekeeper**: Reindirizzamento 2FA per path sensibili

### 📊 Compliance & Reporting
- Comando `check_nis2` per audit della configurazione
- Generazione report incidenti per CSIRT (deadline 24h)
- Preset SIEM per Elasticsearch, Splunk, e altri

## 📦 Installazione

```bash
pip install django-nis2-shield
```

Per lo sviluppo:
```bash
pip install django-nis2-shield[dev]
```

## ⚙️ Configurazione

### settings.py

```python
INSTALLED_APPS = [
    ...,
    'django_nis2_shield',
]

MIDDLEWARE = [
    ...,
    # Inserire dopo SessionMiddleware e prima di CommonMiddleware
    'django_nis2_shield.middleware.Nis2GuardMiddleware', 
    ...,
]

# Configurazione NIS2
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
    'RATE_LIMIT_THRESHOLD': 100,  # requests/minute
    'ENABLE_SESSION_GUARD': True,
    'SESSION_IP_TOLERANCE': 'subnet',  # 'exact', 'subnet', 'none'
    'BLOCK_TOR_EXIT_NODES': True,
    
    # MFA
    'ENFORCE_MFA_ROUTES': ['/admin/', '/finance/'],
    'MFA_SESSION_FLAG': 'is_verified_mfa',
    'MFA_REDIRECT_URL': '/accounts/login/mfa/',
}
```

### Formato Log: CEF (Enterprise SIEM)

Per output in formato CEF invece di JSON:

```python
from django_nis2_shield.cef_formatter import get_cef_logging_config

LOGGING = get_cef_logging_config('/var/log/django_nis2.cef')
```

## 🚀 Utilizzo

### Audit della Configurazione
```bash
python manage.py check_nis2
```

### Aggiornamento Threat Intelligence
```bash
python manage.py update_threat_list
```

### Generazione Report Incidenti
```bash
python manage.py generate_incident_report --hours=24 --output=incident.json
```

## 📈 Dashboard Monitoring

Il progetto include uno stack Docker per visualizzare i log:

```bash
cd dashboard
docker compose up -d

# Accesso:
# - Kibana: http://localhost:5601
# - Grafana: http://localhost:3000 (admin/admin)
```

Vedi [dashboard/README.md](dashboard/README.md) per dettagli.

## 🧪 Testing

```bash
# Con gli script esistenti
PYTHONPATH=. python tests/test_basic.py

# Con pytest
pip install pytest pytest-django
PYTHONPATH=. pytest tests/ -v
```

## 📄 Licenza

MIT License - vedi [LICENSE](LICENSE) per dettagli.

## 🤝 Contributing

Le contribuzioni sono benvenute! Apri una issue o una PR su GitHub.

