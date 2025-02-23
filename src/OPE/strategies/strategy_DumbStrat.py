# Description: This is a template for creating a new strategy. Copy this file and rename it to your strategy name.
# You can then implement your strategy in the execute method.
# You can also add any other methods or attributes that you need.
# Make sure to import your strategy in the main.py file.

class Strategy:

    """
    def make_orders
    def close_condition
    def open_condition
    """
    #Built in function setup
    def __init__(self,name, Grider):
        self.grid_maker = Grider
        self.grid_params= self.set_grid_params()
        self.order_params = self.set_order_params()

    def __call__(self,current_price):
        """
        args :
            current_price : current_price
            grid_params :
                prct_of_intervall : intervall between grid
                nb_orders : 
            order_params :
                'qty':quantity_of_btc_to_sell/buy,
                'leverage': leverage to apply at this order,
                'take_profit': TP_close_condition,
                'stop_loss': SL_close_condition
        """ 
        params = {'grid_origin': current_price, 
                    'prct_of_intervall': self.grid_params['prct_of_intervall'], 
                    'nb_orders': self.grid_params['nb_orders'],
                    'orders_params': self.order_params,
         'open_condition': self.open_condition, 
         'close_condition': self.close_condition}
        return self.make_orders(params)

    # Change grid
    def make_orders(self, grid_parameters):
        """
        grid_parameters :
            - grid_origin: float, the price of the first order
            - prct_of_intervall : float, the percentage of the price between orders
            - nb_orders : int, the number of orders to make
            - orders_hyperparams : dict, the parameters of the orders
                'qty':100,
                'is_buy':True,
                'leverage':1,
                'take_profit':0,
                'stop_loss':0,
                'justif' : 'justif'
            - open_condition : function, the opening condition
            - closing_condition : function, the closing condition
        """
        self.grid_parameters=grid_parameters
        grid = self.grid_maker(self.grid_parameters)
        return {'buy_orders' :grid['buy_orders'],'sell_orders' :grid['sell_orders']}
    
    def set_grid_params(self):
        return {'prct_of_intervall' : 0.01,
                           'nb_orders' : 1}
    
        # Le wrapper est à modifier par le dev qui créé un type de grille. Il devra alors convertir les différents arguements
        # à sa disposition pour que le call soit adapté à l'appel de la grille ou de l'update grille
        #Structure uniforme d'appel inter-module :
        #    strat -> grille
        #    strat -> BACKTEST
        
    def set_order_params(self):
        return {'qty':100,
                'leverage': 1,
                'take_profit': 0.01,
                'stop_loss': 0.01/2}
    
    # Change one element on grid
    def update_grid(self, current_price):
        """
        current_grid : dict, the current grid
        grid_parameters : dict, the parameters of the new grid
        which_orders : str, 'buy_orders' or 'sell_orders'
        """
        self.grid_parameters['grid_origin'] = current_price
        grid = self.grid_maker(self.grid_parameters)
        return {'buy_orders' :grid['buy_orders'],'sell_orders' :grid['sell_orders']}

    # Conditions for orders
    def close_condition(self, position, price_n, price_n_1):
        """
        in :
            position
            price_n
            price_n_1
        Output Struct :
            Position_id à fermer, justif de fermeture
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
    
    def open_condition(self, orders, price_n, price_n_1):
        price_n = float(price_n)
        price_n_1 = float(price_n_1)
        if orders['buy_orders'][0]['level']>=price_n and orders['buy_orders'][0]['level']<price_n_1 :return "BUY"
        if orders['sell_orders'][0]['level']<=price_n and orders['sell_orders'][0]['level']>price_n_1 :return "SELL"
        return False