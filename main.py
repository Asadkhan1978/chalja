from api_management import get_binance_client
from wallet_management import fetch_and_display_wallet_balances

# Main function to initiate the bot
if __name__ == "__main__":
    # Get Binance client
    client, _ = get_binance_client()

    # Fetch and display wallet balances (only pass client)
    fetch_and_display_wallet_balances(client)
