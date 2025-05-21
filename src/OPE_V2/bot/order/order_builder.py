from datetime import datetime, timezone

from event.event import EventType, Event
from .order import Order
from strategy.strategy import StrategyType

class OrderBuilder:

    def __init__(self) -> None:
        pass


    def build(self, strat_type : dict, order_params : dict) -> Order :
        """
        """
        if strat_type == StrategyType.FIX_ORDER:
            #####Procédure pour FIX_ORDER#######
            order_params['created_at'] = int(datetime.now(timezone.utc).timestamp() * 1000)
            order_params['order_event'] = EventType.ORDER_CREATED
            return Order(**order_params)
        
        elif strat_type == StrategyType.DUMB:
            #####Procédure pour DUMB#######
            print(order_params)
            order_params['created_at'] = int(datetime.now(timezone.utc).timestamp() * 1000)
            order_params['order_event'] = EventType.ORDER_CREATED
            return Order(**order_params)
            
       
