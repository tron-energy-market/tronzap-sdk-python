# Changelog

All notable changes to this project are documented in this file. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- `examples/basic_usage.py` reads the API's `amount`, `min_amount` and `max_amount` fields instead of the deprecated
  `energy`, `min_energy` and `max_energy`.

### Fixed

- `examples/basic_usage.py` labels the energy `price` of `get_services()` as per 1000 units, not per unit. Energy and
  bandwidth are both priced per 1000 units: the cost is `price × amount / 1000`.

## [1.5.0] - 2026-10-07

Versions 1.1.0 to 1.4.0 were tagged on GitHub but never published to PyPI, so this is the first release on PyPI
since 1.0.7 and brings everything below to `pip install tronzap-sdk`.

### Added

- `timeout` argument of `Client`, 30 seconds by default. Requests used to wait for the API indefinitely.
- `InvalidRequestException`, raised before any request is sent when a required argument is empty, such as an
  address, both `id` and `external_id` of `check_transaction`, or the type, network or address of an AML check. It
  subclasses both `TronZapException` and `ValueError`.
- `request_id` and `status_code` on `ApiException`.
- Type information for type checkers (`py.typed`).

### Changed

- Python 3.9 or newer is required. The package claimed Python 3 but has needed 3.6 or newer since its first release.
- `calculate` sends the energy amount as the API's `amount` field instead of the deprecated `energy` field. The
  Python argument is still called `energy`.
- `estimate_energy` leaves `contract_address` out of the request when it is empty, so the API estimates a USDT
  (TRC20) transfer, instead of sending an empty string.
- A `duration`, `page` or `per_page` below 1 is sent as 1, 1 and 10.
- `get_aml_services` is annotated as returning a list, which it always did.

### Fixed

- The package now declares its dependency on `requests`. 1.0.7 on PyPI did not, so installing it into an
  environment without `requests` failed on import.
- A response that is valid JSON but not an object, such as `[]` or `"text"`, raised `AttributeError`. It now raises
  `ApiException` with code 1.
- A successful response with `"result": null` returned `None`. It now raises `ServerException`.

## [1.4.0] - 2026-05-05

### Added

- `create_resource_bundle_transaction` buys energy and bandwidth in one transaction.
- Error codes `SERVICE_NOT_AVAILABLE` (35) and `INVALID_BANDWIDTH_AMOUNT` (50).

## [1.3.0] - 2026-03-31

### Added

- `get_address_info` returns the resources and balances of an address.

## [1.2.1] - 2026-03-04

### Fixed

- API errors in responses with a non-2xx HTTP status are raised as `ApiException` instead of an HTTP exception.

## [1.2.0] - 2026-03-02

### Added

- `ApiException.error_key` with the machine-readable error alias.
- A typed exception hierarchy for network, TLS, timeout, rate limit, authorization and server errors.

## [1.1.0] - 2025-12-11

### Added

- AML checks: `get_aml_services`, `create_aml_check`, `check_aml_status` and `get_aml_history`.
- `create_bandwidth_transaction`.
