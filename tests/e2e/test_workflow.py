import pytest
import datetime as dt
from .client import ApiClient
from .validators import assert_successful_response, assert_is_site, assert_is_crane

# Hardcoded IDs from the seed data
SAFETY_MANAGER_ID = "user-safety-manager-01"
MANUFACTURER_ID = "user-manufacturer-01"
DRIVER_ID = "user-driver-01"
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
    site_id = created_site["id"]

    # Step 2: Approve the site
    approve_data = {"approved_by_id": MANUFACTURER_ID}
    response = api_client.post(f"/api/sites/{site_id}/approve", data=approve_data)
    approved_site = assert_successful_response(response)
    assert approved_site["status"] == "ACTIVE"

    # Step 3: List cranes
    response = api_client.get(f"/api/owners/{OWNER_ORG_ID}/cranes")
    cranes = assert_successful_response(response)
    assert isinstance(cranes, list)
    assert len(cranes) > 0
    assert "model" in cranes[0]
    assert "model_name" in cranes[0]["model"]
    crane_id = cranes[0]['id']

    # Step 4: Assign crane
    assign_crane_data = {
        "site_id": site_id,
        "crane_id": crane_id,
        "safety_manager_id": SAFETY_MANAGER_ID,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    response = api_client.post("/api/assignments/crane", data=assign_crane_data)
    crane_assignment = assert_successful_response(response, status_code=201)
    site_crane_id = crane_assignment['assignment_id']

    # Step 5: Assign driver
    assign_driver_data = {
        "site_crane_id": site_crane_id,
        "driver_id": DRIVER_ID,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    response = api_client.post("/api/assignments/driver", data=assign_driver_data)
    driver_assignment = assert_successful_response(response, status_code=201)
    driver_assignment_id = driver_assignment['driver_assignment_id']

    # Step 6: Record attendance
    attendance_data = {
        "driver_assignment_id": driver_assignment_id,
        "work_date": start_date.isoformat(),
        "check_in_at": f"{start_date.isoformat()}T08:00:00Z",
        "check_out_at": f"{start_date.isoformat()}T17:00:00Z",
    }
    response = api_client.post("/api/assignments/attendance", data=attendance_data)
    assert_successful_response(response, status_code=201)

    # Step 7: Request document
    doc_request_data = {
        "site_id": site_id,
        "driver_id": DRIVER_ID,
        "requested_by_id": SAFETY_MANAGER_ID,
        "due_date": end_date.isoformat(),
    }
    response = api_client.post("/api/docs/requests", data=doc_request_data)
    doc_request = assert_successful_response(response, status_code=201)
    request_id = doc_request['request_id']

    # Step 8: Submit document
    doc_submit_data = {
        "request_id": request_id,
        "doc_type": "Safety Certificate",
        "file_url": "https://example.com/safety-cert.pdf"
    }
    response = api_client.post("/api/docs/items/submit", data=doc_submit_data)
    doc_item = assert_successful_response(response, status_code=201)
    item_id = doc_item['item_id']

    # Step 9: Review document
    doc_review_data = {
        "item_id": item_id,
        "reviewer_id": SAFETY_MANAGER_ID,
        "approve": True
    }
    response = api_client.post("/api/docs/items/review", data=doc_review_data)
    reviewed_item = assert_successful_response(response)
    assert reviewed_item['status'] == 'APPROVED'
