from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, List, Callable
from datetime import datetime

class EventType(Enum):
    MARKET_DATA = "MARKET_DATA"
    ORDER_CREATED = "ORDER_CREATED"
    ORDER_FILLED = "ORDER_FILLED"
    POSITION_OPENED = "POSITION_OPENED"
    POSITION_CLOSED = "POSITION_CLOSED"
    SIGNAL_GENERATED = "SIGNAL_GENERATED"

@dataclass
class Event:
    type : EventType
    data : Any
    timestamp : datetime

class EventDispatcher:
    def __init__(self) -> None:
        self._listeners : Dict[EventType, List[Callable]] = {e: [] for e in EventType}

    def add_listeners(self, event_type : EventType, callback : Callable) -> None:
        self._listeners[event_type].append(callback)
        
    def dispatch(self, event : Event) -> None:
        for callback in self._listeners[event.type]:
            callback(event)