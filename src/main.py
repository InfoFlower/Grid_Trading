###
##  IMPORT PACKAGES
###
##
# OUR PACKAGES
import OPE.MakeGrid as MakeGrid
from OPE.strategies.strategy_DumbStrat import Strategy
from OPE.Logger import Logger
from OPE.BackTest import baktest
import requests
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

class main:
    def __init__(self,args_dict):
            ##
        #Set Grid and Strategy names
        self.GridType = 'BasicGrid'
        self.StratName = 'DumbStrat'
        self.GridName='GridPoc'
        self.type_of_file = 'full'
        GridFullName = f'{self.StratName}_{self.GridType}_{self.GridName}'
        ##
        #SETUP DATA
        if self.type_of_file=='full':
            if len(args_dict["DataFile"].split('_'))>3:
                path=f'{WD}data/OPE_DATA/DATA_RAW_S_ORIGIN_test_code/{args_dict["DataFile"]}.csv'
            else: 
                path=f'{WD}data/DATA_RAW_S_ORIGIN/{args_dict["DataFile"]}.csv'
        else :
            start_time = 153
            path=f'data/OPE_DATA/DATA_RAW_S_ORIGIN_test_code/data_raw_BTCUSDT_{start_time}.csv'

        self.data=pl.read_csv(path, truncate_ragged_lines=True)
        self.self_log_path = f'{WD}src/OPE/reporting/BACKTESTS/'
        ##
        #SETUP DATA COLUMNS
        self.DataStructure = args_dict['DataStructure']

        ##
        #Shape data
        self.data=self.data[[i for i in self.DataStructure.values()]]

        self.DataStructure = { 'TimeCol' : 0,
                          'CloseCol' :1,
                          'LowCol' :  2, 
                          'HighCol' : 3}
        self.data=self.data.to_numpy()
        #Setup Grid Parameters
        self.GridOrders_params = args_dict['GridOrders_params']
        self.Grid_Metadata = args_dict['Grid_Metadata']
        #Set initial balance
        self.money_balance= 1000
        self.crypto_balance= self.money_balance/self.data[0][self.DataStructure['CloseCol']] #BTC
        self.time_4_epoch=10000




        self.DataStructure = [i for i in self.DataStructure.values()]

        self.grid_write_path = f'{WD}data/trade_history/grid/'
        ###
        ##INIT CLASS
        ###
        self.logger = Logger(append=False) 
        self.grid_maker = MakeGrid.Grid_Maker(self.GridType, self.GridName,self.grid_write_path)
        strategy = Strategy(self.StratName, self.grid_maker, self.Grid_Metadata, self.GridOrders_params)
        backtest_id=1
        self.bktst=baktest(path, strategy, self.money_balance, self.crypto_balance, self.logger, backtest_id,self_log_path = self.self_log_path,time_4_epoch=self.time_4_epoch,TimeCol=self.DataStructure[0],CloseCol=self.DataStructure[1],LowCol=self.DataStructure[2],HighCol=self.DataStructure[3])



        ###
        ##RUN BACKTEST
        ###
        self.total_line = len(self.bktst)
        self.i=0
        self.last_emitted=0

    def main(self,uuid):
        if self.type_of_file=='full':
            last_progress = -10
            for _ in self.bktst:
                _
                self.i+=1
                self.progress = int((self.i / self.total_line) * 100)
                if self.progress >= last_progress +10:
                    requests.get(f'http://localhost:5000/put_data/{uuid}_status/{self.progress}')
                    last_progress = self.progress
            requests.get(f'http://localhost:5000/put_data/{uuid}_status/100')
            with open(self.bktst.strategy.grid_maker.write_path, 'a') as f:f.write(']')

        else:
            for i in range(start_time, 154):
                for _ in self.bktst:
                    _  # SSE format
                data=pl.read_csv(f'data\OPE_DATA\DATA_RAW_S_ORIGIN_test_code\data_raw_BTCUSDT_{i}.csv', truncate_ragged_lines=True)
                data=data[['Open time','Close']]
                self.bktst(data)
            with open(self.bktst.strategy.grid_maker.write_path, 'a') as f: f.write(']')
        return 'Backtest finished'