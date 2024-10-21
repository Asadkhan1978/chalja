import time
import traceback
from api_management import make_api_call
from error_handling import handle_critical_error, send_critical_error_notification
from binance.client import Client

# Constants for managing capital and drawdown threshold
RESERVE_RATIO = 0.30  # 30% kept as margin reserve
DRAW_DOWN_THRESHOLD = 10  # Trigger wallet management if balance falls below 10 USDT

# Global variable to track initial balance for comparison
initial_balance = None

# Function to fetch USDT futures wallet balance
def fetch_futures_balance(client, asset="USDT"):
    """Fetch USDT balance from the futures wallet."""
    try:
        account_info = make_api_call(client.futures_account)
        if account_info:
            for asset_info in account_info['assets']:
                if asset_info['asset'] == asset:
                    return float(asset_info['availableBalance'])
    except Exception as e:
        error_message = f"Error fetching futures balance: {str(e)}"
        handle_critical_error("Critical error during balance fetching", traceback.format_exc())
        raise Exception(error_message)

# Function to fetch and display wallet balances
def fetch_and_display_wallet_balances(client):
    """Fetch and display wallet balances for USDT and BNB in spot and futures wallets."""
    global initial_balance  # Reference the global initial_balance
    try:
        # Fetch USDT and BNB balances from futures and spot wallets
        futures_balance = make_api_call(client.futures_account)
        usdt_spot_balance = make_api_call(client.get_asset_balance, asset='USDT')
        bnb_spot_balance = make_api_call(client.get_asset_balance, asset='BNB')

        usdt_futures = float(futures_balance['totalWalletBalance'])
        usdt_spot = float(usdt_spot_balance['free'])
        
        # Fetch BNB balance using client.futures_account_balance() method
        futures_balances = make_api_call(client.futures_account_balance)
        bnb_futures_balance = next(item for item in futures_balances if item['asset'] == 'BNB')['balance']

        bnb_spot = float(bnb_spot_balance['free'])

        # Initialize initial balance
        if initial_balance is None:
            initial_balance = usdt_futures
            print(f"Initialized with an initial futures balance of: {initial_balance} USDT")

        # Display the balances
        print(f"USDT Futures: {usdt_futures}, USDT Spot: {usdt_spot}")
        print(f"BNB Futures: {bnb_futures_balance}, BNB Spot: {bnb_spot}")
        
    except Exception as e:
        print(f"Error fetching wallet balances: {str(e)}")

# Function to manage wallet based on capital, reserve, and drawdown
def manage_wallet(client):
    """Manage wallet and check for drawdown or equity growth."""
    global initial_balance  # Reference the global initial_balance
    try:
        futures_balance = fetch_futures_balance(client)
        print(f"Current futures balance: {futures_balance} USDT")

        # Calculate the balance change
        balance_change = futures_balance - initial_balance

        # Check for drawdown or equity growth
        if balance_change < 0:
            print(f"Drawdown detected! Balance decreased by {-balance_change:.2f} USDT.")
            send_critical_error_notification(f"Drawdown detected: Balance decreased by {-balance_change:.2f} USDT. Current balance: {futures_balance} USDT")
            initial_balance = futures_balance  # Update balance after drawdown

        elif balance_change > 0:
            print(f"Equity growth detected! Balance increased by {balance_change:.2f} USDT.")
            send_critical_error_notification(f"Equity growth detected: Balance increased by {balance_change:.2f} USDT. Current balance: {futures_balance} USDT")
            initial_balance = futures_balance  # Update balance after equity growth

        else:
            print(f"No significant balance change detected: {futures_balance} USDT.")

        # Allocate capital
        margin_reserve = futures_balance * RESERVE_RATIO
        trading_capital = futures_balance - margin_reserve

        print(f"Margin reserve: {margin_reserve} USDT, Trading capital: {trading_capital} USDT")

        # Notify on capital allocation
        send_critical_error_notification(f"Updated Capital Allocation: Margin reserve={margin_reserve}, Trading capital={trading_capital}")

        return margin_reserve, trading_capital

    except Exception as e:
        error_message = f"Failed to manage wallet: {str(e)}"
        handle_critical_error("Critical error during wallet management", traceback.format_exc())
        raise Exception(error_message)

# Function to monitor drawdown and equity growth periodically
def periodic_wallet_check(client, interval=60):
    """Run wallet management system periodically every 'interval' seconds."""
    while True:
        try:
            manage_wallet(client)
        except Exception as e:
            print(f"Error during wallet management: {str(e)}")
        time.sleep(interval)

# End of file
