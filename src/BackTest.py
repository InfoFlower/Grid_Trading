import polars as pl
import time

class baktest:
    def __init__(self, data, strategy, money_balance, crypto_balance,TimeCol='Open Time',CloseCol='Close', log_path='data/trade_history/',time_4_epoch=50000):
        """
        """# faire une structure?
        self.start_time = time.time()
        self.step_time_n_1=self.start_time
        self.length_of_data=len(data)
        self.TimeCol=TimeCol
        self.CloseCol=CloseCol
        self.strategy = strategy 
        self.data = data
        self.id_position = 0
        self.positions = pl.DataFrame()
        self.pool_hist=log_path+'pool_hist.csv'
        self.position_hist=log_path+'position_hist.csv'
        self.time_4_epoch=time_4_epoch
        
        self.orders=self.strategy(self.data[0][self.CloseCol], 0.01, 1)
        self.pool={'money_balance' : money_balance, 
                   'crypto_balance' : crypto_balance}
        
        self.log_path=log_path+'sio_time.csv'
        with open(self.position_hist, 'w') as f:f.write('id,timestamp,entryprice,qty,is_buy,signe_buy,leverage,take_profit,stop_loss,state,justif,close_price,crypto_balance,money_balance')
        with open(self.log_path,'w') as f:f.write('epoch,total_of_lines,prct_of_run,time_between_epoch,time_from_start,epoch_size')
    
    def __iter__(self):
        self.index = 0  # Reset index for iteration
        return self

    def __next__(self):
        self.data_n_1 = self.data[self.index]
        if self.index < len(self.data)-1:
            self.index += 1
            self.current_data = self.data[self.index]
            self.check_time_conformity()
            self.trigger()
            return self.current_data
        else:
            raise StopIteration
        
    def check_time_conformity(self):
        """
        Check if the time is conform to the strategy
        """
        self.log_time()
        a=self.data_n_1[self.TimeCol]
        b=self.current_data[self.TimeCol]
        dif=a-b
        dif=dif.item()
        #if abs(dif)>5000 :raise ValueError(f"Time between two data is too long : {dif}")


    def trigger(self):
        """
        Triger the order
        """
        
        condition_open_buy = self.orders['buy_orders'][0]['open_condition'](self.orders, self.current_data[self.CloseCol], self.data_n_1[self.CloseCol])
        if condition_open_buy == 'BUY' and self.pool['money_balance']>self.orders['buy_orders'][0]['level']*self.orders['buy_orders'][0]['orders_params']['qty']:
            params = self.orders['buy_orders'][0]['orders_params']
            params['timestamp'] = self.current_data[self.TimeCol]
            params['entryprice'] = self.current_data[self.CloseCol]
            params['close_condition'] = self.orders['buy_orders'][0]['close_condition']
            self.open_position(params)
            self.orders=self.strategy.update_grid(self.current_data[self.CloseCol])

        condition_open_sell = self.orders['sell_orders'][0]['open_condition'](self.orders, self.current_data[self.CloseCol], self.data_n_1[self.CloseCol])
        if condition_open_sell == 'SELL' and self.pool['crypto_balance']>self.orders['sell_orders'][0]['orders_params']['qty']:
            params = self.orders['sell_orders'][0]['orders_params']
            params['timestamp'] = self.current_data[self.TimeCol]
            params['entryprice'] = self.current_data[self.CloseCol]
            params['close_condition'] = self.orders['sell_orders'][0]['close_condition']
            self.open_position(params)
            self.orders=self.strategy.update_grid(self.current_data[self.CloseCol])

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
            'close_price' : float
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
        position_args['close_price'] = -1
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
                                                        'close_price',
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
        close_position = close_position.with_columns(close_price=pl.lit(self.current_data[self.CloseCol]))
        self.positions = self.positions.filter(pl.col("id") != id)

        self.set_pool(close_position)
        self.log_position(close_position)
    
    def log_time(self):
        if self.index%self.time_4_epoch==0:
            current_time=time.time()
            prct_of_run=self.index/self.length_of_data
            epoch=self.index/self.time_4_epoch
            time_between_epoch=current_time-self.step_time_n_1
            time_from_start=current_time-self.start_time
            print(f'\n',f'EPOCH : {epoch}  \n NUMBER OF LINES : {self.index}\n PRCT OF RUN : {prct_of_run} \n TIME BETWEEN EPOCH : {time_between_epoch} \n TIME FROM START : {time_from_start} \n EPOCH SIZE : {self.time_4_epoch}',f'\n'*2,'#'*20)
            with open(self.log_path,'a') as f : f.write(f'\n{epoch},{self.index},{prct_of_run},{time_between_epoch},{time_from_start},{self.time_4_epoch}')
            self.step_time_n_1=time.time()


    def __call__(self,data):
        self.data=data