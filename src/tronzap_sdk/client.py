"""
TronZap SDK Client

This module provides a Python client for interacting with the TronZap API to purchase TRX energy for low-cost USDT transfers.
"""

import json
import hashlib
import requests
from typing import Dict, Optional, Union, Any
from enum import IntEnum

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

    # Invalid TRON address - Check the TRON address format. It should be a valid 34-character TRON address.
    INVALID_TRON_ADDRESS = 10

    # Invalid energy amount - Ensure the requested energy amount is valid.
    INVALID_ENERGY_AMOUNT = 11

    # Invalid duration - Check that the duration parameter is valid.
    INVALID_DURATION = 12

    # Transaction not found - Verify the transaction ID or external ID is correct.
    TRANSACTION_NOT_FOUND = 20

    # Address not activated - Activate the address first by making an address activation transaction.
    ADDRESS_NOT_ACTIVATED = 24

    # Address already activated - The address is already activated. No action needed.
    ADDRESS_ALREADY_ACTIVATED = 25

class TronZapException(Exception):
    """Base exception for TronZap SDK errors."""
    def __init__(self, message: str, code: int = 1):
        self.message = message
        self.code = code
        super().__init__(f"TronZap API Error {code}: {message}")

class Client:
    """
    TronZap API Client

    This client provides methods to interact with the TronZap API for TRON energy leasing.
    """

    def __init__(
        self,
        api_token: str,
        api_secret: str,
        base_url: str = "https://api.tronzap.com"
    ):
        """
        Initialize the TronZap client.

        Args:
            api_token (str): Your API token
            api_secret (str): Your API secret for signature generation
            base_url (str, optional): Base API URL. Defaults to "https://api.tronzap.com"
        """
        self.api_token = api_token
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/')

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
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
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                data=request_body,
                headers=headers,
                verify=True
            )

            try:
                response_data = response.json()
            except ValueError:
                raise TronZapException("Invalid JSON in response", code=500)

            if response_data.get('code') != 0:
                raise TronZapException(
                    response_data.get('error', 'Unknown API error'),
                    response_data.get('code', 1)
                )

            return response_data['result']

        except requests.exceptions.RequestException as e:
            raise TronZapException(f"API request failed: {str(e)}")

    def get_services(self) -> Dict[str, Any]:
        """
        Get available services.

        Returns:
            Dict[str, Any]: Services data
        """
        return self._request('POST', '/v1/services', {})

    def get_balance(self) -> Dict[str, Any]:
        """
        Get account balance.

        Returns:
            Dict[str, Any]: Balance data
        """
        return self._request('POST', '/v1/balance', {})

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
            contract_address (str, optional): TRON contract address. Defaults to 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'.

        Returns:
            Dict[str, Any]: Energy estimate result
        """
        return self._request('POST', '/v1/estimate-energy', {
            'from_address': from_address,
            'to_address': to_address,
            'contract_address': contract_address
        })

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
        return self._request('POST', '/v1/calculate', {
            'address': address,
            'energy': energy,
            'duration': duration
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
        params = {
            'service': 'energy',
            'params': {
                'address': address,
                'energy_amount': energy_amount,
                'duration': duration
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
        params = {
            'service': 'activate_address',
            'params': {
                'address': address
            }
        }

        if external_id:
            params['external_id'] = external_id

        return self._request('POST', '/v1/transaction/new', params)

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
        params = {}
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