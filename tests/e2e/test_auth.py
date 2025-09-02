import pytest
import uuid

from tests.e2e.client import ApiClient

# Use a consistent dummy ID for tests that need one
DUMMY_USER_ID = str(uuid.uuid4())

@pytest.fixture(scope="module")
def api_client() -> ApiClient:
    """Fixture to provide a base API client without auth."""
    return ApiClient()

def test_login_success(api_client: ApiClient):
    """
    Test case 1: Login (with any email/password) -> 200 OK, response includes user.roles.
    """
    email = "driver.test@example.com"
    payload = {"email": email, "password": "password123"}

    response = api_client.post("/api/v1/auth/login", data=payload)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert data["user"]["email"] == email
    assert data["user"]["roles"] == ["DRIVER"]

def test_unauthorized_access(api_client: ApiClient):
    """
    Test case 3: No Authorization header for /api/v1/me -> 401 Unauthorized.
    """
    # This client has no token
    with pytest.raises(Exception) as e:
        api_client.get("/api/v1/me")

    # The client raises an exception on non-2xx status codes.
    # We can inspect the exception's response attribute.
    assert e.value.response.status_code == 401
    error_data = e.value.response.json()
    assert "Not authenticated" in error_data["detail"]

def test_authorized_access_with_correct_role(api_client: ApiClient):
    """
    Test case 2: Authorization: Bearer dev:{user_id}:OWNER for an OWNER endpoint -> 200 OK.
    """
    # Create a token for an OWNER
    owner_token = f"dev:{DUMMY_USER_ID}:OWNER"

    # Create a new client authenticated with this token
    owner_client = ApiClient(token=owner_token)

    # Access an OWNER-protected endpoint
    # Note: The path is /api/v1/org/owners/{id}/cranes as per the router setup
    response = owner_client.get(f"/api/v1/org/owners/{DUMMY_USER_ID}/cranes", params={"summary": True})

    assert response.status_code == 200
    data = response.json()
    assert "status_counts" in data
    assert "NORMAL" in data["status_counts"]

def test_forbidden_access_with_wrong_role(api_client: ApiClient):
    """
    Test case 4: Authorization: Bearer dev:{user_id}:DRIVER for an OWNER endpoint -> 403 Forbidden.
    """
    # Create a token for a DRIVER
    driver_token = f"dev:{DUMMY_USER_ID}:DRIVER"

    # Create a new client authenticated with this token
    driver_client = ApiClient(token=driver_token)

    # Attempt to access an OWNER-protected endpoint
    with pytest.raises(Exception) as e:
        driver_client.get(f"/api/v1/org/owners/{DUMMY_USER_ID}/cranes", params={"summary": True})

    assert e.value.response.status_code == 403
    error_data = e.value.response.json()
    assert "User does not have the required roles" in error_data["detail"]

def test_me_endpoint(api_client: ApiClient):
    """
    Test the /me endpoint with a valid dev token.
    """
    user_id = str(uuid.uuid4())
    roles = "SAFETY_MANAGER,DRIVER"
    token = f"dev:{user_id}:{roles}"

    authed_client = ApiClient(token=token)
    response = authed_client.get("/api/v1/me")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    # Note: roles are uppercased by the context dependency
    assert sorted(data["roles"]) == sorted(["SAFETY_MANAGER", "DRIVER"])
    assert data["email"] == f"{user_id}@example.dev"
