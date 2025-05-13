from datetime import datetime, timezone

from event.event import EventType, Event
from .order import Order
from strategy.strategy import StrategyType



class OrderBuilder:

    def __init__(self) -> None:
        pass

        #self.event_dispatcher = event_dispatcher

        #event_dispatcher.add_listeners(EventType.STRATEGY_MAKE_ORDER, self.build_order)

    def build(self, event : Event) -> Order :
        """
        """
        strat_type = event.data['type']
        order_params = event.data['args']

        if strat_type == StrategyType.FIX_ORDER:
            #####Procédure pour FIX_ORDER#######
            order_params['created_at'] = int(datetime.now(timezone.utc).timestamp() * 1000)
            order_params['order_event'] = EventType.ORDER_CREATED
            return Order(**order_params)
        

