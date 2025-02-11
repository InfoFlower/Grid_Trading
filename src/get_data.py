import requests
import time
import logging 

logging.basicConfig(level=logging.INFO)

class GetData:
    def __init__(self,cols):
        self.cols=cols

    def transfo_rep(self,rep):
        full_data=[]
        for i in rep :
            data={}
            for m,v in zip(self.cols,i):
                data[m]=v
            full_data.append(data)
        return full_data

    def get_first_available_date(self,symbol):
        base_url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": "1d",
            'startTime': 0,
            "limit": 1
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0][0]  # Return the timestamp of the first available data
        return None

    def get_market_cap_data(self,symbol):
        start_timestamp=self.get_first_available_date(symbol)
        if start_timestamp is None : logging.error(f"None timestamp for {symbol}, check the symbol")
        base_url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": "1s",
            "startTime": start_timestamp,
            "limit": 1000
        }
        with open(f'data/data_raw_{symbol}.csv', 'w') as f: f.write(','.join(self.cols) + '\n')
        current_timestamp = start_timestamp
        while current_timestamp < int(time.time() * 1000):
            params["startTime"] = current_timestamp
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                logging.info(f"Getting data for {symbol} from {current_timestamp}")
                data = response.json()
                with open(f'data/data_raw_{symbol}.csv','a') as f:
                    f.write('\n'.join([','.join([str(i) for i in x]) for x in data]))
                if data: current_timestamp = data[-1][0] + 1
                else : break
            else:
                break
        
    
    def __call__(self,symbol):
        logging.info(f"Getting data for {symbol}")
        return self.get_market_cap_data(symbol)

if __name__ == '__main__':
    cols=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
    symbol=['BTCUSDT','ADAUSDT','DOGEUSDT','DOTUSDT','ETHUSDT','SOLUSDT','XRPUSDT']
    appel=GetData(cols)
    for i in symbol:
        appel(i)