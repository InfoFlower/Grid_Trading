#Main de test au moins pour le moment
import os
from enum import Enum
from dotenv import load_dotenv

from trading_bot import TradingBot
from event.event import EventDispatcher
from data.data_provider.csv_data_provider import CSVDataProvider
from strategy.dumb_strategy import DumbStrategy
from bot.order.order_manager import OrderManager
from bot.position.position_manager import PositionManager
from portfolio.portfolio import Portfolio
from data.data_provider.market_data_cache import DataCache
from data.data_writer.csv_data_writer import CSVDataWriter
from backtest import Backtest

#IMPORT POUR LE TEST
from bot.order.order import  OrderSide

load_dotenv()
WD = os.getenv('WD')

event_dispatcher = EventDispatcher()
data_provider = CSVDataProvider(file_path=f'{WD}data/OPE_DATA/data_raw_BTCUSDT_176_50k_manuel.csv',
                                    event_dispatcher = event_dispatcher)

########## USER (FAIRE UN USER, pour rentrer les params (strat et backtest) ######################
initial_money_balance = 1000
tolerance_pct = 0.005

initial_crypto_price = data_provider.initial_data['CloseCol']

strat_params = {
    'level': initial_crypto_price,
    'asset_qty' : 0.001,#0.01 * initial_money_balance/initial_crypto_price,
    'leverage' : 1.0,
    'tp_pct' : 0.01,
    'sl_pct' : 0.005
}

######################################################################




csv_data_writer = CSVDataWriter(event_dispatcher)
data_cache = DataCache(event_dispatcher)
portfolio = Portfolio(initial_money_balance, event_dispatcher)
order_manager = OrderManager(portfolio, tolerance_pct, event_dispatcher, data_cache)
position_manager = PositionManager(event_dispatcher, data_cache)

strategy = DumbStrategy(event_dispatcher, strat_params)
backtest = Backtest(data_provider, strategy, portfolio, event_dispatcher)
trading_bot = TradingBot(event_dispatcher, data_provider)

trading_bot.run()