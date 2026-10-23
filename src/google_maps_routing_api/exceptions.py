"""Exceptions for Google Maps Routes API."""


class GoogleMapsRoutingApiError(Exception):
    """Exception talking to the Google Maps Routes API."""


class GoogleMapsRoutingApiConnectionError(GoogleMapsRoutingApiError):
    """Exception connecting to the Google Maps Routes API."""


class GoogleMapsRoutingApiConnectionTimeoutError(GoogleMapsRoutingApiConnectionError, TimeoutError):
    """Exception raised when a request to the Google Maps Routes API times out."""


class GoogleMapsRoutingApiAuthError(GoogleMapsRoutingApiError):
    """Exception raised for authentication errors (invalid API key, blocked referrer, disabled service)."""

    def __init__(self, message: str, *, status: str | None = None, reason: str | None = None) -> None:
        """Initialize the error with the API status and reason, when available."""
        super().__init__(message)
        self.status = status
        self.reason = reason


class GoogleMapsRoutingApiResponseError(GoogleMapsRoutingApiError):
    """Exception raised for other errors in the Google Maps Routes API response."""

    def __init__(self, message: str, *, status: str | None = None, reason: str | None = None) -> None:
        """Initialize the error with the API status and reason, when available."""
        super().__init__(message)
        self.status = status
        self.reason = reason
