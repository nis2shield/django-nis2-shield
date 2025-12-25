# Contributing to Django NIS2 Shield

Grazie per il tuo interesse nel contribuire a Django NIS2 Shield! 🛡️

Questo progetto è open source e accoglie contributi dalla community. Che tu sia uno sviluppatore Django, un esperto di sicurezza, o semplicemente un utente con feedback, il tuo contributo è prezioso.

## Come Contribuire

### 🐛 Segnalare Bug

1. Controlla se il bug è già stato segnalato nelle [Issues](../../issues)
2. Se non esiste, apri una nuova issue usando il template "Bug Report"
3. Includi: versione Python, versione Django, passi per riprodurre

### 💡 Proporre Nuove Funzionalità

1. Apri una issue con il template "Feature Request"
2. Descrivi il caso d'uso e il valore per la conformità NIS2
3. Aspetta feedback prima di iniziare l'implementazione

### 🔧 Inviare Pull Request

1. **Fork** il repository
2. Crea un branch: `git checkout -b feature/nome-feature`
3. Scrivi test per le nuove funzionalità
4. Assicurati che tutti i test passino:
   ```bash
   PYTHONPATH=. pytest tests/ -v
   ```
5. Apri una Pull Request con una descrizione chiara

## Setup Ambiente di Sviluppo

```bash
# Clone
git clone https://github.com/nis2shield/django-nis2-shield.git
cd django-nis2-shield

# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure: venv\Scripts\activate  # Windows

# Installa dipendenze dev
pip install -e ".[dev]"

# Esegui i test
PYTHONPATH=. pytest tests/ -v
```

## Stile del Codice

- Usa **Black** per la formattazione: `black django_nis2_shield/`
- Usa **isort** per gli import: `isort django_nis2_shield/`
- Segui PEP 8

## Aree Dove Servono Contributi

| Area | Competenze Richieste | Priorità |
|------|---------------------|----------|
| Review sicurezza codice | Cybersecurity | 🔴 Alta |
| Nuovi preset SIEM | Splunk, QRadar, Graylog | 🟡 Media |
| Test di penetrazione | Pentesting | 🔴 Alta |
| Documentazione | Italiano/Inglese | 🟢 Bassa |
| Compliance check | NIS2, GDPR | 🔴 Alta |

## Domande?

Apri una issue con il tag `question` o contatta i maintainer.

Grazie! 🙏
