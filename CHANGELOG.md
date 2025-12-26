# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2025-12-26

### Added
- **Multi-SIEM Support**: Extended SIEM integration presets
  - New `get_qradar_dsm()` for IBM QRadar DSM configuration
  - New `get_graylog_gelf_config()` for Graylog GELF format
  - New `get_sumologic_config()` for Sumo Logic with query examples
  - New `get_datadog_config()` for Datadog log processing
- **Sliding Window Rate Limiting**: More accurate rate limiting algorithm
  - New `RATE_LIMIT_ALGORITHM` option: 'sliding_window' (default) or 'fixed_window'
  - New `RATE_LIMIT_WINDOW` option for configurable window size
  - New `get_remaining()` method to check remaining requests
  - Backward compatible with fixed window algorithm
- **Webhook Notifications**: Real-time security alerting
  - New `webhooks.py` module with `WebhookNotifier` class
  - Support for Slack, Microsoft Teams, Discord, and generic HTTP
  - Async sending by default (non-blocking)
  - Events: rate_limit_exceeded, session_hijack_detected, tor_node_blocked, mfa_required
- **Enhanced Exports**: All major classes now exported from package root

### Changed
- Middleware now sends webhook notifications for all security events
- Rate limiting logs now include algorithm type and window size
- Bumped version to 0.3.0

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
