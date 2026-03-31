"""
Tests for the TronZap SDK client
"""

import pytest
from unittest.mock import patch, MagicMock
from tronzap_sdk import (
    Client,
    TronZapException,
    ApiException,
    NetworkException,
    ConnectionException,
    TimeoutException,
    SslException,
    HttpException,
    ServerException,
    RateLimitException,
    UnauthorizedException,
)
import requests
import json

@pytest.fixture
def client():
    return Client(
        api_token="test_token",
        api_secret="test_secret"
    )

def test_client_initialization():
    client = Client(
        api_token="test_token",
        api_secret="test_secret"
    )
    assert client.api_token == "test_token"
    assert client.api_secret == "test_secret"
    assert client.base_url == "https://api.tronzap.com"

def test_client_initialization_with_custom_url():
    client = Client(
        api_token="test_token",
        api_secret="test_secret",
        base_url="https://custom.api.tronzap.com"
    )
    assert client.base_url == "https://custom.api.tronzap.com"

@patch('requests.post')
def test_get_services(mock_post, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "code": 0,
        "result": {"services": ["energy", "activate_address"]}
    }
    mock_post.return_value = mock_response

    result = client.get_services()
    assert result == {"services": ["energy", "activate_address"]}

    mock_post.assert_called_once()
    call_args = mock_post.call_args[1]
    assert call_args["headers"]["Authorization"] == "Bearer test_token"
    assert "X-Signature" in call_args["headers"]
    assert call_args["url"] == "https://api.tronzap.com/v1/services"

@patch('requests.post')
def test_get_balance(mock_post, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "code": 0,
        "result": {"balance": "100.5"}
    }
    mock_post.return_value = mock_response

    result = client.get_balance()
    assert result == {"balance": "100.5"}

    mock_post.assert_called_once()
    call_args = mock_post.call_args[1]
    assert call_args["headers"]["Authorization"] == "Bearer test_token"
    assert "X-Signature" in call_args["headers"]
    assert call_args["url"] == "https://api.tronzap.com/v1/balance"

@patch('requests.post')
def test_get_address_info(mock_post, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "code": 0,
        "result": {"resources": {"energy": 131000, "bandwidth": 600}, "balances": {"TRX": 10, "USDT": 2}}
    }
    mock_post.return_value = mock_response

    result = client.get_address_info("TKuV4gsNRCqEZwS8zRuHJHnCgvNBce7MPe")
    assert result == {"resources": {"energy": 131000, "bandwidth": 600}, "balances": {"TRX": 10, "USDT": 2}}

    mock_post.assert_called_once()
    call_args = mock_post.call_args[1]
    assert call_args["url"] == "https://api.tronzap.com/v1/address-info"
    assert json.loads(call_args["data"]) == {
        "address": "TKuV4gsNRCqEZwS8zRuHJHnCgvNBce7MPe"
    }

@patch('requests.post')
def test_estimate_energy(mock_post, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "code": 0,
        "result": {"energy": 131000, "duration": 1, "price": 1.67, "activation_fee": 0, "total": 1.67, "contract_address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t", "from_address": "test_address", "to_address": "test_address"}
    }
    mock_post.return_value = mock_response

    result = client.estimate_energy(
        from_address="test_address",
        to_address="test_address",
        contract_address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
    )
    assert result == {"energy": 131000, "duration": 1, "price": 1.67, "activation_fee": 0, "total": 1.67, "contract_address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t", "from_address": "test_address", "to_address": "test_address"}

    mock_post.assert_called_once()
    call_args = mock_post.call_args[1]
    assert call_args["headers"]["Authorization"] == "Bearer test_token"
    assert "X-Signature" in call_args["headers"]
    assert call_args["url"] == "https://api.tronzap.com/v1/estimate-energy"
    assert json.loads(call_args["data"]) == {
        "from_address": "test_address",
        "to_address": "test_address",
        "contract_address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
    }

@patch('requests.post')
def test_calculate(mock_post, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "code": 0,
        "result": {"cost": "10.5"}
    }
    mock_post.return_value = mock_response

    result = client.calculate(
        address="test_address",
        energy=131000
    )
    assert result == {"cost": "10.5"}

    mock_post.assert_called_once()
    call_args = mock_post.call_args[1]
    assert call_args["headers"]["Authorization"] == "Bearer test_token"
    assert "X-Signature" in call_args["headers"]
    assert call_args["url"] == "https://api.tronzap.com/v1/calculate"
    assert json.loads(call_args["data"]) == {
        "address": "test_address",
        "energy": 131000,
        "duration": 1
    }

@patch('requests.post')
def test_create_energy_transaction(mock_post, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "code": 0,
        "result": {"transaction_id": "test_id"}
    }
    mock_post.return_value = mock_response

    result = client.create_energy_transaction(
        address="test_address",
        energy_amount=131000,
        duration=1,
        activate_address=True
    )
    assert result == {"transaction_id": "test_id"}

    mock_post.assert_called_once()
    call_args = mock_post.call_args[1]
    assert call_args["headers"]["Authorization"] == "Bearer test_token"
    assert "X-Signature" in call_args["headers"]
    assert call_args["url"] == "https://api.tronzap.com/v1/transaction/new"
    assert json.loads(call_args["data"]) == {
        "service": "energy",
        "params": {
            "address": "test_address",
            "energy_amount": 131000,
            "amount": 131000,
            "duration": 1,
            "activate_address": True
        }
    }

@patch('requests.post')
def test_create_bandwidth_transaction(mock_post, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "code": 0,
        "result": {"transaction_id": "bandwidth_id"}
    }
    mock_post.return_value = mock_response

    result = client.create_bandwidth_transaction(
        address="test_address",
        amount=1000,
        external_id="ext-1"
    )
    assert result == {"transaction_id": "bandwidth_id"}

    mock_post.assert_called_once()
    call_args = mock_post.call_args[1]
    assert call_args["url"] == "https://api.tronzap.com/v1/transaction/new"
    assert json.loads(call_args["data"]) == {
        "service": "bandwidth",
        "params": {
            "address": "test_address",
            "amount": 1000,
            "duration": 1
        },
        "external_id": "ext-1"
    }

@patch('requests.post')
def test_get_aml_services(mock_post, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "code": 0,
        "result": [{"id": "service", "price": 1}]
    }
    mock_post.return_value = mock_response

    result = client.get_aml_services()
    assert result == [{"id": "service", "price": 1}]
    mock_post.assert_called_once()
    assert mock_post.call_args[1]["url"] == "https://api.tronzap.com/v1/aml-checks"

@patch('requests.post')
def test_create_aml_check(mock_post, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "code": 0,
        "result": {"id": "aml-id"}
    }
    mock_post.return_value = mock_response

    result = client.create_aml_check(
        type="hash",
        network="TRX",
        address="T123",
        hash="hash",
        direction="deposit"
    )
    assert result == {"id": "aml-id"}
    mock_post.assert_called_once()
    assert json.loads(mock_post.call_args[1]["data"]) == {
        "type": "hash",
        "network": "TRX",
        "address": "T123",
        "hash": "hash",
        "direction": "deposit"
    }

@patch('requests.post')
def test_check_aml_status(mock_post, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "code": 0,
        "result": {"status": "pending"}
    }
    mock_post.return_value = mock_response

    result = client.check_aml_status("aml-id")
    assert result == {"status": "pending"}
    mock_post.assert_called_once()
    assert json.loads(mock_post.call_args[1]["data"]) == {"id": "aml-id"}

@patch('requests.post')
def test_get_aml_history(mock_post, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "code": 0,
        "result": {"items": []}
    }
    mock_post.return_value = mock_response

    result = client.get_aml_history(page=2, per_page=5, status="completed")
    assert result == {"items": []}
    mock_post.assert_called_once()
    assert json.loads(mock_post.call_args[1]["data"]) == {
        "page": 2,
        "per_page": 5,
        "status": "completed"
    }

@patch('requests.post')
def test_api_error(mock_post, client):
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "code": 1,
        "error": "Invalid API token"
    }
    mock_post.return_value = mock_response

    with pytest.raises(TronZapException) as exc_info:
        client.get_services()
    assert isinstance(exc_info.value, ApiException)
    assert str(exc_info.value) == "TronZap API Error 1: Invalid API token"
    assert exc_info.value.code == 1
    assert exc_info.value.message == "Invalid API token"

@patch('requests.post')
def test_connection_error(mock_post, client):
    mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

    with pytest.raises(TronZapException) as exc_info:
        client.get_services()
    assert isinstance(exc_info.value, ConnectionException)
    assert exc_info.value.original_error is not None

@patch('requests.post')
def test_timeout_error(mock_post, client):
    mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

    with pytest.raises(TronZapException) as exc_info:
        client.get_services()
    assert isinstance(exc_info.value, TimeoutException)

@patch('requests.post')
def test_ssl_error(mock_post, client):
    mock_post.side_effect = requests.exceptions.SSLError("certificate verify failed")

    with pytest.raises(TronZapException) as exc_info:
        client.get_services()
    assert isinstance(exc_info.value, SslException)

@patch('requests.post')
def test_network_error(mock_post, client):
    mock_post.side_effect = requests.exceptions.RequestException("Network error")

    with pytest.raises(TronZapException) as exc_info:
        client.get_services()
    assert isinstance(exc_info.value, NetworkException)

@patch('requests.post')
def test_rate_limit_error(mock_post, client):
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 429
    mock_response.text = "Too many requests"
    mock_post.return_value = mock_response

    with pytest.raises(TronZapException) as exc_info:
        client.get_services()
    assert isinstance(exc_info.value, RateLimitException)
    assert exc_info.value.status_code == 429

@patch('requests.post')
def test_server_error(mock_post, client):
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 503
    mock_response.text = "Service unavailable"
    mock_post.return_value = mock_response

    with pytest.raises(TronZapException) as exc_info:
        client.get_services()
    assert isinstance(exc_info.value, ServerException)
    assert exc_info.value.status_code == 503

@patch('requests.post')
def test_unauthorized_error(mock_post, client):
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_post.return_value = mock_response

    with pytest.raises(TronZapException) as exc_info:
        client.get_services()
    assert isinstance(exc_info.value, UnauthorizedException)
    assert exc_info.value.status_code == 401
