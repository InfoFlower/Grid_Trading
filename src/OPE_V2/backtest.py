from datetime import datetime


from data.data_provider.csv_data_provider import CSVDataProvider
from strategy.strategy import Strategy, StrategyType
from portfolio.portfolio import Portfolio
from event.event import EventDispatcher, Event, EventType

class Backtest:

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
                strategy : Strategy, portfolio : Portfolio,
                event_dispatcher : EventDispatcher) -> None:
        
        self.event_dispatcher = event_dispatcher

        self.id : int = 0 #SHA1
        self.label_id : str = "AAA"
        self.historical_start_timestamp : int = data_provider.initial_data['TimeCol']
        self.historical_end_timestamp : int = data_provider.last_data['TimeCol']
        self.pair : str = data_provider.pair
        self.strategy_name : str = strategy.strategy_name
        self.strategy_type : StrategyType = strategy.strategy_type
        self.strategy_params : dict = strategy.params
        self.initial_money : float = portfolio.initial_money
        self.technical_start_timestamp : datetime = datetime.now()
        #self.technical_end_timestamp : datetime = datetime.now()

        self.event_dispatcher.dispatch(Event(
                            type = EventType.INIT_BACKTEST,
                            data = self,
                            timestamp = datetime.now()
                        ))