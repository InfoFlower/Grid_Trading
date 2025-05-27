from event.event import EventDispatcher, EventType, Event


class DataCache:

    def __init__(self, event_dispatcher : EventDispatcher) -> None:

        self.event_dispatcher = event_dispatcher
        self._market_candle = {}

        event_dispatcher.add_listeners(EventType.INIT_MARKET_DATA, self.update_candle)
        event_dispatcher.add_listeners(EventType.MARKET_DATA, self.update_candle)

    def update_candle(self, event : Event) -> None:
        self._market_candle = event.data
        
    @property
    def get_market_candle(self) -> dict:
        return self._market_candle