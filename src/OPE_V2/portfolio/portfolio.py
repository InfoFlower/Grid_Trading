from dataclasses import dataclass
from typing import Dict

from event.event import EventDispatcher, Event, EventType
from bot.order import OrderSide, Order
from bot.position import PositionSide, Position

@dataclass
class Asset:

    long : float
    short : float

class Portfolio:
    
    def __init__(self, money_balance : float, event_dispatcher : EventDispatcher) -> None:

        self.event_dispatcher = event_dispatcher
        
        self.money_balance = money_balance
        print(self.money_balance)
        self.in_orders = Asset(long = 0, short = 0)
        self.in_positions = Asset(long = 0, short = 0)

        event_dispatcher.add_listeners(EventType.ORDER_CREATED, self.set_order_created)
        event_dispatcher.add_listeners(EventType.POSITION_OPENED, self.set_position_opened)
        event_dispatcher.add_listeners(EventType.POSITION_CLOSED, self.set_position_closed)

    def set_order_created(self, event : Event) -> None:
       

        order : Order = event.data
        margin = order.margin
        print(margin)
        self.money_balance -= margin
        if order.side == OrderSide.LONG:
            self.in_orders.long += order.asset_qty
        else :
            self.in_orders.short += order.asset_qty 
        print('ORDER_CREATED', self.money_balance)

    def set_position_opened(self, event : Event) -> None:
        
        position : Position = event.data

        if position.side == PositionSide.LONG:
            self.in_orders.long -= position.asset_qty
            self.in_positions.long += position.asset_qty
        
        else :
            self.in_orders.short -= position.asset_qty
            self.in_positions.short += position.asset_qty

    def set_position_closed(self, event : Event) -> None:
        
        position : Position = event.data

        if position.side == PositionSide.LONG:
            self.in_positions.long -= position.asset_qty
        else :
            self.in_positions.short -= position.asset_qty

        pnl = position.pnl(position.close_price)
        print(pnl)
        margin = position.margin
        print(margin)
        self.money_balance += margin + pnl

        print('POSITION_CLOSED', self.money_balance)

    def enough_money(self, money) -> bool:
        return money < self.money_balance

    




