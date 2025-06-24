import os
from datetime import datetime
from dotenv import load_dotenv
import polars as pl
load_dotenv()
WD = os.getenv('WD')


from data.data_provider.csv_data_provider import CSVDataProvider
from strategy.strategy import Strategy, StrategyType
from portfolio.portfolio import Portfolio
from event.event import EventDispatcher, Event, EventType

class Backtest:

    BACKTEST_OPE_DATA = f"{WD}src/OPE_V2/data/BACKTEST_OPE_DATA/"


    # id : int
    # label_id : str
    # historical_start_timestamp : int  -- data_provider
    # historical_end_timestamp : int  -- data_provider
    # pair : str -- data_provider
    # strategy_name : str -- strategy
    # strategy_type : str -- strategy
    # strategy_params : str -- strategy (user)
    # initial_money : float -- strategy (user)
    # technical_start_timestamp : datetime
    # technical_end_timestamp : datetime

    def __init__(self, data_provider : CSVDataProvider,
                strategy : Strategy, 
                portfolio : Portfolio,
                event_dispatcher : EventDispatcher) -> None:
        
        self.event_dispatcher = event_dispatcher
        self.data_provider = data_provider

        self.id : int = 0 #SHA1
        self.label_id : str = "AAA"
        self.historical_start_timestamp : int = data_provider.initial_data['TimeCol']
        self.historical_end_timestamp : int = data_provider.last_data['TimeCol']
        self.pair : str = data_provider.pair
        self.strategy_name : str = strategy.strategy_name
        self.strategy_type : StrategyType = strategy.strategy_type
        self.strategy_params : dict = strategy.params
        self.initial_money : float = portfolio.initial_cash
        self.technical_start_timestamp : datetime = datetime.now()
        #self.technical_end_timestamp : datetime = datetime.now()

        event_dispatcher.add_listeners(EventType.END_MARKET_DATA, self.compute_kpi)

        event_dispatcher.dispatch(Event(
                            type = EventType.INIT_BACKTEST,
                            data = self,
                            timestamp = datetime.now()
                        ))
        
    def compute_kpi(self, event : Event):
        print("BACKTEST TERMINÉ")

        self.load_data()

    def load_data(self):
        #########################       SQL LITE ????     ##############################
        self.data = self.data_provider.data.clone().select(['TimeCol', 'OpenCol','CloseCol','LowCol','HighCol'])
        self.order = pl.read_csv(f"{self.BACKTEST_OPE_DATA}ORDER.csv")
        self.position = pl.read_csv(f"{self.BACKTEST_OPE_DATA}POSITION.csv")
        self.portfolio = pl.read_csv(f"{self.BACKTEST_OPE_DATA}PORTFOLIO.csv")
        ################################################################################


    
    