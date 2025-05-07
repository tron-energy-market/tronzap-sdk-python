# TronZap SDK para Python

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
    api_secret="tu_api_secret"
)

# Obtener servicios disponibles
services = client.get_services()
print(services)

# Obtener saldo de la cuenta
balance = client.get_balance()
print(balance)

# Estimar costo de energía para transferencia USDT
estimate = client.estimate_energy('DIRECCION_ORIGEN_TRX', 'DIRECCION_DESTINO_TRX', 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t')
print(estimate)

# Calcular costo de energía
calculation = client.calculate(
    address="DIRECCION_BILLETERA_TRON",
    energy=65150  # Cantidad recomendada para transferencias USDT
)
print(calculation)

# Crear transacción de energía
transaction = client.create_energy_transaction(
    address="DIRECCION_BILLETERA_TRON",
    energy_amount=65150, # Desde 60000
    duration=1, # Valores posibles 1 o 24 horas
    activate_address=True  # Si la dirección necesita activación
)
print(transaction)

# Verificar estado de la transacción
status = client.check_transaction(id="ID_TRANSACCION")
print(status)

# Obtener información de recarga directa
recharge_info = client.get_direct_recharge_info()
print(recharge_info)
```

## Características

- Obtener servicios disponibles
- Obtener saldo de la cuenta
- Calcular costo de energía
- Crear transacciones de activación de dirección
- Crear transacciones de compra de energía
- Verificar estado de transacciones
- Obtener información de recarga directa

## Requisitos

- Python 3.7 o superior
- requests >= 2.25.0

## Manejo de Errores

El SDK lanza `TronZapException` cuando la API devuelve un error. Cada excepción incluye las propiedades `.code` y `.message` para depurar y manejar casos específicos.

### Ejemplo

```python
from tronzap_sdk import Client, TronZapException, ErrorCode

client = Client(api_token="your_api_token", api_secret="your_api_secret")

try:
    balance = client.get_balance()
except TronZapException as e:
    if e.code == ErrorCode.AUTH_ERROR:
        print("Error de autenticación")
    elif e.code == ErrorCode.INVALID_SERVICE_OR_PARAMS:
        print("Servicio o parámetros inválidos")
    elif e.code == ErrorCode.WALLET_NOT_FOUND:
        print("Cartera interna no encontrada. Contacte con soporte.")
    elif e.code == ErrorCode.INSUFFICIENT_FUNDS:
        print("Fondos insuficientes")
    elif e.code == ErrorCode.INVALID_TRON_ADDRESS:
        print("Dirección TRON inválida")
    elif e.code == ErrorCode.INVALID_ENERGY_AMOUNT:
        print("Cantidad de energía inválida")
    elif e.code == ErrorCode.INVALID_DURATION:
        print("Duración inválida")
    elif e.code == ErrorCode.TRANSACTION_NOT_FOUND:
        print("Transacción no encontrada")
    elif e.code == ErrorCode.ADDRESS_NOT_ACTIVATED:
        print("Dirección no activada")
    elif e.code == ErrorCode.ADDRESS_ALREADY_ACTIVATED:
        print("La dirección ya está activada")
    elif e.code == ErrorCode.INTERNAL_SERVER_ERROR:
        print("Error interno del servidor")
    else:
        print(f"Error no manejado {e.code}: {e.message}")
```

### Códigos de Error

| Código | Constante                        | Descripción |
|--------|----------------------------------|-------------|
| 1      | `AUTH_ERROR`                    | Error de autenticación – Token API o firma inválida |
| 2      | `INVALID_SERVICE_OR_PARAMS`    | Servicio o parámetros inválidos |
| 5      | `WALLET_NOT_FOUND`             | Cartera interna no encontrada. Contacte con soporte. |
| 6      | `INSUFFICIENT_FUNDS`           | Fondos insuficientes |
| 10     | `INVALID_TRON_ADDRESS`         | Dirección TRON inválida |
| 11     | `INVALID_ENERGY_AMOUNT`        | Cantidad de energía inválida |
| 12     | `INVALID_DURATION`             | Duración inválida |
| 20     | `TRANSACTION_NOT_FOUND`        | Transacción no encontrada |
| 24     | `ADDRESS_NOT_ACTIVATED`        | Dirección no activada |
| 25     | `ADDRESS_ALREADY_ACTIVATED`    | La dirección ya está activada |
| 500    | `INTERNAL_SERVER_ERROR`        | Error interno del servidor – Contacta con soporte |


## Soporte

Para soporte, contáctanos en Telegram: [@tronzap_bot](https://t.me/tronzap_bot)

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.