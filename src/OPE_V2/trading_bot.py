from typing import Dict
from dataclasses import asdict
from datetime import datetime

from data.data_provider.csv_data_provider import CSVDataProvider

from event.event import EventDispatcher, Event, EventType



class TradingBot:

    #position_manager : PositionManager
    def __init__(self, event_dispatcher : EventDispatcher, data_provider : CSVDataProvider) -> None:
        self.event_dispatcher = event_dispatcher
        self.data_provider = data_provider

        event_dispatcher.add_listeners(EventType.END_MARKET_DATA, self.end)

    def run(self):
        self.data_provider.stream_data()

    def end(self, event : Event):

        self.event_dispatcher.dispatch(Event(
                            type = EventType.END_BACKTEST,
                            data = 'fin backtest',
                            timestamp = datetime.now()
                        ))

