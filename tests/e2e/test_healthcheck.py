from .client import ApiClient
from .validators import assert_successful_response

def test_health_check(api_client: ApiClient):
    """
    Tests the health check endpoint to ensure the service is running
    and the database is connected.
    """
    response = api_client.get("/api/v1/system/health")
    data = assert_successful_response(response)

    assert data["status"] == "healthy"
    assert data["database_healthy"] is True
