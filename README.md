# Tron Energy Rental via API
## Python SDK by TronZap.com

**[English](https://github.com/tron-energy-market/tronzap-sdk-python/blob/main/README.md)** | [Español](https://github.com/tron-energy-market/tronzap-sdk-python/blob/main/README.es.md) | [Português](https://github.com/tron-energy-market/tronzap-sdk-python/blob/main/README.pt-br.md) | [Русский](https://github.com/tron-energy-market/tronzap-sdk-python/blob/main/README.ru.md)

Official Python SDK for the TronZap API.
This SDK allows you to easily integrate with TronZap services for TRON energy rental.

TronZap.com allows you to [buy TRON energy](https://tronzap.com/), making USDT (TRC20) transfers cheaper by significantly reducing transaction fees.

👉 [Register for an API key](https://tronzap.com) to start using TronZap API and integrate it via the SDK.

## Installation

```bash
pip install tronzap-sdk
```

Check out at PyPI: https://pypi.org/project/tronzap-sdk/

## Quick Start

```python
from tronzap_sdk import Client

# Initialize the client
client = Client(
    api_token="your_api_token",
    api_secret="your_api_secret",
    timeout=30,  # Seconds, optional; 30 by default
)

# Get available services
services = client.get_services()
print(services)

# Get account balance
balance = client.get_balance()
print(balance)

# Get address info (resources and balances)
address_info = client.get_address_info("TRX_ADDRESS")
print(address_info)

# Estimate energy cost for USDT transfer
estimate = client.estimate_energy('FROM_TRX_ADDRESS', 'TO_TRX_ADDRESS')
print(estimate)

# Calculate energy cost
calculation = client.calculate(
    address="TRON_WALLET_ADDRESS",
    energy=65000  # Recommended amount for USDT transfers
)
print(calculation)

# Create energy transaction
transaction = client.create_energy_transaction(
    address="TRON_WALLET_ADDRESS",
    energy_amount=65000,
    duration=1,  # Hours: one of the durations get_services() lists
    activate_address=True  # If the address needs activation
)
print(transaction)

# Buy bandwidth
bandwidth = client.create_bandwidth_transaction(
    address="TRON_WALLET_ADDRESS",
    amount=345,
    external_id="bandwidth-1"
)
print(bandwidth)

# Buy a resource bundle (energy + bandwidth in one transaction)
bundle = client.create_resource_bundle_transaction(
    address="TRON_WALLET_ADDRESS",
    energy_amount=65000,
    bandwidth_amount=345,
    duration=1,
    external_id="bundle-1",
    activate_address=True
)
print(bundle)

# Check transaction status
status = client.check_transaction(id="TRANSACTION_ID")
print(status)

# Create AML check
aml_check = client.create_aml_check(
    type="address",
    network="TRX",
    address="TXYZ1234567890EXAMPLEADDRESS"
)
print(aml_check)

# Check AML status
aml_status = client.check_aml_status(id=aml_check["id"])
print(aml_status)

# Get direct recharge information
recharge_info = client.get_direct_recharge_info()
print(recharge_info)
```

## Features

- Get available services
- Get AML services
- Get account balance
- Get address info (resources and balances)
- Calculate energy cost
- Create address activation transactions
- Create energy purchase transactions
- Create bandwidth purchase transactions
- Create resource bundle transactions (energy + bandwidth in one purchase)
- Create and track AML checks
- Start, check, stop and list subscriptions
- Check transaction status
- Get direct recharge information

## Requirements

- Python 3.9 or higher
- requests >= 2.25.0

## Subscriptions

A subscription keeps an address supplied with energy for every transaction until it is stopped or runs out of days
or transactions. `get_subscriptions()` returns the plans keyed by their subscription ID; pass that key, such as
`"unlimited_energy"`, to `start_subscription`, not the plan's numeric `id`. Starting a subscription charges the
plan's initial price.

```python
plans = client.get_subscriptions()
for subscription_id, plan in plans.items():
    print(subscription_id, plan["initial_price"], plan["price"])

subscription = client.start_subscription(
    subscription_id="unlimited_energy",
    address="TRON_WALLET_ADDRESS",
    duration_days=30,  # 0 for no time limit
    transactions_limit=0,  # 0 for no limit
    external_id="subscription-42"
)

subscription = client.check_subscription(external_id="subscription-42")

stopped = client.stop_subscription(id=subscription["id"])

history = client.get_subscription_history(page=1, per_page=10, status="active")
```

`duration_days` and `transactions_limit` default to 0, which means no limit. Start, check and stop return the
subscription with its `params`; the history items carry the usage counters `transactions_used`, `energy_used` and
`total_price` instead. A subscription with a transactions limit cannot be stopped (`CANNOT_STOP_SUBSCRIPTION`).

## Error Handling

The SDK uses a hierarchy of exceptions for precise error handling:

```
TronZapException
├── ApiException             — API-level errors (response code != 0)
├── InvalidRequestException  — Invalid arguments, rejected before sending (also a ValueError)
├── NetworkException         — Network/connectivity errors
│   ├── ConnectionException  — Could not connect to server
│   ├── TimeoutException     — Request timed out
│   └── SslException         — SSL/TLS errors
└── HttpException            — HTTP non-2xx responses
    ├── RateLimitException   — HTTP 429 Too Many Requests
    ├── UnauthorizedException — HTTP 401/403
    └── ServerException      — HTTP 5xx errors
```

### Example

```python
from tronzap_sdk import Client
from tronzap_sdk.exceptions import (
    ApiException,
    ConnectionException,
    HttpException,
    NetworkException,
    RateLimitException,
    ServerException,
    SslException,
    TimeoutException,
    TronZapException,
    UnauthorizedException,
    InvalidRequestException,
    ErrorCode,
)

client = Client(api_token="your_api_token", api_secret="your_api_secret")

try:
    transaction = client.create_energy_transaction("TRX_ADDRESS", 65000, 1)
except ApiException as e:
    # API-level error (invalid params, insufficient funds, etc.)
    print(f"API error [{e.code}]: {e.message}")

    # Error key alias, e.g. "invalid_tron_address" or "invalid_tron_address.from_address"
    if e.error_key:
        print(f"Error key: {e.error_key}")

    # Quote it when contacting support
    print(f"Request ID: {e.request_id}")

    if e.code == ErrorCode.INVALID_TRON_ADDRESS:
        print("Check the TRON address format.")
except InvalidRequestException as e:
    print(f"Invalid arguments: {e.message}")
except RateLimitException:
    print("Too many requests, please slow down.")
except UnauthorizedException:
    print("Invalid API token or signature.")
except ServerException as e:
    print(f"TronZap server error [{e.status_code}].")
except HttpException as e:
    print(f"HTTP error [{e.status_code}]: {e.message}")
except TimeoutException:
    print("Request timed out.")
except SslException as e:
    print(f"SSL error: {e.message}")
except ConnectionException as e:
    print(f"Connection failed: {e.message}")
except NetworkException as e:
    print(f"Network error: {e.message}")
except TronZapException as e:
    print(f"Error [{e.code}]: {e.message}")
```

### API Error Codes

| Code | Constant                        | Description |
|------|----------------------------------|-------------|
| 1    | `AUTH_ERROR`                    | Authentication error – Invalid API token or signature |
| 2    | `INVALID_SERVICE_OR_PARAMS`    | Invalid service or parameters |
| 5    | `WALLET_NOT_FOUND`             | Internal wallet not found. Contact support. |
| 6    | `INSUFFICIENT_FUNDS`           | Insufficient funds |
| 10   | `INVALID_TRON_ADDRESS`         | Invalid TRON address, or the address already has an active subscription |
| 11   | `INVALID_ENERGY_AMOUNT`        | Invalid energy amount |
| 12   | `INVALID_DURATION`             | Invalid duration |
| 20   | `TRANSACTION_NOT_FOUND`        | Transaction/subscription not found |
| 21   | `CANNOT_STOP_SUBSCRIPTION`     | Cannot stop subscription, e.g. it has a transactions limit |
| 24   | `ADDRESS_NOT_ACTIVATED`        | Address not activated |
| 25   | `ADDRESS_ALREADY_ACTIVATED`    | Address already activated |
| 30   | `AML_CHECK_NOT_FOUND`          | AML check not found |
| 35   | `SERVICE_NOT_AVAILABLE`        | Service not available |
| 50   | `INVALID_BANDWIDTH_AMOUNT`     | Invalid bandwidth amount |
| 500  | `INTERNAL_SERVER_ERROR`        | Internal server error – Contact support |


## Development

```bash
pip install -r requirements-dev.txt -e .
pytest
```

The tests run against a local HTTP/TLS server and never call the real API. `examples/basic_usage.py` is a smoke test against a real environment; the instructions are at the top of the file.

## Support

For support, please contact us on Telegram: [@tronzap_bot](https://t.me/tronzap_bot)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
