#Main de test au moins pour le moment
import os
import polars as pl
from dotenv import load_dotenv

from bot.trading_bot import TradingBot
from event import EventDispatcher
from csv_data_provider import CSVDataProvider

load_dotenv()
WD = os.getenv('WD')

event_dispatcher = EventDispatcher()
data_provider = CSVDataProvider(file_path=f'{WD}data/OPE_DATA/DATA_RAW_S_ORIGIN_test_code/data_raw_BTCUSDT_176.csv',
                                    event_dispatcher = event_dispatcher)

########## Mieux construire la pool -> @dataclass Pool ?? ##########
initial_pool_value = 1000
crypto_initial_price = data_provider.get_initial_data()['CloseCol']
pool = {'money_balance': initial_pool_value/2, 'crypto_balance' : initial_pool_value/2/crypto_initial_price}
######################################################################

trading_bot = TradingBot(event_dispatcher, data_provider, pool)

trading_bot.run()
