"""
Basic example of using the TronZap SDK
"""
import sys
import os
sys.path.append(os.path.abspath("../src"))

from tronzap_sdk import Client

def main():
    # Initialize the client
    client = Client(
        api_token="YOUR_API_TOKEN",
        api_secret="YOUR_API_SECRET"
    )

    try:
        # Get available services
        print("Available services:")
        services = client.get_services()
        print(services)

        # Get account balance
        print("\nAccount balance:")
        balance = client.get_balance()
        print(balance)

        # Estimate energy amount for a USDT transfer
        print("\nEstimating energy amount:")
        estimate = client.estimate_energy(
            from_address="TRON_WALLET_ADDRESS",
            to_address="TRON_WALLET_ADDRESS",
            contract_address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
        )
        print(estimate)

        # Calculate energy cost for a USDT transfer
        print("\nCalculating energy cost:")
        calculation = client.calculate(
            address="TRON_WALLET_ADDRESS",
            energy=131000  # Recommended amount for USDT transfers
        )
        print(calculation)

        # Create energy transaction
        print("\nCreating energy transaction:")
        transaction = client.create_energy_transaction(
            address="TRON_WALLET_ADDRESS",
            energy_amount=131000, # From 32000
            duration=1, # Possible values: 1 or 24 hours
            activate_address=True
        )
        print(transaction)

        # Check transaction status
        print("\nChecking transaction status:")
        status = client.check_transaction(id=transaction["id"])
        print(status)

        # Get direct recharge information
        print("\nDirect recharge information:")
        recharge_info = client.get_direct_recharge_info()
        print(recharge_info)

    except Exception as e:
        print(f"Error occurred on line {e.__traceback__.tb_lineno}: {str(e)}")
        print(f"Error message: {e}")
        print(f"Error code: {getattr(e, 'code', 'N/A')}")

if __name__ == "__main__":
    main()