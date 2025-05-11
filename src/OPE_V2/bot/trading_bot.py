from typing import Dict
from dataclasses import asdict

from csv_data_provider import CSVDataProvider

from event.event import EventDispatcher



class TradingBot:

    #position_manager : PositionManager
    def __init__(self, event_dispatcher : EventDispatcher, data_provider : CSVDataProvider, pool : Dict[str, float | int]) -> None:
        self.event_dispatcher = event_dispatcher
        self.data_provider = data_provider
        self.pool = pool

    def run(self):
        
        self.data_provider.stream_data()
