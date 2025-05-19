from typing import Dict, Any
from datetime import datetime
import random

from .strategy import Strategy, StrategyType
from event.event import EventDispatcher, Event, EventType
from bot.position.position import Position
from bot.order.order import OrderSide

class FixOrderStrategy(Strategy):

    # De quels arguments une stratégie a-t-elle tout le temps besoin?

    # Pour la fix order ---> TEST :  seul user_params qui sont enfaites les ordres à créer à l'initialisation
    def __init__(self, event_dispatcher : EventDispatcher, order_params : Dict[str, Any]): #faire user_params.py???

        self.strategy_type = StrategyType.FIX_ORDER
        self.event_dispatcher = event_dispatcher
        self.order_params = order_params


        event_dispatcher.add_listeners(EventType.INIT_MARKET_DATA, self.init_statement)
        event_dispatcher.add_listeners(EventType.POSITION_CLOSED, self.create_statement)

    
    def init_statement(self, event : Event):

        data = {
            'type' : self.strategy_type,
            'args' : self.order_params
        }

        self.event_dispatcher.dispatch(Event(
            type = EventType.STRATEGY_MAKE_ORDER,
            data = data,
            timestamp = datetime.now()
        ))

    def create_statement(self, event : Event) -> None:

        print(event)
        closed_position : Position = event.data
        close_price = closed_position.close_price
        args = {
            'level' : close_price*(1+self.order_params['tp_pct']),
            'asset_qty' : self.order_params['asset_qty'],
            'side' : random.choice([OrderSide.LONG, OrderSide.SHORT]),
            'leverage' : self.order_params['leverage'],
            'tp_pct' : self.order_params['tp_pct'],
            'sl_pct' : self.order_params['sl_pct']
        }
        data = {
            'type' : self.strategy_type,
            'args' : args
        }

        self.event_dispatcher.dispatch(Event(
            type = EventType.STRATEGY_MAKE_ORDER,
            data = data,
            timestamp = datetime.now()
        ))



# def create_condition(order, **pre_order) -> Callable[[Order:]]:
#     return order.level == other_order


