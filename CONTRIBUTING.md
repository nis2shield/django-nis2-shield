# Contributing to Django NIS2 Shield

Thank you for your interest in contributing to Django NIS2 Shield! 🛡️

This project is open source and welcomes contributions from the community. Whether you're a Django developer, a security expert, or simply a user with feedback, your contribution is valuable.

## How to Contribute

### 🐛 Reporting Bugs

1. Check if the bug has already been reported in [Issues](../../issues)
2. If not, open a new issue using the "Bug Report" template
3. Include: Python version, Django version, steps to reproduce

### 💡 Proposing New Features

1. Open an issue with the "Feature Request" template
2. Describe the use case and value for NIS2 compliance
3. Wait for feedback before starting implementation

### 🔧 Submitting Pull Requests

1. **Fork** the repository
2. Create a branch: `git checkout -b feature/feature-name`
3. Write tests for new features (we have 41+ tests)
4. Make sure all tests pass:
   ```bash
   PYTHONPATH=. pytest tests/ -v
   ```
5. Open a Pull Request with a clear description

## Development Environment Setup

```bash
# Clone
git clone https://github.com/nis2shield/django-nis2-shield.git
cd django-nis2-shield

# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
PYTHONPATH=. pytest tests/ -v
```

## Code Style

- Use **Black** for formatting: `black django_nis2_shield/`
- Use **isort** for imports: `isort django_nis2_shield/`
- Follow PEP 8

## Areas Where Contributions Are Needed

| Area | Required Skills | Priority |
|------|-----------------|----------|
| Code security review | Cybersecurity | 🔴 High |
| New SIEM presets | Splunk, QRadar, Graylog | 🟡 Medium |
| Penetration testing | Pentesting | 🔴 High |
| Documentation | English | 🟢 Low |
| Compliance checks | NIS2, GDPR | 🔴 High |

## Questions?

Open an issue with the `question` tag or contact the maintainers.

Thank you! 🙏
