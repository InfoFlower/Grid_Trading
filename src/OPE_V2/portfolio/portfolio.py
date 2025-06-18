from dataclasses import dataclass, field
from datetime import datetime

from event.event import EventDispatcher, Event, EventType
from bot.order.order import Order, OrderSide
from bot.position.position import Position, PositionSide

@dataclass
class LongShortAssetBalance:

    long : int = 0
    short : int = 0
    
@dataclass 
class PortfolioBalance:

    cash_balance : float
    orders : LongShortAssetBalance
    positions : LongShortAssetBalance

class Portfolio:
    
    def __init__(self, cash_balance : float, event_dispatcher : EventDispatcher) -> None:

        self.event_dispatcher = event_dispatcher
        self.initial_cash = cash_balance
        self.portfolio_balance = PortfolioBalance(
            cash_balance = cash_balance,
            orders = LongShortAssetBalance(),
            positions = LongShortAssetBalance()
        )

        event_dispatcher.add_listeners(EventType.ORDER_CREATED, self.update_order_created)
        #event_dispatcher.add_listeners(EventType.POSITION_OPENED, self.set_position_opened)
        event_dispatcher.add_listeners(EventType.POSITION_CLOSED, self.update_position_closed)

    def update_order_created(self, event : Event) -> None:
       
        order : Order = event.data
        self.portfolio_event_timestamp = order.order_event_timestamp
        self.portfolio_event_type = order.order_event
        
        print("ORDER MARGIN: ", order.margin)
        self.portfolio_balance.cash_balance -= order.margin
        
        if order.side == OrderSide.LONG:
            self.portfolio_balance.orders.long += order.asset_qty
        
        elif order.side == OrderSide.SHORT:
            self.portfolio_balance.orders.short += order.asset_qty

        self.event_dispatcher.dispatch(Event(
                            type = EventType.UPDATE_PORTFOLIO,
                            data = self,
                            timestamp = datetime.now()
                        ))
        
        

    # def set_position_opened(self, event : Event) -> None:
        
    #     position : Position = event.data

    #     if position.side == PositionSide.LONG:
    #         self.in_orders.long -= position.asset_qty
    #         self.in_positions.long += position.asset_qty
        
    #     else :
    #         self.in_orders.short -= position.asset_qty
    #         self.in_positions.short += position.asset_qty

    def update_position_closed(self, event : Event) -> None:
        
        position : Position = event.data
        self.portfolio_event_timestamp = position.position_event_timestamp
        self.portfolio_event_type = position.position_event

        if position.side == PositionSide.LONG:
            self.portfolio_balance.positions.long -= position.asset_qty
        else :
            self.portfolio_balance.positions.short -= position.asset_qty

        pnl = position.pnl(position.close_price)

        margin = position.margin

        self.portfolio_balance.cash_balance += margin + pnl

        self.event_dispatcher.dispatch(Event(
                            type = EventType.UPDATE_PORTFOLIO,
                            data = self,
                            timestamp = datetime.now()
                        ))


    def enough_money(self, money) -> bool:
        return money < self.portfolio_balance.cash_balance
    
    @property
    def asset_in_orders(self) -> float:
        return self.portfolio_balance.orders.short + self.portfolio_balance.orders.long
    
    # @property
    # def all_not_locked_money(self) -> float:
    #     return self.portfolio_balance.cash_balance + self.money_in_orders