# Alquiler de Energía Tron vía API
## SDK Python por TronZap.com

[English](https://github.com/tron-energy-market/tronzap-sdk-python/blob/main/README.md) | **[Español](https://github.com/tron-energy-market/tronzap-sdk-python/blob/main/README.es.md)** | [Português](https://github.com/tron-energy-market/tronzap-sdk-python/blob/main/README.pt-br.md) | [Русский](https://github.com/tron-energy-market/tronzap-sdk-python/blob/main/README.ru.md)

SDK oficial en Python para la API de TronZap.
Este SDK permite integrar fácilmente los servicios de TronZap para alquilar energía TRON.

TronZap.com permite [comprar energía TRON](https://tronzap.com/), reduciendo significativamente las comisiones en transferencias de USDT (TRC20).

👉 [Regístrate para obtener una clave API](https://tronzap.com) para comenzar a usar la API de TronZap e integrarla a través del SDK.

## Instalación

```bash
pip install tronzap-sdk
```

## Inicio Rápido

```python
from tronzap_sdk import Client

# Inicializar el cliente
client = Client(
    api_token="tu_api_token",
    api_secret="tu_api_secret",
    timeout=30,  # Segundos, opcional; 30 por defecto
)

# Obtener servicios disponibles
services = client.get_services()
print(services)

# Obtener saldo de la cuenta
balance = client.get_balance()
print(balance)

# Obtener información de la dirección (recursos y saldos)
address_info = client.get_address_info("TRX_ADDRESS")
print(address_info)

# Estimar costo de energía para transferencia USDT
estimate = client.estimate_energy('DIRECCION_ORIGEN_TRX', 'DIRECCION_DESTINO_TRX')
print(estimate)

# Calcular costo de energía
calculation = client.calculate(
    address="DIRECCION_BILLETERA_TRON",
    energy=65000  # Cantidad recomendada para transferencias USDT
)
print(calculation)

# Crear transacción de energía
transaction = client.create_energy_transaction(
    address="DIRECCION_BILLETERA_TRON",
    energy_amount=65000,
    duration=1,  # Horas: una de las duraciones que devuelve get_services()
    activate_address=True  # Si la dirección necesita activación
)
print(transaction)

# Comprar ancho de banda
bandwidth = client.create_bandwidth_transaction(
    address="DIRECCION_BILLETERA_TRON",
    amount=345,
    external_id="bandwidth-1"
)
print(bandwidth)

# Comprar un paquete de recursos (energía + ancho de banda en una sola transacción)
bundle = client.create_resource_bundle_transaction(
    address="DIRECCION_BILLETERA_TRON",
    energy_amount=65000,
    bandwidth_amount=345,
    duration=1,
    external_id="bundle-1",
    activate_address=True
)
print(bundle)

# Verificar estado de la transacción
status = client.check_transaction(id="ID_TRANSACCION")
print(status)

# Crear chequeo AML
aml_check = client.create_aml_check(
    type="address",
    network="TRX",
    address="TXYZ1234567890EXAMPLEADDRESS"
)
print(aml_check)

# Verificar estado AML
aml_status = client.check_aml_status(id=aml_check["id"])
print(aml_status)

# Obtener información de recarga directa
recharge_info = client.get_direct_recharge_info()
print(recharge_info)
```

## Características

- Obtener servicios disponibles
- Obtener servicios AML
- Obtener saldo de la cuenta
- Obtener información de dirección (recursos y saldos)
- Calcular costo de energía
- Crear transacciones de activación de dirección
- Crear transacciones de compra de energía
- Crear transacciones de compra de ancho de banda
- Crear transacciones de paquete de recursos (energía + ancho de banda)
- Crear y seguir chequeos AML
- Iniciar, verificar, detener y listar suscripciones
- Verificar estado de transacciones
- Obtener información de recarga directa

## Requisitos

- Python 3.9 o superior
- requests >= 2.25.0

## Suscripciones

Una suscripción mantiene una dirección abastecida de energía para cada transacción hasta que se detiene o se agotan
sus días o transacciones. `get_subscriptions()` devuelve los planes indexados por su ID de suscripción; pase esa
clave, como `"unlimited_energy"`, a `start_subscription`, no el `id` numérico del plan. Iniciar una suscripción cobra
el precio inicial del plan.

```python
plans = client.get_subscriptions()
for subscription_id, plan in plans.items():
    print(subscription_id, plan["initial_price"], plan["price"])

subscription = client.start_subscription(
    subscription_id="unlimited_energy",
    address="TRON_WALLET_ADDRESS",
    duration_days=30,  # 0 para sin límite de tiempo
    transactions_limit=0,  # 0 para sin límite
    external_id="subscription-42"
)

subscription = client.check_subscription(external_id="subscription-42")

stopped = client.stop_subscription(id=subscription["id"])

history = client.get_subscription_history(page=1, per_page=10, status="active")
```

`duration_days` y `transactions_limit` valen 0 por defecto, lo que significa sin límite. Iniciar, verificar y detener
devuelven la suscripción con sus `params`; los elementos del historial traen en su lugar los contadores de uso
`transactions_used`, `energy_used` y `total_price`. Una suscripción con límite de transacciones no se puede detener
(`CANNOT_STOP_SUBSCRIPTION`).

## Manejo de Errores

El SDK utiliza una jerarquía de excepciones para un manejo preciso de errores:

```
TronZapException
├── ApiException             — errores a nivel de API (code != 0 en la respuesta)
├── InvalidRequestException  — argumentos inválidos, rechazados antes del envío (también es ValueError)
├── NetworkException         — errores de red/conectividad
│   ├── ConnectionException  — no se pudo conectar al servidor
│   ├── TimeoutException     — tiempo de espera agotado
│   └── SslException         — errores SSL/TLS
└── HttpException            — respuestas HTTP no 2xx
    ├── RateLimitException   — HTTP 429 Too Many Requests
    ├── UnauthorizedException — HTTP 401/403
    └── ServerException      — errores HTTP 5xx
```

### Ejemplo

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
    InvalidRequestException,
    ErrorCode,
)

client = Client(api_token="tu_api_token", api_secret="tu_api_secret")

try:
    transaction = client.create_energy_transaction("TRX_ADDRESS", 65000, 1)
except ApiException as e:
    # Error a nivel de API (parámetros inválidos, fondos insuficientes, etc.)
    print(f"Error API [{e.code}]: {e.message}")

    # Clave alias del error, p.ej. "invalid_tron_address" o "invalid_tron_address.from_address"
    if e.error_key:
        print(f"Clave de error: {e.error_key}")

    # Indícalo al contactar con soporte
    print(f"ID de solicitud: {e.request_id}")

    if e.code == ErrorCode.INVALID_TRON_ADDRESS:
        print("Revisa el formato de la dirección TRON.")
except InvalidRequestException as e:
    print(f"Argumentos inválidos: {e.message}")
except RateLimitException:
    print("Demasiadas solicitudes. Reduce la frecuencia.")
except UnauthorizedException:
    print("Token API o firma inválidos.")
except ServerException as e:
    print(f"Error del servidor TronZap [{e.status_code}].")
except HttpException as e:
    print(f"Error HTTP [{e.status_code}]: {e.message}")
except TimeoutException:
    print("Tiempo de espera agotado.")
except SslException as e:
    print(f"Error SSL: {e.message}")
except ConnectionException as e:
    print(f"Error de conexión: {e.message}")
except NetworkException as e:
    print(f"Error de red: {e.message}")
except TronZapException as e:
    print(f"Error [{e.code}]: {e.message}")
```

### Códigos de Error

| Código | Constante                        | Descripción |
|--------|----------------------------------|-------------|
| 1      | `AUTH_ERROR`                    | Error de autenticación – Token API o firma inválida |
| 2      | `INVALID_SERVICE_OR_PARAMS`    | Servicio o parámetros inválidos |
| 5      | `WALLET_NOT_FOUND`             | Cartera interna no encontrada. Contacte con soporte. |
| 6      | `INSUFFICIENT_FUNDS`           | Fondos insuficientes |
| 10     | `INVALID_TRON_ADDRESS`         | Dirección TRON inválida, o la dirección ya tiene una suscripción activa |
| 11     | `INVALID_ENERGY_AMOUNT`        | Cantidad de energía inválida |
| 12     | `INVALID_DURATION`             | Duración inválida |
| 20     | `TRANSACTION_NOT_FOUND`        | Transacción/suscripción no encontrada |
| 21     | `CANNOT_STOP_SUBSCRIPTION`     | No se puede detener la suscripción, p. ej. tiene un límite de transacciones |
| 24     | `ADDRESS_NOT_ACTIVATED`        | Dirección no activada |
| 25     | `ADDRESS_ALREADY_ACTIVATED`    | La dirección ya está activada |
| 30     | `AML_CHECK_NOT_FOUND`          | Chequeo AML no encontrado |
| 35     | `SERVICE_NOT_AVAILABLE`        | Servicio no disponible |
| 50     | `INVALID_BANDWIDTH_AMOUNT`     | Cantidad de ancho de banda inválida |
| 500    | `INTERNAL_SERVER_ERROR`        | Error interno del servidor – Contacta con soporte |


## Desarrollo

```bash
pip install -r requirements-dev.txt -e .
pytest
```

Las pruebas se ejecutan contra un servidor HTTP/TLS local y nunca llaman a la API real. `examples/basic_usage.py` es una prueba de humo contra un entorno real; las instrucciones están al principio del archivo.

## Soporte

Para soporte, contáctanos en Telegram: [@tronzap_bot](https://t.me/tronzap_bot)

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
