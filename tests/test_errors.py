import socket
from pathlib import Path
from typing import Type

import pytest
import trustme
from conftest import API_SECRET, API_TOKEN, ApiServer

from tronzap_sdk import (
    ApiException,
    Client,
    ConnectionException,
    ErrorCode,
    HttpException,
    InvalidRequestException,
    NetworkException,
    RateLimitException,
    ServerException,
    SslException,
    TimeoutException,
    TronZapException,
    UnauthorizedException,
)

INSUFFICIENT_FUNDS = {
    "code": 6,
    "error": "Insufficient funds",
    "key": "insufficient_funds",
    "request_id": "req-42",
}


@pytest.mark.parametrize("status", [200, 400, 401, 403, 429, 500, 503])
def test_api_error_wins_over_http_status(client: Client, server: ApiServer, status: int) -> None:
    server.respond(status, INSUFFICIENT_FUNDS)

    with pytest.raises(ApiException) as exc_info:
        client.get_balance()

    error = exc_info.value
    assert type(error) is ApiException
    assert error.code == ErrorCode.INSUFFICIENT_FUNDS
    assert error.message == "Insufficient funds"
    assert error.error_key == "insufficient_funds"


def test_api_error_carries_request_id_and_status(client: Client, server: ApiServer) -> None:
    server.respond(400, INSUFFICIENT_FUNDS)

    with pytest.raises(ApiException) as exc_info:
        client.get_balance()

    assert exc_info.value.request_id == "req-42"
    assert exc_info.value.status_code == 400


def test_api_error_without_message_or_key(client: Client, server: ApiServer) -> None:
    server.respond(200, {"code": 10})

    with pytest.raises(ApiException) as exc_info:
        client.get_balance()

    assert exc_info.value.code == ErrorCode.INVALID_TRON_ADDRESS
    assert exc_info.value.message == "Unknown API error"
    assert exc_info.value.error_key is None


def test_missing_code_is_an_api_error(client: Client, server: ApiServer) -> None:
    server.respond(200, {"result": {"balance": 1}})

    with pytest.raises(ApiException) as exc_info:
        client.get_balance()

    assert exc_info.value.code == 1


@pytest.mark.parametrize("body", ["[]", '"text"', "42", "null", "true"])
def test_json_that_is_not_an_object_is_an_api_error(
    client: Client, server: ApiServer, body: str
) -> None:
    server.respond(200, body)

    with pytest.raises(ApiException) as exc_info:
        client.get_balance()

    assert exc_info.value.code == 1


@pytest.mark.parametrize(
    "status, exception",
    [
        (401, UnauthorizedException),
        (403, UnauthorizedException),
        (429, RateLimitException),
        (500, ServerException),
        (502, ServerException),
        (404, HttpException),
    ],
)
def test_http_errors_without_api_payload(
    client: Client, server: ApiServer, status: int, exception: Type[HttpException]
) -> None:
    server.respond(status, "<html>gateway</html>")

    with pytest.raises(exception) as exc_info:
        client.get_balance()

    error = exc_info.value
    assert type(error) is exception
    assert error.status_code == status
    assert error.code == status
    assert error.response_body == "<html>gateway</html>"


def test_http_error_with_successful_api_code(client: Client, server: ApiServer) -> None:
    server.respond(500, {"code": 0, "result": {}})

    with pytest.raises(ServerException) as exc_info:
        client.get_balance()

    assert exc_info.value.status_code == 500


@pytest.mark.parametrize(
    "body",
    [
        "not json",
        "",
        '{"code": 0, "result": ',
        '{"code": 0}',
        '{"code": 0, "result": null}',
    ],
    ids=["text", "empty", "truncated", "no result", "null result"],
)
def test_invalid_success_response(client: Client, server: ApiServer, body: str) -> None:
    server.respond(200, body)

    with pytest.raises(ServerException) as exc_info:
        client.get_balance()

    assert exc_info.value.status_code == 200
    assert exc_info.value.response_body == body


def test_connection_refused(server: ApiServer) -> None:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    client = Client(API_TOKEN, API_SECRET, base_url=f"http://127.0.0.1:{port}")

    with pytest.raises(ConnectionException) as exc_info:
        client.get_balance()

    assert exc_info.value.code == 0
    assert exc_info.value.original_error is not None


def test_unknown_host() -> None:
    client = Client(API_TOKEN, API_SECRET, base_url="http://tronzap-sdk-test.invalid")

    with pytest.raises(ConnectionException):
        client.get_balance()


def test_other_request_failures_are_network_errors() -> None:
    client = Client(API_TOKEN, API_SECRET, base_url="api.tronzap.com")

    with pytest.raises(NetworkException) as exc_info:
        client.get_balance()

    assert type(exc_info.value) is NetworkException


def test_timeout(server: ApiServer) -> None:
    server.delay = 1.0
    client = Client(API_TOKEN, API_SECRET, base_url=server.url, timeout=0.2)

    with pytest.raises(TimeoutException):
        client.get_balance()


def test_default_timeout() -> None:
    assert Client(API_TOKEN, API_SECRET).timeout == 30


def test_untrusted_certificate_is_rejected(tls_server: ApiServer) -> None:
    client = Client(API_TOKEN, API_SECRET, base_url=tls_server.url)

    with pytest.raises(SslException):
        client.get_balance()

    assert tls_server.requests == []


def test_trusted_certificate_is_accepted(
    tls_server: ApiServer, tls_ca: trustme.CA, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = tmp_path / "ca.pem"
    tls_ca.cert_pem.write_to_path(str(bundle))
    monkeypatch.setenv("REQUESTS_CA_BUNDLE", str(bundle))
    tls_server.ok({"balance": "1"})

    assert Client(API_TOKEN, API_SECRET, base_url=tls_server.url).get_balance() == {"balance": "1"}


@pytest.mark.parametrize(
    "exception, parent",
    [
        (ApiException, TronZapException),
        (NetworkException, TronZapException),
        (ConnectionException, NetworkException),
        (TimeoutException, NetworkException),
        (SslException, NetworkException),
        (HttpException, TronZapException),
        (ServerException, HttpException),
        (RateLimitException, HttpException),
        (UnauthorizedException, HttpException),
        (InvalidRequestException, TronZapException),
        (InvalidRequestException, ValueError),
    ],
)
def test_exception_hierarchy(exception: type, parent: type) -> None:
    assert issubclass(exception, parent)


def test_error_codes() -> None:
    assert {code.name: code.value for code in ErrorCode} == {
        "INTERNAL_SERVER_ERROR": 500,
        "AUTH_ERROR": 1,
        "INVALID_SERVICE_OR_PARAMS": 2,
        "WALLET_NOT_FOUND": 5,
        "INSUFFICIENT_FUNDS": 6,
        "INVALID_TRON_ADDRESS": 10,
        "INVALID_ENERGY_AMOUNT": 11,
        "INVALID_DURATION": 12,
        "TRANSACTION_NOT_FOUND": 20,
        "CANNOT_STOP_SUBSCRIPTION": 21,
        "ADDRESS_NOT_ACTIVATED": 24,
        "ADDRESS_ALREADY_ACTIVATED": 25,
        "AML_CHECK_NOT_FOUND": 30,
        "SERVICE_NOT_AVAILABLE": 35,
        "INVALID_BANDWIDTH_AMOUNT": 50,
    }


def test_exception_message() -> None:
    assert str(ApiException("Insufficient funds", code=6)) == "TronZap API Error 6: Insufficient funds"
