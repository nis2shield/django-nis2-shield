from cryptography.fernet import Fernet

SECRET_KEY = 'test-secret-key'
DEBUG = True
USE_TZ = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django_nis2_shield',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_nis2_shield.middleware.Nis2GuardMiddleware',
]

ROOT_URLCONF = 'tests.urls'  # We might need a dummy urls.py or just set it to None if not testing views directly

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

NIS2_SHIELD = {
    'INTEGRITY_KEY': 'test-integrity-key',
    'ENCRYPTION_KEY': Fernet.generate_key().decode(),
    'ANONYMIZE_IPS': True,
    'ENABLE_RATE_LIMIT': True,
    'BLOCK_TOR_EXIT_NODES': True,
    'ENCRYPT_PII': True,
    'PII_FIELDS': ['user_id', 'ip', 'email'],
    'LOG_FORMAT': 'JSON',
}
