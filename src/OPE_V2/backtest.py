#Main de test au moins pour le moment
import os
import polars as pl
from dotenv import load_dotenv

from bot.trading_bot import TradingBot
from event.event import EventDispatcher
from csv_data_provider import CSVDataProvider
from strategy.fix_order_strategy import FixOrderStrategy
from strategy.dumb_strategy import DumbStrategy
from bot.order.order_manager import OrderManager
from bot.position.position_manager import PositionManager
from bot.order.order_builder import OrderBuilder
from portfolio.portfolio import Portfolio

#IMPORT POUR LE TEST
from bot.order.order import  OrderSide

load_dotenv()
WD = os.getenv('WD')

event_dispatcher = EventDispatcher()
data_provider = CSVDataProvider(file_path=f'{WD}data/OPE_DATA/DATA_RAW_S_ORIGIN_test_code/data_raw_BTCUSDT_176.csv',
                                    event_dispatcher = event_dispatcher)

initial_money_balance = 1000
portfolio = Portfolio(initial_money_balance, event_dispatcher)
order_builder = OrderBuilder(portfolio)
order_manager = OrderManager(order_builder, event_dispatcher)
position_manager = PositionManager(event_dispatcher)

########## Mieux construire la pool -> @dataclass Pool ?? ##########
initial_crypto_price = data_provider.get_initial_data()['CloseCol']
######################################################################

########## Mieux construire les paramètres users##########
init_params = {
    'level': initial_crypto_price,
    'asset_qty' : 0.01 * initial_money_balance/initial_crypto_price,
    'side' : OrderSide.SHORT,
    'leverage' : 1.0,
    'tp_pct' : 0.01,
    'sl_pct' : 0.005
}

######################################################################

#strategy = FixOrderStrategy(event_dispatcher, init_params)
strategy = DumbStrategy(event_dispatcher, init_params)
trading_bot = TradingBot(event_dispatcher, data_provider)

trading_bot.run()
