import websocket
import json
import pandas as pd
import numpy as np
import ta
import asyncio
import threading
import time

# Initialize a DataFrame to store incoming tick data for each coin
data_frames = {}

# WebSocket message handler for tick data
def on_message(ws, message):
    """Handle incoming WebSocket messages with real-time trade data (tick data)."""
    try:
        json_message = json.loads(message)

        # Access the trade data from the 'data' key
        if 'data' in json_message:
            trade_data = json_message['data']
            symbol = trade_data['s']  # Get the symbol (coin)
            price = float(trade_data['p'])  # Trade price
            timestamp = pd.to_datetime(trade_data['T'], unit='ms')  # Trade time

            print(f"Received new tick for {symbol} at {timestamp}: price={price}")

            global data_frames
            if symbol not in data_frames:
                data_frames[symbol] = pd.DataFrame(columns=['timestamp', 'price'])

            # Create a new DataFrame for the incoming tick data
            new_data = pd.DataFrame({'timestamp': [timestamp], 'price': [price]})

            # Append the new tick data
            data_frames[symbol] = pd.concat([data_frames[symbol], new_data], ignore_index=True)

            # Keep only the most recent 1000 rows (tick data accumulates quickly)
            if len(data_frames[symbol]) > 1000:
                data_frames[symbol] = data_frames[symbol].iloc[-1000:]

            # Print out the current state of the DataFrame
            print(f"{symbol} DataFrame (last 5 ticks):")
            print(data_frames[symbol].tail())

            # Run analysis on the tick data asynchronously
            asyncio.run(process_signals(symbol))
        else:
            print(f"Unexpected message format: {json_message}")
    except Exception as e:
        print(f"Error in on_message: {e}")

def on_open(ws):
    print("WebSocket connection opened.")

def on_close(ws):
    print("WebSocket connection closed.")

def on_error(ws, error):
    print(f"WebSocket error: {error}")

# Function to start the WebSocket connection for multiple coins synchronously
def start_websocket(symbols):
    """Start the Binance WebSocket connection to stream real-time trade data (tick data) for multiple symbols."""
    streams = "/".join([f"{symbol.lower()}@trade" for symbol in symbols])
    ws_url = f"wss://stream.binance.com:9443/stream?streams={streams}"
    print(f"Connecting to {ws_url}...")
    
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_open=on_open,
                                on_close=on_close,
                                on_error=on_error)
    
    # Run WebSocket in a separate thread for handling multiple connections
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()

# Function to calculate RSI using the ta library (shortened period for HFT)
def calculate_rsi(data, period=3):  # Shortened RSI period
    """Calculate the RSI using tick prices."""
    rsi = ta.momentum.RSIIndicator(data['price'], window=period)
    return rsi.rsi()

# Function to calculate Hull Moving Average (HMA) with shorter periods for HFT
def calculate_hma(data, period=7):  # Shortened HMA period
    """Calculate Hull Moving Average (HMA) based on tick prices."""
    half_period = int(period / 2)
    sqrt_period = int(np.sqrt(period))
    
    # Weighted Moving Average (WMA) calculation using TA-Lib
    wma_half = ta.trend.WMAIndicator(data['price'], window=half_period).wma()
    wma_full = ta.trend.WMAIndicator(data['price'], window=period).wma()
    
    # Hull Moving Average (HMA) formula
    hma = ta.trend.WMAIndicator(2 * wma_half - wma_full, window=sqrt_period).wma()
    
    return hma

# Function to generate trade signals based on the shortened HMA and RSI periods
async def generate_trade_signals(symbol):
    """Generate Buy, Sell, Short signals based on HMA crossover and RSI filters (using tick data)."""
    global data_frames
    data = data_frames[symbol]
    
    if len(data) < 7:  # Ensure there is enough tick data for HMA(7)
        print(f"Not enough tick data for {symbol} yet ({len(data)} ticks)")
        return None

    # Calculate the RSI and HMA for the latest tick data (shortened periods)
    data['RSI'] = calculate_rsi(data, period=3)
    data['HMA_7'] = calculate_hma(data, period=7)
    data['HMA_14'] = calculate_hma(data, period=14)

    # Only consider the most recent row for signal generation
    latest_row = data.iloc[-1]
    
    # Check conditions for buy, sell, and short signals
    if latest_row['HMA_7'] > latest_row['HMA_14'] and 50 < latest_row['RSI'] < 65:
        return "BUY"
    elif latest_row['HMA_7'] < latest_row['HMA_14'] and 35 < latest_row['RSI'] < 45:
        return "SELL"
    elif latest_row['HMA_7'] < latest_row['HMA_14'] and latest_row['RSI'] > 35:
        return "SELL SHORT"
    elif latest_row['HMA_7'] > latest_row['HMA_14'] and latest_row['RSI'] < 35:
        return "EXIT SHORT"
    
    return None

# Asynchronous function to process signals (no trade execution here, just signal generation)
async def process_signals(symbol):
    """Process signals for the given symbol based on tick data."""
    signal = await generate_trade_signals(symbol)
    if signal:
        print(f"{symbol}: {signal}")
        # Here, the signal would be passed on to trade_management.py for execution

# Function to run everything
def main():
    """Main entry point to start WebSocket connections and process coins in parallel."""
    coins_to_analyze = ['DOGEUSDT', 'XRPUSDT', 'ADAUSDT', 'EOSUSDT', 'CVXUSDT', 'CFXUSDT', 'CRVUSDT']
    start_websocket(coins_to_analyze)

    # Keep the main thread alive while WebSocket threads run
    while True:
        time.sleep(10)

# Start the WebSocket with tick data stream
if __name__ == '__main__':
    main()
