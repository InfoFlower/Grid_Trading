from datetime import datetime, timezone

from event.event import EventType, Event
from .order import Order
from strategy.strategy import StrategyType
from data.data_provider.market_data_cache import DataCache

class OrderBuilder:

    def __init__(self, data_cache : DataCache) -> None:
        self.data_cache = data_cache

    def build(self, strat_type : dict, order_params : dict, event_type : EventType) -> Order:
        """
        """
        current_candle = self.data_cache.get_market_candle
        current_candle_datetime = datetime.fromtimestamp(current_candle['TimeCol']/1000)

        if strat_type == StrategyType.FIX_ORDER:
            #####Procédure pour FIX_ORDER#######
            order_params['order_event_timestamp'] = current_candle_datetime
            order_params['order_event'] = event_type
            return Order(**order_params)
        
        elif strat_type == StrategyType.DUMB:
            #####Procédure pour DUMB#######
            order_params['order_event_timestamp'] = current_candle_datetime
            order_params['order_event'] = event_type
            return Order(**order_params)
        
    def modify(self, order : Order, event_type : EventType) -> Order:
        
        current_candle = self.data_cache.get_market_candle
        current_candle_datetime = datetime.fromtimestamp(current_candle['TimeCol']/1000)

        if event_type == EventType.ORDER_EXECUTED:
            
            order.order_event_timestamp = current_candle_datetime
            order.order_event = event_type
            return order
            
       
