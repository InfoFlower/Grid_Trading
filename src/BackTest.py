class baktest:
    def __init__(self, data, strategy, money_balance, crypto_balance,TimeCol='Open Time',CloseCol='Close', log_path='data/trade_history/'):
        """
        """# faire une structure?
        self.TimeCol=TimeCol
        self.CloseCol=CloseCol
        self.strategy = strategy 
        self.data = data
        self.pool_hist=log_path+'pool_hist.csv'
        self.position_hist=log_path+'position_hist.csv'
        self.pool={'money_balance' : money_balance, 
                   'crypto_balance' : crypto_balance}
        
        with open(self.position_hist, 'w') as f:
            f.write('id,timestamp,entryprice,qty,is_buy,signe_buy,leverage,take_profit,stop_loss,state,justif,crypto_balance,money_balance')#A faire
    
    def __iter__(self):
        self.id_position = 0
        self.positions = pl.DataFrame()
        self.index = 0  # Reset index for iteration
        self.current_data = self.data[self.index]
        self.orders=self.strategy(self.current_data[self.CloseCol], 0.01, 10)
        return self

    def __next__(self):
        self.data_n_1 = self.current_data
        if self.index < len(self.data)-1:
            self.index += 1
            self.current_data = self.data[self.index]
            self.trigger()
            return self.current_data
        else:
            raise StopIteration
        
    def trigger(self):
        """
        Triger the order
        """
        condition_open_buy = self.orders['buy_orders'][0]['open_condition'](self.orders, self.current_data[self.CloseCol], self.data_n_1[self.CloseCol])
        if condition_open_buy == 'BUY' and self.pool['money_balance']>self.orders['buy_orders'][0]['level']*self.orders['buy_orders'][0]['orders_params']['qty']:
            print('buy')
            params = self.orders['buy_orders'][0]['orders_params']
            params['timestamp'] = self.current_data[self.TimeCol]
            params['entryprice'] = self.current_data[self.CloseCol]
            params['close_condition'] = self.orders['buy_orders'][0]['close_condition']
            self.open_position(params)
            self.orders=self.strategy.grid_maker.update_grid(current_grid = self.orders,wich_orders = 'sell_orders')

        condition_open_sell = self.orders['sell_orders'][0]['open_condition'](self.orders, self.current_data[self.CloseCol], self.data_n_1[self.CloseCol])
        if condition_open_sell == 'SELL' and self.pool['crypto_balance']>self.orders['sell_orders'][0]['orders_params']['qty']:
            print('sell')
            params = self.orders['sell_orders'][0]['orders_params']
            params['timestamp'] = self.current_data[self.TimeCol]
            params['entryprice'] = self.current_data[self.CloseCol]
            params['close_condition'] = self.orders['sell_orders'][0]['close_condition']
            self.open_position(params)
            self.orders=self.strategy.grid_maker.update_grid(current_grid = self.orders,wich_orders = 'buy_orders')

        Ids_to_close = [position['close_condition'](position,self.current_data[self.CloseCol], self.data_n_1[self.CloseCol]) for position in self.positions.to_dicts()]
        if len(Ids_to_close)>0 and all(Ids_to_close) is not None: 
            [self.close_position(*i) for i in Ids_to_close if i[0] is not False]

    def set_pool(self, position):
        """
        Update the pool state

        Pool Stucture

            {'money_balance' : money_balance, 
           'crypto_balance' : crypto_balance}
        """

        if position['state'].item() == 'Opening':
            signe_open = 1
            #SET POOL
            self.pool['crypto_balance']+=position['qty'].item() * position['signe_buy'].item() * signe_open
            self.pool['money_balance']-=position['qty'].item()*position['entryprice'].item() * position['signe_buy'].item() * signe_open
        elif position['state'].item() == 'Closing' :
            signe_open = -1
            self.pool['crypto_balance']+=position['qty'].item() * position['signe_buy'].item() * signe_open
            self.pool['money_balance']-=position['qty'].item()* self.current_data[self.CloseCol] * position['signe_buy'].item() * signe_open

        

        
    
    def log_position(self, position):
        """
        log the position
        """
        info = list(position.rows()[0])
        for i in [self.pool['crypto_balance'],self.pool['money_balance']]:
            info.append(i)

        with open(self.position_hist, 'a') as f:
            f.write('\n'+','.join([str(i) for i in info if not callable(i)]))

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
            'close_condition' : function
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
            'state' : string
            'justif' : string,
            
        }
        
        """
        if position_args['is_buy'] is False : 
            position_args['signe_buy']=-1
        else:
            position_args['signe_buy']=1

        #SET POSITION

        position_args['id'] = self.id_position
        position_args['state'] = 'Opening'
        position_args['justif'] = 'Opening'
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
                                                        'state',
                                                        'justif',
                                                        'close_condition'])
        
        self.positions = pl.concat([self.positions, current_position])

        self.set_pool(current_position)
        self.log_position(current_position)
        return self.id_position

    def close_position(self, id, justif):
        """
        Close a position by its id
        """
        close_position = self.positions.filter(pl.col("id") == id)
        close_position = close_position.with_columns(state=pl.lit('Closing')) #Ajouter étape de log du prix de closing
        close_position = close_position.with_columns(justif=pl.lit(justif))
        self.positions = self.positions.filter(pl.col("id") != id)

        self.set_pool(close_position)
        self.log_position(close_position)
    

if __name__ == '__main__':
    import polars as pl
    import MakeGrid as MakeGrid
    from strategies.strategy_example import Strategy
    data=pl.read_csv('data\OPE_DATA\DATA_RAW_S_ORIGIN_test_code\data_raw_BTCUSDT_176.csv', truncate_ragged_lines=True)
    data=data[['Open time','Close']].to_numpy()
    TimeCol=0
    CloseCol=1
    money_balance=1000000 #USD
    crypto_balance=money_balance/data[0][CloseCol] #BTC
    print(crypto_balance)
    strategy = Strategy('basic_grid', MakeGrid.Grid_Maker('basic_grid', 'grid_test'))
    bktst=baktest(data, strategy, money_balance,crypto_balance,TimeCol,CloseCol)
    for i in bktst:
        pass

