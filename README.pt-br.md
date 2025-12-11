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
- Calcular custo de energia
- Criar transações de ativação de endereço
- Criar transações de compra de energia
- Criar transações de compra de bandwidth
- Criar e acompanhar checagens AML
- Verificar status de transações
- Obter informações de recarga direta

## Requisitos

- Python 3.7 ou superior
- requests >= 2.25.0

## Tratamento de Erros

O SDK lança a exceção `TronZapException` quando a API retorna um erro. Cada exceção inclui as propriedades `.code` e `.message` para facilitar o diagnóstico e o tratamento de erros específicos.

### Exemplo

```python
from tronzap_sdk import Client, TronZapException, ErrorCode

client = Client(api_token="your_api_token", api_secret="your_api_secret")

try:
    balance = client.get_balance()
except TronZapException as e:
    if e.code == ErrorCode.AUTH_ERROR:
        print("Erro de autenticação")
    elif e.code == ErrorCode.INVALID_SERVICE_OR_PARAMS:
        print("Serviço ou parâmetros inválidos")
    elif e.code == ErrorCode.WALLET_NOT_FOUND:
        print("Carteira interna não encontrada. Entre em contato com o suporte.")
    elif e.code == ErrorCode.INSUFFICIENT_FUNDS:
        print("Fundos insuficientes")
    elif e.code == ErrorCode.INVALID_TRON_ADDRESS:
        print("Endereço TRON inválido")
    elif e.code == ErrorCode.INVALID_ENERGY_AMOUNT:
        print("Quantidade de energia inválida")
    elif e.code == ErrorCode.INVALID_DURATION:
        print("Duração inválida")
    elif e.code == ErrorCode.TRANSACTION_NOT_FOUND:
        print("Transação não encontrada")
    elif e.code == ErrorCode.ADDRESS_NOT_ACTIVATED:
        print("Endereço não ativado")
    elif e.code == ErrorCode.ADDRESS_ALREADY_ACTIVATED:
        print("Endereço já ativado")
    elif e.code == ErrorCode.AML_CHECK_NOT_FOUND:
        print("Checagem AML não encontrada")
    elif e.code == ErrorCode.SERVICE_NOT_AVAILABLE:
        print("Serviço não disponível")
    elif e.code == ErrorCode.INTERNAL_SERVER_ERROR:
        print("Erro interno do servidor")
    else:
        print(f"Erro não tratado {e.code}: {e.message}")
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
| 20     | `TRANSACTION_NOT_FOUND`        | Transação não encontrada |
| 24     | `ADDRESS_NOT_ACTIVATED`        | Endereço não ativado |
| 25     | `ADDRESS_ALREADY_ACTIVATED`    | Endereço já ativado |
| 30     | `AML_CHECK_NOT_FOUND`          | Checagem AML não encontrada |
| 35     | `SERVICE_NOT_AVAILABLE`        | Serviço não disponível |
| 500    | `INTERNAL_SERVER_ERROR`        | Erro interno do servidor – Contate o suporte |


## Suporte

Para suporte, entre em contato conosco no Telegram: [@tronzap_bot](https://t.me/tronzap_bot)

## Licença

Este projeto está licenciado sob a Licença MIT - consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
