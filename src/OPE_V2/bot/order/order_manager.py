from typing import Dict, Any, Callable
from datetime import datetime, timezone

from .order import Order
from .order_builder import OrderBuilder
from event.event import EventDispatcher, Event, EventType
from portfolio.portfolio import Portfolio


class OrderManager:

    def __init__(self, portfolio : Portfolio, tolerance_pct : int, event_dispatcher : EventDispatcher) -> None:
        """
        Initialise l'orderbook à un dictionnaire vide
        """
        self.portfolio = portfolio
        self.order_builder = OrderBuilder()
        self.event_dispatcher = event_dispatcher
        self.tolerance_pct = tolerance_pct
        self.order_book : Dict[int, Order] = {}

        event_dispatcher.add_listeners(EventType.MARKET_DATA, self.orders_to_execute)
        event_dispatcher.add_listeners(EventType.STRATEGY_MAKE_ORDER, self.make_order)

    def make_order(self, event : Event) -> None:
        """
        Ajoute un ordre à la liste d'ordre
        """
        strat_type = event.data['type']
        order_params = event.data['args']
        margin = order_params['level'] * order_params['asset_qty'] / order_params['leverage']

        if self.portfolio.enough_money(margin):
            
            order_already_exists = self.check_order_already_exists(event)

            if not order_already_exists:
                order = self.order_builder.build(strat_type, order_params)

                if order.id in self.order_book:
                    raise KeyError(f"Order {order.id} already exists in the order book") 
            
                self.order_book[order.id] = order
                self.event_dispatcher.dispatch(Event(
                            type = EventType.ORDER_CREATED,
                            data = order,
                            timestamp = datetime.now()
                        ))
            else :
                k, v = order_already_exists.popitem()
                print(f"L'ordre {k} ({v.level, v.side}) existe déjà")
        
        else:
            raise ValueError(f'Not enough money: wanted = {margin}> available={self.portfolio.money_balance}')
        
    def orders_to_execute(self, event : Event) -> None:
        for order_id in list(self.order_book.keys()):
            if self.order_book[order_id].is_executable(event.data):
                self.take_order(self.order_book[order_id])

    def take_order(self, order : Order) -> None:
        """
        Retire un ordre de l'order book
        """
        if order.id not in self.order_book:
            raise KeyError(f"Order {order.id} does not exists in the order book")
        
        self.delete_order(order.id)
        
        #### BUILDER & MODIFIER ####
        order.executed_at = int(datetime.now(timezone.utc).timestamp() * 1000)
        order.order_event = EventType.ORDER_EXECUTED
        ############################

        self.event_dispatcher.dispatch(Event(
                    type = EventType.ORDER_EXECUTED,
                    data = order,
                    timestamp = datetime.now()
                ))
        
    def delete_order(self, id : int):
        del self.order_book[id]

    def filter(self, condition : Callable[[Order],bool]) -> Dict[int,Order]:
        """
        Retourne un dictionnaire des ordres qui vérifient la condition.
        """
        return {order_id : order for order_id, order in self.order_book.items() if condition(order)}
    
    def check_order_already_exists(self, event) -> Dict[int,Order]:

        order_args = event.data['args']
        
        def condition(order):
            return abs(order.level - order_args['level']) <= order_args['level']*self.tolerance_pct and order.side == order_args['side']
        
        return self.filter(condition)