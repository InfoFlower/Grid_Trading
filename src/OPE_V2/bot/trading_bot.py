from .order_manager import OrderManager
from event import EventDispatcher
from typing import Dict
#from position_manager import PositionManager

class TradingBot:

    #position_manager : PositionManager
    def __init__(self, event_dispatcher : EventDispatcher, pool : Dict[str, float | int]) -> None:
        self.order_manager = OrderManager()
        #self.position_manager = PositionManager()
        self.event_dispatcher = event_dispatcher
        self.pool = pool


    def run(self):
        pass