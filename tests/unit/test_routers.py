import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from server.main import app
from server.domain.schemas import SiteOut, SiteCreate, SiteStatus

@pytest.fixture
def client():
    """Provides a TestClient instance for testing the API."""
    return TestClient(app, root_path="/api")

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
        response = client.post("/api/sites/", json=site_in)

        # Assert
        assert response.status_code == 201
        assert response.json()["name"] == site_in["name"]
        mock_create.assert_called_once()

def test_approve_site_router(client):
    # Arrange
    site_id = "site-id-123"
    approve_in = {"approved_by_id": "user2"}
    mock_site_out = SiteOut(
        id=site_id,
        name="Test Site",
        address="123 Test St",
        start_date="2025-01-01",
        end_date="2025-12-31",
        requested_by_id="user1",
        status=SiteStatus.ACTIVE,
        created_at="2025-01-01T12:00:00",
        updated_at="2025-01-01T12:00:00",
        requested_at="2025-01-01T12:00:00",
        **approve_in
    )

    with patch("server.api.routers.sites.site_service.approve_site", return_value=mock_site_out) as mock_approve:
        # Act
        response = client.post(f"/api/sites/{site_id}/approve", json=approve_in)

        # Assert
        assert response.status_code == 200
        assert response.json()["status"] == "ACTIVE"
        assert mock_approve.call_count == 1
