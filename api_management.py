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
    {'api_key': 'N4bc8GJirpmDz7nStgnMSfMXDJeSLT14NNwY4IdQITcssnwLjovXORaVvqj3kJGJ', 'api_secret': 'U2JCvGxqG3lie0sPw7lwNlAmwjTUujL2C4WAQ7kRPndE5tEVu5CoCCO44UV9v3ko'},
    {'api_key': 'dja8XZ1JePZgVtWfMm8vuROFqsEOUtWJi4yCItUCc3Yh4QRiVZCCRKnBooHqYSjD', 'api_secret': 'XzPLzfy8TrLrHE89QLdhNvH4yBSFaX1cTnGaHPRl0JgF4M1kbzAiSrREAT7omjFM'},
    {'api_key': 'FU4toz09SttqMZDj7jl8ZIqoC1PMcpPELdH9i7d89fux7nhO7hjG9AORp3DJpa3V', 'api_secret': 'WC3pfe03BeWshfIXsbbeireEDTaBmwzAujlXN8hhhVUm5mR1fhThRZMRB8lbbIYS'},
    {'api_key': 'eCafNCA1l0ho2WJyWWHSHHAfugGU5Agg4t9VDGI8nbXpt4tIiPRuyaNXRPV7Fcux', 'api_secret': 'kkqYhovf9prO0IPxFI1cYUG8UGiqE6ftc7ypnxGfURwcGXSXPwOTSdhy8kFJkDZm'},
    {'api_key': 'UqgmsNC59dAJ2P2clsMZ3aIj2FxqEY9VtDPleKznTmmMjQJMt6qXD8oauh0JfleZ', 'api_secret': 'KDzMYwtwjVNT1eZHquTkKgQTTYen4OpvoZfwRoCvvtPSvaxuD6MaxOcow5XqMrDw'},
    {'api_key': 'zjaq003TtnHrHA6ciRFbq1s2NSMzMtOrJNhpd5yibplFbSU8obUwSME9a1k9g4vb', 'api_secret': 'rhmLA4meRfqRVxibP79Oud7i76v7aK1XmcMhpnP7ZiG96Np0s12qMqSOxWw6B9Y4'},
    {'api_key': 'B8v8T4ynN9D3lcQKsS75WrflCmgX4k3cNElCWAeGSOr1yTPzxvGCCZlfSK1ghLna', 'api_secret': 'F6dhx42c95eEPDBabEWQtlFWVoO9qLPDB7etdRRxuRD4de4G4A2lpl6KUzcfygpO'},
    {'api_key': 'Q27KjQCqESwO8dc2QwNnnVhOgd5LJBoSTCz8yx20zx0hnSbhDoMfaKpxy8tgaiFB', 'api_secret': '5nTNCXVQHW3eGvby3D1XrcUiG40IbMnSVHpVVhYW7xCn0pf2oHhu5Bh9xRblBl95'}
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
            # Call the API function with provided arguments
            result = api_function(client, *args, **kwargs)
            # Track API usage
            api_usage[api_key] += 1
            return result  # Return result on success

        except Exception as e:
            logging.error(f"Error with API Key {api_key}: {e}")
            print(f"Error with API Key {api_key}: {e}")
            time.sleep(delay * (2 ** attempt))  # Exponential backoff for retries
            attempt += 1

    return None  # Return None after max retry attempts
