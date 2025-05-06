from typing import Dict, Callable
from datetime import datetime

from .order import Order, OrderEvent, OrderSide
from event import EventDispatcher, Event, EventType


class OrderManager:

    def __init__(self, event_dispatcher : EventDispatcher) -> None:
        """
        Initialise l'orderbook à un dictionnaire vide
        """
        self.event_dispatcher = event_dispatcher
        self.order_book : Dict[int, Order] = {}

        event_dispatcher.add_listeners(EventType.MARKET_DATA, self.orders_to_execute)
        

    def make_order(self, order : Order) -> None:
        """
        Ajoute un ordre à la liste d'ordre
        """
        if order.id in self.order_book:
            raise KeyError(f"Order {order.id} already exists in the order book") 
        self.order_book[order.id] = order

    def take_order(self, order : Order) -> None:
        """
        Retire un ordre de l'order book
        """
        if order.id not in self.order_book:
            raise KeyError(f"Order {order.id} does not exists in the order book")
        
        del self.order_book[order.id]
        self.event_dispatcher(Event(
                    type = EventType.ORDER_EXECUTED,
                    data = order,
                    timestamp = datetime.now()
                ))

    def orders_to_execute(self, event : Event):
        for order in self.order_book.values():
            if order.is_executable():
                self.take_order(order)
                


    def filter(self, condition : Callable[[Order],bool]) -> Dict[int,Order]:
        """
        Retourne un dictionnaire des ordres qui vérifient la condition.
        """
        return {order_id : order for order_id, order in self.order_book.items() if condition(order)}
    

    
if __name__ == '__main__':
    def main():
        order_manager = OrderManager()
        print(order_manager.order_book)

        order_1 = Order(
            id=1,
            level=1000.0,
            asset_qty=1.0,
            quote_qty=1000.0,
            side=OrderSide.BUY,
            leverage=1,
            tp_pct=0.1,
            sl_pct=0.05,
            event=OrderEvent.CREATED
        )
        order_2 = Order(
            id=2,
            level=1000.0,
            asset_qty=1.0,
            quote_qty=1000.0,
            side=OrderSide.BUY,
            leverage=1,
            tp_pct=0.1,
            sl_pct=0.05,
            event=OrderEvent.CREATED
        )
        order_manager.make_order(order_1)
        order_manager.make_order(order_1)
        print(order_manager.order_book)
        order_manager.take_order(order_1)
        print(order_manager.order_book)
        order_manager.take_order(order_2)

    main()