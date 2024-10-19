from api_management import make_api_call

# Function to fetch and display USDT and BNB balances
def fetch_and_display_wallet_balances(client):
    try:
        # Fetch USDT and BNB balances from futures, spot, and funding wallets
        futures_balance = client.futures_account_balance()
        spot_balance = client.get_asset_balance(asset='USDT')
        funding_balance = client.get_funding_wallet()

        # Extract balances from responses
        usdt_futures = next(item for item in futures_balance if item["asset"] == "USDT")["balance"]
        usdt_spot = spot_balance['free']
        usdt_funding = next(item for item in funding_balance if item["asset"] == "USDT")["free"]

        bnb_futures = next(item for item in futures_balance if item["asset"] == "BNB")["balance"]
        bnb_spot = client.get_asset_balance(asset='BNB')['free']
        bnb_funding = next(item for item in funding_balance if item["asset"] == "BNB")["free"]

        # Display balances on the console
        print(f"USDT Futures: {usdt_futures}, USDT Spot: {usdt_spot}, USDT Funding: {usdt_funding}")
        print(f"BNB Futures: {bnb_futures}, BNB Spot: {bnb_spot}, BNB Funding: {bnb_funding}")

        # You can also send these balances to a Telegram bot here if needed
    except Exception as e:
        print(f"Error fetching balances: {e}")

