from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, ClassVar, Dict
from datetime import datetime

from event.event import EventType


class OrderSide(Enum):
    LONG = "LONG"
    SHORT = "SHORT"

@dataclass
class Order:

    _instance_count: ClassVar[int] = -1

    id : int = field(init=False)

    # Constant
    level : float
    asset_qty : float
    side : OrderSide
    leverage : float

    # Events
    order_event_timestamp : datetime
    order_event : EventType

    #Optionnel
    tp_pct: Optional[float] = None
    sl_pct : Optional[float] = None
    

    def __post_init__(self) -> None:
        """
        Data Validation \n
        Return None si OK ou raise ValueError si l'une des conditions n'est pas vérifiée
        """
        # Typage strict
        # if self.id is not None and not isinstance(self.id, int):
        #     raise TypeError(f"id must be int, got {type(self.id).__name__}")
        # if not isinstance(self.created_at, int):
        #     raise TypeError(f"created_at must be int (Unix ms timestamp), got {type(self.created_at).__name__}")
        # if self.executed_at is not None and not isinstance(self.executed_at, int):
        #     raise TypeError(f"executed_at must be int or None, got {type(self.executed_at).__name__}")
        # if not isinstance(self.level, float):
        #     raise TypeError(f"level must be float, got {type(self.level).__name__}")
        # if not isinstance(self.asset_qty, float):
        #     raise TypeError(f"asset_qty must be float, got {type(self.asset_qty).__name__}")
        # if not isinstance(self.leverage, float):
        #     raise TypeError(f"leverage must be float, got {type(self.leverage).__name__}")
        # if not isinstance(self.side, OrderSide):
        #     raise TypeError(f"side must be an instance of OrderSide, got {type(self.side).__name__}")
        # if not isinstance(self.order_event, EventType):
        #     raise TypeError(f"order_event must be an instance of EventType, got {type(self.order_event).__name__}")
        # if self.tp_pct is not None and not isinstance(self.tp_pct, float):
        #     raise TypeError(f"tp_pct must be float or None, got {type(self.tp_pct).__name__}")
        # if self.sl_pct is not None and not isinstance(self.sl_pct, float):
        #     raise TypeError(f"sl_pct must be float or None, got {type(self.sl_pct).__name__}")

        # Validation de valeurs
        if self.level < 0:
            raise ValueError(f"level {self.level} must be greater or equal to 0")
        if self.asset_qty < 0:
            raise ValueError(f"asset_qty {self.asset_qty} must be greater or equal to 0")
        if self.leverage < 1:
            raise ValueError(f"leverage {self.leverage} must be greater or equal to 1")
        if self.tp_pct is not None and self.tp_pct <= 0:
            raise ValueError(f"tp_pct {self.tp_pct} must be greater than 0")
        if self.sl_pct is not None and self.sl_pct <= 0:
            raise ValueError(f"sl_pct {self.sl_pct} must be greater than 0")
        
        
        Order._instance_count += 1
        self.id = Order._instance_count

    
    @property
    def tp_price(self) -> Optional[float]:
        """
        Calcule le prix de TP
        TP_price = level*(1±tp_pct)
        """
        if self.tp_pct is None:
            return None
        return self.level*(1 + (1 if self.side == OrderSide.LONG else -1)*self.tp_pct)
    
    @property
    def sl_price(self) -> Optional[float]:
        """
        Calcule le prix de SL
        SL_price = level*(1±sl_pct)
        """
        if self.sl_pct is None:
            return None
        return self.level*(1 + (-1 if self.side == OrderSide.LONG else 1)*self.sl_pct)

    @property
    def value(self) -> float:
        return self.asset_qty * self.level

    @property
    def margin(self) -> float:
        return self.value / self.leverage

    def is_executable(self, current_data:Dict[str, int | float]) -> bool:
        """
        """
        
        low = current_data['LowCol']
        high = current_data['HighCol']

        return self.order_event == EventType.ORDER_CREATED and low <= self.level <= high