from typing import Any, Dict, List
from requests import Response

def assert_successful_response(response: Response, status_code: int = 200):
    """
    Asserts that the response has a successful status code and returns the JSON body.
    """
    assert response.status_code == status_code, \
        f"Expected status code {status_code}, but got {response.status_code}. Response: {response.text}"
    return response.json()

def assert_is_site(data: Dict[str, Any]):
    """
    Asserts that the given data dictionary represents a site object.
    """
    assert "id" in data
    assert "name" in data
    assert "status" in data

def assert_is_crane(data: Dict[str, Any]):
    """
    Asserts that the given data dictionary represents a crane object.
    """
    assert "id" in data
    assert "model_name" in data
    assert "status" in data
