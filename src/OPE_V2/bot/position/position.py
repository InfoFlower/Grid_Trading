from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, ClassVar, Dict
from datetime import datetime, timezone

from event.event import EventType

class PositionSide(Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class PositionCloseType(Enum):
    TAKEPROFIT = "TAKEPROFIT"
    STOPLOSS = "STOPLOSS"

@dataclass
class Position:

    _instance_count: ClassVar[int] = 0 

    id : int  = field(init=False)
    entry_at : int
    entry_price : float
    asset_qty : float
    leverage : float
    side : PositionSide
    position_event : EventType
    tp_price : Optional[float] = None
    sl_price : Optional[float] = None
    closed_at : int = 0
    close_price : float = 0.0
    close_type : PositionCloseType = None

    def __post_init__(self) -> None:
        """
        Data Validation
        Return None si OK ou raise ValueError si l'une des conditions n'est pas vérifiée
        """
        # Typage strict
        # if self.id is not None and not isinstance(self.id, int):
        #     raise TypeError(f"id must be int, got {type(self.id).__name__}")
        if not isinstance(self.entry_at, int):
            raise TypeError(f"entry_at must be int (Unix ms timestamp), got {type(self.entry_at).__name__}")
        # if self.closed_at is not None and not isinstance(self.closed_at, int):
        #     raise TypeError(f"closed_at must be int or None, got {type(self.closed_at).__name__}")
        if not isinstance(self.entry_price, float):
            raise TypeError(f"entry_price must be float, got {type(self.entry_price).__name__}")
        if not isinstance(self.asset_qty, float):
            raise TypeError(f"asset_qty must be float, got {type(self.asset_qty).__name__}")
        if not isinstance(self.leverage, float):
            raise TypeError(f"leverage must be float, got {type(self.leverage).__name__}")
        if not isinstance(self.side, PositionSide):
            raise TypeError(f"side must be an instance of PositionSide, got {type(self.side).__name__}")
        if not isinstance(self.position_event, EventType):
            raise TypeError(f"position_event must be an instance of EventType, got {type(self.position_event).__name__}")
        # if self.close_price is not None and not isinstance(self.close_price, float):
        #     raise TypeError(f"close_price must be float or None, got {type(self.close_price).__name__}")
        if self.tp_price is not None and not isinstance(self.tp_price, float):
            raise TypeError(f"tp_price must be float or None, got {type(self.tp_price).__name__}")
        if self.sl_price is not None and not isinstance(self.sl_price, float):
            raise TypeError(f"sl_price must be float or None, got {type(self.sl_price).__name__}")

        # Validation de valeurs
        if self.entry_price < 0:
            raise ValueError(f"entry_price {self.entry_price} must be greater or equal to 0")
        
        if self.asset_qty < 0:
            raise ValueError(f"asset_qty {self.asset_qty} must be greater or equal to 0")
        
        if self.leverage < 1:
            raise ValueError(f"leverage {self.leverage} must be greater or equal to 1")

        if self.close_price is not None:
            if self.close_price < 0:
                raise ValueError(f"close_price {self.close_price} must be greater or equal to 0")
        
        #Check les positions des takeprofit TP en fonction de l'entryprice EP et du side
        if self.tp_price is not None:
            if (self.tp_price < self.entry_price) if self.side == PositionSide.LONG else (self.tp_price > self.entry_price):
                raise ValueError(f"Side:{self.side};TP={self.tp_price} < EP={self.entry_price};TP must be greater than Entry_price EP" if self.side == PositionSide.LONG \
                                else f"Side:{self.side};TP={self.tp_price} > EP={self.entry_price};TP must be lower than Entry_price EP")
            
        #Check les positions des stoploss SL en fonction de l'entryprice EP et du side
        if self.sl_price is not None:
            if (self.sl_price > self.entry_price) if self.side == PositionSide.LONG else (self.sl_price < self.entry_price):
                raise ValueError(f"Side:{self.side};SL={self.sl_price} > EP={self.entry_price};SL must be lower than Entry_price EP" if self.side == PositionSide.LONG \
                                else f"Side:{self.side};SL={self.sl_price} < EP={self.entry_price};SL must be greater than Entry_price EP")

        Position._instance_count += 1
        self.id = Position._instance_count

    @property
    def margin(self) -> float:
        return self.asset_qty * self.entry_price / self.leverage


    def pnl(self, current_price : float) -> float:
        """
        Calcul le PnL de la position par rapport au prix actuel
        """
        bool_side = 1 if self.side == PositionSide.LONG else -1
        return (current_price - self.entry_price) * self.asset_qty * bool_side * self.leverage
    
    def is_closable_tp(self, current_data : Dict[str, int | float]):
            low = current_data['LowCol']
            high = current_data['HighCol']
            return self.position_event == EventType.POSITION_OPENED and low <= self.tp_price <= high

    def is_closable_sl(self, current_data : Dict[str, int | float]):
            low = current_data['LowCol']
            high = current_data['HighCol']
            return self.position_event == EventType.POSITION_OPENED and low <= self.sl_price <= high


