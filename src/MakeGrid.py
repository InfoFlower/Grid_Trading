######################################################################################################################################
########################                           MAKE GRID FOR GRID TRADING                        #################################
######################################################################################################################################

######################################################################################################################################
#                            
#                                            STRUCTURE OF THE BASIC_GRID GRID
#                       
#                                            grid_origin: float, the price of the first order
#                                            prct_of_intervall : float, the percentage of the price between orders
#                                            nb_orders : int, the number of orders to make
#
######################################################################################################################################

class Grid_Maker:
    def __init__(self, grid_type, grid_name, write_path='data/trade_history/grid/'):
        """
        STRUCTURE OF THE 'basic_grid' arguments :
            - grid_origin: float, the price of the first order
            - prct_of_intervall : float, the percentage of the price between orders
            - nb_orders : int, the number of orders to make
            - open_condition : function, the opening condition
            - closing_condition : function, the closing condition
        """
        self.grid_type = grid_type
        self.index=0
        self.write_path = write_path+grid_name+'.csv'
        with open(self.write_path, 'w') as f:
            f.write('Index;Buy_orders;Sell_orders;Grid_origin\n')

    def __call__(self, args):
        self.index+=1
        if self.grid_type == 'basic_grid':
            return self.Make_Basic_Grid(args)
        else:
            raise ValueError(f"Unknown grid type: {self.grid_type}")

    def update_grid(self,args):#ici aucune utilité, faire des grilles (donc strat avec besoin pour implémentation)
        pass


    def make_order(self,i,args,params):
        signe_buy=-1
        if params['is_buy']:signe_buy=1
        return {'level' : args['grid_origin']-signe_buy*args['grid_origin']*(i*args['prct_of_intervall']),
                        'orders_params' : params,
                        'open_condition' : args['open_condition'],
                        'close_condition' : args['close_condition']}
        
    def Make_Basic_Grid(self,args):
        """
        Make a grid of orders
            args : 
                dict, the parameters of the grid
            output :
                dict, index of the grid, the grid of orders
        """
        buy_params = args['orders_params'].copy()
        buy_params['is_buy'] = True
        buy_orders = [self.make_order(i,args,buy_params) for i in range(1, args['nb_orders']+1)]
        sell_params = args['orders_params'].copy()
        sell_params['is_buy'] = False
        sell_orders = [self.make_order(i,args,sell_params) for i in range(1, args['nb_orders']+1)]
        
        grid={'index':self.index,
                'buy_orders' : buy_orders,
                'sell_orders': sell_orders, 
                'origin' : args['grid_origin']}
        
        self.log_grid(grid)
        return grid
    
    def log_grid(self,grid):
        pass