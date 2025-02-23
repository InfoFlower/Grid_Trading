# Description: This is a template for creating a new strategy. Copy this file and rename it to your strategy name.
# You can then implement your strategy in the execute method.
# You can also add any other methods or attributes that you need.
# Make sure to import your strategy in the main.py file.

class Strategy:
    def __init__(self,name, Grider):
        self.grid_maker = Grider

    def __call__(self,current_data_info , grid_params , order_params):
        """
        Exemple de structure de données :
                    params = {
                    current_data_info : Info du backtest sur market data
                    grid_params: grid_params,
                    'orders_params': order_params,
                    'open_condition': self.open_condition, 
                    'close_condition': self.close_condition}
        
        Output uniformisé pour grille
            {
            A FAIRE
            }

        Output uniformisé pour baktest
            {
            A FAIRE
            }
        !!!Wrapper à appeler dans le call pour uniformiser fonction d'appel à la grille/baktest!!!
        """
        pass
        
    def wrapper_in(self,**kwargs):
        pass

    def make_orders(self, grid_parameters):
        pass
    
    def close_condition(self, position, price_n, price_n_1):
        pass
    
    def open_condition(self, orders, price_n, price_n_1):
        pass