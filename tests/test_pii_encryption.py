import unittest
import json
from django.conf import settings
from cryptography.fernet import Fernet

# Generate a valid Fernet key for testing
TEST_ENCRYPTION_KEY = Fernet.generate_key()

# Configure minimal Django settings
if not settings.configured:
    settings.configure(
        NIS2_SHIELD={
            'INTEGRITY_KEY': 'test-secret',
            'ENCRYPTION_KEY': TEST_ENCRYPTION_KEY,
            'ANONYMIZE_IPS': True,
            'ENCRYPT_PII': True,
            'PII_FIELDS': ['user_id', 'email', 'ip', 'user_agent']
        },
        DEBUG=True,
        ALLOWED_HOSTS=['*'],
        INSTALLED_APPS=['django_nis2_shield'],
    )

from django_nis2_shield.loggers import (
    PIIEncryptor, 
    encrypt_pii_fields, 
    Nis2JsonFormatter,
    DEFAULT_PII_FIELDS
)


class TestPIIEncryption(unittest.TestCase):
    def setUp(self):
        self.encryptor = PIIEncryptor(TEST_ENCRYPTION_KEY)
        self.fernet = Fernet(TEST_ENCRYPTION_KEY)
        
    def test_encrypt_single_field(self):
        """Test encryption of a single PII field."""
        data = {'user_id': '12345', 'action': 'login'}
        result = encrypt_pii_fields(data, self.encryptor, ['user_id'])
        
        self.assertIn('[ENCRYPTED]', result['user_id'])
        self.assertEqual(result['action'], 'login')  # Non-PII unchanged
        
    def test_encrypt_nested_fields(self):
        """Test encryption of nested PII fields."""
        data = {
            'who': {
                'user_id': '12345',
                'email': 'test@example.com',
                'ip': '192.168.1.1'
            },
            'what': {
                'url': '/api/login',
                'method': 'POST'
            }
        }
        result = encrypt_pii_fields(data, self.encryptor, ['user_id', 'email', 'ip'])
        
        self.assertIn('[ENCRYPTED]', result['who']['user_id'])
        self.assertIn('[ENCRYPTED]', result['who']['email'])
        self.assertIn('[ENCRYPTED]', result['who']['ip'])
        self.assertEqual(result['what']['url'], '/api/login')
        
    def test_decrypt_verification(self):
        """Test that encrypted values can be decrypted."""
        original_value = 'sensitive_data_123'
        encrypted = self.encryptor.encrypt(original_value)
        
        # Use the decrypt method
        decrypted = self.encryptor.decrypt(encrypted)
        self.assertEqual(decrypted, original_value)
        
    def test_encrypted_log_format(self):
        """Test encrypted log contains marked fields."""
        data = {'user_id': 'alice', 'ip': '10.0.0.1'}
        result = encrypt_pii_fields(data, self.encryptor, ['user_id', 'ip'])
        
        # Extract and decrypt
        encrypted_user_id = result['user_id'].replace('[ENCRYPTED]', '')
        decrypted = self.fernet.decrypt(encrypted_user_id.encode()).decode()
        self.assertEqual(decrypted, 'alice')
        
    def test_no_encryption_without_key(self):
        """Test that data is unchanged when no encryption key is provided."""
        # Create a new encryptor explicitly with None key
        from django_nis2_shield.loggers import PIIEncryptor, encrypt_pii_fields
        encryptor_no_key = PIIEncryptor(key=None)
        encryptor_no_key.fernet = None  # Force no fernet
        data = {'user_id': '12345'}
        result = encrypt_pii_fields(data, encryptor_no_key, ['user_id'])
        
        self.assertEqual(result['user_id'], '12345')  # Unchanged
        
    def test_list_fields_encryption(self):
        """Test encryption of fields in list items."""
        data = {
            'users': [
                {'user_id': 'user1', 'email': 'a@b.com'},
                {'user_id': 'user2', 'email': 'c@d.com'}
            ]
        }
        result = encrypt_pii_fields(data, self.encryptor, ['user_id', 'email'])
        
        self.assertIn('[ENCRYPTED]', result['users'][0]['user_id'])
        self.assertIn('[ENCRYPTED]', result['users'][1]['email'])
        
    def test_formatter_applies_encryption(self):
        """Test that Nis2JsonFormatter applies PII encryption."""
        import logging
        formatter = Nis2JsonFormatter()
        
        record = logging.LogRecord(
            name='test', 
            level=logging.INFO, 
            pathname='', 
            lineno=1, 
            msg='test_message', 
            args=(), 
            exc_info=None
        )
        record.nis2_data = {
            'who': {'user_id': 'test_user', 'ip': '1.2.3.4'}
        }
        
        output = formatter.format(record)
        data = json.loads(output)
        
        # Check that PII fields are encrypted
        self.assertIn('[ENCRYPTED]', data['log']['who']['user_id'])
        self.assertIn('[ENCRYPTED]', data['log']['who']['ip'])
        # Check integrity hash exists
        self.assertIn('integrity_hash', data)


if __name__ == '__main__':
    unittest.main()
