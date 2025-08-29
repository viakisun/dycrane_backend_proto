import pytest
from tests.e2e.client import ApiClient

@pytest.fixture(scope="session")
def api_client() -> ApiClient:
    """
    Provides a session-scoped API client fixture.
    This ensures that all tests in a session share the same client instance.
    """
    return ApiClient()
