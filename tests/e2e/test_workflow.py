import pytest
import datetime as dt
from .client import ApiClient
from .validators import assert_successful_response, assert_is_site

# Hardcoded IDs from the seed data
# In a real-world scenario, these might be dynamically fetched
# or created as part of the test setup.
SAFETY_MANAGER_ID = "user-safety-manager-01"
MANUFACTURER_ID = "user-manufacturer-01"
OWNER_ORG_ID = "org-owner-01"

@pytest.mark.workflow
def test_full_business_workflow(api_client: ApiClient):
    """
    Tests the full 9-step business workflow from a client's perspective.
    """
    # Step 1: Create a new site
    start_date = dt.date.today() + dt.timedelta(days=30)
    end_date = start_date + dt.timedelta(days=90)

    site_data = {
        "name": f"E2E Test Site - {dt.datetime.now().strftime('%Y%m%d%H%M%S')}",
        "address": "123 Test Street, Test City",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "requested_by_id": SAFETY_MANAGER_ID,
    }

    response = api_client.post("/api/sites/", data=site_data)
    created_site = assert_successful_response(response, status_code=201)
    assert_is_site(created_site)
    assert created_site["name"] == site_data["name"]
    assert created_site["status"] == "PENDING_APPROVAL"
    site_id = created_site["id"]

    # Step 2: Approve the site
    approve_data = {"approved_by_id": MANUFACTURER_ID}
    response = api_client.post(f"/api/sites/{site_id}/approve", data=approve_data)
    approved_site = assert_successful_response(response)
    assert_is_site(approved_site)
    assert approved_site["id"] == site_id
    assert approved_site["status"] == "ACTIVE"

    # Step 3: List cranes for the owner organization
    response = api_client.get(f"/api/owners/{OWNER_ORG_ID}/cranes")
    cranes = assert_successful_response(response)
    assert isinstance(cranes, list)
    assert len(cranes) > 0, "Expected at least one crane for the owner organization"

    # For now, we'll stop here. The rest of the workflow will be implemented
    # as the corresponding services are refactored.
    pytest.skip("Workflow test is partially implemented.")
