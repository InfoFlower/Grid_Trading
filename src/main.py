###
##  IMPORT PACKAGES
###
##
# OUR PACKAGES
import OPE.MakeGrid as MakeGrid
from OPE.strategies.strategy_DumbStrat import Strategy
from OPE.Logger import Logger
from OPE.BackTest import baktest
#from OPE.reporting.app import Reporting
##
# OTHER PACKAGES
import os
import time
from dotenv import load_dotenv
import polars as pl
from datetime import datetime


load_dotenv()
start_time = datetime.fromtimestamp(time.time())
WD = os.getenv('WD')

def main(args_dict):
    ##
    #Set Grid and Strategy names
    GridType = 'BasicGrid'
    StratName = 'DumbStrat'
    GridName='GridPoc'
    type_of_file = 'full'
    GridFullName = f'{StratName}_{GridType}_{GridName}'
    ##
    #SETUP DATA
    if type_of_file=='full':
        path=f'{WD}data/OPE_DATA/DATA_RAW_S_ORIGIN_test_code/data_raw_BTCUSDT_176.csv'
    else :
        start_time = 153
        path=f'data/OPE_DATA/DATA_RAW_S_ORIGIN_test_code/data_raw_BTCUSDT_{start_time}.csv'

    data=pl.read_csv(path, truncate_ragged_lines=True)
    self_log_path = f'{WD}src/OPE/reporting/BACKTESTS/'
    ##
    #SETUP DATA COLUMNS
    DataStructure = args_dict['DataStructure']
    {"GridOrders_params":{"qty":0.1,"leverage":1,"take_profit":0.01,"stop_loss":0.005,"justif":"init","state":"open"},"Grid_Metadata":{"prct_of_intervall":0.01,"nb_orders":1},"money_balance":1000,"time_4_epoch":50000}
    ##
    #Shape data
    data=data[[i for i in DataStructure.values()]]

    DataStructure = { 'TimeCol' : 0,
                      'CloseCol' :1,
                      'LowCol' :  2, 
                      'HighCol' : 3}

    data=data.to_numpy()
    #Setup Grid Parameters
    GridOrders_params = args_dict['GridOrders_params']
    Grid_Metadata = args_dict['Grid_Metadata']
    #Set initial balance
    money_balance= 1000
    crypto_balance= money_balance/data[0][DataStructure['CloseCol']] #BTC
    time_4_epoch=10000




    DataStructure = [i for i in DataStructure.values()]

    grid_write_path = f'{WD}data/trade_history/grid/'
    ###
    ##INIT CLASS
    ###
    logger = Logger(append=False) 
    grid_maker = MakeGrid.Grid_Maker(GridType, GridName,grid_write_path)
    strategy = Strategy(StratName, grid_maker, Grid_Metadata, GridOrders_params)
    backtest_id=1
    bktst=baktest(path, strategy, money_balance, crypto_balance, logger, backtest_id,self_log_path = self_log_path,time_4_epoch=time_4_epoch,TimeCol=DataStructure[0],CloseCol=DataStructure[1],LowCol=DataStructure[2],HighCol=DataStructure[3])



    ###
    ##RUN BACKTEST
    ###

    if type_of_file=='full':
        for _ in bktst:
            _
        with open(bktst.strategy.grid_maker.write_path, 'a') as f:f.write(']')

    else:
        for i in range(start_time, 154):
            for _ in bktst:
                _  # SSE format
            data=pl.read_csv(f'data\OPE_DATA\DATA_RAW_S_ORIGIN_test_code\data_raw_BTCUSDT_{i}.csv', truncate_ragged_lines=True)
            data=data[['Open time','Close']]
            bktst(data)
        with open(bktst.strategy.grid_maker.write_path, 'a') as f: f.write(']')
    return 'Backtest finished'