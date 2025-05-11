from typing import Dict, Any
from datetime import datetime, timezone

from .order import Order
from .order_builder import OrderBuilder
from event.event import EventDispatcher, Event, EventType


class OrderManager:

    def __init__(self, event_dispatcher : EventDispatcher) -> None:
        """
        Initialise l'orderbook à un dictionnaire vide
        """
        self.event_dispatcher = event_dispatcher
        self.order_builder = OrderBuilder()
        self.order_book : Dict[int, Order] = {}

        event_dispatcher.add_listeners(EventType.MARKET_DATA, self.orders_to_execute)
        event_dispatcher.add_listeners(EventType.STRATEGY_MAKE_ORDER, self.make_order)

    def make_order(self, event : Event) -> None:
        """
        Ajoute un ordre à la liste d'ordre
        """

        order = self.order_builder.build(event)

        if order.id in self.order_book:
            raise KeyError(f"Order {order.id} already exists in the order book") 
        self.order_book[order.id] = order
        self.event_dispatcher.dispatch(Event(
                    type = EventType.ORDER_CREATED,
                    data = order,
                    timestamp = datetime.now()
                ))
        
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
        
        del self.order_book[order.id]
        
        #### BUILDER & MODIFIER ####
        order.executed_at = int(datetime.now(timezone.utc).timestamp() * 1000)
        order.order_event = EventType.ORDER_EXECUTED
        ############################

        self.event_dispatcher.dispatch(Event(
                    type = EventType.ORDER_EXECUTED,
                    data = order,
                    timestamp = datetime.now()
                ))

    

    # def filter(self, condition : Callable[[Order],bool]) -> Dict[int,Order]:
    #     """
    #     Retourne un dictionnaire des ordres qui vérifient la condition.
    #     """
    #     return {order_id : order for order_id, order in self.order_book.items() if condition(order)}
