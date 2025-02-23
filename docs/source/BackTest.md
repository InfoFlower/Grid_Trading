# backtest

La classe [backtest](src/BackTest.py) prend les arguments suivants
- data #
- strategy # Une instance de la classe strategy
- money_balance # la balance d'argent initiale (USD)
- crypto_balance # la balance de crypto initiale (BTC)
- TimeCol # L'index de la colonne du temps, prend 'Open Time' par défaut
- CloseCol # L'index de la colonne du close_price, prend 'Close' par défaut
- log_path # Le chemin relatif du réperoire de log, prend 'data/trade_history/' par défaut
- time_4_epoch # Nombre de ligne=50000

et inialise les variables