from dataclasses import dataclass, field

from event.event import EventDispatcher, Event, EventType
from bot.order.order import Order, OrderSide
from bot.position.position import Position

@dataclass
class LongShortBalance:

    long : dict = field(default_factory=lambda: {'money': 0,
                                                 'asset': 0})
    short : dict = field(default_factory=lambda: {'money': 0,
                                                  'asset': 0})
    
@dataclass 
class PortfolioBalance:

    money_available : float
    orders : LongShortBalance
    positions : LongShortBalance

class Portfolio:
    
    def __init__(self, money_balance : float, event_dispatcher : EventDispatcher) -> None:

        self.event_dispatcher = event_dispatcher

        self.portfolio_balance = PortfolioBalance(
            money_available = money_balance,
            orders = LongShortBalance(),
            positions = LongShortBalance()
        )

        event_dispatcher.add_listeners(EventType.ORDER_CREATED, self.update_order_created)
        #event_dispatcher.add_listeners(EventType.POSITION_OPENED, self.set_position_opened)
        event_dispatcher.add_listeners(EventType.POSITION_CLOSED, self.update_position_closed)

    def update_order_created(self, event : Event) -> None:
       
        order : Order = event.data
        
        print("ORDER MARGIN: ", order.margin)
        self.portfolio_balance.money_available -= order.margin
        
        if order.side == OrderSide.LONG:
            self.portfolio_balance.orders.long['money'] += order.margin
            self.portfolio_balance.orders.long['asset'] += order.asset_qty
        
        elif order.side == OrderSide.SHORT:
            self.portfolio_balance.orders.short['money'] += order.margin
            self.portfolio_balance.orders.short['asset'] += order.asset_qty

        print('MONEY AVAILABLE AFTER ORDER CREATED: ', self.portfolio_balance.money_available)
        print('MONEY IN ORDERS', self.money_in_orders)
        print('NOT LOCKED MONEY AFTER ORDER CREATED: ', self.all_not_locked_money)

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

        # if position.side == PositionSide.LONG:
        #     self.in_positions.long -= position.asset_qty
        # else :
        #     self.in_positions.short -= position.asset_qty

        pnl = position.pnl(position.close_price)
        print("POSITION PNL: ", pnl)
        margin = position.margin
        print("POSITION MARGIN: ", margin)
        self.portfolio_balance.money_available += margin + pnl

        print('MONEY BALANCE AFTER POSITION CLOSED: ', self.portfolio_balance.money_available)

    def enough_money(self, money) -> bool:
        return money < self.portfolio_balance.money_available
    
    @property
    def money_in_orders(self) -> float:
        return self.portfolio_balance.orders.short['money'] + self.portfolio_balance.orders.long['money']
    
    @property
    def all_not_locked_money(self) -> float:
        money_in_orders = self.money_in_orders
        return self.portfolio_balance.money_available + money_in_orders