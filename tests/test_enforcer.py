import unittest
from unittest.mock import MagicMock, patch
from django.conf import settings
from django.core.cache import cache
from django.test import SimpleTestCase, override_settings

from django_nis2_shield.enforcer import RateLimiter, SessionGuard, TorBlocker
from django_nis2_shield.utils import get_subnet

@override_settings(NIS2_SHIELD={
    'RATE_LIMIT_THRESHOLD': 5,
    'ENABLE_RATE_LIMIT': True,
    'SESSION_IP_TOLERANCE': 'subnet',
    'ENABLE_SESSION_GUARD': True,
    'BLOCK_TOR_EXIT_NODES': True,
    'ENCRYPTION_KEY': 'test-key', # Required by other components potentially
})
class TestEnforcer(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def test_rate_limiter(self):
        limiter = RateLimiter()
        ip = '1.2.3.4'
        # Should allow 5 requests
        for _ in range(5):
            self.assertTrue(limiter.is_allowed(ip))
        
        # 6th should fail
        self.assertFalse(limiter.is_allowed(ip))

    def test_session_guard_subnet(self):
        guard = SessionGuard()
        request = MagicMock()
        request.user.is_authenticated = True
        request.session = {}
        request.META = {'REMOTE_ADDR': '192.168.1.50'}
        
        # First request sets the IP
        self.assertTrue(guard.validate(request))
        self.assertEqual(request.session['nis2_session_ip'], '192.168.1.50')
        
        # Same IP -> OK
        self.assertTrue(guard.validate(request))
        
        # Same Subnet -> OK (Tolerance)
        request.META['REMOTE_ADDR'] = '192.168.1.55'
        self.assertTrue(guard.validate(request))
        
        # Different Subnet -> Fail
        request.META['REMOTE_ADDR'] = '192.168.2.1'
        self.assertFalse(guard.validate(request))

    def test_tor_blocker(self):
        blocker = TorBlocker()
        # Mock cache
        cache.set('nis2_tor_exit_nodes', {'10.0.0.1'})
        
        self.assertTrue(blocker.is_tor_exit_node('10.0.0.1'))
        self.assertFalse(blocker.is_tor_exit_node('10.0.0.2'))

if __name__ == '__main__':
    unittest.main()
