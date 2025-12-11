# TronZap SDK для Python

[English](https://github.com/tron-energy-market/tronzap-sdk-python/blob/main/README.md) | [Español](https://github.com/tron-energy-market/tronzap-sdk-python/blob/main/README.es.md) | [Português](https://github.com/tron-energy-market/tronzap-sdk-python/blob/main/README.pt-br.md) | **[Русский](https://github.com/tron-energy-market/tronzap-sdk-python/blob/main/README.ru.md)**

Официальный Python SDK для API TronZap.
Данный SDK позволяет легко интегрировать сервисы TronZap для аренды энергии TRON.

TronZap.com позволяет [покупать энергию TRON](https://tronzap.com/), существенно снижая комиссии при переводах USDT (TRC20).

👉 [Зарегистрируйтесь для получения API ключа](https://tronzap.com), чтобы начать использовать TronZap API.

## Установка

```bash
pip install tronzap-sdk
```

## Быстрый старт

```python
from tronzap_sdk import Client

# Инициализация клиента
client = Client(
    api_token="ваш_api_token",
    api_secret="ваш_api_secret"
)

# Получение доступных сервисов
services = client.get_services()
print(services)

# Получение баланса аккаунта
balance = client.get_balance()
print(balance)

# Оценка стоимости энергии для перевода USDT
estimate = client.estimate_energy('АДРЕС_ОТПРАВИТЕЛЯ_TRX', 'АДРЕС_ПОЛУЧАТЕЛЯ_TRX', 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t')
print(estimate)

# Расчет стоимости энергии
calculation = client.calculate(
    address="АДРЕС_КОШЕЛЬКА_TRON",
    energy=65150  # Рекомендуемое количество для переводов USDT
)
print(calculation)

# Создание транзакции энергии
transaction = client.create_energy_transaction(
    address="АДРЕС_КОШЕЛЬКА_TRON",
    energy_amount=65150, # От 60000
    duration=1, # Возможные значения 1 или 24 часа
    activate_address=True  # Если адрес требует активации
)
print(transaction)

# Покупка bandwidth
bandwidth = client.create_bandwidth_transaction(
    address="АДРЕС_КОШЕЛЬКА_TRON",
    amount=1000,
    external_id="bandwidth-1"
)
print(bandwidth)

# Проверка статуса транзакции
status = client.check_transaction(id="ID_ТРАНЗАКЦИИ")
print(status)

# Создание AML-проверки
aml_check = client.create_aml_check(
    type="address",
    network="TRX",
    address="TXYZ1234567890EXAMPLEADDRESS"
)
print(aml_check)

# Проверка статуса AML
aml_status = client.check_aml_status(id=aml_check["id"])
print(aml_status)

# Получение информации о прямом пополнении
recharge_info = client.get_direct_recharge_info()
print(recharge_info)
```

## Возможности

- Получение доступных сервисов
- Получение AML-сервисов
- Получение баланса аккаунта
- Расчет стоимости энергии
- Создание транзакций активации адреса
- Создание транзакций покупки энергии
- Создание транзакций покупки bandwidth
- Создание и отслеживание AML-проверок
- Проверка статуса транзакций
- Получение информации о прямом пополнении

## Требования

- Python 3.7 или выше
- requests >= 2.25.0

## Обработка ошибок

SDK выбрасывает исключение `TronZapException`, когда API возвращает ошибку. Каждое исключение содержит свойства `.code` и `.message` для отладки и обработки конкретных случаев.

### Пример

```python
from tronzap_sdk import Client, TronZapException, ErrorCode

client = Client(api_token="your_api_token", api_secret="your_api_secret")

try:
    balance = client.get_balance()
except TronZapException as e:
    if e.code == ErrorCode.AUTH_ERROR:
        print("Ошибка аутентификации")
    elif e.code == ErrorCode.INVALID_SERVICE_OR_PARAMS:
        print("Неверный сервис или параметры")
    elif e.code == ErrorCode.WALLET_NOT_FOUND:
        print("Внутренний кошелёк не найден. Обратитесь в службу поддержки.")
    elif e.code == ErrorCode.INSUFFICIENT_FUNDS:
        print("Недостаточно средств")
    elif e.code == ErrorCode.INVALID_TRON_ADDRESS:
        print("Неверный TRON-адрес")
    elif e.code == ErrorCode.INVALID_ENERGY_AMOUNT:
        print("Неверное количество энергии")
    elif e.code == ErrorCode.INVALID_DURATION:
        print("Неверная длительность")
    elif e.code == ErrorCode.TRANSACTION_NOT_FOUND:
        print("Транзакция не найдена")
    elif e.code == ErrorCode.ADDRESS_NOT_ACTIVATED:
        print("Адрес не активирован")
    elif e.code == ErrorCode.ADDRESS_ALREADY_ACTIVATED:
        print("Адрес уже активирован")
    elif e.code == ErrorCode.AML_CHECK_NOT_FOUND:
        print("AML-проверка не найдена")
    elif e.code == ErrorCode.SERVICE_NOT_AVAILABLE:
        print("Сервис недоступен")
    elif e.code == ErrorCode.INTERNAL_SERVER_ERROR:
        print("Внутренняя ошибка сервера")
    else:
        print(f"Необработанная ошибка {e.code}: {e.message}")
```

### Коды ошибок

| Код  | Константа                      | Описание |
|------|--------------------------------|----------|
| 1    | `AUTH_ERROR`                  | Ошибка аутентификации — неверный API токен или подпись |
| 2    | `INVALID_SERVICE_OR_PARAMS`  | Неверный сервис или параметры |
| 5    | `WALLET_NOT_FOUND`           | Внутренний кошелёк не найден. Обратитесь в службу поддержки. |
| 6    | `INSUFFICIENT_FUNDS`         | Недостаточно средств |
| 10   | `INVALID_TRON_ADDRESS`       | Неверный TRON-адрес |
| 11   | `INVALID_ENERGY_AMOUNT`      | Неверное количество энергии |
| 12   | `INVALID_DURATION`           | Неверная длительность |
| 20   | `TRANSACTION_NOT_FOUND`      | Транзакция не найдена |
| 24   | `ADDRESS_NOT_ACTIVATED`      | Адрес не активирован |
| 25   | `ADDRESS_ALREADY_ACTIVATED`  | Адрес уже активирован |
| 30   | `AML_CHECK_NOT_FOUND`        | AML-проверка не найдена |
| 35   | `SERVICE_NOT_AVAILABLE`      | Сервис недоступен |
| 500  | `INTERNAL_SERVER_ERROR`      | Внутренняя ошибка сервера — обратитесь в поддержку |

## Поддержка

Для поддержки свяжитесь с нами в Telegram: [@tronzap_bot](https://t.me/tronzap_bot)

## Лицензия

Этот проект лицензирован под лицензией MIT - см. файл [LICENSE](LICENSE) для подробностей.
