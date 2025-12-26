# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.3.x   | ✅ Yes    |
| 0.2.x   | ✅ Yes    |
| 0.1.x   | ❌ No     |
| < 0.1   | ❌ No     |

## Reporting a Vulnerability

**⚠️ Do NOT open public issues for security vulnerabilities.**

If you discover a security vulnerability in Django NIS2 Shield:

1. **Email**: Send a detailed description to `security@nis2shield.com`
2. **Subject**: `[SECURITY] Django NIS2 Shield - Brief description`
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Proposed fix (if any)

### What to Expect

| Phase | Timeframe |
|-------|-----------|
| Acknowledgment | 48 hours |
| Initial assessment | 7 days |
| Fix released | 30 days (depending on severity) |

### Responsible Disclosure

- We ask that you do not publicly disclose the vulnerability before a fix is released.
- You will be credited in the CHANGELOG (if you wish).
- We will not take legal action against researchers acting in good faith.

## Best Practices for Users

1. **Update regularly**: `pip install --upgrade django-nis2-shield`
2. **Secure keys**: Do not use default keys in production.
3. **Monitor logs**: Generated logs must be actively analyzed.
4. **Defense in depth**: This library is a layer, not a complete solution.

## Security Audit

This project **has not yet undergone a professional security audit**.

If you are a security expert and want to contribute with a review, you are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

---

*This policy is inspired by [security.txt](https://securitytxt.org/) best practices.*
