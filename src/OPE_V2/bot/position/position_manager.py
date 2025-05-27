from typing import Dict, Any
from datetime import datetime, timezone

from .position import Position, PositionCloseType
from .position_builder import PositionBuilder
from event.event import EventDispatcher, Event, EventType
from data.data_provider.market_data_cache import DataCache

class PositionManager:

    def __init__(self, event_dispatcher : EventDispatcher, data_cache = DataCache) -> None:
        self.position_builder = PositionBuilder(data_cache)
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

                event_type = EventType.POSITION_CLOSED
                close_type = PositionCloseType.TAKEPROFIT
                
                position = self.position_builder.modify(position, event_type, close_type)
                
                self.close_position(position)

            if position.is_closable_sl(event.data):

                event_type = EventType.POSITION_CLOSED
                close_type = PositionCloseType.STOPLOSS

                position = self.position_builder.modify(position, event_type, close_type)
                
                self.close_position(position)

    def close_position(self, position : Position) -> None:

        if position.id not in self.position_book:
            raise KeyError(f"Position {position.id} does not exists in the position book")
        
        self.delete_position(position.id)

        self.event_dispatcher.dispatch(Event(
            type = position.position_event,
            data = position,
            timestamp = datetime.now()
        ))

    def delete_position(self, id : int):
        del self.position_book[id]