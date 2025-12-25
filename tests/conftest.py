"""
Pytest configuration for Django NIS2 Shield tests.
"""
import pytest
from django.conf import settings
from cryptography.fernet import Fernet

# Define settings configuration in a hook to ensure it runs at the right time
def pytest_configure():
    if not settings.configured:
        settings.configure(
            SECRET_KEY='test-secret-key',
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django_nis2_shield',
            ],
            MIDDLEWARE=[
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django_nis2_shield.middleware.Nis2GuardMiddleware',
            ],
            ROOT_URLCONF=__name__,
            CACHES={
                'default': {
                    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                    'LOCATION': 'unique-snowflake',
                }
            },
            NIS2_SHIELD={
                'INTEGRITY_KEY': 'test-integrity-key',
                'ENCRYPTION_KEY': Fernet.generate_key().decode(),
                'ANONYMIZE_IPS': True,
                'ENABLE_RATE_LIMIT': True,
                'BLOCK_TOR_EXIT_NODES': True,
                'ENCRYPT_PII': True,
                'PII_FIELDS': ['user_id', 'ip', 'email'],
                'LOG_FORMAT': 'JSON',
            },
            USE_TZ=True,
        )
    try:
        import django
        django.setup()
    except Exception:
        pass


@pytest.fixture
def django_settings():
    """Return the Django settings object."""
    return settings


@pytest.fixture
def nis2_settings(settings):
    """Fixture to easily override NIS2 settings in tests."""
    return settings.NIS2_SHIELD


@pytest.fixture
def encryption_key(nis2_settings):
    """Return the test encryption key."""
    return nis2_settings['ENCRYPTION_KEY'].encode()


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
