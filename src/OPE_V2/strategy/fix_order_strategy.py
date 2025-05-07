from typing import Dict, Any
from datetime import datetime


from event import EventDispatcher, Event, EventType

class FixOrderStrategy:

    # De quels arguments une stratégie a-t-elle tout le temps besoin?

    # Pour la fix order ---> TEST :  seul user_params qui sont enfaites les ordres à créer à l'initialisation

    def __init__(self, event_dispatcher : EventDispatcher, user_params : Dict[str, Any]): #faire user_params.py???

        self.event_dispatcher = event_dispatcher
        self.user_params = user_params

        self.event_dispatcher.add_listeners(EventType.INIT_MARKET_DATA, self.init_orders)

    def init_orders(self, event : Event):

        self.event_dispatcher.dispatch(Event(
            type = EventType.STRATEGY_MAKE_ORDER,
            data = self.user_params,
            timestamp = datetime.now()
        ))


