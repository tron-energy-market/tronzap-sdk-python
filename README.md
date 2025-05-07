# TronZap SDK for Python

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
    api_secret="your_api_secret"
)

# Get available services
services = client.get_services()
print(services)

# Get account balance
balance = client.get_balance()
print(balance)

# Estimate energy cost for USDT transfer
estimate = client.estimate_energy('FROM_TRX_ADDRESS', 'TO_TRX_ADDRESS', 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t')
print(estimate)

# Calculate energy cost
calculation = client.calculate(
    address="TRON_WALLET_ADDRESS",
    energy=65150  # Recommended amount for USDT transfers
)
print(calculation)

# Create energy transaction
transaction = client.create_energy_transaction(
    address="TRON_WALLET_ADDRESS",
    energy_amount=65150, # From 60000
    duration=1, # Possible values 1 or 24 hours
    activate_address=True  # If the address needs activation
)
print(transaction)

# Check transaction status
status = client.check_transaction(id="TRANSACTION_ID")
print(status)

# Get direct recharge information
recharge_info = client.get_direct_recharge_info()
print(recharge_info)
```

## Features

- Get available services
- Get account balance
- Calculate energy cost
- Create address activation transactions
- Create energy purchase transactions
- Check transaction status
- Get direct recharge information

## Requirements

- Python 3.7 or higher
- requests >= 2.25.0

## Error Handling

The SDK raises `TronZapException` when the API returns an error. Each exception includes a `.code` and a `.message` property for debugging and handling specific cases.

### Example

```python
from tronzap_sdk import Client, TronZapException, ErrorCode

client = Client(api_token="your_api_token", api_secret="your_api_secret")

try:
    balance = client.get_balance()
except TronZapException as e:
    if e.code == ErrorCode.AUTH_ERROR:
        print("Authentication error")
    elif e.code == ErrorCode.INVALID_SERVICE_OR_PARAMS:
        print("Invalid service or parameters")
    elif e.code == ErrorCode.WALLET_NOT_FOUND:
        print("Internal wallet not found. Contact support.")
    elif e.code == ErrorCode.INSUFFICIENT_FUNDS:
        print("Insufficient funds")
    elif e.code == ErrorCode.INVALID_TRON_ADDRESS:
        print("Invalid TRON address")
    elif e.code == ErrorCode.INVALID_ENERGY_AMOUNT:
        print("Invalid energy amount")
    elif e.code == ErrorCode.INVALID_DURATION:
        print("Invalid duration")
    elif e.code == ErrorCode.TRANSACTION_NOT_FOUND:
        print("Transaction not found")
    elif e.code == ErrorCode.ADDRESS_NOT_ACTIVATED:
        print("Address not activated")
    elif e.code == ErrorCode.ADDRESS_ALREADY_ACTIVATED:
        print("Address already activated")
    elif e.code == ErrorCode.INTERNAL_SERVER_ERROR:
        print("Internal server error")
    else:
        print(f"Unhandled error {e.code}: {e.message}")
```

### Error Codes

| Code | Constant                        | Description |
|------|----------------------------------|-------------|
| 1    | `AUTH_ERROR`                    | Authentication error – Invalid API token or signature |
| 2    | `INVALID_SERVICE_OR_PARAMS`    | Invalid service or parameters |
| 5    | `WALLET_NOT_FOUND`             | Internal wallet not found. Contact support. |
| 6    | `INSUFFICIENT_FUNDS`           | Insufficient funds |
| 10   | `INVALID_TRON_ADDRESS`         | Invalid TRON address |
| 11   | `INVALID_ENERGY_AMOUNT`        | Invalid energy amount |
| 12   | `INVALID_DURATION`             | Invalid duration |
| 20   | `TRANSACTION_NOT_FOUND`        | Transaction not found |
| 24   | `ADDRESS_NOT_ACTIVATED`        | Address not activated |
| 25   | `ADDRESS_ALREADY_ACTIVATED`    | Address already activated |
| 500  | `INTERNAL_SERVER_ERROR`        | Internal server error – Contact support |


## Support

For support, please contact us on Telegram: [@tronzap_bot](https://t.me/tronzap_bot)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.