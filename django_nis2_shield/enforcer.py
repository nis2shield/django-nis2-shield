import logging
import ipaddress
from django.core.cache import cache
from django.conf import settings
from .utils import get_subnet

logger = logging.getLogger('django_nis2_shield')

class RateLimiter:
    def __init__(self):
        self.nis2_conf = getattr(settings, 'NIS2_SHIELD', {})
        self.threshold = self.nis2_conf.get('RATE_LIMIT_THRESHOLD', 100) # req/min
        self.enabled = self.nis2_conf.get('ENABLE_RATE_LIMIT', True)

    def is_allowed(self, ip: str) -> bool:
        if not self.enabled:
            return True
            
        cache_key = f"nis2_rl_{ip}"
        # Simple fixed window counter
        # In prod, consider sliding window or token bucket
        count = cache.get(cache_key, 0)
        
        if count >= self.threshold:
            return False
            
        cache.set(cache_key, count + 1, timeout=60)
        return True

class SessionGuard:
    def __init__(self):
        self.nis2_conf = getattr(settings, 'NIS2_SHIELD', {})
        self.tolerance = self.nis2_conf.get('SESSION_IP_TOLERANCE', 'subnet') # 'exact', 'subnet', 'none'
        self.enabled = self.nis2_conf.get('ENABLE_SESSION_GUARD', True)

    def validate(self, request) -> bool:
        if not self.enabled or not request.user.is_authenticated:
            return True

        current_ip = request.META.get('REMOTE_ADDR') # In middleware we trust get_client_ip has run
        # Note: Middleware should attach the real IP to request.META['REMOTE_ADDR'] or similar if behind proxy
        # For this implementation, we assume the middleware passes the resolved IP.
        
        # We need to store initial IP in session on login. 
        # Since we are a middleware, we might need to set it if missing (first request after login?)
        # Or rely on a login signal. For simplicity, we set it if missing.
        
        session_ip = request.session.get('nis2_session_ip')
        
        if not session_ip:
            # First time seeing this session (or just logged in)
            request.session['nis2_session_ip'] = current_ip
            return True
            
        if self.tolerance == 'exact':
            return current_ip == session_ip
        elif self.tolerance == 'subnet':
            # Compare subnets
            return get_subnet(current_ip) == get_subnet(session_ip)
            
        return True

class TorBlocker:
    def __init__(self):
        self.nis2_conf = getattr(settings, 'NIS2_SHIELD', {})
        self.enabled = self.nis2_conf.get('BLOCK_TOR_EXIT_NODES', False)
        self.cache_key = 'nis2_tor_exit_nodes'

    def is_tor_exit_node(self, ip: str) -> bool:
        if not self.enabled:
            return False
            
        tor_nodes = cache.get(self.cache_key, set())
        return ip in tor_nodes
