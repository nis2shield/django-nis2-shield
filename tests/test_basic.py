import unittest
import json
import logging
from django.conf import settings
from django.http import HttpResponse
from django.test import RequestFactory
from unittest.mock import MagicMock

# Configure minimal Django settings
if not settings.configured:
    settings.configure(
        NIS2_SHIELD={
            'INTEGRITY_KEY': 'test-secret',
            'ENCRYPTION_KEY': b'gQjXDy7y7y7y7y7y7y7y7y7y7y7y7y7y7y7y7y7y7y7=', # 32 url-safe base64-encoded bytes
            'ANONYMIZE_IPS': True
        },
        DEBUG=True,
        ALLOWED_HOSTS=['*'],
        INSTALLED_APPS=['django_nis2_shield'],
    )

from django_nis2_shield.loggers import Nis2JsonFormatter, SecuritySigner, PIIEncryptor
from django_nis2_shield.middleware import Nis2GuardMiddleware
from django_nis2_shield.utils import anonymize_ip

class TestNis2Components(unittest.TestCase):
    def test_anonymize_ip(self):
        self.assertEqual(anonymize_ip('192.168.1.50'), '192.168.1.0')
        self.assertEqual(anonymize_ip('2001:db8::1'), '2001:db8::')

    def test_signer(self):
        signer = SecuritySigner('secret')
        sig = signer.sign('message')
        self.assertTrue(len(sig) > 0)
        # Verify deterministic
        self.assertEqual(sig, signer.sign('message'))
        self.assertNotEqual(sig, signer.sign('message2'))

    def test_encryptor(self):
        # Generate a valid key for testing if needed, but we used a static one in settings
        key = settings.NIS2_SHIELD['ENCRYPTION_KEY']
        encryptor = PIIEncryptor(key)
        encrypted = encryptor.encrypt('sensitive')
        self.assertNotEqual(encrypted, 'sensitive')
        # Decrypt to verify (need Fernet instance)
        from cryptography.fernet import Fernet
        f = Fernet(key)
        self.assertEqual(f.decrypt(encrypted.encode()).decode(), 'sensitive')

    def test_formatter(self):
        formatter = Nis2JsonFormatter()
        record = logging.LogRecord('name', logging.INFO, 'pathname', 1, 'msg', (), None)
        record.nis2_data = {'foo': 'bar'}
        output = formatter.format(record)
        data = json.loads(output)
        
        self.assertIn('log', data)
        self.assertIn('integrity_hash', data)
        self.assertEqual(data['log']['foo'], 'bar')

    def test_middleware(self):
        factory = RequestFactory()
        request = factory.get('/test-url')
        
        # Add mock anonymous user
        class AnonymousUser:
            is_authenticated = False
        request.user = AnonymousUser()
        
        # Mock response
        def get_response(req):
            return HttpResponse("OK")
            
        middleware = Nis2GuardMiddleware(get_response)
        
        # Mock logger to capture output
        with unittest.mock.patch('django_nis2_shield.middleware.logger') as mock_logger:
            response = middleware(request)
            self.assertEqual(response.status_code, 200)
            
            # Verify logger was called
            self.assertTrue(mock_logger.info.called)
            args, kwargs = mock_logger.info.call_args
            self.assertIn('nis2_data', kwargs['extra'])
            payload = kwargs['extra']['nis2_data']
            
            self.assertEqual(payload['what']['url'], '/test-url')
            self.assertEqual(payload['who']['ip'], '127.0.0.0') # Loopback anonymized

if __name__ == '__main__':
    unittest.main()
