from datetime import datetime, timezone

from event.event import EventType, Event
from .position import Position, PositionSide

from bot.order.order import Order, OrderSide


class PositionBuilder:

    def __init__(self) -> None:
        pass

    def classic_order_to_position(self, order : Order) -> Position:
        """
        """
        position_params = {}
        position_params['order_id'] = order.id
        position_params['entry_at'] = int(datetime.now(timezone.utc).timestamp() * 1000)
        position_params['entry_price'] = order.level
        position_params['asset_qty'] = order.asset_qty
        position_params['leverage'] = order.leverage
        position_params['side'] = PositionSide.LONG if order.side == OrderSide.LONG else PositionSide.SHORT
        position_params['position_event'] = EventType.POSITION_OPENED
        
        if order.tp_pct is not None :
            position_params['tp_price'] = order.tp_price
        if order.sl_pct is not None :    
            position_params['sl_price'] = order.sl_price

        return Position(**position_params)

    def build(self, event : Event) -> Position :
        """
        """
        order =  event.data
        position = self.classic_order_to_position(order)
        return position