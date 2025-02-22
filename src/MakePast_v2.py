class baktest:
    def __init__(self, data, Struct, money_balance, crypto_balance,TimeCol='Open Time',CloseCol='Close', log_path='data/trade_history/'):
        self.TimeCol=TimeCol
        self.CloseCol=CloseCol
        self.Struct = Struct
        self.data = data
        self.index=0
        self.pool_hist=log_path+'pool_hist.csv'
        self.position_hist=log_path+'position_hist.csv'
        self.pool={'money_balance' : money_balance, 
                   'crypto_balance' : crypto_balance}
        with open(self.pool_hist, 'w') as f:
            f.write('Time,Open,High,Low,Close,Volume,Vol,Justification,crypto_balance,money_balance\n')
        with open(self.position_hist, 'w') as f:
            f.write('')#A faire
    
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

    def make_position(self,vol,justif, top_buy=True,price_col=1):
        info=list(self.current_data)
        signe_buy=1
        if top_buy is False : signe_buy=-1
        self.crypto_balance+=vol*info[price_col] * signe_buy
        self.money_balance-=vol*info[price_col] * signe_buy
        for i in [vol,justif,self.crypto_balance,self.money_balance]:
            info.append(i)
        
        with open(self.position_hist, 'a') as f:
            f.write()#AFAIRE quand structure
        
        with open(self.pool_hist, 'a') as f:
            f.write(','.join([str(i) for i in info])+'\n')
    




if __name__ == '__main__':
    import polars as pl
    data=pl.read_csv('data/data_raw_DOTUSDT.csv')
    data=data[['Open time','Close']].to_numpy()
    TimeCol=0
    CloseCol=1
    money_balance=1000
    crypto_balance=1000
    bktst=baktest(data, 0, money_balance, crypto_balance,TimeCol,CloseCol)
    for i in bktst:
        print(i)