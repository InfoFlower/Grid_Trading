import os

from dotenv import load_dotenv
load_dotenv()
WD = os.getenv('WD')



#Définition des structures

Data_Structure = {
    'BackTest': ['BackTest_ID', 'StartData_Time', 'EndData_Time', 'Symbol', 'InitialCapital', 'FinalCapital'],
    'Position': ['Position_ID','OrderId','Grid_ID','EventData_Time','BackTest_ID','EventCode','PositionQty','PositionClosePrice','CryptoBalance','MoneyBalance'],
    'Order': ['Order_ID','Grid_ID','OrderTime','OrderType','OrderPrice','OrderQuantity','OrderLeverage','OrderTakeProfit','OrderStopLoss','OrderStatus','OrderJustif'],
    'Strategy' : ['BackTest_ID', 'StrategyName','GridPrctIntervall','GridNbOrder','OrderQty','OrderLeverage','OrderTakeProfit','OrderStopLoss','OrderJustif','OrderState']
}



Folder=WD+'src/OPE/reporting/data_logger'


class Logger:
    def __init__(self, LoggingFolder=Folder, Data_Structure=Data_Structure, append=False):
        """
        Logger class to log backtest, trade, and order data.
        """
        print(f'Logger initialized : {LoggingFolder}')
        self.files_path = {}
        self.logged_orders=[]
        self.LoggingFolder = LoggingFolder
        if not os.path.exists(LoggingFolder):
            os.makedirs(LoggingFolder)
        for i in Data_Structure.keys():
            self.files_path[i] = f'{LoggingFolder}/{i}.csv'
            if not os.path.exists(self.files_path[i]) or append == False:
                with open(self.files_path[i], 'w') as f:
                    f.write(','.join(Data_Structure[i]))
                    f.close()

    def __call__(self, data):
        """
        Log data to the appropriate file based on the provided keyword arguments.
        """
        for key, value in data.items():
            if key in self.files_path.keys():
                if key == 'Order' : 
                    if  (value['Order_ID'],value['Grid_ID']) not in self.logged_orders :
                        self.logged_orders.append((value['Order_ID'], value['OrderStatus']))
                        log = True
                    else : log = False
                else : log = True
                if log :
                    with open(self.files_path[key], 'a') as f:
                        f.write('\n' + ','.join([str(value[i]) for i in Data_Structure[key]]))
                        f.close()
            else:
                print(f'Key {key} not found in files_path.')

    def __wrapper__(self, BackTest_Post_Dict):
        """
        Wrapper function to log data.
        """
        self.pos_log = {'Position_ID' :  self.id_position,
            'OrderId' : self.orders[order_type][0]['index'],
            'Grid_ID': self.orders['metadatas']['grid_index'],
            'EventData_Time' : position_args['timestamp'],
            'BackTest_ID' : self.id,
            'EventCode' : 'OPEN SELL',
            'PositionValue' : position_args['entryprice']*position_args['qty']}
        
if __name__ == "__main__":
    logger = Logger()
