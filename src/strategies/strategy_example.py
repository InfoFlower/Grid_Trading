# Description: This is a template for creating a new strategy. Copy this file and rename it to your strategy name.
# You can then implement your strategy in the execute method.
# You can also add any other methods or attributes that you need.
# Make sure to import your strategy in the main.py file.

class Strategy:
    def __init__(self,name, baktest, Grider, price='Close'):
        self.price = price
        self.baktest = baktest
        self.grid = Grider

    def decision(self, data, grid_parameters):
            self.first=False
            self.baktest.buy_grid = self.grid[1]
            self.baktest.sell_grid = self.grid[2]
            return data

    
if __name__ == '__main__':
    Price = 1
    strat = Strategy('basic_grid', Price)
    strat()