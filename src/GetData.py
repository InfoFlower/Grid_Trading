######################################################################################################################################
############################################### IMPORT LIBRARIES #####################################################################
######################################################################################################################################

import requests
import time
import logging 
import os
logging.basicConfig(level=logging.INFO)

######################################################################################################################################
############################################### Get DATA api calls #####################################################################
######################################################################################################################################


class GetData:
    def __init__(self,cols,dirname,partiton=20000,nb_core=4,suffixe='index',path_sep='/'):
        self.cols=cols
        self.partion_maker=Make_Op_data(partiton,nb_core,suffixe,path_sep)
        self.dirname=dirname

    def transfo_rep(self,rep):
        full_data=[]
        for i in rep :
            data={}
            for m,v in zip(self.cols,i):
                data[m]=v
            full_data.append(data)
        return full_data

    def get_first_available_date(self,symbol):
        base_url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": "1d",
            'startTime': 0,
            "limit": 1
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0][0]  # Return the timestamp of the first available data
        return None

    def get_market_cap_data(self,symbol,start_timestamp=None):
        if start_timestamp is None:start_timestamp=self.get_first_available_date(symbol)
        if start_timestamp is None : logging.error(f"None timestamp for {symbol}, check the symbol")
        base_url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": "1s",
            "startTime": start_timestamp,
            "limit": 1000
        }
        with open(f'data/data_raw_{symbol}.csv', 'w') as f: f.write(','.join(self.cols) + '\n')
        current_timestamp = start_timestamp
        while current_timestamp < int(time.time() * 1000):
            params["startTime"] = current_timestamp
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                logging.info(f"Getting data for {symbol} from {current_timestamp}")
                data = response.json()
                with open(f'data/data_raw_{symbol}.csv','a') as f:
                    f.write('\n'.join([','.join([str(i) for i in x]) for x in data]))
                if data: current_timestamp = data[-1][0] + 1
                else : break
            else:
                break
        
    
    def __call__(self,symbol):
        logging.info(f"Getting data for {symbol}")
        self.get_market_cap_data(symbol)
        self.partion_maker(f'data/{self.dirname}/data_raw_{symbol}.csv')


######################################################################################################################################
############################################### MAKE PARTITION OF DATA #####################################################################
######################################################################################################################################



class Make_Op_data:
    def __init__(self,partition,nb_core,suffix,path_sep):
        self.partition=partition
        self.read_init='data/'
        self.write_init='data/OPE_DATA/'
        self.suffix=suffix
        self.path_sep=path_sep
        self.nb_core=nb_core


    def make_partition(self):
        """
        This function will create a file with the index of partition of the data
        """
        read_path=self.read_path
        write_path=self.write_path
        writer=open(write_path,'w') #Open the file to write/erase
        writer.write('NUM_core;ID_partition;First_ind;Last_ind;First_byte;Last_byte\n')
        with open(read_path,'r') as f:
            i=[0,0,0,0,0,0]
            lines = f.readlines()
            i[4]=f.tell()
            for _ in lines:
                i[3]+=1
                if i[3]%self.partition == 0:
                    i[5]=f.tell()
                    writer.write(f'{i[0]};{i[1]};{i[2]};{i[3]-1};{i[4]};{i[5]}\n')
                    i[1]+=1
                    i[4]=i[5]
                    i[2]=i[3]
                    i[0]+=1
                    i[0]=i[0]%self.nb_core
            writer.write(f'{i[0]};{i[1]};{i[2]};{i[3]};{i[4]};{i[5]}')
        writer.close()

    def make_file(self,path):
        Opath=path[:path.rfind(self.path_sep)]
        Opath=Opath[path.find(self.path_sep)+1:]
        File_name=path[path.rfind(self.path_sep)+1:path.rfind('.')]
        print(Opath)
        self.write_path=f'data/OPE_DATA/{Opath}/{File_name}_{self.suffix}.csv'
        if Opath not in os.listdir('data/OPE_DATA'): 
            os.makedirs('data/OPE_DATA/'+Opath)
        self.read_path=path
    
    def __call__(self,path):
        self.make_file(path)
        self.make_partition()


######################################################################################################################################
############################################### USE EXEMPLE #####################################################################
######################################################################################################################################


if __name__ == '__main__':
    cols=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
    symbol=['BTCUSDT','ADAUSDT','DOGEUSDT','DOTUSDT','ETHUSDT','SOLUSDT','XRPUSDT']
    appel=GetData(cols)
    for i in symbol:
        appel(i)