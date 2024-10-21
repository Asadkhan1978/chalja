import itertools
import time
import logging
from binance.client import Client

# Set up logging
logging.basicConfig(filename='api_errors.log', level=logging.ERROR)

# List of API keys and secrets
api_keys = [
    {'api_key': 'de0baLVpCBc7xwCq3WHv2V10A6WuLpOrWWv2UfeAhQx8Uw67gzs6oXYGY697PB2T', 'api_secret': 'TDTcaKB9HJTZZnfj3SBRuBkrZt0HODxCc1lVUdWjsmdS2mxRuiXw3cWRo3fVL7xL'},
    {'api_key': '26t5D3HqN8RJ4AgcHyZVW4azR6oWKc8JwNEKd2egJoY4oQx5BFh8xrQZOKeUqnjh', 'api_secret': 'RVnc5BpkAbvPUYWleLIqirBA4GKCaUey4PtHSEf8F8KOyl5MtpBdpokSRwdrr2vn'},
    # Add remaining API keys here...
]

# Rotates between API keys to avoid rate limits
api_iterator = itertools.cycle(api_keys)

# API rate limit usage tracking
api_usage = {key['api_key']: 0 for key in api_keys}
MAX_API_USAGE = 1000  # Example usage limit (set according to your rate limit needs)

# Get Binance client for the current API key
def get_binance_client():
    """Fetch Binance client using the next API key in the rotation."""
    current_key = next(api_iterator)
    return Client(current_key['api_key'], current_key['api_secret']), current_key['api_key']

# Wrapper for making API calls with retries and API key switching
def make_api_call(api_function, *args, retries=3, delay=2, **kwargs):
    """
    Makes an API call with retries and exponential backoff, switches API key if limit is hit.
    Args:
        api_function: The Binance API function to call.
        retries: Number of times to retry on failure.
        delay: Initial delay between retries (doubles on each retry).
    """
    attempt = 0
    while attempt < retries:
        client, api_key = get_binance_client()

        # Check if API key has exceeded the usage limit
        if api_usage[api_key] >= MAX_API_USAGE:
            print(f"API key {api_key} exceeded usage limit, switching to next API key...")
            continue  # Skip to next key without sleeping

        try:
            # Call the API function without extra positional arguments unless specified
            result = api_function(*args, **kwargs)
            # Track API usage
            api_usage[api_key] += 1
            return result  # Return result on success

        except Exception as e:
            logging.error(f"Error with API Key {api_key}: {e}")
            print(f"Error with API Key {api_key}: {e}")
            time.sleep(delay * (2 ** attempt))  # Exponential backoff for retries
            attempt += 1

    return None  # Return None after max retry attempts
