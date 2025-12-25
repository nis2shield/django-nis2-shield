# NIS2 Shield Monitoring Dashboard

Questo stack Docker fornisce una soluzione completa per visualizzare e monitorare i log di sicurezza NIS2.

## Componenti

| Servizio | Porta | Descrizione |
|----------|-------|-------------|
| **Elasticsearch** | 9200 | Storage e ricerca log |
| **Kibana** | 5601 | Visualizzazione e analisi |
| **Grafana** | 3000 | Dashboard avanzate |

## Quick Start

```bash
# Avvia tutti i servizi
docker compose up -d

# Verifica lo stato
docker compose ps

# Attendi che Elasticsearch sia healthy (~30s)
docker compose logs -f elasticsearch
```

### Accesso

- **Kibana**: http://localhost:5601
- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin`
- **Elasticsearch**: http://localhost:9200

## Configurazione Django

Aggiungi questo handler di logging al tuo `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'nis2_json': {
            '()': 'django_nis2_shield.loggers.Nis2JsonFormatter',
        },
    },
    'handlers': {
        'elasticsearch': {
            'class': 'logging.handlers.HTTPHandler',
            'host': 'localhost:9200',
            'url': '/django-nis2-logs/_doc',
            'method': 'POST',
            'formatter': 'nis2_json',
        },
    },
    'loggers': {
        'django_nis2_shield': {
            'handlers': ['elasticsearch'],
            'level': 'INFO',
        },
    },
}
```

> **Nota**: Per produzione, usa [python-elasticsearch](https://github.com/elastic/elasticsearch-py) o Logstash.

## Cleanup

```bash
# Stop e rimuovi i container
docker compose down

# Rimuovi anche i volumi (cancella i dati!)
docker compose down -v
```
