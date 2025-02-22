# Description: This is a template for creating a new strategy. Copy this file and rename it to your strategy name.
# You can then implement your strategy in the execute method.
# You can also add any other methods or attributes that you need.
# Make sure to import your strategy in the main.py file.

class Strategy:
    def __init__(self,name, baktest, Grider, price='Close'):
        self.price = price
        self.baktest = baktest
        self.grid = Grider

    def init_decision(self, data, grid_parameters):
            self.first=False
            self.buy_grid = self.grid[1]
            self.sell_grid = self.grid[2]
            return data


    def decision(self, data, grid_parameters):
        #Init decision
        if self.first: data_n_1 = self.init_decision(data, grid_parameters)
        
        #Decision
        if 0 not in self.baktest.pool.values():
            print(data_n_1)
            if data[self.price] > buy_grid[0] and data_n_1[self.price] < buy_grid[0]:
                print('buy')
                self.baktest.make_position(10, 'buy', top_buy=True)
                self.grid=self.grid
            if data[self.price] > sell_grid[0] and data_n_1[self.price] < sell_grid[0]:
                print('sell')
                self.sell_signal = True
                self.amount = 10
                self.buy_signal = False
            else:
                self.buy_signal = False
                self.sell_signal = False
        else:
            StopIteration #Ici mettre la stratégie de re-création de la grille
        data_n_1 = data


    
if __name__ == '__main__':
    Price = 1
    strat = Strategy('basic_grid', Price)
    strat()