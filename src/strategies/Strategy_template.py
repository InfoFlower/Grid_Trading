# Description: This is a template for creating a new strategy. Copy this file and rename it to your strategy name.
# You can then implement your strategy in the execute method.
# You can also add any other methods or attributes that you need.
# Make sure to import your strategy in the main.py file.

class Strategy:
    def __init__(self,name, Grider):
        self.grid_maker = Grider

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
        grid = self.grid_maker(grid_parameters)
        return {'buy_orders' :grid['buy_orders'],'sell_orders' :grid['sell_orders']}
    
    def close_condition(self, position, price_n, price_n_1):
        """
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
        if orders['buy_orders'][0]['level']>=price_n and orders['buy_orders'][0]['level']<price_n_1 :return "BUY"
        if orders['sell_orders'][0]['level']<=price_n and orders['sell_orders'][0]['level']>price_n_1 :return "SELL"
        return False
    
    def __call__(self,grid_origin, prct_of_intervall, nb_orders):
        params = {'grid_origin': grid_origin, 
                    'prct_of_intervall': prct_of_intervall, 
                    'nb_orders': nb_orders,
                    'orders_params': {
                            'qty':100,
                            'leverage':1,
                            'take_profit':prct_of_intervall,
                            'stop_loss':prct_of_intervall/2
                    },
         'open_condition': self.open_condition, 
         'close_condition': self.close_condition}
        return self.make_orders(params)
    
