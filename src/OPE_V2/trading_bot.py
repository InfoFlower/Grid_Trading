from order_manager import OrderManager
from typing import Dict
#from position_manager import PositionManager

class TradingBot:

    #position_manager : PositionManager
    def __init__(self, order_manager : OrderManager, ) -> None:
        self.order_manager = order_manager
        pass

    def update(self, current_data : Dict[str, float | int]) -> None:
        
        
        pass