# Description: This is a template for creating a new strategy. Copy this file and rename it to your strategy name.
# You can then implement your strategy in the execute method.
# You can also add any other methods or attributes that you need.
# Make sure to import your strategy in the main.py file.
from src.MakeGrid import Grid_Maker as Grid_Maker
from src.MakePast import  baktest as baktest
import polars as pl


class Strategy:
    def __init__(self,name, price='Close'):
        self.price = price

    def execute(self, data):
        if self.first:
            print('first')
            self.first=False
            data_n_1 = data
        buy_grid = self.grid[1]
        sell_grid = self.grid[2]
        if 0 not in self.pool.values():
            print(data_n_1)
            if data[self.price] > buy_grid[0] and data_n_1[self.price] < buy_grid[0]:
                print('buy')
                self.buy_signal = True
                self.amount = 10
                self.sell_signal = False
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

    
    def __call__(self):
        data = pl.read_csv(r'data\OPE_DATA\DATA_RAW_S_ORIGIN_test_code\data_raw_BTCUSDT_251.csv',separator=',',truncate_ragged_lines=True)
        data=data[['Open time','Close']].to_numpy()
        TimeCol=0
        CloseCol=1
        money_balance=1000
        crypto_balance=1000
        bktst=baktest(data, 0, money_balance, crypto_balance,TimeCol,CloseCol)
        self.pool=bktst.pool
        Grider = Grid_Maker('basic_grid', 'grid_test')
        it=0
        for i in bktst:
            if it==0:
                self.first=True
                self.grid = Grider({'grid_origin': i[CloseCol], 'prct_of_intervall': 0.001, 'nb_orders': 10})
            self.execute(i)
            if self.buy_signal:
                bktst.make_position(self.amount, 'buy', top_buy=True)
            if self.sell_signal:
                bktst.make_position(self.amount, 'buy')
            self.pool = bktst.pool
            it+=1


if __name__ == '__main__':
    Price = 1
    strat = Strategy('basic_grid', Price)
    strat()