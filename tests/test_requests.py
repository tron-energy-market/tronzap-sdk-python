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
    "create_aml_check hash without direction": (
        lambda c: c.create_aml_check("hash", "TRX", ADDRESS, hash="abc123"),
        "/v1/aml-checks/new",
        {"type": "hash", "network": "TRX", "address": ADDRESS, "hash": "abc123", "direction": "deposit"},
    ),
    "create_aml_check hash with empty direction": (
        lambda c: c.create_aml_check("hash", "TRX", ADDRESS, hash="abc123", direction=""),
        "/v1/aml-checks/new",
        {"type": "hash", "network": "TRX", "address": ADDRESS, "hash": "abc123", "direction": "deposit"},
    ),
    "create_aml_check hash withdrawal": (
        lambda c: c.create_aml_check("hash", "TRX", ADDRESS, hash="abc123", direction="withdrawal"),
        "/v1/aml-checks/new",
        {"type": "hash", "network": "TRX", "address": ADDRESS, "hash": "abc123", "direction": "withdrawal"},
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
    "get_subscriptions": (lambda c: c.get_subscriptions(), "/v1/subscriptions", {}),
    "start_subscription": (
        lambda c: c.start_subscription("unlimited_energy", ADDRESS),
        "/v1/subscription/start",
        {
            "subscription_id": "unlimited_energy",
            "params": {"address": ADDRESS, "duration": 0, "transactions_limit": 0},
        },
    ),
    "start_subscription full": (
        lambda c: c.start_subscription(
            "unlimited_energy",
            ADDRESS,
            duration_days=30,
            transactions_limit=10,
            external_id="sub-1",
            activate_address=True,
        ),
        "/v1/subscription/start",
        {
            "subscription_id": "unlimited_energy",
            "external_id": "sub-1",
            "params": {
                "address": ADDRESS,
                "duration": 30,
                "transactions_limit": 10,
                "activate_address": True,
            },
        },
    ),
    "check_subscription by id": (
        lambda c: c.check_subscription(id="sub-id-1"),
        "/v1/subscription/check",
        {"id": "sub-id-1"},
    ),
    "check_subscription by external_id": (
        lambda c: c.check_subscription(external_id="sub-1"),
        "/v1/subscription/check",
        {"external_id": "sub-1"},
    ),
    "stop_subscription": (
        lambda c: c.stop_subscription(id="sub-id-1", external_id="sub-1"),
        "/v1/subscription/stop",
        {"id": "sub-id-1", "external_id": "sub-1"},
    ),
    "get_subscription_history": (
        lambda c: c.get_subscription_history(),
        "/v1/subscriptions/history",
        {"page": 1, "per_page": 10},
    ),
    "get_subscription_history filtered": (
        lambda c: c.get_subscription_history(page=2, per_page=50, status="active"),
        "/v1/subscriptions/history",
        {"page": 2, "per_page": 50, "status": "active"},
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
        (
            lambda c: c.get_subscription_history(page=0, per_page=-5, status=""),
            {"page": 1, "per_page": 10},
        ),
    ],
    ids=["calculate duration", "energy duration", "aml history paging", "subscription history paging"],
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
    "start_subscription without plan": lambda c: c.start_subscription("", ADDRESS),
    "start_subscription without address": lambda c: c.start_subscription("unlimited_energy", ""),
    "start_subscription negative duration": lambda c: c.start_subscription(
        "unlimited_energy", ADDRESS, duration_days=-1
    ),
    "start_subscription negative limit": lambda c: c.start_subscription(
        "unlimited_energy", ADDRESS, transactions_limit=-1
    ),
    "check_subscription without ids": lambda c: c.check_subscription(),
    "stop_subscription without ids": lambda c: c.stop_subscription(id="", external_id=""),
}


@pytest.mark.parametrize("call", INVALID_CALLS.values(), ids=INVALID_CALLS.keys())
def test_invalid_arguments_are_rejected_before_sending(
    client: Client, server: ApiServer, call: Callable[[Client], Any]
) -> None:
    with pytest.raises(InvalidRequestException):
        call(client)

    assert server.requests == []


SUBSCRIPTION = {
    "id": "01m4e1z3q0r7x225zc6p63m5ey",
    "subscription_id": "unlimited_energy",
    "created_at": "2026-10-08T15:26:32+00:00",
    "expire_at": "2026-11-07T15:26:32+00:00",
    "address": "TAddress",
    "status": "active",
    "external_id": "sub-1",
    "params": {"address": "TAddress", "duration": 30, "transactions_limit": 0, "activate_address": False},
}


def test_get_subscriptions_keeps_the_api_order(client: Client, server: ApiServer) -> None:
    server.respond(
        200,
        '{"code": 0, "result": {'
        '"unlimited_energy": {"id": 8, "name": "Unlimited Energy", "activation_fee": 0, "initial_price": 8,'
        ' "price": 2.8, "transactions_limit": 0, "duration_days": 0},'
        '"energy_pack_100": {"id": 2, "name": "Energy Pack", "activation_fee": "2.0", "initial_price": 8,'
        ' "price": 2.8, "transactions_limit": 10, "duration_days": 5}}}',
    )

    plans = client.get_subscriptions()

    assert list(plans) == ["unlimited_energy", "energy_pack_100"]
    assert plans["unlimited_energy"]["price"] == 2.8
    assert plans["energy_pack_100"]["activation_fee"] == "2.0"
    assert plans["energy_pack_100"]["transactions_limit"] == 10
    assert plans["energy_pack_100"]["duration_days"] == 5


@pytest.mark.parametrize("empty", [{}, []], ids=["object", "array"])
def test_get_subscriptions_returns_an_empty_dict_when_no_plans(client: Client, server: ApiServer, empty: Any) -> None:
    server.ok(empty)

    assert client.get_subscriptions() == {}


@pytest.mark.parametrize(
    "call",
    [
        lambda c: c.start_subscription("unlimited_energy", "TAddress", duration_days=30, external_id="sub-1"),
        lambda c: c.check_subscription(external_id="sub-1"),
    ],
    ids=["start", "check"],
)
def test_subscription_is_returned_as_is(client: Client, server: ApiServer, call: Callable[[Client], Any]) -> None:
    server.ok(SUBSCRIPTION)

    assert call(client) == SUBSCRIPTION


def test_stop_subscription_without_address_or_expiry(client: Client, server: ApiServer) -> None:
    stopped = {key: value for key, value in SUBSCRIPTION.items() if key not in ("address", "expire_at")}
    stopped.update(status="stopped", stopped_at="2026-10-08T15:28:44+00:00")
    server.ok(stopped)

    result = client.stop_subscription(id=str(SUBSCRIPTION["id"]))

    assert result == stopped
    assert "address" not in result
    assert result["params"]["address"] == "TAddress"


def test_get_subscription_history_result(client: Client, server: ApiServer) -> None:
    history = {
        "page": 1,
        "per_page": 10,
        "total": 1,
        "items": [
            {
                "id": "01m4e1z3q0r7x225zc6p63m5ey",
                "status": "active",
                "subscription_id": "unlimited_energy",
                "address": "TAddress",
                "transactions_limit": 0,
                "transactions_used": 4,
                "energy_used": 262000,
                "total_price": "8.00",
                "started_at": "2026-10-08T15:26:33+00:00",
                "renewed_at": "2026-10-08T15:27:35+00:00",
                "stopped_at": None,
                "expire_at": "2026-11-07T15:26:32+00:00",
                "created_at": "2026-10-08T15:26:32+00:00",
            }
        ],
    }
    server.ok(history)

    assert client.get_subscription_history() == history
