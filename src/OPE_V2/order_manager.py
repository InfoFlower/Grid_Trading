from typing import Dict, Callable
from order import Order, OrderEvent, OrderSide


class OrderManager:

    def __init__(self) -> None:
        """
        Initialise l'orderbook à un dictionnaire vide
        """
        self.order_book : Dict[int, Order] = {}

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
        try:
            del self.order_book[order.id]
        except KeyError as e:
            print(f"Order {order.id} does not exists in the order book")

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