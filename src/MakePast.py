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
        self.id_position = 0

        self.pool={'money_balance' : money_balance, 
                   'crypto_balance' : crypto_balance}
        
        with open(self.pool_hist, 'w') as f:
            #Time,Open,High,Low,Close,Volume,Vol,Justification,crypto_balance,money_balance
            f.write('Time,Price,Qty,Justification,crypto_balance,money_balance\n')
        with open(self.position_hist, 'w') as f:
            f.write('id,timestamp,entryprice,qty,is_buy,signe_buy,leverage,take_profit,stop_loss,justif,state,money_balance,crypto_balance\n')#A faire
    
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
        
    def set_pool(self, position):
        """
        Update the pool state

        Pool Stucture

            {'money_balance' : money_balance, 
           'crypto_balance' : crypto_balance}
        """

        if position['state'].item() == 'Opening':
            signe_open = 1
        elif position['state'].item() == 'Closing' :
            signe_open = -1

        #SET POOL
        self.pool['crypto_balance']+=position['qty'].item()*position['entryprice'].item() * position['signe_buy'].item() * signe_open
        self.pool['money_balance']-=position['qty'].item()*position['entryprice'].item() * position['signe_buy'].item() * signe_open

        
    
    def log_position(self, position):
        """
        log the position
        """
        info = list(position.rows()[0])
        for i in [self.pool['crypto_balance'],self.pool['money_balance']]:
            info.append(i)

        with open(self.position_hist, 'a') as f:
            f.write(','.join([str(i) for i in info])+'\n')

    def open_position(self,position_args):
        """
        Position Structure

        In
        {
            'timestamp':timestamp,
            'entryprice':float,
            'qty':float,
            'is_buy':bool,
            'leverage':float,
            'take_profit':float,
            'stop_loss':float,
            'justif' : string
        }

        Out
        {
            'id' : string,
            'timestamp' : timestamp,
            'entryprice' : float,
            'qty' : float,
            'is_buy' : bool,
            'signe_buy': int,
            'leverage' : float,
            'take_profit':float,
            'stop_loss':float,
            'justif' : string,
            'state' : string
        }
        
        """
        if position_args['is_buy'] is False : 
            position_args['signe_buy']=-1
        else:
            position_args['signe_buy']=1

        #SET POSITION

        position_args['id'] = self.id_position
        position_args['state'] = 'Opening'
        self.id_position += 1
        current_position = pl.DataFrame(position_args).select(['id',
                                                       'timestamp', 
                                                        'entryprice',
                                                        'qty',
                                                        'is_buy',
                                                        'signe_buy',
                                                        'leverage',
                                                        'take_profit',
                                                        'stop_loss',
                                                        'justif',
                                                        'state'])
        
        self.positions = pl.concat([self.positions, current_position])

        self.set_pool(current_position)
        self.log_position(current_position)

    def close_position(self, id):
        """
        Close a position by its id
        """
        close_position = self.positions.filter(pl.col("id") == id)
        print(close_position)
        close_position = close_position.with_columns(state=pl.lit('Closing')) #Ajouter étape de log du prix de closing
        print(close_position)
        self.positions = self.positions.filter(pl.col("id") != id)

        self.set_pool(close_position)
        self.log_position(close_position)
    
    def __call__(self, position_args,Open=True):
        if Open: self.open_position(position_args)
        else: self.close_position(0)


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
            position_args = {'timestamp':i[TimeCol],
                'entryprice':i[CloseCol],
                'qty':100,
                'is_buy':True,
                'leverage':1,
                'take_profit':0,
                'stop_loss':0,
                'justif' : 'justif'}
            bktst(position_args)
        n+=1

    print(bktst.positions)

    bktst(48)

    print(bktst.positions)