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
        
    def Make_Basic_Grid(self,args):
        buy_orders = [args['grid_origin']+args['grid_origin']*(i*args['prct_of_intervall']) for i in range(1, args['nb_orders']+1)]
        sell_orders = [args['grid_origin']-args['grid_origin']*(i*args['prct_of_intervall']) for i in range(1, args['nb_orders']+1)]
        with open(self.write_path, 'a') as f:
            f.write(f"{self.index};{buy_orders};{sell_orders};{args['grid_origin']}\n")
        return self.index, buy_orders, sell_orders, args['grid_origin']
    

if __name__ == '__main__':
    grid_type, grid_name, write_path='basic_grid', 'grid_test', 'data/trade_history/grid/'
    maker = Grid_Maker(grid_type, grid_name, write_path)
    for i in range(100,500+1,100):
        args = {'grid_origin': i, 'prct_of_intervall': 0.01, 'nb_orders': 10}
        maker(args)