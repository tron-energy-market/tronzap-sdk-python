"""
TronZap SDK Client

This module provides a Python client for interacting with the TronZap API to purchase TRX energy for low-cost USDT transfers.
"""

import hashlib
import json
from typing import Any, Dict, List, Optional

import requests

from .exceptions import (
    ApiException,
    ConnectionException,
    HttpException,
    InvalidRequestException,
    NetworkException,
    RateLimitException,
    ServerException,
    SslException,
    TimeoutException,
    UnauthorizedException,
)

DEFAULT_TIMEOUT = 30.0

_NOT_JSON = object()


def _require(value: Optional[str], name: str) -> None:
    if not value:
        raise InvalidRequestException(f"{name} is required")


def _at_least_one(value: int, default: int) -> int:
    return value if value >= 1 else default


class Client:
    """
    TronZap API Client

    This client provides methods to interact with the TronZap API for TRON energy leasing.
    """

    def __init__(
        self,
        api_token: str,
        api_secret: str,
        base_url: str = "https://api.tronzap.com",
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the TronZap client.

        Args:
            api_token (str): Your API token
            api_secret (str): Your API secret for signature generation
            base_url (str, optional): Base API URL. Defaults to "https://api.tronzap.com"
            timeout (float, optional): Seconds to wait for the API to connect and to answer. Defaults to 30.
        """
        self.api_token = api_token
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, Any]
    ) -> Any:
        """
        Make an API request to TronZap.

        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            params (Dict[str, Any]): Request parameters

        Returns:
            Dict[str, Any]: API response

        Raises:
            TronZapException: If the API request fails
        """
        request_body = json.dumps(params)
        signature = hashlib.sha256(
            (request_body + self.api_secret).encode()
        ).hexdigest()

        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'X-Signature': signature,
            'Content-Type': 'application/json',
        }

        # 1. Network-level errors
        # SSLError must come before ConnectionError (it's a subclass of it).
        # Timeout must come before ConnectionError (ConnectTimeout is a subclass of both).
        try:
            response = requests.post(
                url=f"{self.base_url}{endpoint}",
                data=request_body,
                headers=headers,
                verify=True,
                timeout=self.timeout,
            )
        except requests.exceptions.SSLError as e:
            raise SslException(str(e), original_error=e) from e
        except requests.exceptions.Timeout as e:
            raise TimeoutException(str(e), original_error=e) from e
        except requests.exceptions.ConnectionError as e:
            raise ConnectionException(str(e), original_error=e) from e
        except requests.exceptions.RequestException as e:
            raise NetworkException(str(e), original_error=e) from e

        # 2. Try to parse JSON
        response_data: Any = _NOT_JSON
        try:
            response_data = response.json()
        except ValueError:
            pass

        # 3. API-level errors (valid JSON + code !== 0, regardless of HTTP status)
        if response_data is not _NOT_JSON:
            if not isinstance(response_data, dict):
                raise ApiException('Unknown API error', code=1, status_code=response.status_code)
            if response_data.get('code') != 0:
                code = response_data.get('code')
                raise ApiException(
                    response_data.get('error') or 'Unknown API error',
                    code=1 if code is None else code,
                    error_key=response_data.get('key'),
                    request_id=response_data.get('request_id'),
                    status_code=response.status_code,
                )

        # 4. HTTP-level errors (non-2xx: invalid JSON or valid JSON with code=0)
        if not response.ok:
            body = response.text
            if response.status_code == 429:
                raise RateLimitException(response_body=body)
            if response.status_code in (401, 403):
                raise UnauthorizedException(response.status_code, 'Unauthorized', body)
            if response.status_code >= 500:
                raise ServerException(response.status_code, 'Server error', body)
            raise HttpException(response.status_code, f'HTTP error {response.status_code}', body)

        # 5. HTTP 2xx but invalid JSON
        if response_data is _NOT_JSON:
            raise ServerException(response.status_code, 'Invalid JSON response', response.text)

        # 6. Missing result key in a successful response
        if response_data.get('result') is None:
            raise ServerException(response.status_code, 'Missing result in response', response.text)

        return response_data['result']

    def get_services(self) -> Dict[str, Any]:
        """
        Get available services.

        Returns:
            Dict[str, Any]: Services data
        """
        return self._request('POST', '/v1/services', {})

    def get_aml_services(self) -> List[Dict[str, Any]]:
        """
        Get available AML services.

        Returns:
            List[Dict[str, Any]]: AML services data
        """
        return self._request('POST', '/v1/aml-checks', {})

    def get_balance(self) -> Dict[str, Any]:
        """
        Get account balance.

        Returns:
            Dict[str, Any]: Balance data
        """
        return self._request('POST', '/v1/balance', {})

    def get_address_info(self, address: str) -> Dict[str, Any]:
        """
        Get address info (resources and balances).

        Args:
            address (str): TRON address to query

        Returns:
            Dict[str, Any]: Address resources (energy, bandwidth) and balances (TRX, USDT)
        """
        _require(address, 'address')
        return self._request('POST', '/v1/address-info', {
            'address': address
        })

    def estimate_energy(
        self,
        from_address: str,
        to_address: str,
        contract_address: str = ''
    ) -> Dict[str, Any]:
        """
        Estimate energy cost for a TRON transaction.

        Args:
            from_address (str): TRON wallet address of the sender
            to_address (str): TRON wallet address of the recipient
            contract_address (str, optional): TRON contract address. Leave empty to estimate a USDT (TRC20) transfer.

        Returns:
            Dict[str, Any]: Energy estimate result
        """
        _require(from_address, 'from_address')
        _require(to_address, 'to_address')
        params: Dict[str, Any] = {
            'from_address': from_address,
            'to_address': to_address,
        }
        if contract_address:
            params['contract_address'] = contract_address
        return self._request('POST', '/v1/estimate-energy', params)

    def calculate(
        self,
        address: str,
        energy: int,
        duration: int = 1
    ) -> Dict[str, Any]:
        """
        Calculate cost for energy purchase.

        Args:
            address (str): TRON wallet address
            energy (int): Amount of energy to purchase
            duration (int, optional): Duration in hours. Defaults to 1.

        Returns:
            Dict[str, Any]: Calculation result
        """
        _require(address, 'address')
        return self._request('POST', '/v1/calculate', {
            'address': address,
            'amount': energy,
            'duration': _at_least_one(duration, 1)
        })

    def create_energy_transaction(
        self,
        address: str,
        energy_amount: int,
        duration: int = 1,
        external_id: Optional[str] = None,
        activate_address: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new transaction for energy purchase.

        Args:
            address (str): TRON wallet address
            energy_amount (int): Amount of energy to purchase
            duration (int, optional): Duration in hours. Defaults to 1.
            external_id (Optional[str], optional): External transaction ID.
            activate_address (bool, optional): Whether to activate the address.

        Returns:
            Dict[str, Any]: Transaction data
        """
        _require(address, 'address')
        params: Dict[str, Any] = {
            'service': 'energy',
            'params': {
                'address': address,
                'amounts': {
                    'energy': energy_amount
                },
                'duration': _at_least_one(duration, 1)
            }
        }

        if activate_address:
            params['params']['activate_address'] = True

        if external_id:
            params['external_id'] = external_id

        return self._request('POST', '/v1/transaction/new', params)

    def create_bandwidth_transaction(
        self,
        address: str,
        amount: int,
        external_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new transaction for bandwidth purchase.

        Args:
            address (str): TRON wallet address
            amount (int): Amount of bandwidth to purchase
            external_id (Optional[str], optional): External transaction ID.

        Returns:
            Dict[str, Any]: Transaction data
        """
        _require(address, 'address')
        params: Dict[str, Any] = {
            'service': 'bandwidth',
            'params': {
                'address': address,
                'amounts': {
                    'bandwidth': amount
                },
                'duration': 1
            }
        }

        if external_id:
            params['external_id'] = external_id

        return self._request('POST', '/v1/transaction/new', params)

    def create_resource_bundle_transaction(
        self,
        address: str,
        energy_amount: int,
        bandwidth_amount: int,
        duration: int = 1,
        external_id: Optional[str] = None,
        activate_address: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new transaction for a resource bundle (energy + bandwidth in one purchase).

        Args:
            address (str): TRON wallet address
            energy_amount (int): Amount of energy to purchase
            bandwidth_amount (int): Amount of bandwidth to purchase
            duration (int, optional): Duration in hours. Defaults to 1.
            external_id (Optional[str], optional): External transaction ID.
            activate_address (bool, optional): Whether to activate the address.

        Returns:
            Dict[str, Any]: Transaction data
        """
        _require(address, 'address')
        params: Dict[str, Any] = {
            'service': 'resource_bundle',
            'params': {
                'address': address,
                'amounts': {
                    'energy': energy_amount,
                    'bandwidth': bandwidth_amount
                },
                'duration': _at_least_one(duration, 1)
            }
        }

        if activate_address:
            params['params']['activate_address'] = True

        if external_id:
            params['external_id'] = external_id

        return self._request('POST', '/v1/transaction/new', params)

    def create_address_activation_transaction(
        self,
        address: str,
        external_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new transaction for address activation.

        Args:
            address (str): TRON wallet address
            external_id (Optional[str], optional): External transaction ID.

        Returns:
            Dict[str, Any]: Transaction data
        """
        _require(address, 'address')
        params: Dict[str, Any] = {
            'service': 'activate_address',
            'params': {
                'address': address
            }
        }

        if external_id:
            params['external_id'] = external_id

        return self._request('POST', '/v1/transaction/new', params)

    def create_aml_check(
        self,
        type: str,
        network: str,
        address: str,
        hash: Optional[str] = None,
        direction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new AML check.

        Args:
            type (str): AML service type: address or hash
            network (str): Network code (e.g. TRX, BTC, ETH)
            address (str): Wallet address
            hash (Optional[str]): Transaction hash (for type=hash)
            direction (Optional[str]): Direction for hash checks (deposit or withdrawal)

        Returns:
            Dict[str, Any]: AML check data
        """
        _require(type, 'type')
        _require(network, 'network')
        _require(address, 'address')
        params: Dict[str, Any] = {
            'type': type,
            'network': network,
            'address': address
        }

        if hash is not None:
            params['hash'] = hash

        if direction is not None:
            params['direction'] = direction

        return self._request('POST', '/v1/aml-checks/new', params)

    def check_aml_status(self, id: str) -> Dict[str, Any]:
        """
        Check AML status.

        Args:
            id (str): AML check ID

        Returns:
            Dict[str, Any]: AML status data
        """
        _require(id, 'id')
        return self._request('POST', '/v1/aml-checks/check', {'id': id})

    def get_aml_history(
        self,
        page: int = 1,
        per_page: int = 10,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get AML history.

        Args:
            page (int, optional): Page number. Defaults to 1.
            per_page (int, optional): Items per page. Defaults to 10.
            status (Optional[str], optional): Filter by status.

        Returns:
            Dict[str, Any]: AML history data
        """
        params: Dict[str, Any] = {
            'page': _at_least_one(page, 1),
            'per_page': _at_least_one(per_page, 10)
        }

        if status is not None:
            params['status'] = status

        return self._request('POST', '/v1/aml-checks/history', params)

    def check_transaction(
        self,
        id: Optional[str] = None,
        external_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check transaction status.

        Args:
            id (Optional[str], optional): Internal transaction ID
            external_id (Optional[str], optional): External transaction ID.
            Note: Either id or external_id must be provided.

        Returns:
            Dict[str, Any]: Transaction status data
        """
        if not id and not external_id:
            raise InvalidRequestException('either id or external_id is required')
        params: Dict[str, Any] = {}
        if id:
            params['id'] = id
        if external_id:
            params['external_id'] = external_id

        return self._request('POST', '/v1/transaction/check', params)

    def get_direct_recharge_info(self) -> Dict[str, Any]:
        """
        Get direct recharge information.

        Returns:
            Dict[str, Any]: Direct recharge information
        """
        return self._request('POST', '/v1/direct-recharge-info', {})
