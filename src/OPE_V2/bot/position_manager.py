from typing import Dict, Any
from datetime import datetime, timezone

from .position import Position, PositionSide
from event.event import EventDispatcher, Event, EventType

from .order import Order, OrderSide



class PositionManager:

    def __init__(self, event_dispatcher : EventDispatcher) -> None:

        self.event_dispatcher = event_dispatcher
        self.position_book : Dict[int, Position] = {}

        event_dispatcher.add_listeners(EventType.ORDER_EXECUTED, self.construct_position)

    def construct_position(self, event : Event) -> None:

        """
        Les params de l'ouverture d'une position sont passés depuis les attributs d'un Order
        
        class Order:
        
            id : int  = field(init=False)
            created_at : int
            level : float
            asset_qty : float
            side : OrderSide
            leverage : float
            order_event : EventType
            executed_at : Optional[int] = None
            tp_pct: Optional[float] = None
            sl_pct : Optional[float] = None

        class Position:

            id : int  = field(init=False)
            entry_at : int
            entry_price : float
            asset_qty : float
            leverage : float
            side : PositionSide
            position_event : EventType
            tp_price : Optional[float] = None
            sl_price : Optional[float] = None
            closed_at : Optional[int] = None
            close_price : Optional[float] = None
        """
        created_order : Order = event.data 

        ### TODO : Construire une liaison robuste entre params envoyés par la strat et la construction des ordres
        # soit - découpler efficacement les arguments envoyés par la strat (**kwargs, wrapper)
        #      - avoir une strcture bloquée mais assez bien pensée pour contenir TOUT ce qu'on aurait besoin pour TOUT type d'ordre 

        position_args = {}
        position_args['entry_at'] = int(datetime.now(timezone.utc).timestamp() * 1000)
        position_args['entry_price'] = created_order.level
        position_args['asset_qty'] = created_order.asset_qty
        position_args['leverage'] = created_order.leverage
        position_args['side'] = PositionSide.LONG if created_order.side == OrderSide.BUY else PositionSide.SHORT
        position_args['position_event'] = EventType.POSITION_OPENED
        # position_args['tp_price'] = created_order.tp_price
        # position_args['sl_price'] = created_order.sl_price
        position = Position(**position_args)

        self.open_position(position)
        
        
        



    def open_position(self, position : Position) -> None:
        if position.id in self.position_book:
            raise KeyError(f"Order {position.id} already exists in the order book") 
        print("###POSITION###\n###POSITION###\n###POSITION###\n###POSITION###\n")
        self.position_book[position.id] = position
        self.event_dispatcher.dispatch(Event(
                    type = EventType.POSITION_OPENED,
                    data = position,
                    timestamp = datetime.now()
                ))

        



