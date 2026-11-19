# Покупка энергии Tron через API
## Python SDK от TronZap.com

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
    api_secret="ваш_api_secret",
    timeout=30,  # Секунды, необязательно; по умолчанию 30
)

# Получение доступных сервисов
services = client.get_services()
print(services)

# Получение баланса аккаунта
balance = client.get_balance()
print(balance)

# Получение информации об адресе (ресурсы и балансы)
address_info = client.get_address_info("TRX_ADDRESS")
print(address_info)

# Оценка стоимости энергии для перевода USDT
estimate = client.estimate_energy('АДРЕС_ОТПРАВИТЕЛЯ_TRX', 'АДРЕС_ПОЛУЧАТЕЛЯ_TRX')
print(estimate)

# Расчет стоимости энергии
calculation = client.calculate(
    address="АДРЕС_КОШЕЛЬКА_TRON",
    energy=65000  # Рекомендуемое количество для переводов USDT
)
print(calculation)

# Создание транзакции энергии
transaction = client.create_energy_transaction(
    address="АДРЕС_КОШЕЛЬКА_TRON",
    energy_amount=65000,
    duration=1,  # Часы: одна из длительностей, которые возвращает get_services()
    activate_address=True  # Если адрес требует активации
)
print(transaction)

# Покупка bandwidth
bandwidth = client.create_bandwidth_transaction(
    address="АДРЕС_КОШЕЛЬКА_TRON",
    amount=345,
    external_id="bandwidth-1"
)
print(bandwidth)

# Покупка пакета ресурсов (energy + bandwidth одной транзакцией)
bundle = client.create_resource_bundle_transaction(
    address="АДРЕС_КОШЕЛЬКА_TRON",
    energy_amount=65000,
    bandwidth_amount=345,
    duration=1,
    external_id="bundle-1",
    activate_address=True
)
print(bundle)

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

Для проверки по hash `address` — это адрес получателя средств в транзакции, а
`direction` указывает, на какой стороне транзакции вы: `"deposit"`, если средства
пришли на ваш адрес (`address` — ваш адрес), `"withdrawal"`, если их отправили вы
(`address` — адрес внешнего получателя). Риск оценивается для контрагента: для
deposit — для отправителя, для withdrawal — для получателя. Если не указать
`direction` для проверки по hash, SDK отправит `"deposit"`.

## Возможности

- Получение доступных сервисов
- Получение AML-сервисов
- Получение баланса аккаунта
- Получение информации об адресе (ресурсы и балансы)
- Расчет стоимости энергии
- Создание транзакций активации адреса
- Создание транзакций покупки энергии
- Создание транзакций покупки bandwidth
- Создание транзакций пакета ресурсов (energy + bandwidth)
- Создание и отслеживание AML-проверок
- Запуск, проверка, остановка и история подписок
- Проверка статуса транзакций
- Получение информации о прямом пополнении
- Массовые заказы энергии до 10 000 адресов с CSV-отчётом и проверкой подписи вебхука

## Требования

- Python 3.9 или выше
- requests >= 2.32.4

## Подписки

Подписка обеспечивает адрес энергией для каждой транзакции, пока её не остановят или не закончатся её дни или
транзакции. `get_subscriptions()` возвращает планы с ключом — ID подписки; передайте этот ключ, например
`"unlimited_energy"`, в `start_subscription`, а не числовой `id` плана. При запуске подписки списывается начальная
цена плана.

```python
plans = client.get_subscriptions()
for subscription_id, plan in plans.items():
    print(subscription_id, plan["initial_price"], plan["price"])

subscription = client.start_subscription(
    subscription_id="unlimited_energy",
    address="TRON_WALLET_ADDRESS",
    duration_days=30,  # 0 — без ограничения по времени
    transactions_limit=0,  # 0 — без ограничения
    external_id="subscription-42"
)

subscription = client.check_subscription(external_id="subscription-42")

stopped = client.stop_subscription(id=subscription["id"])

history = client.get_subscription_history(page=1, per_page=10, status="active")
```

`duration_days` и `transactions_limit` по умолчанию равны 0, что означает отсутствие ограничения. Запуск, проверка и
остановка возвращают подписку с её `params`, а элементы истории вместо них — счётчики использования
`transactions_used`, `energy_used` и `total_price`. Подписку с лимитом транзакций остановить нельзя
(`CANNOT_STOP_SUBSCRIPTION`).

## Массовые заказы

Покупка энергии на 10 000 адресов одним заказом. `bulk_calculate` проверяет и рассчитывает строки и возвращает расчёт, действительный 10 минут; ничего не списывается. Некорректные строки не валят запрос: они возвращаются в `rejected` с номером строки. `bulk_create` запускает заказ; каждый адрес списывается в момент обработки, неактивированные адреса пропускаются без списания.

Если цена изменилась после расчёта, `bulk_create` не запускает заказ и бросает `ApiException` с кодом `BULK_PRICE_CHANGED`. Новый расчёт — в `e.result`: подтвердите новую сумму и запустите его по `id`.

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
        print(e.result["rejected"])  # Все строки отклонены
    raise

print(f"Итого: {calculation['total_amount']} TRX, отклонено: {calculation['rejected_count']}")

try:
    order = client.bulk_create(
        calculation["id"],
        external_id="order-42",
        webhook_url="https://example.com/tronzap/bulk",
    )
except ApiException as e:
    if e.code != ErrorCode.BULK_PRICE_CHANGED:
        raise
    calculation = e.result  # Новый расчёт: подтвердите новую сумму и запустите его
    order = client.bulk_create(calculation["id"], external_id="order-42")

order = client.bulk_check(external_id="order-42")  # Опрашивайте до completed, partial или failed

report = client.bulk_report(order["id"])  # row,address,amount,status,reason,charged,transaction_id
```

С `webhook_url` API один раз отправит на него `POST`, когда заказ станет финальным. Проверьте заголовок `X-Signature` по сырому телу, прежде чем доверять запросу, например во Flask:

```python
from flask import abort, request

if not client.verify_webhook_signature(request.get_data(), request.headers.get("X-Signature", "")):
    abort(403)
```

## Обработка ошибок

SDK использует иерархию исключений для точной обработки ошибок:

```
TronZapException
├── ApiException             — ошибки API (code != 0 в ответе), включая HTTP 429 от API
├── InvalidRequestException  — неверные аргументы, отклонены до отправки (также ValueError)
├── NetworkException         — сетевые ошибки
│   ├── ConnectionException  — невозможно подключиться к серверу
│   ├── TimeoutException     — превышено время ожидания
│   └── SslException         — ошибки SSL/TLS
└── HttpException            — HTTP-ответы с кодом не 2xx
    ├── RateLimitException   — HTTP 429 без ответа API, например от прокси
    ├── UnauthorizedException — HTTP 401/403
    └── ServerException      — HTTP 5xx
```

### Пример

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

client = Client(api_token="ваш_api_token", api_secret="ваш_api_secret")

try:
    transaction = client.create_energy_transaction("TRX_ADDRESS", 65000, 1)
except ApiException as e:
    # Ошибка API (неверные параметры, недостаточно средств и т.д.)
    print(f"Ошибка API [{e.code}]: {e.message}")

    # Ключ-алиас ошибки, например "invalid_tron_address" или "invalid_tron_address.from_address"
    if e.error_key:
        print(f"Ключ ошибки: {e.error_key}")

    # Укажите его при обращении в поддержку
    print(f"ID запроса: {e.request_id}")

    # Данные, которые API вернул вместе с ошибкой, например новый расчёт для BULK_PRICE_CHANGED
    result = e.result

    if e.code == ErrorCode.RATE_LIMITED:
        # Сколько секунд ждать, если API это передал
        time.sleep(60 if e.retry_after is None else e.retry_after)

    if e.code == ErrorCode.INVALID_TRON_ADDRESS:
        print("Проверьте формат адреса TRON.")
except InvalidRequestException as e:
    print(f"Неверные аргументы: {e.message}")
except RateLimitException:
    print("Слишком много запросов. Замедлите частоту обращений.")
except UnauthorizedException:
    print("Неверный API-токен или подпись.")
except ServerException as e:
    print(f"Ошибка сервера TronZap [{e.status_code}].")
except HttpException as e:
    print(f"HTTP-ошибка [{e.status_code}]: {e.message}")
except TimeoutException:
    print("Превышено время ожидания запроса.")
except SslException as e:
    print(f"Ошибка SSL: {e.message}")
except ConnectionException as e:
    print(f"Ошибка подключения: {e.message}")
except NetworkException as e:
    print(f"Сетевая ошибка: {e.message}")
except TronZapException as e:
    print(f"Ошибка [{e.code}]: {e.message}")
```

### Коды ошибок API

| Код  | Константа                      | Описание |
|------|--------------------------------|----------|
| 1    | `AUTH_ERROR`                  | Ошибка аутентификации — неверный API-токен или подпись |
| 2    | `INVALID_SERVICE_OR_PARAMS`  | Неверный сервис или параметры |
| 5    | `WALLET_NOT_FOUND`           | Внутренний кошелёк не найден. Обратитесь в поддержку. |
| 6    | `INSUFFICIENT_FUNDS`         | Недостаточно средств |
| 10   | `INVALID_TRON_ADDRESS`       | Неверный TRON-адрес, или у адреса уже есть активная подписка |
| 11   | `INVALID_ENERGY_AMOUNT`      | Неверное количество энергии |
| 12   | `INVALID_DURATION`           | Неверная длительность |
| 20   | `TRANSACTION_NOT_FOUND`      | Транзакция/подписка не найдена |
| 21   | `CANNOT_STOP_SUBSCRIPTION`   | Невозможно остановить подписку, например, у неё есть лимит транзакций |
| 24   | `ADDRESS_NOT_ACTIVATED`      | Адрес не активирован |
| 25   | `ADDRESS_ALREADY_ACTIVATED`  | Адрес уже активирован |
| 30   | `AML_CHECK_NOT_FOUND`        | AML-проверка не найдена |
| 35   | `SERVICE_NOT_AVAILABLE`      | Сервис недоступен |
| 50   | `INVALID_BANDWIDTH_AMOUNT`   | Неверное количество bandwidth |
| 90   | `BULK_NOT_FOUND`             | Массовый заказ не найден |
| 91   | `BULK_EXPIRED`               | Расчёт истёк, рассчитайте заново |
| 92   | `BULK_PRICE_CHANGED`         | Цена изменилась; новый расчёт в `e.result` |
| 93   | `BULK_TOO_MANY_ITEMS`        | Больше 10 000 строк |
| 94   | `BULK_NO_VALID_ITEMS`        | Нет корректных строк; они в `e.result["rejected"]` |
| 95   | `BULK_RESOURCE_NOT_SUPPORTED`| Массово можно заказать только энергию |
| 96   | `PAYLOAD_TOO_LARGE`          | Слишком большое тело запроса (HTTP 413) |
| 429  | `RATE_LIMITED`               | Слишком много запросов; подождите `e.retry_after` секунд, если указано |
| 500  | `INTERNAL_SERVER_ERROR`      | Внутренняя ошибка сервера — обратитесь в поддержку |

## Разработка

```bash
pip install -r requirements-dev.txt -e .
pytest
```

Тесты работают с локальным HTTP/TLS-сервером и никогда не обращаются к реальному API. `examples/basic_usage.py` — smoke-тест против реального окружения; инструкции в начале файла.

## Поддержка

Для поддержки свяжитесь с нами в Telegram: [@tronzap_bot](https://t.me/tronzap_bot)

## Лицензия

Этот проект лицензирован под лицензией MIT - см. файл [LICENSE](LICENSE) для подробностей.
