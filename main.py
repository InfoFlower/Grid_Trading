###
##  IMPORT PACKAGES
###
##
# OUR PACKAGES
import src.MakeGrid as MakeGrid
from src.strategies.Strategy_template import Strategy
from src.BackTest import baktest
import time
##
# OTHER PACKAGES
import polars as pl
import pandas as pd
import argparse
from datetime import datetime

start_time = datetime.fromtimestamp(time.time())
print('Start time :', start_time)
###
##SETUP VARIABLES
###
argparser = argparse.ArgumentParser()
argparser.add_argument('--type_of_file', type=str, default='full')
args=argparser.parse_args()
type_of_file=args.type_of_file
##
#Set Grid and Strategy names
GridType = 'BasicGrid'
StratName = 'DumbStrat'
GridName='GridPoc'

GridFullName = f'{StratName}_{GridType}_{GridName}'

print('\n'*2, '#'*20,'\n'*2)
print('STARTING PROCESS AYAAAAAA')
print('\n'*2, '#'*20,'\n'*2)


after_vars = datetime.fromtimestamp(time.time())
print('After vars :', after_vars)
print('Time to setup vars :', after_vars - start_time)
print('General time to setup :', after_vars - start_time)
##
#SETUP DATA
if type_of_file=='full':
    path='data\DATA_RAW_S_ORIGIN\data_raw_BTCUSDT.csv' ### A modif
else :
    start_time = 153
    path=f'data\OPE_DATA\DATA_RAW_S_ORIGIN_test_code\data_raw_BTCUSDT_{start_time}.csv'

data=pl.read_csv(path, truncate_ragged_lines=True)

print('\n'*2, '#'*20,'\n'*2)
after_data = datetime.fromtimestamp(time.time())
print('After data :', after_data)
print('Time to setup data :', after_data - after_vars)
print('General time to setup :', after_data - start_time)

##
#SETUP DATA COLUMNS
TimeCol='Open time'
CloseCol='Close'

##
#Shape data
data=data[[TimeCol,CloseCol]]
TimeCol=0
CloseCol=1
data=data.to_numpy()
##
#Set initial balance
money_balance=1000000 #USD
crypto_balance=money_balance/data[0][CloseCol] #BTC


time_4_epoch=50000

###
##INIT CLASS
###
grid_maker = MakeGrid.Grid_Maker(GridType, GridName)
strategy = Strategy(StratName, grid_maker)
bktst=baktest(data, strategy, money_balance,crypto_balance,TimeCol,CloseCol,time_4_epoch=500000)


print('\n'*2, '#'*20,'\n'*2)
after_init = datetime.fromtimestamp(time.time())
print('After init :', after_init)
print('Time to setup data :', after_init - after_data)
print('General time to setup :', after_init - start_time)

###
##RUN BACKTEST
###



if type_of_file=='full':
    for _ in bktst:
        pass
    with open(bktst.strategy.grid_maker.write_path, 'a') as f:f.write(']')

else:
    for i in range(start_time, 154):
        for _ in bktst:
            pass
        data=pl.read_csv(f'data\OPE_DATA\DATA_RAW_S_ORIGIN_test_code\data_raw_BTCUSDT_{i}.csv', truncate_ragged_lines=True)
        data=data[['Open time','Close']]
        bktst(data)
        print(i)
    with open(bktst.strategy.grid_maker.write_path, 'a') as f: f.write(']')


print('\n'*2, '#'*20,'\n'*2)
after_end = datetime.fromtimestamp(time.time())
print('After end :', after_end)
print('Time to end run :', after_end - after_data)
print('General time to run :', after_end - start_time)