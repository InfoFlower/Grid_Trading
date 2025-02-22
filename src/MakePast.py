class baktest:
    def __init__(self, data, Struct, money_balance, crypto_balance,TimeCol='Open Time',CloseCol='Close', log_path='data/trade_history/'):
        """
        Data Structure

        Open time,
        Open,
        High,
        Low,
        Close,
        Volume,
        Close time,
        Quote asset volume,
        Number of trades,
        Taker buy base asset volume,
        Taker buy quote asset volume,
        Ignore
        
        """
        self.TimeCol=TimeCol
        self.CloseCol=CloseCol
        self.Struct = Struct
        self.data = data
        self.positions = pl.DataFrame()
        self.index=0
        self.pool_hist=log_path+'pool_hist.csv'
        self.position_hist=log_path+'position_hist.csv'
        self.pool={'money_balance' : money_balance, 
                   'crypto_balance' : crypto_balance}
        with open(self.pool_hist, 'w') as f:
            #Time,Open,High,Low,Close,Volume,Vol,Justification,crypto_balance,money_balance
            f.write('Time,Price,Qty,Justification,crypto_balance,money_balance\n')
        with open(self.position_hist, 'w') as f:
            f.write('id,timestamp,entryprice,qty,is_buy,leverage,take_profit,stop_loss\n')#A faire
    
    def __iter__(self):
        self.index = 0  # Reset index for iteration
        return self

    def __next__(self):
        if self.index < len(self.data):
            self.current_data = self.data[self.index]
            self.index += 1
            return self.current_data
        else:
            raise StopIteration
        
    def set_position(self, position_args):
        """
        Add a new position by setting self.current_position

        Position Structure

        In
        {
            'timestamp':timestamp,
            'qty':float,
            'is_buy':bool,
            'leverage':float,
            'take_profit':float,
            'stop_loss':float
        }

        Out
        {
            'id' : varchar (int),
            'timestamp' : timestamp,
            'entryprice' : float,
            'qty' : float,
            'is_buy' : bool,
            'leverage' : float,
            'take_profit':float,
            'stop_loss':float
        }
        """
        #SET POSITION
        position_args['id'] = 0
        self.current_position = pl.DataFrame(position_args).select(['id',
                                                       'timestamp', 
                                                        'entryprice',
                                                        'qty',
                                                        'is_buy',
                                                        'leverage',
                                                        'take_profit',
                                                        'stop_loss'])
        
        self.positions = pl.concat([self.positions, self.current_position])

        with open(self.position_hist, 'a') as f:
            f.write(','.join([str(i) for i in self.current_position.rows()[0]])+'\n')#AFAIRE quand structure
        
    def set_pool(self, justif, signe_buy):
        """
        Update the pool state

        Pool Stucture

            {'money_balance' : money_balance, 
           'crypto_balance' : crypto_balance}
        """
        info=list(self.current_data.copy())

        #SET POOL
        self.pool['crypto_balance']+=self.current_position['qty'].item()*self.current_position['entryprice'].item() * signe_buy
        self.pool['money_balance']-=self.current_position['qty'].item()*self.current_position['entryprice'].item() * signe_buy

        for i in [self.current_position['qty'].item(),justif,self.pool['crypto_balance'],self.pool['money_balance']]:
            info.append(i)
            
        with open(self.pool_hist, 'a') as f:
            f.write(','.join([str(i) for i in info])+'\n')

    def open_position(self,justif,position_args):
        """
        
        """
        signe_buy=1
        if position_args['is_buy'] is False : signe_buy=-1

        self.set_position(position_args)
        self.set_pool(justif, signe_buy)
        

    def close_position(self):
        pass

if __name__ == '__main__':
    import polars as pl
    data=pl.read_csv('data/OPE_DATA/data_raw_BTCUSDT_176.csv', truncate_ragged_lines=True)
    data=data[['Open time','Close']].to_numpy()
    TimeCol=0
    CloseCol=1
    money_balance=1000
    crypto_balance=1000
    bktst=baktest(data, 0, money_balance,crypto_balance,TimeCol,CloseCol)
    n = 0
    for i in bktst:
        
        if n%1000 == 0:
            print('i' ,i)
            position_args = {'timestamp':i[TimeCol],
                'entryprice':i[CloseCol],
                'qty':100,
                'is_buy':True,
                'leverage':1,
                'take_profit':0,
                'stop_loss':0}

            bktst.open_position('justif', position_args)
        n+=1
    print(bktst.positions)