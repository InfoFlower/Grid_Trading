# Architecture Orientée Événements pour un TradingBot

Voici une conception basée sur des événements qui permet une plus grande flexibilité et modularité. Dans cette approche, chaque composant émet des événements que d'autres composants peuvent écouter et traiter.

## Structure de Base

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Callable, Any
import pandas as pd
import uuid

class EventType(Enum):
    MARKET_DATA = "market_data"
    ORDER_CREATED = "order_created"
    ORDER_FILLED = "order_filled"
    POSITION_OPENED = "position_opened"
    POSITION_CLOSED = "position_closed"
    SIGNAL_GENERATED = "signal_generated"

@dataclass
class Event:
    type: EventType
    data: Any
    timestamp: pd.Timestamp

class EventDispatcher:
    def __init__(self):
        self._listeners: Dict[EventType, List[Callable]] = {e: [] for e in EventType}
    
    def add_listener(self, event_type: EventType, callback: Callable):
        self._listeners[event_type].append(callback)
    
    def dispatch(self, event: Event):
        for callback in self._listeners[event.type]:
            callback(event)

class OrderManager:
    def __init__(self, event_dispatcher: EventDispatcher):
        self.event_dispatcher = event_dispatcher
        self.open_orders: Dict[str, Order] = {}
        
        # S'abonne aux événements pertinents
        event_dispatcher.add_listener(EventType.MARKET_DATA, self._process_orders)
        event_dispatcher.add_listener(EventType.SIGNAL_GENERATED, self._create_order)
    
    def _process_orders(self, event: Event):
        # Logique pour traiter les ordres en fonction des données de marché
        pass
    
    def _create_order(self, event: Event):
        # Crée un nouvel ordre basé sur le signal
        pass

class PositionManager:
    def __init__(self, event_dispatcher: EventDispatcher):
        self.event_dispatcher = event_dispatcher
        self.open_positions: Dict[str, Position] = {}
        
        # S'abonne aux événements d'ordres exécutés
        event_dispatcher.add_listener(EventType.ORDER_FILLED, self._update_positions)

    def _update_positions(self, event: Event):
        # Met à jour les positions basées sur les ordres exécutés
        pass

class Strategy(ABC):
    def __init__(self, event_dispatcher: EventDispatcher):
        self.event_dispatcher = event_dispatcher
        event_dispatcher.add_listener(EventType.MARKET_DATA, self._generate_signals)
    
    @abstractmethod
    def _generate_signals(self, event: Event):
        """Analyse les données de marché et émet des signaux"""
        pass

class TradingBot:
    def __init__(self, strategy: Strategy):
        self.event_dispatcher = EventDispatcher()
        self.strategy = strategy(self.event_dispatcher)
        self.order_manager = OrderManager(self.event_dispatcher)
        self.position_manager = PositionManager(self.event_dispatcher)
        self.portfolio_value = 100000
    
    def run_backtest(self, data: pd.DataFrame):
        for i in range(len(data)):
            current_data = data.iloc[i]
            current_time = data.index[i]
            
            # Émet un événement de données de marché
            self.event_dispatcher.dispatch(Event(
                type=EventType.MARKET_DATA,
                data=current_data,
                timestamp=current_time
            ))
            
            # Mise à jour de la valeur du portefeuille (pourrait aussi être événementiel)
            self._update_portfolio_value(current_data['close'])
```

## Exemple de Stratégie Événementielle

```python
class MovingAverageStrategy(Strategy):
    def __init__(self, event_dispatcher: EventDispatcher, short_window=10, long_window=50):
        super().__init__(event_dispatcher)
        self.short_window = short_window
        self.long_window = long_window
        self.data_window = []
    
    def _generate_signals(self, event: Event):
        self.data_window.append(event.data['close'])
        
        if len(self.data_window) < self.long_window:
            return
        
        # Calcul des moyennes mobiles
        short_ma = sum(self.data_window[-self.short_window:]) / self.short_window
        long_ma = sum(self.data_window[-self.long_window:]) / self.long_window
        
        # Émission de signaux
        if (self.data_window[-2] < long_ma and 
            self.data_window[-1] > short_ma > long_ma):
            self.event_dispatcher.dispatch(Event(
                type=EventType.SIGNAL_GENERATED,
                data={
                    'action': 'BUY',
                    'symbol': event.data['symbol'],
                    'price': event.data['close'],
                    'quantity': self._calculate_quantity(event.data['close'])
                },
                timestamp=event.timestamp
            ))
    
    def _calculate_quantity(self, price: float) -> float:
        return 100  # Exemple simplifié
```

## Avantages de cette Architecture

1. **Découplage fort**: Les composants ne se connaissent pas directement, ils communiquent via événements.
2. **Extensibilité**: Ajouter de nouveaux composants est facile - il suffit de les abonner aux événements pertinents.
3. **Flexibilité**: On peut modifier le comportement en changeant les abonnements aux événements.
4. **Testabilité**: Chaque composant peut être testé isolément en simulant des événements.

## Workflow Typique

1. Le bot reçoit des données de marché → émet un événement `MARKET_DATA`
2. La stratégie écoute `MARKET_DATA` et émet un `SIGNAL_GENERATED` si nécessaire
3. L'OrderManager écoute `SIGNAL_GENERATED` et émet `ORDER_CREATED`
4. L'OrderManager traite les ordres et émet `ORDER_FILLED` quand exécuté
5. Le PositionManager écoute `ORDER_FILLED` et met à jour les positions

## Gestion Avancée des Événements

Pour une gestion plus sophistiquée, vous pourriez:

```python
class PriorityEventDispatcher(EventDispatcher):
    def __init__(self):
        super().__init__()
        self._priority_listeners: Dict[int, List[Callable]] = {}
    
    def add_priority_listener(self, event_type: EventType, callback: Callable, priority: int = 0):
        if priority not in self._priority_listeners:
            self._priority_listeners[priority] = []
        self._priority_listeners[priority].append((event_type, callback))
    
    def dispatch(self, event: Event):
        # Exécute les callbacks par ordre de priorité
        for priority in sorted(self._priority_listeners.keys()):
            for event_type, callback in self._priority_listeners[priority]:
                if event_type == event.type:
                    callback(event)
        
        # Exécute les callbacks normaux
        super().dispatch(event)
```

Cette version permet de définir des priorités pour les handlers d'événements, ce qui peut être utile pour garantir un certain ordre d'exécution.

## Conclusion

Cette architecture événementielle offre une grande flexibilité pour:
- Ajouter de nouvelles stratégies sans modifier le code existant
- Modifier le flux de traitement en réorganisant les abonnements aux événements
- Débugger le système en enregistrant tous les événements
- Étendre les fonctionnalités en ajoutant de nouveaux types d'événements

Pour un système encore plus robuste, vous pourriez envisager d'utiliser un pattern comme CQRS (Command Query Responsibility Segregation) ou un event sourcing pour garder un historique complet de tous les événements.