from typing import Dict, Any
from datetime import datetime

from .strategy import Strategy, StrategyType
from event.event import EventDispatcher, Event, EventType
from bot.position.position import Position
from bot.order.order import OrderSide

class DumbStrategy(Strategy):

    def __init__(self, event_dispatcher : EventDispatcher, params : Dict[str, Any]) -> None:

        super().__init__(event_dispatcher,params)
        self.strategy_type = StrategyType.DUMB
        self.event_dispatcher = event_dispatcher
        self.params = params

        event_dispatcher.add_listeners(EventType.INIT_MARKET_DATA, self.init_statement)
        event_dispatcher.add_listeners(EventType.POSITION_OPENED, self.create_statement)

    def init_statement(self, event : Event) -> None:
        
        orders_args = self.pre_create_orders_args(self.params['level'])
        
        for args in orders_args:
            
            data = {
                'type': self.strategy_type,
                'args':args
                }
            
            self.event_dispatcher.dispatch(Event(
                type = EventType.STRATEGY_MAKE_ORDER,
                data = data,
                timestamp = datetime.now()
            ))
        
    def create_statement(self, event : Event) -> None:

        opened_position : Position = event.data
        entry_price = opened_position.entry_price
        
        orders_args = self.pre_create_orders_args(entry_price)

        for args in orders_args:
            
            data = {
                'type': self.strategy_type,
                'args':args
                }
            
            self.event_dispatcher.dispatch(Event(
                type = EventType.STRATEGY_MAKE_ORDER,
                data = data,
                timestamp = datetime.now()
            ))

    
    def pre_create_orders_args(self, level) -> list[dict]:
        
        orders_args = []
        for side in (OrderSide.SHORT, OrderSide.LONG):
            
            orders_args.append(
                {
                    'level' : level*(1+(-1 if side == OrderSide.LONG else 1)*self.params['tp_pct']),
                    'asset_qty' : self.params['asset_qty'],
                    'side' :  side,
                    'leverage' : self.params['leverage'],
                    'tp_pct' : self.params['tp_pct'],
                    'sl_pct' : self.params['sl_pct']
                }
            )
        return orders_args