#Main de test au moins pour le moment
import os
import polars as pl
from dotenv import load_dotenv

from bot.trading_bot import TradingBot
from event import EventDispatcher
from csv_data_provider import CSVDataProvider
from strategy.fix_order_strategy import FixOrderStrategy

#IMPORT POUR LE TEST
from bot.order import OrderEvent, OrderSide

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

user_params = {
    'level': crypto_initial_price+200,
    'asset_qty' : 0.01* pool['crypto_balance'],
    'side' : OrderSide.SELL,
    'leverage' : 0.0
}

strategy = FixOrderStrategy(event_dispatcher, user_params)
trading_bot = TradingBot(event_dispatcher, data_provider, pool)

trading_bot.run()
