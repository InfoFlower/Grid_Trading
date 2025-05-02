from dataclasses import dataclass
from enum import Enum
from typing import Optional

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderEvent(Enum):
    OPEN = "OPEN"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"

@dataclass
class Order:

    id : int
    level : float
    asset_qty : float
    quote_qty : float
    side : OrderSide
    leverage : float
    event : OrderEvent
    tp_pct: Optional[float] = None
    sl_pct : Optional[float] = None
    

    def __post_init__(self) -> None:
        """
        Data Validation \n
        Return None si OK ou raise ValueError si l'une des conditions n'est pas vérifiée
        """
        if self.level < 0:
            raise ValueError(f"level {self.level} must be greater or equal to zero")
        if self.asset_qty < 0:
            raise ValueError(f"asset_qty {self.asset_qty} must be greater or equal to zero")
        if self.quote_qty < 0:
            raise ValueError(f"quote_qty {self.quote_qty} must be greater or equal to zero")
        if self.leverage < 1:
            raise ValueError(f"leverage {self.leverage} must be greater or equal to 1")
        
        if self.tp_pct is not None:
            if not 0 < self.tp_pct:
                raise ValueError(f"tp_pct {self.tp_pct} must be greater than 0")
        if self.sl_pct is not None:
            if not 0 < self.sl_pct:
                raise ValueError(f"sl_pct {self.sl_pct} must be greater than 0")
    
    @property
    def tp_price(self) -> Optional[float]:
        """
        Calcule le prix de TP
        TP_price = level*(1±tp_pct)
        """
        if self.tp_pct is None:
            return None
        return self.level*(1 + (1 if self.side == OrderSide.BUY else -1)*self.tp_pct)
    
    @property
    def sl_price(self) -> Optional[float]:
        """
        Calcule le prix de SL
        SL_price = level*(1±sl_pct)
        """
        if self.sl_pct is None:
            return None
        return self.level*(1 + (-1 if self.side == OrderSide.BUY else 1)*self.sl_pct)
        
# if __name__ == '__main__':
#     order = Order(
#         id=1,
#         level=1000,
#         asset_qty=1,
#         quote_qty=1000,
#         side=OrderSide.BUY,
#         leverage=1,
#         tp_pct=0.1,
#         sl_pct=None,
#         event=OrderEvent.OPEN
#     )
#     print(order.tp_price)
#     print(order.sl_price)