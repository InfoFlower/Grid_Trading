#Main de test au moins pour le moment
import os
from dotenv import load_dotenv

from bot.trading_bot import TradingBot
from event.event import EventDispatcher
from data.data_provider.csv_data_provider import CSVDataProvider
from strategy.dumb_strategy import DumbStrategy
from bot.order.order_manager import OrderManager
from bot.position.position_manager import PositionManager
from portfolio.portfolio import Portfolio
from data.data_provider.market_data_cache import DataCache
from data.data_writer.csv_data_writer import CSVDataWriter

#IMPORT POUR LE TEST
from bot.order.order import  OrderSide

load_dotenv()
WD = os.getenv('WD')

event_dispatcher = EventDispatcher()
data_provider = CSVDataProvider(file_path=f'{WD}data/OPE_DATA/DATA_RAW_S_ORIGIN_test_code/data_raw_BTCUSDT_176.csv',
                                    event_dispatcher = event_dispatcher)
csv_data_writer = CSVDataWriter(event_dispatcher)
data_cache = DataCache(event_dispatcher)
########## Mieux construire les paramètres users##########
initial_money_balance = 1000
tolerance_pct = 0.005
##########################################################
portfolio = Portfolio(initial_money_balance, event_dispatcher)
order_manager = OrderManager(portfolio, tolerance_pct, event_dispatcher, data_cache)
position_manager = PositionManager(event_dispatcher, data_cache)

######################################################################
initial_crypto_price = data_provider.get_initial_data()['CloseCol']
######################################################################

########## Mieux construire les paramètres users ######################
init_params = {
    'level': initial_crypto_price,
    'asset_qty' : 0.001,#0.01 * initial_money_balance/initial_crypto_price,
    'side' : OrderSide.SHORT,
    'leverage' : 1.0,
    'tp_pct' : 0.01,
    'sl_pct' : 0.005
}

######################################################################

strategy = DumbStrategy(event_dispatcher, init_params)
trading_bot = TradingBot(event_dispatcher, data_provider)

trading_bot.run()