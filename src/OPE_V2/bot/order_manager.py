from typing import Dict, Callable, Any
from datetime import datetime, timezone

from .order import Order, OrderSide
from event.event import EventDispatcher, Event, EventType


class OrderManager:

    def __init__(self, event_dispatcher : EventDispatcher) -> None:
        """
        Initialise l'orderbook à un dictionnaire vide
        """
        self.event_dispatcher = event_dispatcher
        self.order_book : Dict[int, Order] = {}

        event_dispatcher.add_listeners(EventType.MARKET_DATA, self.orders_to_execute)
        event_dispatcher.add_listeners(EventType.STRATEGY_MAKE_ORDER, self.construct_order)
        
    def construct_order(self, event : Event) -> None:
        """
        user_params = {
                'level': crypto_initial_price+200,
                'asset_qty' : 0.01* pool['crypto_balance'],
                'side' : OrderSide.SELL,
                'leverage' : 0
            }
        """
        ### TODO : Construire une liaison robuste entre params envoyés par la strat et la construction des ordres
        # soit - découpler efficacement les arguments envoyés par la strat (**kwargs, wrapper)
        #      - avoir une strcture bloquée mais assez bien pensée pour contenir TOUT ce qu'on aurait besoin pour TOUT type d'ordre 
        order_params = event.data
        order_params['created_at'] = int(datetime.now(timezone.utc).timestamp() * 1000)
        order_params['order_event'] = EventType.ORDER_CREATED
        print(order_params)
        order = Order(**order_params)
        self.make_order(order)

    def make_order(self, order : Order) -> None:
        """
        Ajoute un ordre à la liste d'ordre
        """
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
        self.event_dispatcher.dispatch(Event(
                    type = EventType.ORDER_EXECUTED,
                    data = order,
                    timestamp = datetime.now()
                ))

    

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
            event=EventType.ORDER_EXECUTED
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
            event=EventType.ORDER_EXECUTED
        )
        order_manager.make_order(order_1)
        order_manager.make_order(order_1)
        print(order_manager.order_book)
        order_manager.take_order(order_1)
        print(order_manager.order_book)
        order_manager.take_order(order_2)

    main()