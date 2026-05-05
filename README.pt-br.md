# TronZap SDK para Python

[English](https://github.com/tron-energy-market/tronzap-sdk-python/blob/main/README.md) | [Español](https://github.com/tron-energy-market/tronzap-sdk-python/blob/main/README.es.md) | **[Português](https://github.com/tron-energy-market/tronzap-sdk-python/blob/main/README.pt-br.md)** | [Русский](https://github.com/tron-energy-market/tronzap-sdk-python/blob/main/README.ru.md)

SDK oficial em Python para a API do TronZap.
Este SDK permite integrar facilmente os serviços TronZap para aluguel de energia TRON.

TronZap.com permite [comprar energia TRON](https://tronzap.com/), reduzindo significativamente as taxas nas transferências de USDT (TRC20).

👉 [Registre-se para obter uma chave API](https://tronzap.com) para começar a usar a API TronZap e integrá-la através do SDK.

## Instalação

```bash
pip install tronzap-sdk
```

## Início Rápido

```python
from tronzap_sdk import Client

# Inicializar o cliente
client = Client(
    api_token="seu_api_token",
    api_secret="seu_api_secret"
)

# Obter serviços disponíveis
services = client.get_services()
print(services)

# Obter saldo da conta
balance = client.get_balance()
print(balance)

# Obter informações do endereço (recursos e saldos)
address_info = client.get_address_info("TRX_ADDRESS")
print(address_info)

# Estimar custo de energia para transferência USDT
estimate = client.estimate_energy('ENDERECO_ORIGEM_TRX', 'ENDERECO_DESTINO_TRX', 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t')
print(estimate)

# Calcular custo de energia
calculation = client.calculate(
    address="ENDERECO_CARTEIRA_TRON",
    energy=65150  # Quantidade recomendada para transferências USDT
)
print(calculation)

# Criar transação de energia
transaction = client.create_energy_transaction(
    address="ENDERECO_CARTEIRA_TRON",
    energy_amount=65150, # A partir de 60000
    duration=1, # Valores possíveis 1 ou 24 horas
    activate_address=True  # Se o endereço precisar de ativação
)
print(transaction)

# Comprar bandwidth
bandwidth = client.create_bandwidth_transaction(
    address="ENDERECO_CARTEIRA_TRON",
    amount=1000,
    external_id="bandwidth-1"
)
print(bandwidth)

# Comprar pacote de recursos (energia + bandwidth em uma só transação)
bundle = client.create_resource_bundle_transaction(
    address="ENDERECO_CARTEIRA_TRON",
    energy_amount=65000,
    bandwidth_amount=350,
    duration=1,
    external_id="bundle-1",
    activate_address=True
)
print(bundle)

# Verificar status da transação
status = client.check_transaction(id="ID_TRANSACAO")
print(status)

# Criar checagem AML
aml_check = client.create_aml_check(
    type="address",
    network="TRX",
    address="TXYZ1234567890EXAMPLEADDRESS"
)
print(aml_check)

# Verificar status AML
aml_status = client.check_aml_status(id=aml_check["id"])
print(aml_status)

# Obter informações de recarga direta
recharge_info = client.get_direct_recharge_info()
print(recharge_info)
```

## Recursos

- Obter serviços disponíveis
- Obter serviços AML
- Obter saldo da conta
- Obter informações do endereço (recursos e saldos)
- Calcular custo de energia
- Criar transações de ativação de endereço
- Criar transações de compra de energia
- Criar transações de compra de bandwidth
- Criar transações de pacote de recursos (energia + bandwidth)
- Criar e acompanhar checagens AML
- Verificar status de transações
- Obter informações de recarga direta

## Requisitos

- Python 3.7 ou superior
- requests >= 2.25.0

## Tratamento de Erros

O SDK utiliza uma hierarquia de exceções para tratamento preciso de erros:

```
TronZapException
├── ApiException             — erros a nível de API (code != 0 na resposta)
├── NetworkException         — erros de rede/conectividade
│   ├── ConnectionException  — não foi possível conectar ao servidor
│   ├── TimeoutException     — tempo de espera esgotado
│   └── SslException         — erros SSL/TLS
└── HttpException            — respostas HTTP não 2xx
    ├── RateLimitException   — HTTP 429 Too Many Requests
    ├── UnauthorizedException — HTTP 401/403
    └── ServerException      — erros HTTP 5xx
```

### Exemplo

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
    ErrorCode,
)

client = Client(api_token="seu_api_token", api_secret="seu_api_secret")

try:
    transaction = client.create_energy_transaction("TRX_ADDRESS", 65000, 1)
except ApiException as e:
    # Erro a nível de API (parâmetros inválidos, saldo insuficiente, etc.)
    print(f"Erro API [{e.code}]: {e.message}")

    # Chave alias do erro, ex. "invalid_tron_address" ou "invalid_tron_address.from_address"
    if e.error_key:
        print(f"Chave de erro: {e.error_key}")

    if e.code == ErrorCode.INVALID_TRON_ADDRESS:
        print("Verifique o formato do endereço TRON.")
except RateLimitException:
    print("Muitas requisições. Reduza a frequência.")
except UnauthorizedException:
    print("Token API ou assinatura inválidos.")
except ServerException as e:
    print(f"Erro do servidor TronZap [{e.status_code}].")
except HttpException as e:
    print(f"Erro HTTP [{e.status_code}]: {e.message}")
except TimeoutException:
    print("Tempo de espera esgotado.")
except SslException as e:
    print(f"Erro SSL: {e.message}")
except ConnectionException as e:
    print(f"Falha na conexão: {e.message}")
except NetworkException as e:
    print(f"Erro de rede: {e.message}")
except TronZapException as e:
    print(f"Erro [{e.code}]: {e.message}")
```

### Códigos de Erro

| Código | Constante                       | Descrição |
|--------|----------------------------------|-----------|
| 1      | `AUTH_ERROR`                    | Erro de autenticação – Token da API ou assinatura inválidos |
| 2      | `INVALID_SERVICE_OR_PARAMS`    | Serviço ou parâmetros inválidos |
| 5      | `WALLET_NOT_FOUND`             | Carteira interna não encontrada. Entre em contato com o suporte |
| 6      | `INSUFFICIENT_FUNDS`           | Fundos insuficientes |
| 10     | `INVALID_TRON_ADDRESS`         | Endereço TRON inválido |
| 11     | `INVALID_ENERGY_AMOUNT`        | Quantidade de energia inválida |
| 12     | `INVALID_DURATION`             | Duração inválida |
| 20     | `TRANSACTION_NOT_FOUND`        | Transação/assinatura não encontrada |
| 21     | `CANNOT_STOP_SUBSCRIPTION`     | Não é possível parar a assinatura |
| 24     | `ADDRESS_NOT_ACTIVATED`        | Endereço não ativado |
| 25     | `ADDRESS_ALREADY_ACTIVATED`    | Endereço já ativado |
| 30     | `AML_CHECK_NOT_FOUND`          | Checagem AML não encontrada |
| 35     | `SERVICE_NOT_AVAILABLE`        | Serviço não disponível |
| 50     | `INVALID_BANDWIDTH_AMOUNT`     | Quantidade de bandwidth inválida |
| 500    | `INTERNAL_SERVER_ERROR`        | Erro interno do servidor – Contate o suporte |


## Suporte

Para suporte, entre em contato conosco no Telegram: [@tronzap_bot](https://t.me/tronzap_bot)

## Licença

Este projeto está licenciado sob a Licença MIT - consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
