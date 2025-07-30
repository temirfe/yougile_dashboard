import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ExternalApiClient:
    def __init__(self, base_url=None, company=None):
        # Allow base_url and token to be passed explicitly (for testing/flexibility)
        # or fall back to Django settings
        self.base_url = base_url if base_url is not None else settings.YG_API_URL
        #self.token = token if token is not None else settings.YG_DARTLAB_KEY
        if company == 'dartlab':
            self.token = settings.YG_DARTLAB_KEY
        elif company == 'prosoft':
            self.token = settings.YG_PROSOFT_KEY
        elif company == 'product':
            self.token = settings.YG_PRODUCT_KEY
        elif company == 'pm':
            self.token = settings.YG_PM_KEY
        else:
            self.token = settings.YG_DARTLAB_KEY

        if not self.base_url:
            raise ValueError("External API Base URL not configured.")
        if not self.token:
            raise ValueError("External API Bearer Token not configured.")

        self._session = requests.Session() # Use a session for persistent connections and headers

    def _get_headers(self):
        """Constructs common headers for API requests."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _send_request(self, method, endpoint, params=None, json_data=None):
        """Helper to send various types of requests and handle common errors."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        try:
            response = self._session.request(
                method,
                url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=10 # Add a timeout for robustness
            )
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"HTTP Error {method} {url}: {e.response.status_code} - {e.response.text}"
            )
            # You can raise a custom exception here, or return specific error info
            raise ExternalApiException(
                f"API returned error: {e.response.status_code} - {e.response.text}",
                status_code=e.response.status_code,
                response_data=e.response.json() if e.response.text else None
            ) from e
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error {method} {url}: {e}")
            raise ExternalApiException(f"API request timed out to {url}") from e
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error {method} {url}: {e}")
            raise ExternalApiException(f"Could not connect to API at {url}") from e
        except requests.exceptions.RequestException as e:
            logger.error(f"An unexpected request error occurred for {method} {url}: {e}")
            raise ExternalApiException(f"An unexpected error occurred during API request to {url}") from e
        except ValueError as e: # For response.json() if it's not valid JSON
            logger.error(f"Failed to parse JSON response from {url}: {e}")
            raise ExternalApiException(f"Failed to parse JSON response from {url}") from e

    def get(self, endpoint, params=None):
        return self._send_request("GET", endpoint, params=params)

    def post(self, endpoint, data=None):
        return self._send_request("POST", endpoint, json_data=data)

    def put(self, endpoint, data=None):
        return self._send_request("PUT", endpoint, json_data=data)

    def delete(self, endpoint):
        return self._send_request("DELETE", endpoint)

# Custom exception for API-related errors
class ExternalApiException(Exception):
    def __init__(self, message, status_code=None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data