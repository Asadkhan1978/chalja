# Function to fetch and display only USDT and BNB balances from spot and futures wallets
def fetch_and_display_wallet_balances(client):
    try:
        # Fetch USDT and BNB balances from futures wallet
        futures_balance = client.futures_account_balance()
        spot_balances = client.get_account()["balances"]

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
        print(f"Error fetching balances: {e}")
