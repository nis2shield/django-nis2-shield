import logging
import ipaddress
from django.core.cache import cache
from django.conf import settings
from .utils import get_subnet

logger = logging.getLogger('django_nis2_shield')

class RateLimiter:
    """
    Rate limiter with support for both fixed window and sliding window algorithms.
    
    Sliding window provides more accurate rate limiting by tracking individual
    request timestamps rather than just counting within fixed time buckets.
    
    Configuration options:
        RATE_LIMIT_THRESHOLD: Max requests per window (default: 100)
        RATE_LIMIT_WINDOW: Window size in seconds (default: 60)
        RATE_LIMIT_ALGORITHM: 'sliding_window' or 'fixed_window' (default: 'sliding_window')
        ENABLE_RATE_LIMIT: Enable/disable rate limiting (default: True)
    """
    
    def __init__(self):
        self.nis2_conf = getattr(settings, 'NIS2_SHIELD', {})
        self.threshold = self.nis2_conf.get('RATE_LIMIT_THRESHOLD', 100)
        self.window_seconds = self.nis2_conf.get('RATE_LIMIT_WINDOW', 60)
        self.enabled = self.nis2_conf.get('ENABLE_RATE_LIMIT', True)
        self.algorithm = self.nis2_conf.get('RATE_LIMIT_ALGORITHM', 'sliding_window')

    def is_allowed(self, ip: str) -> bool:
        """Check if request from IP is allowed under rate limit."""
        if not self.enabled:
            return True
        
        if self.algorithm == 'sliding_window':
            return self._sliding_window_check(ip)
        else:
            return self._fixed_window_check(ip)
    
    def _sliding_window_check(self, ip: str) -> bool:
        """
        Sliding window log algorithm for precise rate limiting.
        
        Tracks individual request timestamps and counts only those
        within the current sliding window. More memory intensive but
        provides smoother rate limiting without boundary issues.
        """
        import time
        cache_key = f"nis2_rl_sw_{ip}"
        now = time.time()
        window_start = now - self.window_seconds
        
        # Get existing timestamps
        timestamps = cache.get(cache_key, [])
        
        # Filter to only timestamps within current window
        timestamps = [t for t in timestamps if t > window_start]
        
        if len(timestamps) >= self.threshold:
            logger.warning(f"NIS2 Rate Limit (sliding window): {ip} exceeded {self.threshold} req/{self.window_seconds}s")
            return False
        
        # Add current request timestamp
        timestamps.append(now)
        
        # Store with timeout slightly longer than window to handle edge cases
        cache.set(cache_key, timestamps, timeout=self.window_seconds * 2)
        return True
    
    def _fixed_window_check(self, ip: str) -> bool:
        """
        Original fixed window counter (backward compatibility).
        
        Simple counter that resets every window. Can allow burst traffic
        at window boundaries (up to 2x threshold in worst case).
        """
        cache_key = f"nis2_rl_{ip}"
        count = cache.get(cache_key, 0)
        
        if count >= self.threshold:
            logger.warning(f"NIS2 Rate Limit (fixed window): {ip} exceeded {self.threshold} req/{self.window_seconds}s")
            return False
        
        cache.set(cache_key, count + 1, timeout=self.window_seconds)
        return True
    
    def get_remaining(self, ip: str) -> int:
        """Get remaining requests allowed for this IP in current window."""
        if not self.enabled:
            return self.threshold
        
        if self.algorithm == 'sliding_window':
            import time
            cache_key = f"nis2_rl_sw_{ip}"
            now = time.time()
            window_start = now - self.window_seconds
            timestamps = cache.get(cache_key, [])
            current_count = len([t for t in timestamps if t > window_start])
        else:
            cache_key = f"nis2_rl_{ip}"
            current_count = cache.get(cache_key, 0)
        
        return max(0, self.threshold - current_count)

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
