from typing import Dict, Any
from datetime import datetime
from enum import Enum

from event.event import EventDispatcher, Event, EventType

class StrategyType(Enum):
    FIX_ORDER = "FIX_ORDER"


class Strategy:

    # De quels arguments une stratégie a-t-elle tout le temps besoin?

    # Pour la fix order ---> TEST :  seul user_params qui sont enfaites les ordres à créer à l'initialisation

    def __init__(self, event_dispatcher : EventDispatcher, user_params : Dict[str, Any]): #faire user_params.py???

        self.event_dispatcher = event_dispatcher
        self.user_params = user_params

        self.event_dispatcher.add_listeners(EventType.INIT_MARKET_DATA, self.init_state)

    def init_state(self):
        #actuellement FixOrderStrategy.init_orders
        pass

    def create_condition(self):
        pass
