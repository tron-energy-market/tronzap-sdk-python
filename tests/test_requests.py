import hashlib
from typing import Any, Callable, Dict

import pytest
from conftest import API_SECRET, API_TOKEN, ApiServer

from tronzap_sdk import Client, InvalidRequestException

ADDRESS = "TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE"
FROM_ADDRESS = "TJRabPrwbZy45sbavfcjinPJC18kjpRTv8"
TO_ADDRESS = "TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj"
USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

CASES: Dict[str, Any] = {
    "get_services": (lambda c: c.get_services(), "/v1/services", {}),
    "get_balance": (lambda c: c.get_balance(), "/v1/balance", {}),
    "get_address_info": (
        lambda c: c.get_address_info(ADDRESS),
        "/v1/address-info",
        {"address": ADDRESS},
    ),
    "estimate_energy": (
        lambda c: c.estimate_energy(FROM_ADDRESS, TO_ADDRESS, USDT_CONTRACT),
        "/v1/estimate-energy",
        {"from_address": FROM_ADDRESS, "to_address": TO_ADDRESS, "contract_address": USDT_CONTRACT},
    ),
    "estimate_energy without contract": (
        lambda c: c.estimate_energy(FROM_ADDRESS, TO_ADDRESS),
        "/v1/estimate-energy",
        {"from_address": FROM_ADDRESS, "to_address": TO_ADDRESS},
    ),
    "calculate": (
        lambda c: c.calculate(ADDRESS, 65000, 24),
        "/v1/calculate",
        {"address": ADDRESS, "amount": 65000, "duration": 24},
    ),
    "calculate default duration": (
        lambda c: c.calculate(ADDRESS, 65000),
        "/v1/calculate",
        {"address": ADDRESS, "amount": 65000, "duration": 1},
    ),
    "create_energy_transaction": (
        lambda c: c.create_energy_transaction(ADDRESS, 65000),
        "/v1/transaction/new",
        {"service": "energy", "params": {"address": ADDRESS, "amounts": {"energy": 65000}, "duration": 1}},
    ),
    "create_energy_transaction full": (
        lambda c: c.create_energy_transaction(
            ADDRESS, 65000, duration=24, external_id="order-1", activate_address=True
        ),
        "/v1/transaction/new",
        {
            "service": "energy",
            "external_id": "order-1",
            "params": {
                "address": ADDRESS,
                "amounts": {"energy": 65000},
                "duration": 24,
                "activate_address": True,
            },
        },
    ),
    "create_bandwidth_transaction": (
        lambda c: c.create_bandwidth_transaction(ADDRESS, 345, external_id="order-2"),
        "/v1/transaction/new",
        {
            "service": "bandwidth",
            "external_id": "order-2",
            "params": {"address": ADDRESS, "amounts": {"bandwidth": 345}, "duration": 1},
        },
    ),
    "create_resource_bundle_transaction": (
        lambda c: c.create_resource_bundle_transaction(
            ADDRESS, 65000, 345, external_id="order-3", activate_address=True
        ),
        "/v1/transaction/new",
        {
            "service": "resource_bundle",
            "external_id": "order-3",
            "params": {
                "address": ADDRESS,
                "amounts": {"energy": 65000, "bandwidth": 345},
                "duration": 1,
                "activate_address": True,
            },
        },
    ),
    "create_bandwidth_transaction minimal": (
        lambda c: c.create_bandwidth_transaction(ADDRESS, 345),
        "/v1/transaction/new",
        {"service": "bandwidth", "params": {"address": ADDRESS, "amounts": {"bandwidth": 345}, "duration": 1}},
    ),
    "create_resource_bundle_transaction minimal": (
        lambda c: c.create_resource_bundle_transaction(ADDRESS, 65000, 345),
        "/v1/transaction/new",
        {
            "service": "resource_bundle",
            "params": {"address": ADDRESS, "amounts": {"energy": 65000, "bandwidth": 345}, "duration": 1},
        },
    ),
    "create_address_activation_transaction minimal": (
        lambda c: c.create_address_activation_transaction(ADDRESS),
        "/v1/transaction/new",
        {"service": "activate_address", "params": {"address": ADDRESS}},
    ),
    "create_address_activation_transaction": (
        lambda c: c.create_address_activation_transaction(ADDRESS, external_id="order-4"),
        "/v1/transaction/new",
        {"service": "activate_address", "external_id": "order-4", "params": {"address": ADDRESS}},
    ),
    "check_transaction by id": (
        lambda c: c.check_transaction(id="tx-1"),
        "/v1/transaction/check",
        {"id": "tx-1"},
    ),
    "check_transaction by external_id": (
        lambda c: c.check_transaction(external_id="order-1"),
        "/v1/transaction/check",
        {"external_id": "order-1"},
    ),
    "get_direct_recharge_info": (
        lambda c: c.get_direct_recharge_info(),
        "/v1/direct-recharge-info",
        {},
    ),
    "get_aml_services": (lambda c: c.get_aml_services(), "/v1/aml-checks", {}),
    "create_aml_check address": (
        lambda c: c.create_aml_check("address", "TRX", ADDRESS),
        "/v1/aml-checks/new",
        {"type": "address", "network": "TRX", "address": ADDRESS},
    ),
    "create_aml_check hash": (
        lambda c: c.create_aml_check("hash", "TRX", ADDRESS, hash="abc123", direction="deposit"),
        "/v1/aml-checks/new",
        {"type": "hash", "network": "TRX", "address": ADDRESS, "hash": "abc123", "direction": "deposit"},
    ),
    "check_aml_status": (
        lambda c: c.check_aml_status("aml-1"),
        "/v1/aml-checks/check",
        {"id": "aml-1"},
    ),
    "get_aml_history": (
        lambda c: c.get_aml_history(),
        "/v1/aml-checks/history",
        {"page": 1, "per_page": 10},
    ),
    "get_aml_history filtered": (
        lambda c: c.get_aml_history(page=3, per_page=50, status="completed"),
        "/v1/aml-checks/history",
        {"page": 3, "per_page": 50, "status": "completed"},
    ),
}


@pytest.mark.parametrize("call, path, expected", CASES.values(), ids=CASES.keys())
def test_request_body(
    client: Client, server: ApiServer, call: Callable[[Client], Any], path: str, expected: Any
) -> None:
    call(client)

    assert len(server.requests) == 1
    assert server.last.method == "POST"
    assert server.last.path == path
    assert server.last.json == expected


@pytest.mark.parametrize("call, path, expected", CASES.values(), ids=CASES.keys())
def test_signature_is_sha256_of_the_body_actually_sent(
    client: Client, server: ApiServer, call: Callable[[Client], Any], path: str, expected: Any
) -> None:
    call(client)

    received = server.last
    assert received.headers["x-signature"] == hashlib.sha256(received.body + API_SECRET.encode()).hexdigest()


def test_signature_covers_non_ascii_body(client: Client, server: ApiServer) -> None:
    client.check_transaction(external_id="pedido-año-订单-😀")

    received = server.last
    assert received.json == {"external_id": "pedido-año-订单-😀"}
    assert received.headers["x-signature"] == hashlib.sha256(received.body + API_SECRET.encode()).hexdigest()


def test_headers(client: Client, server: ApiServer) -> None:
    client.get_balance()

    headers = server.last.headers
    assert headers["authorization"] == f"Bearer {API_TOKEN}"
    assert headers["content-type"] == "application/json"


def test_returns_the_result_field(client: Client, server: ApiServer) -> None:
    server.ok({"balance": "12.5", "address": ADDRESS})

    assert client.get_balance() == {"balance": "12.5", "address": ADDRESS}


def test_returns_list_results(client: Client, server: ApiServer) -> None:
    server.ok([{"id": "address", "price": 1}])

    assert client.get_aml_services() == [{"id": "address", "price": 1}]


def test_base_url_trailing_slash_is_ignored(server: ApiServer) -> None:
    Client(API_TOKEN, API_SECRET, base_url=server.url + "/").get_balance()

    assert server.last.path == "/v1/balance"


def test_default_base_url() -> None:
    assert Client(API_TOKEN, API_SECRET).base_url == "https://api.tronzap.com"


@pytest.mark.parametrize(
    "call, expected_params",
    [
        (
            lambda c: c.calculate(ADDRESS, 65000, 0),
            {"address": ADDRESS, "amount": 65000, "duration": 1},
        ),
        (
            lambda c: c.create_energy_transaction(ADDRESS, 65000, duration=0),
            {"service": "energy", "params": {"address": ADDRESS, "amounts": {"energy": 65000}, "duration": 1}},
        ),
        (
            lambda c: c.get_aml_history(page=0, per_page=0),
            {"page": 1, "per_page": 10},
        ),
    ],
    ids=["calculate duration", "energy duration", "aml history paging"],
)
def test_defaults_are_normalized(
    client: Client, server: ApiServer, call: Callable[[Client], Any], expected_params: Any
) -> None:
    call(client)

    assert server.last.json == expected_params


INVALID_CALLS: Dict[str, Callable[[Client], Any]] = {
    "get_address_info without address": lambda c: c.get_address_info(""),
    "estimate_energy without from": lambda c: c.estimate_energy("", TO_ADDRESS),
    "estimate_energy without to": lambda c: c.estimate_energy(FROM_ADDRESS, ""),
    "calculate without address": lambda c: c.calculate("", 65000),
    "energy without address": lambda c: c.create_energy_transaction("", 65000),
    "bandwidth without address": lambda c: c.create_bandwidth_transaction("", 345),
    "bundle without address": lambda c: c.create_resource_bundle_transaction("", 65000, 345),
    "activation without address": lambda c: c.create_address_activation_transaction(""),
    "check_transaction without ids": lambda c: c.check_transaction(),
    "aml check without type": lambda c: c.create_aml_check("", "TRX", ADDRESS),
    "aml check without network": lambda c: c.create_aml_check("address", "", ADDRESS),
    "aml check without address": lambda c: c.create_aml_check("address", "TRX", ""),
    "aml status without id": lambda c: c.check_aml_status(""),
}


@pytest.mark.parametrize("call", INVALID_CALLS.values(), ids=INVALID_CALLS.keys())
def test_invalid_arguments_are_rejected_before_sending(
    client: Client, server: ApiServer, call: Callable[[Client], Any]
) -> None:
    with pytest.raises(InvalidRequestException):
        call(client)

    assert server.requests == []
