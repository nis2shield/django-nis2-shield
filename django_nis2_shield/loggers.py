import json
import logging
import hmac
import hashlib
import copy
from cryptography.fernet import Fernet
from django.conf import settings

# Default PII fields to encrypt
DEFAULT_PII_FIELDS = ['user_id', 'email', 'username', 'ip', 'user_agent']


class PIIEncryptor:
    """
    Encrypts sensitive data (PII) using Fernet (symmetric encryption).
    Requires NIS2_SHIELD['ENCRYPTION_KEY'] in settings.
    """
    def __init__(self, key=None):
        if not key:
            key = getattr(settings, 'NIS2_SHIELD', {}).get('ENCRYPTION_KEY')
        
        if not key:
            self.fernet = None
        else:
            self.fernet = Fernet(key)

    def encrypt(self, data: str) -> str:
        if not self.fernet or not data:
            return data
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data for verification/auditing purposes."""
        if not self.fernet or not encrypted_data:
            return encrypted_data
        try:
            return self.fernet.decrypt(encrypted_data.encode()).decode()
        except Exception:
            return encrypted_data  # Return as-is if decryption fails


def encrypt_pii_fields(data: dict, encryptor: PIIEncryptor, pii_fields: list) -> dict:
    """
    Recursively encrypt PII fields in a dictionary.
    
    Args:
        data: Dictionary containing log data
        encryptor: PIIEncryptor instance
        pii_fields: List of field names to encrypt
        
    Returns:
        New dictionary with encrypted PII fields
    """
    if not encryptor.fernet:
        return data
    
    result = copy.deepcopy(data)
    
    def _encrypt_recursive(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                if key in pii_fields and isinstance(value, str):
                    obj[key] = f"[ENCRYPTED]{encryptor.encrypt(value)}"
                elif isinstance(value, (dict, list)):
                    _encrypt_recursive(value, current_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                _encrypt_recursive(item, f"{path}[{i}]")
    
    _encrypt_recursive(result)
    return result


class SecuritySigner:
    """
    Signs log entries using HMAC-SHA256 to ensure integrity (Non-Repudiation).
    """
    def __init__(self, secret_key):
        self.secret_key = secret_key.encode()

    def sign(self, message: str) -> str:
        return hmac.new(
            self.secret_key, 
            message.encode(), 
            hashlib.sha256
        ).hexdigest()


class Nis2JsonFormatter(logging.Formatter):
    """
    Formats log records as JSON with NIS2 specific fields.
    Supports PII encryption for GDPR compliance.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        nis2_conf = getattr(settings, 'NIS2_SHIELD', {})
        self.signer = SecuritySigner(nis2_conf.get('INTEGRITY_KEY', 'default-insecure-key'))
        self.encryptor = PIIEncryptor(nis2_conf.get('ENCRYPTION_KEY'))
        self.pii_fields = nis2_conf.get('PII_FIELDS', DEFAULT_PII_FIELDS)
        self.encrypt_pii = nis2_conf.get('ENCRYPT_PII', True)

    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }

        # Add extra fields if present (passed via extra={...})
        if hasattr(record, 'nis2_data'):
            log_data.update(record.nis2_data)

        # Encrypt PII fields if enabled
        if self.encrypt_pii and self.encryptor.fernet:
            log_data = encrypt_pii_fields(log_data, self.encryptor, self.pii_fields)

        # Serialize to JSON
        json_output = json.dumps(log_data)

        # Sign the log entry
        signature = self.signer.sign(json_output)
        
        # Final structure
        final_log = {
            'log': json.loads(json_output),
            'integrity_hash': signature
        }
        
        return json.dumps(final_log)
