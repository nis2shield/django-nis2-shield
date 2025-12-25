# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-12-25

### Added
- **PII Encryption**: Configurable encryption of sensitive fields in logs
  - New `PII_FIELDS` configuration option (default: user_id, email, username, ip, user_agent)
  - New `ENCRYPT_PII` toggle (default: true)
  - Recursive encryption for nested data structures
- **CEF Format Support**: Common Event Format for enterprise SIEM integration
  - New `cef_formatter.py` module with `Nis2CefFormatter` class
  - CEF v25 compliant output with proper escaping
  - Pre-configured logging helper `get_cef_logging_config()`
- **Monitoring Dashboard**: Docker Compose stack for log visualization
  - Elasticsearch 8.11 for storage
  - Kibana 8.11 with pre-configured dashboard
  - Grafana 10 with security metrics dashboard
- **Enhanced Testing**: New test files for PII encryption and CEF formatting
- **PyPI Ready**: Complete metadata, classifiers, and optional dev dependencies

### Changed
- Updated `loggers.py` with improved code structure and documentation
- Bumped version to 0.2.0

## [0.1.0] - 2025-12-25

### Added
- **Forensic Logger**: Structured JSON logging with HMAC-SHA256 signing
  - IP anonymization for GDPR compliance
  - Fernet encryption support for PII
  - Integrity hash on each log entry
- **Middleware**: `Nis2GuardMiddleware` for request interception
  - Captures WHO (user, IP, user agent)
  - Captures WHAT (URL, method, view)
  - Captures RESULT (status code, duration)
- **Active Defense Layer**
  - Rate Limiter with configurable threshold
  - Session Guard with subnet tolerance for mobile networks
  - Tor Exit Node blocker
  - MFA Gatekeeper for protected routes
- **Audit Command**: `python manage.py check_nis2` for configuration auditing
- **Threat Intelligence**: `update_threat_list` command for Tor node updates
- **Incident Reporting**: `generate_incident_report` command for CSIRT notifications
- **SIEM Presets**: Elasticsearch and Splunk configuration helpers

[Unreleased]: https://github.com/nis2shield/django-nis2-shield/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/nis2shield/django-nis2-shield/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/nis2shield/django-nis2-shield/releases/tag/v0.1.0
