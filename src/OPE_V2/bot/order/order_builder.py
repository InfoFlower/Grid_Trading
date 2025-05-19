from datetime import datetime, timezone

from event.event import EventType, Event
from .order import Order
from strategy.strategy import StrategyType
from portfolio.portfolio import Portfolio



class OrderBuilder:

    def __init__(self, portfolio : Portfolio) -> None:
        self.portfolio = portfolio

        #self.event_dispatcher = event_dispatcher

        #event_dispatcher.add_listeners(EventType.STRATEGY_MAKE_ORDER, self.build_order)

    def build(self, event : Event) -> Order :
        """
        """
        strat_type = event.data['type']
        order_params = event.data['args']

        margin = order_params['level'] * order_params['asset_qty']

        if self.portfolio.enough_money(margin):
            
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
            
        else:
            raise ValueError(f'Not enough money: wanted = {margin}> available={self.portfolio.money_balance}')
            

