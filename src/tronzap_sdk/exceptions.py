"""
TronZap SDK Exceptions
"""

from enum import IntEnum
from typing import Any, Optional


class ErrorCode(IntEnum):
    # Internal server error - Contact support if this error persists.
    INTERNAL_SERVER_ERROR = 500

    # Authentication error - Check your API token and ensure your signature is calculated correctly.
    AUTH_ERROR = 1

    # Invalid service or parameters - Check that the service name and parameters are correct.
    INVALID_SERVICE_OR_PARAMS = 2

    # Wallet not found - Verify the wallet address or contact support if you believe this is an error.
    WALLET_NOT_FOUND = 5

    # Insufficient funds - Add funds to your account or reduce the amount of energy you're requesting.
    INSUFFICIENT_FUNDS = 6

    # Invalid TRON address, or the address already has an active subscription - Check the TRON address format.
    # It should be a valid 34-character TRON address.
    INVALID_TRON_ADDRESS = 10

    # Invalid energy amount - Ensure the requested energy amount is valid.
    INVALID_ENERGY_AMOUNT = 11

    # Invalid duration - Check that the duration parameter is valid.
    INVALID_DURATION = 12

    # Transaction not found - Verify the transaction ID or external ID is correct.
    TRANSACTION_NOT_FOUND = 20

    # Cannot stop subscription, e.g. it has a transactions limit.
    CANNOT_STOP_SUBSCRIPTION = 21

    # Address not activated - Activate the address first by making an address activation transaction.
    ADDRESS_NOT_ACTIVATED = 24

    # Address already activated - The address is already activated. No action needed.
    ADDRESS_ALREADY_ACTIVATED = 25

    # AML check not found - Re-run the AML check or confirm the ID.
    AML_CHECK_NOT_FOUND = 30

    # Service not available - The service is temporarily unavailable.
    SERVICE_NOT_AVAILABLE = 35

    # Invalid bandwidth amount - Ensure the requested bandwidth amount is valid.
    INVALID_BANDWIDTH_AMOUNT = 50

    # Bulk order not found - Check the order ID or external ID. A calculation that was never started is not an order.
    BULK_NOT_FOUND = 90

    # Bulk calculation expired - Call bulk_calculate() again; a calculation is valid for 10 minutes.
    BULK_EXPIRED = 91

    # Price changed - The new calculation is in ApiException.result; to start the order, call bulk_create() with its id.
    BULK_PRICE_CHANGED = 92

    # Too many items - Send at most 10 000 rows in one calculation.
    BULK_TOO_MANY_ITEMS = 93

    # No valid items - Fix the rows listed in ApiException.result["rejected"].
    BULK_NO_VALID_ITEMS = 94

    # Resource not supported for bulk orders - Only energy can be ordered in bulk.
    BULK_RESOURCE_NOT_SUPPORTED = 95

    # Request body too large (HTTP 413) - Send fewer rows in one calculation.
    PAYLOAD_TOO_LARGE = 96

    # Too many requests (HTTP 429) - Wait ApiException.retry_after seconds, when given, and retry.
    RATE_LIMITED = 429


class TronZapException(Exception):
    """Base exception — backward-compatible."""

    def __init__(self, message: str, code: int = 1):
        self.message = message
        self.code = code
        super().__init__(f"TronZap API Error {code}: {message}")


class ApiException(TronZapException):
    """API-level error (response body code != 0).

    result holds the data the API sent with the error, such as the new calculation for
    BULK_PRICE_CHANGED, or None. retry_after is the seconds to wait before retrying, from the
    Retry-After header or the body, or None when the API did not send it.
    """

    def __init__(
        self,
        message: str,
        code: int = 1,
        error_key: Optional[str] = None,
        request_id: Optional[str] = None,
        status_code: Optional[int] = None,
        result: Any = None,
        retry_after: Optional[int] = None,
    ):
        super().__init__(message, code)
        self.error_key: Optional[str] = error_key
        self.request_id: Optional[str] = request_id
        self.status_code: Optional[int] = status_code
        self.result: Any = result
        self.retry_after: Optional[int] = retry_after


class InvalidRequestException(TronZapException, ValueError):
    """Invalid arguments, rejected before any request is sent."""

    def __init__(self, message: str):
        super().__init__(message, code=0)


class NetworkException(TronZapException):
    """Network-level error (request failed before receiving a response)."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, code=0)
        self.original_error = original_error


class ConnectionException(NetworkException):
    """Could not connect to the server (ECONNREFUSED, ENOTFOUND, etc.)."""


class TimeoutException(NetworkException):
    """Request timed out."""


class SslException(NetworkException):
    """SSL/TLS certificate or connection error."""


class HttpException(TronZapException):
    """HTTP-level error (non-2xx response)."""

    def __init__(self, status_code: int, message: str, response_body: str = ""):
        super().__init__(message, code=status_code)
        self.status_code = status_code
        self.response_body = response_body


class ServerException(HttpException):
    """Server error (5xx)."""


class RateLimitException(HttpException):
    """Too many requests (429). retry_after is the seconds to wait, or None when not sent."""

    def __init__(self, response_body: str = "", retry_after: Optional[int] = None):
        super().__init__(429, "Too many requests", response_body)
        self.retry_after: Optional[int] = retry_after


class UnauthorizedException(HttpException):
    """Unauthorized (401/403)."""
