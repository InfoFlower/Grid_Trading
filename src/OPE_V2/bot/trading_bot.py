from typing import Dict
from dataclasses import asdict

from data.data_provider.csv_data_provider import CSVDataProvider

from event.event import EventDispatcher



class TradingBot:

    #position_manager : PositionManager
    def __init__(self, event_dispatcher : EventDispatcher, data_provider : CSVDataProvider) -> None:
        self.event_dispatcher = event_dispatcher
        self.data_provider = data_provider

    def run(self):
        
        self.data_provider.stream_data()
