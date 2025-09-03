import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from server.main import app
from server.domain.schemas import SiteOut, SiteCreate, SiteStatus

@pytest.fixture
def client():
    """Provides a TestClient instance for testing the API."""
    return TestClient(app)

def test_create_site_router(client):
    # Arrange
    site_in = {
        "name": "Test Site",
        "address": "123 Test St",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "requested_by_id": "user1"
    }
    mock_site_out = SiteOut(
        id="site-id-123",
        status=SiteStatus.PENDING_APPROVAL,
        created_at="2025-01-01T12:00:00",
        updated_at="2025-01-01T12:00:00",
        requested_at="2025-01-01T12:00:00",
        **site_in
    )

    with patch("server.api.routers.sites.site_service.create_site", return_value=mock_site_out) as mock_create:
        # Act
        response = client.post("/api/v1/org/sites", json=site_in)

        # Assert
        assert response.status_code == 201
        assert response.json()["name"] == site_in["name"]
        mock_create.assert_called_once()

def test_update_site_router(client):
    # Arrange
    site_id = "site-id-123"
    update_in = {
        "status": "ACTIVE",
        "approved_by_id": "user-approver-id"
    }
    # Create a mock of the input data that would be used to create the SiteOut
    site_data = {
        "id": site_id,
        "name": "Test Site",
        "address": "123 Test St",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "requested_by_id": "user1",
        "created_at": "2025-01-01T12:00:00",
        "updated_at": "2025-01-02T12:00:00",
        "requested_at": "2025-01-01T12:00:00",
        **update_in
    }
    mock_site_out = SiteOut(**site_data)

    with patch("server.api.routers.sites.site_service.update_site", return_value=mock_site_out) as mock_update:
        # Act
        response = client.patch(f"/api/v1/org/sites/{site_id}", json=update_in)

        # Assert
        assert response.status_code == 200
        assert response.json()["status"] == "ACTIVE"
        assert response.json()["approved_by_id"] == "user-approver-id"
        mock_update.assert_called_once()
