"""
Pytest configuration for Django NIS2 Shield tests.
"""
import pytest
from django.conf import settings
from cryptography.fernet import Fernet

# Generate a valid Fernet key for testing
TEST_ENCRYPTION_KEY = Fernet.generate_key()


def pytest_configure():
    """Configure Django settings for pytest."""
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'django.contrib.sessions',
                'django_nis2_shield',
            ],
            MIDDLEWARE=[
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django_nis2_shield.middleware.Nis2GuardMiddleware',
            ],
            ROOT_URLCONF='',
            SECRET_KEY='test-secret-key',
            ALLOWED_HOSTS=['*'],
            LOGIN_URL='/login/',
            CACHES={
                'default': {
                    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                }
            },
            NIS2_SHIELD={
                'INTEGRITY_KEY': 'test-secret-key',
                'ENCRYPTION_KEY': TEST_ENCRYPTION_KEY,
                'ANONYMIZE_IPS': True,
                'ENCRYPT_PII': True,
                'PII_FIELDS': ['user_id', 'email', 'ip', 'user_agent'],
                'ENABLE_RATE_LIMIT': True,
                'RATE_LIMIT_THRESHOLD': 100,
                'ENABLE_SESSION_GUARD': True,
                'SESSION_IP_TOLERANCE': 'subnet',
                'BLOCK_TOR_EXIT_NODES': False,
                'ENFORCE_MFA_ROUTES': [],
            },
        )


@pytest.fixture
def django_settings():
    """Return the Django settings object."""
    return settings


@pytest.fixture
def encryption_key():
    """Return the test encryption key."""
    return TEST_ENCRYPTION_KEY


@pytest.fixture
def nis2_config():
    """Return the NIS2 Shield configuration."""
    return settings.NIS2_SHIELD


@pytest.fixture
def mock_request(rf):
    """Create a mock request using Django's RequestFactory."""
    request = rf.get('/test/')
    request.META['REMOTE_ADDR'] = '192.168.1.100'
    request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 Test'
    return request
