from typing import Dict, Any
from enum import Enum

from event.event import EventDispatcher, EventType

class StrategyType(Enum):
    FIX_ORDER = "FIX_ORDER"
    DUMB = "DUMB"

class Strategy:

    # De quels arguments une stratégie a-t-elle tout le temps besoin?

    # Pour la fix order ---> TEST :  seul user_params qui sont enfaites les ordres à créer à l'initialisation

    def __init__(self, event_dispatcher : EventDispatcher, params : Dict[str, Any]) -> None: #faire user_params.py???

        self.strategy_name : str = ""
        self.strategy_type : StrategyType = StrategyType.DUMB # Par défault à DUMB
        self.event_dispatcher = event_dispatcher
        self.params = params

        self.event_dispatcher.add_listeners(EventType.INIT_MARKET_DATA, self.init_statement)

    def init_statement(self):
        #actuellement FixOrderStrategy.init_orders
        pass

    def create_statement(self):
        pass
