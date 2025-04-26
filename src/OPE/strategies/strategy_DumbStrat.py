# Description: This is a template for creating a new strategy. Copy this file and rename it to your strategy name.
# You can then implement your strategy in the execute method.
# You can also add any other methods or attributes that you need.
# Make sure to import your strategy in the main.py file.

class Strategy:
    """
    Implémente une Stratégie,\n 
    c'est à dire une manière de créer les ordres dans la grille (grid_params et order_params)\n
    et leurs conditions d'ouverture et de fermeture (close_condition et open_condition)\n

    Dans le cas de la DumbStrat, les paramètres des ordres et de la grille sont définis à l'initialisation\n
    et ne changeront pas pendant l'itération.\n

    Les ordres ont donc tous un RR = 2 (TP = 2*SL où TP = 1%), sans levier et avec une qty arbitraire\n
    La grille crée 1 ordre de vente au dessus du prix et un ordre d'achat en dessous du prix (±1%).\n

    Arguments:
        - name : Nom de la stratégie
        - Grider : Instance de la classe MakeGrid.Grid_Maker

    Attributes:
        - grid_maker (object) : Grider
        - grid_params (dict) : Paramètres de la grille
        - order_params (dict) : Paramètres des ordres
        - grid_parameters (dict) : Combinaison des paramètres d'ordre et de grille

    Methods:
        - __call__(current_price) : Process les paramètres et les passe dans make_order
        - set_grid_params : Définit les paramètres de la grille
        - set_order_params : Définit les paramètres des ordres
        - make_orders(grid_parameters) : Génère une grille grâce à grid_maker
        - update_grid(current_price) : Met à jour la grille (ATTENTION : il semble que le comportement soit strictement identique à __call__)
        - close_condition(position, price_n, price_n_1) : Définit la condition de fermeture d'une position
        - open_condition(orders, price_n, price_n_1) : Définit la condition d'ouverture d'une position
    """
    #Built in function setup
    def __init__(self,name, Grider, grid_params=None, order_params=None):
        """
        """
        self.grid_maker = Grider
        self.grid_params= grid_params
        self.order_params = order_params
        self.metadata = {'StrategyName': name,
                'GridPrctIntervall': self.grid_params['prct_of_intervall'], 
                'GridNbOrder': self.grid_params['nb_orders'], 
                'OrderQty': self.order_params['qty'],
                'OrderLeverage': self.order_params['leverage'],
                'OrderTakeProfit': self.order_params['take_profit'],
                'OrderStopLoss': self.order_params['stop_loss'],
                'OrderJustif': self.order_params['justif'],
                'OrderState': self.order_params['state']}

    def __call__(self,current_price):
        """
        Appelle self.make_orders.\n

        Arguments:
            - current_price (float) : Prix au niveau n de l'itération

        Returns:
            - self.make_orders
        """ 
        params = {'grid_origin': current_price, 
                    'prct_of_intervall': self.grid_params['prct_of_intervall'], 
                    'nb_orders': self.grid_params['nb_orders'],
                    'orders_params': self.order_params,
         'open_condition': self.open_condition, 
         'close_condition': self.close_condition,
         'justif' : 'init'}

        return self.make_orders(params)

    # Change grid
    def make_orders(self, grid_parameters):
        """
        Génère une grille grâce à grid_maker.\n

        Arguments:
            - grid_parameters (dict) : Combinaison des paramètres d'ordre et de grille
            
        Returns:
            - dict : Dictionnaire {'buy_orders', 'sell_orders'} contenant les listes d'ordres d'achat et de vente
        """
        self.grid_parameters=grid_parameters
        grid = self.grid_maker(self.grid_parameters)
        return {'buy_orders' :grid['buy_orders'],'sell_orders' :grid['sell_orders'],'metadatas':{'grid_index' : grid['index']}}
    
    # Change one element on grid
    def update_grid(self, current_price):
        """
        Met à jour la grille (ATTENTION : il semble que le comportement soit strictement identique à __call__).\n

        current_grid : dict, the current grid\n
        grid_parameters : dict, the parameters of the new grid\n
        which_orders : str, 'buy_orders' or 'sell_orders'\n

        Arguments:
            - current_price (float) : Prix au niveau n de l'itération
        
        Returns:
            - dict : Dictionnaire {'buy_orders', 'sell_orders'} contenant les listes d'ordres d'achat et de vente
        
        """
        self.grid_parameters['grid_origin'] = current_price
        grid = self.grid_maker(self.grid_parameters)
        return {'buy_orders' :grid['buy_orders'],'sell_orders' :grid['sell_orders'],'metadatas':{'grid_index' : grid['index']}}

    # Conditions for orders
    def close_condition(self, position, price_n, price_n_1):
        """
        Définit la condition de fermeture d'une position.\n
        Si la condition est rempli retourne l'id de cette position.\n

        Dans ce cas, on teste juste si le prix a passé un palier de TP ou SL

        Arguments:
            - position (dict) : Position à tester
            - price_n (float) : Prix au niveau n de l'itération
            - price_n_1 (float) : Prix au niveau n-1 de l'itération
        
        Returns:
            - (int, str) : Si la position doit être fermée
            - (False, False) : Si la position reste ouverte
        """
        if position['is_buy']:
            stop_loss_price = position['entryprice']*(1-position['stop_loss'])
            take_profit_price = position['entryprice']*(1+position['take_profit'])
            if   price_n <= stop_loss_price and price_n_1 >stop_loss_price : 
                return (position['id'], 'STOPLOSS BUY')
            elif price_n >= take_profit_price and price_n_1 < take_profit_price : 
                return (position['id'], 'TAKEPROFIT BUY')
        
        if position['is_buy']==False:
            stop_loss_price = position['entryprice']*(1+position['stop_loss'])
            take_profit_price = position['entryprice']*(1-position['take_profit'])
            if price_n >=  stop_loss_price and price_n_1 <stop_loss_price: 
                return (position['id'], 'STOPLOSS SELL')
            elif price_n <= take_profit_price and price_n_1 > take_profit_price: 
                return (position['id'], 'TAKEPROFIT BUY')
        return False, False
    
    def open_condition(self, orders, price_n, price_n_1,order_type):
        """
        Définit la condition d'ouverture des ordres les plus proches du prix.\n
        Teste donc 1 ordre d'achat et 1 ordre de vente.\n
        On ne peut pas ouvrir les deux ordres en même temps.\n

        Arguments:
            - orders (dict) : Ordre à tester 
            - price_n (float) : Prix au niveau n de l'itération
            - price_n_1 (float) : Prix au niveau n-1 de l'itération

        Returns:
            - str : Si ordre à ouvrir
            - False : Sinon
        """
        price_n = float(price_n)
        price_n_1 = float(price_n_1)
        if  orders[order_type][0]['level']>=price_n and orders[order_type][0]['level']<price_n_1 :return "BUY"
        if  orders[order_type][0]['level']<=price_n and orders[order_type][0]['level']>price_n_1 :return "SELL"
        return False
    #order_type == 'buy_orders' and
    #order_type == 'sell_orders' and