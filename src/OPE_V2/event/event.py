from enum import Enum
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Callable
from datetime import datetime
import json


class EventType(Enum):

    INIT_MARKET_DATA = "INIT_MARKET_DATA"
    MARKET_DATA = "MARKET_DATA"
    ORDER_CREATED = "ORDER_CREATED"
    ORDER_EXECUTED = "ORDER_EXECUTED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    POSITION_OPENED = "POSITION_OPENED"
    POSITION_CLOSED = "POSITION_CLOSED"
    POSITION_CANCELLED = "POSITION_CANCELLED"
    STRATEGY_MAKE_ORDER = "STRATEGY_MAKE_ORDER"
    SIGNAL_GENERATED = "SIGNAL_GENERATED"


@dataclass
class Event:
    type : EventType
    data : Any
    timestamp : datetime

class EventDispatcher:
    def __init__(self) -> None:
        self._listeners : Dict[EventType, List[Callable]] = {e: [] for e in EventType}

        self._setup_event_logging()

    def add_listeners(self, event_type : EventType, callback : Callable) -> None:
        self._listeners[event_type].append(callback)
        
    def dispatch(self, event : Event) -> None:
        for callback in self._listeners[event.type]:
            callback(event)

    def _setup_event_logging(self):
        """Enregistre tous les événements pour débogage"""
        def log_event(event: Event):
            if event.type.value != 'MARKET_DATA':
                log_entry = {
                    'timestamp': event.timestamp.isoformat(),
                    'type': event.type.value,
                    'data': asdict(event.data) if hasattr(event.data, '__dataclass_fields__') else event.data
                }
                #print(f"[EVENT] {json.dumps(log_entry, indent=2, default=enum_encoder)}")
                #print(self._listeners)

            # S'abonne à tous les types d'événements
        for event_type in EventType:
            self.add_listeners(event_type, log_event)

def enum_encoder(obj):
    if isinstance(obj, Enum):
        return obj.value
    return obj