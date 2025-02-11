import requests
import time

def get_binance_historical_data(crypto_list, interval="1s"):
    base_url = "https://api.binance.com/api/v3/klines"
    data_dict = {}
    limit = 1000  # Maximum number of records per request

    for crypto in crypto_list:
        data_dict[crypto] = []
        end_time = int(time.time() * 1000)  # Current time in milliseconds
        start_time = 0  # Start from the earliest available data

        while True:
            params = {
                "symbol": crypto,
                "interval": interval,
                "startTime": start_time,
                "endTime": end_time,
                "limit": limit
            }
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if not data:
                    break
                data_dict[crypto].extend(data)
                start_time = data[-1][0] + 1  # Move to the next timestamp
            else:
                data_dict[crypto] = f"Error {response.status_code}: {response.text}"
                break

    return data_dict

# Example usage
crypto_list = ["BTCUSDT"]
data = get_binance_historical_data(crypto_list)
print(data)