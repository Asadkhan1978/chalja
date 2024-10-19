from api_management import get_binance_client
from wallet_management import fetch_and_display_wallet_balances
from error_handagement.py`_ import make_safe_api_call, send_trade_alert, handle_critical_error

# Example function to execute a trade with error handling and notifications
def execute_trade(client, symbol, side, quantity):
    try:
        # Place the order using a safe API call
        order = make_safe_api_call(
            client.futures_create_order,
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity
        )
        if order:
            # If order is successful, send a trade alert
            message = f"Trade executed: {side} {quantity} {symbol}"
            print(message)
            send_trade_alert(message)
        else:
            # Handle order execution failure
            raise Exception(f"Failed to execute trade for {symbol}")
    except Exception as e:
        handle_critical_error("Critical error during trade execution", e)

# Main execution function
if __name__ == "__main__":
    try:
        # Initialize Binance client
        client, _ = get_binance_client()

        # Fetch and display wallet balances (USDT and BNB)
        fetch_and_display_wallet_balances(client)

        # Execute a sample trade (this can be replaced with actual trading logic)
        symbol = "BTCUSDT"
        side = "BUY"
        quantity = 0.001  # Adjust based on your trading requirements

        # Execute the trade and handle any errors
        execute_trade(client, symbol, side, quantity)

    except Exception as e:
        # Handle unexpected errors that occur in the main execution
        handle_critical_error("Unexpected error in main execution", e)
