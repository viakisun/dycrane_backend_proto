import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from server.main import app
from server.domain.schemas import SiteOut, SiteCreate, SiteStatus, SiteUpdate
from server.auth.schemas import CurrentUserSchema
from server.auth.context import get_current_user

# --- Test Setup ---
# Mock the auth dependency for all tests in this file
def get_mock_user():
    return CurrentUserSchema(id="test-user", roles=["SAFETY_MANAGER"])

app.dependency_overrides[get_current_user] = get_mock_user

@pytest.fixture
def client():
    """Provides a TestClient instance for testing the API."""
    return TestClient(app)

# --- Tests ---

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

def test_update_site_to_approve_router(client):
    # Arrange
    site_id = "site-id-123"
    update_in = SiteUpdate(status=SiteStatus.ACTIVE, approved_by_id="user-approver")

    mock_site_out = SiteOut(
        id=site_id,
        name="Test Site",
        address="123 Test St",
        start_date="2025-01-01",
        end_date="2025-12-31",
        requested_by_id="user1",
        status=SiteStatus.ACTIVE,
        approved_by_id=update_in.approved_by_id,
        created_at="2025-01-01T12:00:00",
        updated_at="2025-01-01T12:00:00",
        requested_at="2025-01-01T12:00:00",
    )

    with patch("server.api.routers.sites.site_service.update_site", return_value=mock_site_out) as mock_update:
        # Act
        response = client.patch(f"/api/v1/org/sites/{site_id}", json=update_in.model_dump())

        # Assert
        assert response.status_code == 200
        assert response.json()["status"] == "ACTIVE"
        mock_update.assert_called_once()

# Cleanup the dependency override after all tests in this file have run
def teardown_module(module):
    app.dependency_overrides.clear()
