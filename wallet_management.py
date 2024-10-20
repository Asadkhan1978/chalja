from error_handling import make_safe_api_call, handle_critical_error

# Function to fetch and display USDT and BNB balances from spot and futures wallets
def fetch_and_display_wallet_balances(client):
    try:
        # Fetch USDT and BNB balances from futures wallet
        futures_balance = make_safe_api_call(client.futures_account_balance)
        spot_account = make_safe_api_call(client.get_account)

        # Ensure valid responses from both API calls
        if futures_balance is None or spot_account is None:
            raise Exception("Failed to retrieve balances")

        # Extract balances from the spot account
        spot_balances = spot_account['balances']

        # Extract USDT and BNB balances from futures wallet
        usdt_futures = next(item for item in futures_balance if item["asset"] == "USDT")["balance"]
        bnb_futures = next(item for item in futures_balance if item["asset"] == "BNB")["balance"]

        # Extract USDT and BNB balances from spot wallet
        usdt_spot = next(item for item in spot_balances if item["asset"] == "USDT")["free"]
        bnb_spot = next(item for item in spot_balances if item["asset"] == "BNB")["free"]

        # Display USDT and BNB balances on the console
        print(f"USDT Futures: {usdt_futures}, USDT Spot: {usdt_spot}")
        print(f"BNB Futures: {bnb_futures}, BNB Spot: {bnb_spot}")

    except Exception as e:
        # Handle any errors by sending a critical error notification
        handle_critical_error("Error fetching wallet balances", e)
