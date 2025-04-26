###
##  IMPORT PACKAGES
###
##
# OUR PACKAGES
import src.OPE.MakeGrid as MakeGrid
from src.OPE.strategies.strategy_DumbStrat import Strategy
from src.OPE.Logger import Logger
from src.OPE.BackTest import baktest
#from src.OPE.reporting.app import Reporting
##
# OTHER PACKAGES
import os
import time
from dotenv import load_dotenv
import polars as pl
import argparse
from datetime import datetime

load_dotenv()
start_time = datetime.fromtimestamp(time.time())
WD = os.getenv('WD')
print('Start time :', start_time)
###
##SETUP VARIABLES
###
argparser = argparse.ArgumentParser()
argparser.add_argument('--type_of_file', type=str, default='full')
args=argparser.parse_args()
type_of_file=args.type_of_file

# print('\n'*2, '#'*20,'\n'*2)
# print('STARTING PROCESS AYAAAAAA')
# print('\n'*2, '#'*20,'\n'*2)


# after_vars = datetime.fromtimestamp(time.time())
# print('After vars :', after_vars)
# print('Time to setup vars :', after_vars - start_time)
# print('General time to setup :', after_vars - start_time)


# print('\n'*2, '#'*20,'\n'*2)
# after_data = datetime.fromtimestamp(time.time())
# print('After data :', after_data)
# print('Time to setup data :', after_data - after_vars)
# print('General time to setup :', after_data - start_time)



##
#Set Grid and Strategy names
GridType = 'BasicGrid'
StratName = 'DumbStrat'
GridName='GridPoc'

GridFullName = f'{StratName}_{GridType}_{GridName}'
##
#SETUP DATA
if type_of_file=='full':
    path=f'{WD}data/DATA_RAW_S_ORIGIN\data_raw_BTCUSDT.csv'
    print(path)
else :
    start_time = 153
    path=f'data\OPE_DATA\DATA_RAW_S_ORIGIN_test_code\data_raw_BTCUSDT_{start_time}.csv'

data=pl.read_csv(path, truncate_ragged_lines=True)
##
#SETUP DATA COLUMNS
DataStructure = {'TimeCol' : 'Open time', 'CloseCol' : 'Close', 'LowCol' : 'Low',  'HighCol' : 'High'}
#Setup Grid Parameters
GridOrders_params = {'qty':0.1, 'leverage': 1, 'take_profit': 0.01, 'stop_loss': 0.01/2, 'justif' : 'init', 'state' : 'open'}
Grid_Metadata = {'prct_of_intervall' : 0.01, 'nb_orders' : 1}
#Set initial balance
money_balance= 1000 #USD
crypto_balance=money_balance/data[0][DataStructure['CloseCol']] #BTC
time_4_epoch=50000

##
#Shape data
print('Data shape :', data.columns)
data=data[[i for i in DataStructure.values()]]

DataStructure = { 'TimeCol' : 0,
                  'CloseCol' :1,
                  'LowCol' :  2, 
                  'HighCol' : 3}
DataStructure = [i for i in DataStructure.values()]
data=data.to_numpy()





###
##INIT CLASS
###
logger = Logger() 
grid_maker = MakeGrid.Grid_Maker(GridType, GridName)
strategy = Strategy(StratName, grid_maker, Grid_Metadata, GridOrders_params)
backtest_id=1
bktst=baktest(path, strategy, money_balance, crypto_balance, logger, backtest_id,time_4_epoch=500000,TimeCol=DataStructure[0],CloseCol=DataStructure[1],LowCol=DataStructure[2],HighCol=DataStructure[3])



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