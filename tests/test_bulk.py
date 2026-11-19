import hashlib

import pytest
from conftest import API_SECRET, ApiServer

from tronzap_sdk import ApiException, Client, ErrorCode, InvalidRequestException, ServerException

CSV = (
    "row,address,amount,status,reason,charged,transaction_id\n"
    "1,TPY1Kb8cKAZQfm95gXQQs2Mh8Uygtos21D,65000,delivered,,3.25,01kb2m9c4de5fg6hj7km8np9qr\n"
    "2,TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE,131000,skipped,address_not_activated,,\n"
)

CALCULATION = {
    "id": "01kb2m7a1bc2de3fg4hj5km6np",
    "status": "draft",
    "resource": "energy",
    "duration": 1,
    "total_amount": 1240.1,
    "accepted": 1,
    "rejected_count": 0,
    "rejected": [],
    "expires_at": "2026-11-16T12:15:00+00:00",
}


def test_calculate_sends_energy_and_the_rows(client: Client, server: ApiServer) -> None:
    server.ok(CALCULATION)
    rows = (
        {"address": "TPY1Kb8cKAZQfm95gXQQs2Mh8Uygtos21D", "amount": 65000},
        {"address": "TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE", "amount": 131000},
    )

    assert client.bulk_calculate(iter(rows), 24) == CALCULATION
    assert server.last.path == "/v1/bulk/calculate"
    assert server.last.json == {"resource": "energy", "duration": 24, "items": list(rows)}


def test_calculate_defaults_the_duration_to_one_hour(client: Client, server: ApiServer) -> None:
    client.bulk_calculate([{"address": "TAddress", "amount": 65000}], 0)

    assert server.last.json["duration"] == 1


def test_calculate_without_items_is_not_sent(client: Client, server: ApiServer) -> None:
    with pytest.raises(InvalidRequestException):
        client.bulk_calculate([])

    assert server.requests == []


def test_calculate_with_no_valid_rows_returns_them_in_the_error(
    client: Client, server: ApiServer
) -> None:
    rejected = [{"row": 1, "address": "abc", "reason": "invalid_address"}]
    server.respond(200, {
        "code": 94,
        "key": "bulk_no_valid_items",
        "error": "No valid items",
        "result": {"rejected": rejected},
    })

    with pytest.raises(ApiException) as exc_info:
        client.bulk_calculate([{"address": "abc", "amount": 65000}])

    assert exc_info.value.code == ErrorCode.BULK_NO_VALID_ITEMS
    assert exc_info.value.result == {"rejected": rejected}


def test_create_sends_only_the_given_options(client: Client, server: ApiServer) -> None:
    client.bulk_create("calc-1")

    assert server.last.path == "/v1/bulk/create"
    assert server.last.json == {"id": "calc-1"}


def test_create_with_all_options(client: Client, server: ApiServer) -> None:
    client.bulk_create(
        "calc-1",
        external_id="order-42",
        force=True,
        max_price_increase=0,
        webhook_url="https://example.com/hook",
    )

    assert server.last.json == {
        "id": "calc-1",
        "force": True,
        "max_price_increase": 0,
        "webhook_url": "https://example.com/hook",
        "external_id": "order-42",
    }


def test_create_without_id_is_not_sent(client: Client, server: ApiServer) -> None:
    with pytest.raises(InvalidRequestException):
        client.bulk_create("")

    assert server.requests == []


def test_create_returns_the_new_calculation_when_the_price_changed(
    client: Client, server: ApiServer
) -> None:
    server.respond(200, {
        "code": 92,
        "key": "bulk_price_changed",
        "error": "Price changed, confirmation required",
        "request_id": "req-92",
        "result": CALCULATION,
    })

    with pytest.raises(ApiException) as exc_info:
        client.bulk_create("calc-old")

    assert exc_info.value.code == ErrorCode.BULK_PRICE_CHANGED
    assert exc_info.value.error_key == "bulk_price_changed"
    assert exc_info.value.result == CALCULATION


def test_check_by_id_or_external_id(client: Client, server: ApiServer) -> None:
    server.ok({"id": "order-1", "status": "processing"})

    assert client.bulk_check("order-1") == {"id": "order-1", "status": "processing"}
    assert server.last.path == "/v1/bulk/check"
    assert server.last.json == {"id": "order-1"}

    client.bulk_check(external_id="my-order")
    assert server.last.json == {"external_id": "my-order"}


def test_check_needs_an_id(client: Client) -> None:
    with pytest.raises(InvalidRequestException):
        client.bulk_check()


def test_history_paging(client: Client, server: ApiServer) -> None:
    client.bulk_history(3, 50)
    assert server.last.path == "/v1/bulk/history"
    assert server.last.json == {"page": 3, "per_page": 50}

    client.bulk_history(0, 0)
    assert server.last.json == {"page": 1, "per_page": 10}


def test_report_returns_the_csv(client: Client, server: ApiServer) -> None:
    server.respond(200, CSV, {"Content-Type": "text/csv; charset=UTF-8"})

    assert client.bulk_report("order-1", status="skipped") == CSV
    assert server.last.path == "/v1/bulk/report"
    assert server.last.json == {"id": "order-1", "status": "skipped"}


def test_report_is_utf8_without_a_charset(client: Client, server: ApiServer) -> None:
    csv = "row,reason\n1,адреса не активована\n"
    server.respond(200, csv, {"Content-Type": "text/csv"})

    assert client.bulk_report("order-1") == csv


def test_report_errors_are_json(client: Client, server: ApiServer) -> None:
    server.respond(200, {"code": 90, "key": "bulk_not_found", "error": "Bulk order not found"})

    with pytest.raises(ApiException) as exc_info:
        client.bulk_report(external_id="missing")

    assert exc_info.value.code == ErrorCode.BULK_NOT_FOUND


def test_report_that_is_not_csv_is_an_invalid_response(client: Client, server: ApiServer) -> None:
    server.ok({"rows": []})

    with pytest.raises(ServerException) as exc_info:
        client.bulk_report("order-1")

    assert exc_info.value.message == "Expected a CSV report"


def test_report_needs_an_id(client: Client) -> None:
    with pytest.raises(InvalidRequestException):
        client.bulk_report()


def test_webhook_signature(client: Client) -> None:
    body = '{"id":"01kb2m5x9qj4v8n3c7d6e5f4g3","external_id":"my-order-42","status":"partial"}'
    signature = hashlib.sha256((body + API_SECRET).encode()).hexdigest()

    assert client.verify_webhook_signature(body, signature)
    assert client.verify_webhook_signature(body.encode(), signature)
    assert client.verify_webhook_signature(body, f" {signature.upper()}\n")
    assert not client.verify_webhook_signature(body + " ", signature)
    assert not client.verify_webhook_signature(body, "")
    assert not client.verify_webhook_signature(body, "підпис")
    other = hashlib.sha256((body + "other-secret").encode()).hexdigest()
    assert not client.verify_webhook_signature(body, other)
