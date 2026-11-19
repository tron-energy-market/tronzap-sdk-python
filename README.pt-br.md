# Aluguel de Energia Tron via API
## SDK Python por TronZap.com

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
    api_secret="seu_api_secret",
    timeout=30,  # Segundos, opcional; 30 por padrão
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
estimate = client.estimate_energy('ENDERECO_ORIGEM_TRX', 'ENDERECO_DESTINO_TRX')
print(estimate)

# Calcular custo de energia
calculation = client.calculate(
    address="ENDERECO_CARTEIRA_TRON",
    energy=65000  # Quantidade recomendada para transferências USDT
)
print(calculation)

# Criar transação de energia
transaction = client.create_energy_transaction(
    address="ENDERECO_CARTEIRA_TRON",
    energy_amount=65000,
    duration=1,  # Horas: uma das durações retornadas por get_services()
    activate_address=True  # Se o endereço precisar de ativação
)
print(transaction)

# Comprar bandwidth
bandwidth = client.create_bandwidth_transaction(
    address="ENDERECO_CARTEIRA_TRON",
    amount=345,
    external_id="bandwidth-1"
)
print(bandwidth)

# Comprar pacote de recursos (energia + bandwidth em uma só transação)
bundle = client.create_resource_bundle_transaction(
    address="ENDERECO_CARTEIRA_TRON",
    energy_amount=65000,
    bandwidth_amount=345,
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

Em uma verificação por hash, `address` é o endereço do destinatário da
transação, onde os fundos foram recebidos, e `direction` indica de que lado você
está: `"deposit"` se os fundos chegaram ao seu endereço (`address` é o seu
endereço), `"withdrawal"` se foi você quem enviou (`address` é o endereço do
destinatário externo). O risco é calculado para a contraparte: o remetente em um
deposit, o destinatário em um withdrawal. Se você omitir `direction` em uma
verificação por hash, o SDK envia `"deposit"`.

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
- Iniciar, verificar, parar e listar assinaturas
- Verificar status de transações
- Obter informações de recarga direta
- Pedidos de energia em massa para até 10 000 endereços, com relatório CSV e verificação da assinatura do webhook

## Requisitos

- Python 3.9 ou superior
- requests >= 2.32.4

## Assinaturas

Uma assinatura mantém um endereço abastecido de energia para cada transação até ser parada ou esgotar seus dias ou
transações. `get_subscriptions()` retorna os planos indexados pelo ID de assinatura; passe essa chave, como
`"unlimited_energy"`, para `start_subscription`, não o `id` numérico do plano. Iniciar uma assinatura cobra o preço
inicial do plano.

```python
plans = client.get_subscriptions()
for subscription_id, plan in plans.items():
    print(subscription_id, plan["initial_price"], plan["price"])

subscription = client.start_subscription(
    subscription_id="unlimited_energy",
    address="TRON_WALLET_ADDRESS",
    duration_days=30,  # 0 para sem limite de tempo
    transactions_limit=0,  # 0 para sem limite
    external_id="subscription-42"
)

subscription = client.check_subscription(external_id="subscription-42")

stopped = client.stop_subscription(id=subscription["id"])

history = client.get_subscription_history(page=1, per_page=10, status="active")
```

`duration_days` e `transactions_limit` valem 0 por padrão, o que significa sem limite. Iniciar, verificar e parar
retornam a assinatura com seus `params`; os itens do histórico trazem, em vez disso, os contadores de uso
`transactions_used`, `energy_used` e `total_price`. Uma assinatura com limite de transações não pode ser parada
(`CANNOT_STOP_SUBSCRIPTION`).

## Pedidos em massa

Compre energia para até 10 000 endereços em um único pedido. `bulk_calculate` valida e calcula as linhas e retorna um cálculo válido por 10 minutos; nada é cobrado. Linhas inválidas não fazem a requisição falhar: elas voltam em `rejected` com o número da linha. `bulk_create` inicia o pedido; cada endereço é cobrado quando é processado, e endereços não ativados são pulados sem cobrança.

Se o preço mudou desde o cálculo, `bulk_create` não inicia o pedido e lança `ApiException` com o código `BULK_PRICE_CHANGED`. O novo cálculo está em `e.result`: confirme o novo total e inicie-o pelo `id`.

```python
from tronzap_sdk import ApiException, ErrorCode

items = [
    {"address": "TRX_ADDRESS_1", "amount": 65000},
    {"address": "TRX_ADDRESS_2", "amount": 131000},
]

try:
    calculation = client.bulk_calculate(items, duration=1)
except ApiException as e:
    if e.code == ErrorCode.BULK_NO_VALID_ITEMS:
        print(e.result["rejected"])  # Todas as linhas foram rejeitadas
    raise

print(f"Total: {calculation['total_amount']} TRX, rejeitadas: {calculation['rejected_count']}")

try:
    order = client.bulk_create(
        calculation["id"],
        external_id="order-42",
        webhook_url="https://example.com/tronzap/bulk",
    )
except ApiException as e:
    if e.code != ErrorCode.BULK_PRICE_CHANGED:
        raise
    calculation = e.result  # Novo cálculo: confirme o novo total e inicie-o
    order = client.bulk_create(calculation["id"], external_id="order-42")

order = client.bulk_check(external_id="order-42")  # Consulte até completed, partial ou failed

report = client.bulk_report(order["id"])  # row,address,amount,status,reason,charged,transaction_id
```

Com `webhook_url`, a API envia um único `POST` quando o pedido se torna final. Verifique o cabeçalho `X-Signature` com o corpo bruto antes de confiar na requisição, por exemplo no Flask:

```python
from flask import abort, request

if not client.verify_webhook_signature(request.get_data(), request.headers.get("X-Signature", "")):
    abort(403)
```

## Tratamento de Erros

O SDK utiliza uma hierarquia de exceções para tratamento preciso de erros:

```
TronZapException
├── ApiException             — erros a nível de API (code != 0 na resposta), incluindo HTTP 429 da API
├── InvalidRequestException  — argumentos inválidos, rejeitados antes do envio (também é ValueError)
├── NetworkException         — erros de rede/conectividade
│   ├── ConnectionException  — não foi possível conectar ao servidor
│   ├── TimeoutException     — tempo de espera esgotado
│   └── SslException         — erros SSL/TLS
└── HttpException            — respostas HTTP não 2xx
    ├── RateLimitException   — HTTP 429 sem resposta da API, p. ex. de um proxy
    ├── UnauthorizedException — HTTP 401/403
    └── ServerException      — erros HTTP 5xx
```

### Exemplo

```python
import time

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

client = Client(api_token="seu_api_token", api_secret="seu_api_secret")

try:
    transaction = client.create_energy_transaction("TRX_ADDRESS", 65000, 1)
except ApiException as e:
    # Erro a nível de API (parâmetros inválidos, saldo insuficiente, etc.)
    print(f"Erro API [{e.code}]: {e.message}")

    # Chave alias do erro, ex. "invalid_tron_address" ou "invalid_tron_address.from_address"
    if e.error_key:
        print(f"Chave de erro: {e.error_key}")

    # Informe-o ao contatar o suporte
    print(f"ID da requisição: {e.request_id}")

    # Dados que a API enviou com o erro, p. ex. o novo cálculo para BULK_PRICE_CHANGED
    result = e.result

    if e.code == ErrorCode.RATE_LIMITED:
        # Segundos de espera, se a API os enviou
        time.sleep(60 if e.retry_after is None else e.retry_after)

    if e.code == ErrorCode.INVALID_TRON_ADDRESS:
        print("Verifique o formato do endereço TRON.")
except InvalidRequestException as e:
    print(f"Argumentos inválidos: {e.message}")
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
| 10     | `INVALID_TRON_ADDRESS`         | Endereço TRON inválido, ou o endereço já tem uma assinatura ativa |
| 11     | `INVALID_ENERGY_AMOUNT`        | Quantidade de energia inválida |
| 12     | `INVALID_DURATION`             | Duração inválida |
| 20     | `TRANSACTION_NOT_FOUND`        | Transação/assinatura não encontrada |
| 21     | `CANNOT_STOP_SUBSCRIPTION`     | Não é possível parar a assinatura, p. ex. ela tem um limite de transações |
| 24     | `ADDRESS_NOT_ACTIVATED`        | Endereço não ativado |
| 25     | `ADDRESS_ALREADY_ACTIVATED`    | Endereço já ativado |
| 30     | `AML_CHECK_NOT_FOUND`          | Checagem AML não encontrada |
| 35     | `SERVICE_NOT_AVAILABLE`        | Serviço não disponível |
| 50     | `INVALID_BANDWIDTH_AMOUNT`     | Quantidade de bandwidth inválida |
| 90     | `BULK_NOT_FOUND`               | Pedido em massa não encontrado |
| 91     | `BULK_EXPIRED`                 | O cálculo expirou, calcule novamente |
| 92     | `BULK_PRICE_CHANGED`           | O preço mudou; o novo cálculo está em `e.result` |
| 93     | `BULK_TOO_MANY_ITEMS`          | Mais de 10 000 linhas |
| 94     | `BULK_NO_VALID_ITEMS`          | Nenhuma linha válida; elas estão em `e.result["rejected"]` |
| 95     | `BULK_RESOURCE_NOT_SUPPORTED`  | Apenas energia pode ser pedida em massa |
| 96     | `PAYLOAD_TOO_LARGE`            | Corpo da requisição grande demais (HTTP 413) |
| 429    | `RATE_LIMITED`                 | Requisições demais; aguarde `e.retry_after` segundos, quando informado |
| 500    | `INTERNAL_SERVER_ERROR`        | Erro interno do servidor – Contate o suporte |


## Desenvolvimento

```bash
pip install -r requirements-dev.txt -e .
pytest
```

Os testes rodam contra um servidor HTTP/TLS local e nunca chamam a API real. `examples/basic_usage.py` é um teste de fumaça contra um ambiente real; as instruções estão no início do arquivo.

## Suporte

Para suporte, entre em contato conosco no Telegram: [@tronzap_bot](https://t.me/tronzap_bot)

## Licença

Este projeto está licenciado sob a Licença MIT - consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
