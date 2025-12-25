"""
Pytest configuration for Django NIS2 Shield tests.
"""
import pytest
from django.conf import settings

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
