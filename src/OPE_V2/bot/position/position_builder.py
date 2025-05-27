from datetime import datetime, timezone

from event.event import EventType, Event
from .position import Position, PositionSide, PositionCloseType
from data.data_provider.market_data_cache import DataCache
from bot.order.order import Order, OrderSide


class PositionBuilder:

    def __init__(self, data_cache : DataCache) -> None:
        self.data_cache = data_cache

    def classic_order_to_position(self, order : Order) -> Position:
        """
        """
        current_candle = self.data_cache.get_market_candle

        position_params = {}
        position_params['order_id'] = order.id
        position_params['position_event_timestamp'] = current_candle['TimeCol']
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
        order = event.data
        position = self.classic_order_to_position(order)
        return position
    
    def modify(self, position : Position, event_type : EventType, close_type : PositionCloseType) -> Position:

        current_candle = self.data_cache.get_market_candle

        if event_type == EventType.POSITION_CLOSED:

            position.position_event = event_type
            position.close_type = close_type
            position.position_event_timestamp = current_candle['TimeCol']
            
            if close_type == PositionCloseType.TAKEPROFIT:
                position.close_price = position.tp_price

            elif close_type == PositionCloseType.STOPLOSS:
                position.close_price = position.sl_price

        return position
                