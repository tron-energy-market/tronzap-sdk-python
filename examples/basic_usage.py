"""
Walks through the TronZap API operations. By default it only reads and spends nothing.

    export TRONZAP_API_TOKEN=your_api_token
    export TRONZAP_API_SECRET=your_api_secret
    export TRONZAP_BASE_URL=https://api.tronzap.com  # optional, e.g. a dev host
    export TRONZAP_ADDRESS=TRON_ADDRESS              # optional
    export TRONZAP_FROM_ADDRESS=TRON_ADDRESS         # optional, with TO_ADDRESS
    export TRONZAP_TO_ADDRESS=TRON_ADDRESS           # optional, with FROM_ADDRESS
    export TRONZAP_TRANSACTION_ID=id                 # optional
    export TRONZAP_AML_CHECK_ID=id                   # optional
    export TRONZAP_SUBSCRIPTION_ID=id                # optional
    pip install -e .
    python examples/basic_usage.py

Setting TRONZAP_ALLOW_PURCHASES=1 additionally exercises the endpoints that create transactions and AML checks.
Those DEBIT THE ACCOUNT BALANCE. It is meant for verifying an integration against a development environment, and
it also needs TRONZAP_ADDRESS.

Setting TRONZAP_SUBSCRIPTION_PLAN as well, e.g. to unlimited_energy, starts a one-day subscription to that plan for
TRONZAP_ADDRESS and stops it straight away. Starting one charges the plan's initial price.
"""

import os
import sys
import time
from typing import Any, Callable, Dict, List, Optional

from tronzap_sdk import ApiException, Client, ErrorCode, TronZapException

ENERGY = 65000
BANDWIDTH = 345


def env(name: str) -> Optional[str]:
    value = os.environ.get(name, "").strip()
    return value or None


def print_transaction(transaction: Dict[str, Any]) -> None:
    print(
        f"  {transaction.get('id')} {transaction.get('service')} {transaction.get('status')}, "
        f"charged {transaction.get('amount')}, created {transaction.get('created_at')}"
    )


def print_subscription(subscription: Dict[str, Any]) -> None:
    print(
        f"  {subscription.get('id')} {subscription.get('subscription_id')} {subscription.get('status')}, "
        f"address {subscription.get('address')}, created {subscription.get('created_at')}, "
        f"expires {subscription.get('expire_at')}"
    )


def main() -> int:
    token = env("TRONZAP_API_TOKEN")
    secret = env("TRONZAP_API_SECRET")
    if not token or not secret:
        sys.exit("set TRONZAP_API_TOKEN and TRONZAP_API_SECRET")

    base_url = env("TRONZAP_BASE_URL")
    if base_url:
        client = Client(token, secret, base_url=base_url, timeout=20)
    else:
        client = Client(token, secret, timeout=20)
    print(f"Calling {client.base_url}")

    failed: List[str] = []

    def step(name: str, call: Callable[[], None]) -> None:
        print(f"\n{name}")
        try:
            call()
        except TronZapException as e:
            print(f"  FAILED: {type(e).__name__}: {e}")
            failed.append(name)

    def optional_step(name: str, subject: Optional[str], call: Callable[[str], None]) -> None:
        if subject is None:
            print(f"\n{name}\n  skipped: its environment variable is not set")
            return
        step(name, lambda: call(subject))

    def get_balance() -> None:
        balance = client.get_balance()
        print(f"  balance {balance.get('balance')}, deposit address {balance.get('address')}")

    def get_services() -> None:
        services = client.get_services()
        for rate in services.get("energy") or []:
            print(
                f"  energy {rate.get('duration')}h {rate.get('min_amount')}..{rate.get('max_amount')} "
                f"at {rate.get('price')} per 1000 units (65k = {rate.get('price_65k')})"
            )
        for rate in services.get("bandwidth") or []:
            print(
                f"  bandwidth {rate.get('duration')}h {rate.get('min_amount')}..{rate.get('max_amount')} "
                f"at {rate.get('price')} per 1000 units"
            )
        activation = services.get("activate_address")
        if activation:
            print(f"  activation {activation.get('price')}")

    def get_direct_recharge_info() -> None:
        info = client.get_direct_recharge_info()
        print(f"  pay to {info.get('address')}, {len(info.get('rates') or [])} rate(s)")

    def get_aml_services() -> None:
        for service in client.get_aml_services():
            print(f"  {service.get('id')} {service.get('type')} at {service.get('price')}")

    def get_aml_history() -> None:
        history = client.get_aml_history()
        items = history.get("items") or []
        print(f"  page {history.get('page')}, {len(items)} of {history.get('total')} check(s)")

    def get_subscriptions() -> None:
        plans = client.get_subscriptions()
        for subscription_id, plan in plans.items():
            print(
                f"  {subscription_id} ({plan.get('name')}): activation {plan.get('activation_fee')}, "
                f"initial {plan.get('initial_price')}, {plan.get('price')} per transaction, "
                f"limit {plan.get('transactions_limit')} transactions, {plan.get('duration_days')} days"
            )

    def get_subscription_history() -> None:
        history = client.get_subscription_history(per_page=3)
        items = history.get("items") or []
        print(f"  page {history.get('page')}, {len(items)} of {history.get('total')} subscription(s)")
        for item in items:
            print(
                f"  {item.get('id')} {item.get('subscription_id')} {item.get('status')}, "
                f"used {item.get('transactions_used')} transactions and {item.get('energy_used')} energy, "
                f"charged {item.get('total_price')}, expires {item.get('expire_at')}"
            )

    step("get_balance", get_balance)
    step("get_services", get_services)
    step("get_direct_recharge_info", get_direct_recharge_info)
    step("get_aml_services", get_aml_services)
    step("get_aml_history", get_aml_history)
    step("get_subscriptions", get_subscriptions)
    step("get_subscription_history", get_subscription_history)

    address = env("TRONZAP_ADDRESS")

    def get_address_info(value: str) -> None:
        info = client.get_address_info(value)
        resources = info.get("resources") or {}
        balances = ", ".join(f"{symbol} {amount}" for symbol, amount in (info.get("balances") or {}).items())
        print(
            f"  energy {resources.get('energy')}, bandwidth {resources.get('bandwidth')}, balances {balances}"
        )

    def calculate(value: str) -> None:
        calculation = client.calculate(value, energy=ENERGY)
        print(
            f"  {calculation.get('amount')} energy for {calculation.get('duration')}h "
            f"costs {calculation.get('total')}"
        )

    optional_step("get_address_info", address, get_address_info)
    optional_step("calculate", address, calculate)

    from_address = env("TRONZAP_FROM_ADDRESS")
    to_address = env("TRONZAP_TO_ADDRESS")

    def estimate_energy(value: str) -> None:
        estimate = client.estimate_energy(value, to_address or "")
        print(f"  {estimate.get('amount')} energy, total {estimate.get('total')}")

    optional_step("estimate_energy", from_address if to_address else None, estimate_energy)

    def check_aml_status(value: str) -> None:
        check = client.check_aml_status(value)
        risk = check.get("risk_score")
        print(f"  {check.get('status')}, risk {risk if risk is not None else 'not scored yet'}")

    optional_step(
        "check_transaction",
        env("TRONZAP_TRANSACTION_ID"),
        lambda value: print_transaction(client.check_transaction(id=value)),
    )
    optional_step("check_aml_status", env("TRONZAP_AML_CHECK_ID"), check_aml_status)
    optional_step(
        "check_subscription",
        env("TRONZAP_SUBSCRIPTION_ID"),
        lambda value: print_subscription(client.check_subscription(id=value)),
    )

    if env("TRONZAP_ALLOW_PURCHASES") != "1":
        print("\nSkipping purchases: set TRONZAP_ALLOW_PURCHASES=1 to create transactions (debits the balance)")
    elif address is None:
        print("\nSkipping purchases: TRONZAP_ADDRESS is not set")
    else:
        run_id = f"python-example-{int(time.time() * 1000)}"
        buyer = address

        def activate() -> None:
            try:
                print_transaction(
                    client.create_address_activation_transaction(buyer, external_id=f"{run_id}-activate")
                )
            except ApiException as e:
                if e.code != ErrorCode.ADDRESS_ALREADY_ACTIVATED:
                    raise
                print("  already activated")

        def buy_energy() -> None:
            print_transaction(
                client.create_energy_transaction(buyer, ENERGY, external_id=f"{run_id}-energy")
            )
            print_transaction(client.check_transaction(external_id=f"{run_id}-energy"))

        def buy_bandwidth() -> None:
            print_transaction(
                client.create_bandwidth_transaction(buyer, BANDWIDTH, external_id=f"{run_id}-bandwidth")
            )

        def buy_bundle() -> None:
            print_transaction(
                client.create_resource_bundle_transaction(
                    buyer, ENERGY, BANDWIDTH, external_id=f"{run_id}-bundle"
                )
            )

        def create_aml_check() -> None:
            check = client.create_aml_check("address", "TRX", buyer)
            print(f"  AML check {check.get('id')} is {check.get('status')}")

        step("create_address_activation_transaction", activate)
        step("create_energy_transaction", buy_energy)
        step("create_bandwidth_transaction", buy_bandwidth)
        step("create_resource_bundle_transaction", buy_bundle)
        step("create_aml_check", create_aml_check)

        plan = env("TRONZAP_SUBSCRIPTION_PLAN")

        def try_subscription(value: str) -> None:
            subscription = client.start_subscription(
                value, buyer, duration_days=1, external_id=f"{run_id}-subscription"
            )
            print_subscription(subscription)
            try:
                print_subscription(client.check_subscription(id=subscription["id"]))
            finally:
                stopped = client.stop_subscription(id=subscription["id"])
                print(f"  stopped: {stopped.get('status')} at {stopped.get('stopped_at')}")

        optional_step("start_subscription, check_subscription, stop_subscription", plan, try_subscription)

    if failed:
        print(f"\nFailed: {', '.join(failed)}", file=sys.stderr)
        return 1
    print("\nAll calls succeeded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
