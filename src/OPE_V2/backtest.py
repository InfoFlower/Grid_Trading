from datetime import datetime
import polars as pl


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
                strategy : Strategy, 
                portfolio : Portfolio,
                event_dispatcher : EventDispatcher) -> None:
        
        self.event_dispatcher = event_dispatcher

        self.id : int = 0 #SHA1
        self.label_id : str = "AAA"
        #self.data = data_provider.data.clone()
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
        

        
    def equity(self, position : pl.DataFrame):

        left_join_data_X_position = self.data.join(position, left_on='Open time', right_on='PositionEventTimestamp', how='left')

        left_join_data_X_position.with_columns(
            [
                (pl.col('crypto_balance').fill_null(strategy='forward')).alias('crypto_balance'),
                (pl.col('money_balance').fill_null(strategy='forward')).alias('money_balance')
            ]
        )