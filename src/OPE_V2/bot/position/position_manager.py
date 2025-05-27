from typing import Dict, Any
from datetime import datetime, timezone

from .position import Position, PositionCloseType
from .position_builder import PositionBuilder
from event.event import EventDispatcher, Event, EventType

class PositionManager:

    def __init__(self, event_dispatcher : EventDispatcher) -> None:
        self.position_builder = PositionBuilder()
        self.event_dispatcher = event_dispatcher
        self.position_book : Dict[int, Position] = {}

        event_dispatcher.add_listeners(EventType.ORDER_EXECUTED, self.open_position)
        event_dispatcher.add_listeners(EventType.MARKET_DATA, self.positions_to_close)


    def open_position(self, event : Event) -> None:

        position = self.position_builder.build(event)

        if position.id in self.position_book:
            raise KeyError(f"Position {position.id} already exists in the order book") 
        print("###POSITION###\n###POSITION###\n###POSITION###\n###POSITION###\n")
        self.position_book[position.id] = position
        self.event_dispatcher.dispatch(Event(
                    type = EventType.POSITION_OPENED,
                    data = position,
                    timestamp = datetime.now()
                ))
        
    def positions_to_close(self, event : Event) -> None:

        for position_id in list(self.position_book.keys()):
            position = self.position_book[position_id]
            
            if position.is_closable_tp(event.data):
                
                #### BUILDER & MODIFIER ####
                position.position_event = EventType.POSITION_CLOSED
                position.close_type = PositionCloseType.TAKEPROFIT
                position.closed_at = int(datetime.now(timezone.utc).timestamp() * 1000)
                position.close_price = position.tp_price
                ############################
                self.close_position(position)

            if position.is_closable_sl(event.data):

                #### BUILDER & MODIFIER ####
                position.position_event = EventType.POSITION_CLOSED
                position.close_type = PositionCloseType.STOPLOSS
                position.closed_at = int(datetime.now(timezone.utc).timestamp() * 1000)
                position.close_price = position.sl_price
                ############################
                
                self.close_position(position)

    def close_position(self, position : Position) -> None:

        if position.id not in self.position_book:
            raise KeyError(f"Position {position.id} does not exists in the position book")
        
        self.delete_position(position.id)

        self.event_dispatcher.dispatch(Event(
            type = EventType.POSITION_CLOSED,
            data = position,
            timestamp = datetime.now()
        ))

    def delete_position(self, id : int):
        del self.position_book[id]