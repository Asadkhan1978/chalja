import traceback
from api_management import get_binance_client
from wallet_management import fetch_and_display_wallet_balances
from error_handling import make_safe_api_call, send_trade_alert, handle_critical_error, send_critical_error_email

# Function to fetch symbol info and determine precision and minimum notional value
def get_symbol_info(symbol, client):
    """Retrieve symbol precision and filters."""
    exchange_info = client.futures_exchange_info()
    for s in exchange_info['symbols']:
        if s['symbol'] == symbol:
            min_notional = None
            for f in s['filters']:
                if f['filterType'] == 'MIN_NOTIONAL':
                    min_notional = float(f['notional'])
                    break
            if min_notional is None:
                raise ValueError(f"'minNotional' filter not found for {symbol}")
            return s, min_notional
    raise ValueError(f"Symbol {symbol} not found.")

# Function to round the value to the required precision
def round_to_precision(value, precision):
    """Round the value to the required precision."""
    return float(f"{value:.{precision}f}")

# Function to fetch USDT balance from the futures wallet
def get_usdt_futures_balance(client):
    """Fetch the USDT balance from the futures wallet."""
    account_info = make_safe_api_call(client.futures_account)
    if account_info:
        for asset in account_info['assets']:
            if asset['asset'] == 'USDT':
                return float(asset['availableBalance'])
    raise Exception("Failed to fetch USDT Futures balance.")

# Function to execute a trade with error handling and symbol-specific notional value check
def execute_trade(client, symbol, side):
    try:
        # Fetch available USDT balance in the futures wallet
        available_usdt = get_usdt_futures_balance(client)
        print(f"Available USDT balance: {available_usdt} USDT")

        # Fetch symbol info for precision and filters
        symbol_info, min_notional = get_symbol_info(symbol, client)
        quantity_precision = symbol_info['quantityPrecision']
        price_precision = symbol_info['pricePrecision']
        min_qty = float(symbol_info['filters'][2]['minQty'])

        # Check if available balance meets min_notional
        if available_usdt < min_notional:
            raise ValueError(f"Insufficient balance to meet minimum notional value: {min_notional} USDT required, but only {available_usdt} USDT available.")
        
        # Get current price of the symbol
        entry_price = float(client.futures_symbol_ticker(symbol=symbol)['price'])
        print(f"Current price of {symbol}: {entry_price}")

        # Calculate quantity based on available balance and entry price
        quantity = round_to_precision(available_usdt / entry_price, quantity_precision)
        print(f"Calculated quantity for {symbol}: {quantity}")

        # Ensure quantity meets the minimum requirement
        if quantity < min_qty:
            raise ValueError(f"Quantity {quantity} is below the minimum allowed: {min_qty}")

        # Simulate the order without placing it
        print(f"Simulating order: symbol={symbol}, side={side}, quantity={quantity}, price={entry_price}")
        print(f"Simulation successful: {side} {quantity} {symbol} at {entry_price} USDT")

        # Simulate trade alert without placing a real order
        message = f"Simulated trade: {side} {quantity} {symbol} at {entry_price} USDT"
        send_trade_alert(message)

    except Exception as e:
        error_message = f"Failed to execute trade: {str(e)}"
        print(f"Error: {error_message}")
        error_details = traceback.format_exc()
        handle_critical_error(f"Critical error during trade execution: {str(e)}", error_details)

# Main execution function
if __name__ == "__main__":
    try:
        print("Initializing Binance client...")
        client, _ = get_binance_client()

        print("Fetching and displaying wallet balances...")
        fetch_and_display_wallet_balances(client)

        # Execute a trade for the given symbol
        print("Executing trade...")
        symbol = "GMTUSDT"  # Replace with the coin symbol you want to trade
        side = "BUY"  # Can be "BUY" or "SELL" depending on the strategy

        execute_trade(client, symbol, side)

        print("Sending test email...")
        send_critical_error_email("Test Email", "This is a test error message to verify email functionality.")

        print("Finished execution.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        error_details = traceback.format_exc()
        handle_critical_error("Unexpected error in main execution", error_details)
