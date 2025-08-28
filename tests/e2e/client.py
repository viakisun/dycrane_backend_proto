import os
import logging
import time
from typing import Optional, Dict, Any

import requests
from requests import Response, Session
from tenacity import retry, stop_after_attempt, wait_exponential

# --- Configuration ---
BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000")
REQUEST_TIMEOUT = 10  # seconds
RETRY_ATTEMPTS = 5
RETRY_WAIT_MULTIPLIER = 1
RETRY_WAIT_MAX = 4  # seconds

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ApiClient:
    """A client for interacting with the API, with built-in retry and logging."""

    def __init__(self, base_url: str = BASE_URL, token: Optional[str] = None):
        self.base_url = base_url
        self.session = Session()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        self.session.headers["Content-Type"] = "application/json"

    @retry(
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=RETRY_WAIT_MULTIPLIER, max=RETRY_WAIT_MAX),
        reraise=True,
    )
    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Sends a request to the API.

        Args:
            method: The HTTP method (e.g., 'GET', 'POST').
            endpoint: The API endpoint (e.g., '/sites').
            data: The JSON payload for the request body.
            params: The URL parameters.

        Returns:
            The Response object from the requests library.
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.monotonic()

        try:
            response = self.session.request(
                method, url, json=data, params=params, timeout=REQUEST_TIMEOUT
            )
            elapsed_ms = (time.monotonic() - start_time) * 1000

            # Log request and response details
            log_extra = {
                "method": method,
                "url": url,
                "status_code": response.status_code,
                "latency_ms": f"{elapsed_ms:.2f}",
            }

            if 200 <= response.status_code < 300:
                logger.info("API request successful", extra=log_extra)
            else:
                logger.warning("API request failed", extra=log_extra)
                # Raise HTTPError to trigger tenacity retry for server-side errors
                response.raise_for_status()

            return response
        except requests.exceptions.RequestException as e:
            elapsed_ms = (time.monotonic() - start_time) * 1000
            logger.error(
                "API request connection error",
                extra={"method": method, "url": url, "latency_ms": f"{elapsed_ms:.2f}", "error": str(e)},
            )
            # Re-raise the exception to allow tenacity to handle retries
            raise

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Response:
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Response:
        return self.request("POST", endpoint, data=data)

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Response:
        return self.request("PUT", endpoint, data=data)

    def delete(self, endpoint: str) -> Response:
        return self.request("DELETE", endpoint)
