import time
import logging
import json
from django.conf import settings
from django.urls import resolve
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth import logout
from .utils import get_client_ip, anonymize_ip
from .enforcer import RateLimiter, SessionGuard, TorBlocker
from .webhooks import get_webhook_notifier

logger = logging.getLogger('django_nis2_shield')

class Nis2GuardMiddleware:
    """
    NIS2 compliance middleware for Django.
    Provides forensic logging (Art 21.2.h), rate limiting, session protection, and MFA gates.

    Intercepts every request to:
    1.  **Block** Tor exit nodes and malicious IPs.
    2.  **Rate Limit** excessive requests (Token Bucket).
    3.  **Validate** session integrity (IP/User-Agent binding).
    4.  **Enforce MFA** on critical routes.
    5.  **Log** secure, signed JSON audit trails.

    Configuration (`settings.py`):
    ------------------------------
    ```python
    NIS2_SHIELD = {
        # Crypto Keys (Required)
        'INTEGRITY_KEY': os.environ['NIS2_HMAC_KEY'],       # HMAC-SHA256 signing key
        'ENCRYPTION_KEY': os.environ['NIS2_ENC_KEY'],       # AES-256 PII encryption key

        # Privacy (Art 21.2.e)
        'ANONYMIZE_IPS': True,                              # Mask last octet (e.g., 1.2.3.0)

        # Active Defense
        'ENABLE_RATE_LIMIT': True,
        'RATE_LIMIT_THRESHOLD': 100,                        # Requests per minute
        'BLOCK_TOR': True,                                  # Block known Tor exit nodes

        # MFA Gatekeeper (Art 21.2.d)
        'ENFORCE_MFA_ROUTES': ['/admin/', '/finance/'],     # Paths requiring MFA
        'MFA_SESSION_FLAG': 'is_verified_mfa',              # Session key to check
        'MFA_REDIRECT_URL': '/mfa/verify/',                 # Where to send unverified users
    }
    ```
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.nis2_conf = getattr(settings, 'NIS2_SHIELD', {})
        self.anonymize = self.nis2_conf.get('ANONYMIZE_IPS', True)
        
        # Initialize Enforcers
        self.rate_limiter = RateLimiter()
        self.session_guard = SessionGuard()
        self.tor_blocker = TorBlocker()
        
        self.mfa_routes = self.nis2_conf.get('ENFORCE_MFA_ROUTES', [])
        self.mfa_flag = self.nis2_conf.get('MFA_SESSION_FLAG', 'is_verified_mfa')
        
        # Initialize Webhook Notifier
        self.webhook_notifier = get_webhook_notifier()

    def __call__(self, request):
        start_time = time.time()
        
        # --- ACTIVE DEFENSE LAYER ---
        
        # 1. Get IP
        client_ip = get_client_ip(request)
        
        # 2. Tor Blocking
        if self.tor_blocker.is_tor_exit_node(client_ip):
            logger.warning(f"NIS2 Blocked Tor Node: {client_ip}")
            self.webhook_notifier.notify('tor_node_blocked', {
                'ip': client_ip,
                'path': request.path,
                'method': request.method
            })
            return HttpResponseForbidden("Access Denied (High Risk IP)")
            
        # 3. Rate Limiting
        if not self.rate_limiter.is_allowed(client_ip):
            logger.warning(f"NIS2 Rate Limit Exceeded: {client_ip}")
            self.webhook_notifier.notify('rate_limit_exceeded', {
                'ip': client_ip,
                'path': request.path,
                'threshold': self.rate_limiter.threshold,
                'window': self.rate_limiter.window_seconds
            })
            return HttpResponseForbidden("Too Many Requests", status=429)
            
        # 4. Session Guard (Anti-Hijacking)
        if not self.session_guard.validate(request):
            logger.warning(f"NIS2 Session Hijack Detected: {client_ip} - Invalidating Session")
            user_info = str(request.user) if hasattr(request, 'user') else 'unknown'
            self.webhook_notifier.notify('session_hijack_detected', {
                'ip': client_ip,
                'user': user_info,
                'path': request.path,
                'session_ip': request.session.get('nis2_session_ip', 'unknown')
            })
            logout(request)
            # Redirect to login or show error
            return HttpResponseRedirect(settings.LOGIN_URL)

        # 5. MFA Gatekeeper
        if self.mfa_routes and request.user.is_authenticated:
            current_path = request.path
            # Check if path starts with any of the protected routes
            if any(current_path.startswith(route) for route in self.mfa_routes):
                if not request.session.get(self.mfa_flag):
                    logger.warning(f"NIS2 MFA Required: {request.user} at {current_path}")
                    self.webhook_notifier.notify('mfa_required', {
                        'user': str(request.user),
                        'path': current_path,
                        'ip': client_ip
                    })
                    # Redirect to MFA setup/verify page (configurable)
                    mfa_url = self.nis2_conf.get('MFA_REDIRECT_URL', '/mfa/verify/')
                    return HttpResponseRedirect(f"{mfa_url}?next={current_path}")

        # --- END ACTIVE DEFENSE ---

        # Process Request
        response = self.get_response(request)
        
        # Calculate Duration
        duration = time.time() - start_time
        
        # Capture Data
        self.log_request(request, response, duration, client_ip)
        
        return response

    def log_request(self, request, response, duration, client_ip):
        try:
            # WHO
            # client_ip passed from __call__ to avoid re-calculation
            real_ip = client_ip 
            if self.anonymize:
                client_ip = anonymize_ip(client_ip)
            
            user_id = 'anonymous'
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_id = str(request.user.id)
                
            # WHAT
            url = request.path
            method = request.method
            try:
                view_name = resolve(request.path).view_name
            except:
                view_name = 'unknown'
                
            # RESULT
            status_code = response.status_code
            
            # Construct Log Payload (NIS2 V1.0 Schema)
            log_payload = {
                'event_id': 'HTTP_ACCESS', # Default event
                'request': {
                    'method': method,
                    'url': url,
                    'ip': client_ip,
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')
                },
                'response': {
                    'status': status_code,
                    'duration_ms': round(duration * 1000, 2) # Convert seconds to ms
                },
                'user': {
                    'id': user_id
                } if user_id != 'anonymous' else None
            }
            
            # Send to Logger (The Formatter will handle signing/encryption)
            # We pass the payload in the 'extra' dict so the Formatter can pick it up
            logger.info('NIS2_AUDIT_LOG', extra={'nis2_data': log_payload})
            
        except Exception as e:
            # Fail-safe: Don't crash the app if logging fails
            # But log the error to the default django logger
            logging.getLogger('django').error(f"NIS2 Middleware Error: {str(e)}")
