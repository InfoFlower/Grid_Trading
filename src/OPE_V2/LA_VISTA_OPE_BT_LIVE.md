\--------- Question ------------

Comment arriver à un niveau d’abstraction assez fort pour utiliser deux méthodes de stockages différents comme dans l’exemple suivant:
Actuellement, dans le backtest, les ordres sont stocker dans un dictionnaire python.
self.order_book : Dict[int, Order] = {}
Lorsque je dois vérifier si un ordre doit être executer, je parcours le dictionnaire et je vérifie la condition d’exécution pour chaque order
def orders_to_execute(self, event : Event) -> None:
        for order_id in list(self.order_book.keys()):
            if self.order_book[order_id].is_executable(event.data):
                self.take_order(self.order_book[order_id])
Comment modifier le code pour que les ordres soient stockés et extrais d’un dictionnaire dans le backtest et d’une base de données dans le live?

\---------- Réponse Mistral --------------

Pour atteindre un niveau d'abstraction suffisant qui vous permet d'utiliser deux méthodes de stockage différentes (un dictionnaire en mémoire pour le backtest et une base de données pour le live), vous pouvez utiliser un modèle de conception appelé le pattern "Repository". Ce pattern permet de séparer la logique de stockage des données du reste de votre application, ce qui facilite le changement de méthode de stockage sans affecter la logique métier.

Voici comment vous pouvez structurer votre code en utilisant ce pattern :

Définir une Interface de Repository :

Créez une interface (ou une classe abstraite) qui définit les opérations de base que vous souhaitez effectuer sur vos ordres.

Copy
from abc import ABC, abstractmethod
from typing import Dict, List

class OrderRepository(ABC):
    @abstractmethod
    def add_order(self, order_id: int, order: 'Order') -> None:
        pass

    @abstractmethod
    def get_order(self, order_id: int) -> 'Order':
        pass

    @abstractmethod
    def get_all_orders(self) -> Dict[int, 'Order']:
        pass

    @abstractmethod
    def remove_order(self, order_id: int) -> None:
        pass
Implémenter des Repositories Concrets :

Créez des classes concrètes qui implémentent l'interface OrderRepository pour chaque méthode de stockage.

Pour le backtest :

Copy
class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self.order_book: Dict[int, Order] = {}

    def add_order(self, order_id: int, order: 'Order') -> None:
        self.order_book[order_id] = order

    def get_order(self, order_id: int) -> 'Order':
        return self.order_book.get(order_id)

    def get_all_orders(self) -> Dict[int, 'Order']:
        return self.order_book

    def remove_order(self, order_id: int) -> None:
        if order_id in self.order_book:
            del self.order_book[order_id]

Pour le live (exemple avec une base de données SQLite) :

Copy
import sqlite3
from typing import Dict

class DatabaseOrderRepository(OrderRepository):
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self._init_db()

    def _init_db(self):
        with self.db_connection:
            self.db_connection.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY,
                    order_data TEXT
                )
            ''')

    def add_order(self, order_id: int, order: 'Order') -> None:
        with self.db_connection:
            self.db_connection.execute(
                'INSERT INTO orders (order_id, order_data) VALUES (?, ?)',
                (order_id, str(order))
            )

    def get_order(self, order_id: int) -> 'Order':
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT order_data FROM orders WHERE order_id = ?', (order_id,))
        result = cursor.fetchone()
        if result:
            return eval(result[0])  # Assurez-vous que cette évaluation est sécurisée
        return None

    def get_all_orders(self) -> Dict[int, 'Order']:
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT order_id, order_data FROM orders')
        return {row[0]: eval(row[1]) for row in cursor.fetchall()}  # Assurez-vous que cette évaluation est sécurisée

    def remove_order(self, order_id: int) -> None:
        with self.db_connection:
            self.db_connection.execute(
                'DELETE FROM orders WHERE order_id = ?',
                (order_id,)
            )
Utiliser le Repository dans votre Code :

Maintenant, vous pouvez utiliser le OrderRepository dans votre code sans vous soucier de la méthode de stockage sous-jacente.

Copy
class TradingSystem:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def orders_to_execute(self, event: 'Event') -> None:
        for order_id, order in self.order_repository.get_all_orders().items():
            if order.is_executable(event.data):
                self.take_order(order)
                self.order_repository.remove_order(order_id)

    def take_order(self, order: 'Order') -> None:
        # Logique pour exécuter un ordre
        pass
Configuration et Injection de Dépendances :

Enfin, configurez votre système pour injecter le bon repository en fonction de l'environnement (backtest ou live).

Copy
# Pour le backtest
order_repository = InMemoryOrderRepository()
trading_system = TradingSystem(order_repository)

# Pour le live
db_connection = sqlite3.connect('orders.db')
order_repository = DatabaseOrderRepository(db_connection)
trading_system = TradingSystem(order_repository)

En utilisant ce pattern, vous pouvez facilement basculer entre différentes méthodes de stockage sans modifier la logique métier de votre système de trading.