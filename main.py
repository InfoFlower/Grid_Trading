from src.MakeGrid import Grid_Maker as Grid_Maker
from src.MakePast_v2 import  baktest as baktest
from src.strategies.strategy_example import  Strategy
import polars as pl

#Make data
data = pl.read_csv(r'data\OPE_DATA\DATA_RAW_S_ORIGIN_test_code\data_raw_BTCUSDT_251.csv',separator=',',truncate_ragged_lines=True)
data=data[['Open time','Close']].to_numpy()

#Set structure
TimeCol=0
CloseCol=1

#Set balance
money_balance=1000
crypto_balance=1000

# SETTING UP THE STRATEGY (STRATEGY : make bktst and grid)
Grider = Grid_Maker('basic_grid', 'grid_test')
bktst=baktest(data, 0, money_balance, crypto_balance,TimeCol,CloseCol)
strat=Strategy('basic_grid', bktst, Grider, 'Close')





#ITERATING OVER THE DATA

it=0
for i in strat.bktst:
    if it==0:
        first=True
        strat.grid = strat.baktest.grid({'grid_origin': i[CloseCol], 'prct_of_intervall': 0.001, 'nb_orders': 10})
    strat.execute(i)
    if strat.buy_signal:
        strat.bktst.make_position(strat.amount, 'buy', top_buy=True)
    if strat.sell_signal:
        strat.bktst.make_position(strat.amount, 'buy')
    it+=1