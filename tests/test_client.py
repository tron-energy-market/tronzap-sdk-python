"""
Tests for the TronZap SDK client
"""

import pytest
from unittest.mock import patch, MagicMock
from tronzap_sdk import Client, TronZapException
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
            "duration": 1,
            "activate_address": True
        }
    }

@patch('requests.post')
def test_api_error(mock_post, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "code": 1,
        "error": "Invalid API token"
    }
    mock_post.return_value = mock_response

    with pytest.raises(TronZapException) as exc_info:
        client.get_services()
    assert str(exc_info.value) == "TronZap API Error 1: Invalid API token"
    assert exc_info.value.code == 1
    assert exc_info.value.message == "Invalid API token"

@patch('requests.post')
def test_network_error(mock_post, client):
    mock_post.side_effect = requests.exceptions.RequestException("Network error")

    with pytest.raises(TronZapException) as exc_info:
        client.get_services()
    assert "API request failed" in str(exc_info.value)