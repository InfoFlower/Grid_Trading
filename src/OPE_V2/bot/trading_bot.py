from typing import Dict
from dataclasses import asdict
from enum import Enum
import json

from csv_data_provider import CSVDataProvider
from .order_manager import OrderManager
from event import EventDispatcher, Event, EventType
#from .position_manager import PositionManager


class TradingBot:

    #position_manager : PositionManager
    def __init__(self, event_dispatcher : EventDispatcher, data_provider : CSVDataProvider, pool : Dict[str, float | int]) -> None:
        self.order_manager = OrderManager(event_dispatcher)
        #self.position_manager = PositionManager()
        self.event_dispatcher = event_dispatcher
        self.data_provider = data_provider
        self.pool = pool

        self._setup_event_logging()

    def run(self):
        
        self.data_provider.stream_data()

    def _setup_event_logging(self):
        """Enregistre tous les événements pour débogage"""
        def log_event(event: Event):
            if event.type.value != 'MARKET_DATA':
                log_entry = {
                    'timestamp': event.timestamp.isoformat(),
                    'type': event.type.value,
                    'data': asdict(event.data) if hasattr(event.data, '__dataclass_fields__') else event.data
                }
                print(f"[EVENT] {json.dumps(log_entry, indent=2, default=enum_encoder)}")
        
        # S'abonne à tous les types d'événements
        for event_type in EventType:
            self.event_dispatcher.add_listeners(event_type, log_event)


def enum_encoder(obj):
        if isinstance(obj, Enum):
            return obj.value
        return obj