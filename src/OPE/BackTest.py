import os
import polars as pl
import time
import shutil
from dotenv import load_dotenv
import src.OPE.technical_report.log_time_for_iter as know_your_perf
load_dotenv()
WD = os.getenv('WD')

class baktest:
    """
        Classe de backtest qui constitue la couche opérationnelle permettant d'appliquer des stratégies.\n

        Itère sur data et évalue une fonction de trigger à chaque itération pour savoir si:\n
            •un ordre doit être fill -> open_position\n
            •une position doit être fermée -> close_position\n

        Met à jour la pool {money_balance,crypto_balance}.\n

        Log l'évolution des positions au cours du temps.\n

        Arguments:
            - data (np.ndarray) : Historical market data.
            - strategy (object) : Une trading strategy
            - money_balance (float) : Balance initiale en USD
            - crypto_balance (float) : Balance initiale en BTC
            - TimeCol (str) : Nom de la colonne timestamp
            - CloseCol (str) : Nom de la colonne du prix
            - log_path (str) : Chemin relatif du répertoire de log
            - time_4_epoch (int) : Nombre de ligne par epoch

        Attributes:
            - index (int) : Identifiant de la ligne courante
            - TimeCol (str or int) : TimeCol
            - CloseCol (str or int) : CloseCol
            - data (np.ndarray) : data
            - current_data (np.ndarray) : Ligne numéro index
            - data_n_1 (np.ndarray) : Ligne numéro index-1
            - strategy (object) : strategy
            - orders (dict) : Dictionnaire {buy_orders, sell_orders} contenant les listes des ordres
            - id_position (int) : Identifiant de la dernière position, incrémenté à l'ouverture d'une position
            - positions (polars.DataFrame) : Liste l'ensemble des positions actuellement ouvertes
            - pool (dict) : Dictionnaire {crypto_balance, money_balance}, mis à jour à chaque ouverture ou fermeture de position
            - position_hist (str) : Chemin vers le fichier csv de log des positions
            - log_path (str): log_path

            # A determiner
            - start_time
            - time_4_epoch (int)
            - step_time_n_1
            - length_of_data (int)
        
        Methods:
            - __iter__(): Initialise index
            - __next__(): Itère sur data et appelle trigger
            - check_time_conformity(): 
            - trigger(): Evalue si une position doit être ouverte ou fermée
            - set_pool(position): Met à jour la pool après qu'une position soit ouverte ou fermée
            - log_position(position): Log les changements d'état de self.positions dans un fichier csv
            - open_position(position_args): Ajoute une position dans self.positions
            - close_position(id, justif): Supprimer une position de self.positions
            - log_time(): Log des stats temporelles par epoch
            - __call__(data): Met à jour la data lors d'un changement de fichier
        """
    def __init__(self, data_path, strategy, money_balance, crypto_balance, logger, backtest_id, self_log_path='src/OPE/reporting/BACKTESTS', TimeCol='Open Time',CloseCol='Close',LowCol = 'Low', HighCol='High', time_4_epoch=50000, start_index=0, end_index=-1):
        self.id = backtest_id
        self.start_index = start_index
        self.end_index = end_index
        self.symbol = get_symbol_from_path(data_path)

        #PATHS FOR INTERNAL LOGS
        self.logger=logger
        self.id = backtest_id
        self.log_path = self_log_path
        self.backtest_log_path = f'{self.log_path}/{self.id}/'
        print(f'Creating folder: {self.backtest_log_path}')
        self.data_hist=self.backtest_log_path+'data.csv'
        self.position_event=self.backtest_log_path+'position_event.csv'
        self.orders_hist=self.backtest_log_path+'orders.json'
        self.sio_time=self.backtest_log_path+'sio_time.csv'
        #Vide le repertoire de log des backtest
        #A mieux gérer dans le future, juste pour dev
        for file_name in os.listdir(self.log_path):
            shutil.rmtree(self.log_path+f'/{str(file_name)}')
    
        os.mkdir(self.backtest_log_path)

        self.data = pl.read_csv(data_path, truncate_ragged_lines=True)
        with open(self.position_event, 'w') as f:f.write('id,timestamp,entryprice,qty,is_buy,signe_buy,leverage,take_profit,stop_loss,state,justif,close_price,crypto_balance,money_balance')


        #TODO : Changer la structure de data -> ['Open time','Open','High','Low','Close']
        self.data = self.data[['Open time','Open','High','Low','Close']]
        self.data = self.data.to_numpy()

        
        # faire une structure? #TODO CARRÉMENT FAIRE DES STRUCTURES
        self.start_time = time.time()
        self.step_time_n_1 = self.start_time
        self.length_of_data = len(self.data)
        self.time_4_epoch = time_4_epoch

        self.TimeCol = TimeCol
        self.CloseCol = CloseCol
        self.LowCol = LowCol
        self.HighCol = HighCol
        self.struct={'TimeCol' : self.TimeCol,
                     'CloseCol' : self.CloseCol,
                     'LowCol' : self.LowCol, 
                     'HighCol' : self.HighCol}
        self.strategy = strategy
        
        self.id_position = 0
        self.orders = None
        self.positions = pl.DataFrame()
        self.pool={'money_balance' : money_balance, 
                   'crypto_balance' : crypto_balance}
        self.strategy.metadata['BackTest_ID'] = self.id
        self.logger({'Strategy' : self.strategy.metadata})
        
    
    def __iter__(self):
        """
        Initialise l'index de l'itération.
        
        Returns:
            self: L'instance elle-même pour l'itération.
        """
        self.checkeur = know_your_perf.know_your_perf(sniffing_name='HiHi',is_working=True)
        self.index = self.start_index
        self.orders_n_1 = self.orders
        self.orders=self.strategy(self.data[self.index][self.CloseCol])
        self.Log_data = {'BackTest_ID' : self.id,
                         'index' : self.start_index,
                         'StartData_Time' : self.data[self.start_index][self.TimeCol],
                         'EndData_Time' : self.data[self.end_index][self.TimeCol],
                         'Symbol' : self.symbol,
                         'InitialCapital' : f'({self.pool["money_balance"]},{self.pool["crypto_balance"]})'}
        return self

    def __next__(self):
        """
        Passe à la ligne suivante des données et déclenche la vérification des conditions de trading.
        
        Returns:
            np.ndarray: La ligne actuelle des données de marché.
        
        Raises:
            StopIteration: Si toutes les lignes ont été parcourues.
        """
        self.data_n_1 = self.data[self.index]
        if self.index < len(self.data)-1 or self.index == self.end_index:
            self.index += 1
            self.current_data = self.data[self.index]
            self.check_time_conformity()
            self.trigger()
            return self.current_data
        else:
            self.Log_data['FinalCapital'] = f'{self.pool["money_balance"]},{self.pool["crypto_balance"]}'
            send_log={'BackTest':self.Log_data}
            self.logger(send_log)
            raise StopIteration
    
    def __call__(self,data):
        """
        Met à jour les données de marché lors d'un changement de fichier.
        
        Parameters:
            data (np.ndarray): Nouvelles données de marché.
        """
        self.data=data


#Class trigger ==> EVOL prio 2
    def check_time_conformity(self):
        """
        Vérifie que les timestamps des données sont conformes et détecte les écarts anormaux.
        
        Raises:
            ValueError: Si l'écart temporel entre deux lignes est trop important.
        """
        a=self.data_n_1[self.TimeCol]
        b=self.current_data[self.TimeCol]
        dif=a-b
        dif=dif.item()
        if abs(dif)>500000000 :raise ValueError(f"Time between two data is too long : {dif}")

    def trigger(self):
        """
        Trigger des actions à réaliser à chaque itération sur les données de marché.
        """
        if self.orders != self.orders_n_1:
            self.log_orders()
        self.checkeur()
        self.open_conditions_check(0, orders_types=['buy_orders','sell_orders'])

        Ids_to_close = [position['close_condition'](position,self.current_data, self.struct, self.data_n_1[self.CloseCol]) for position in self.positions.to_dicts()]
        if len(Ids_to_close)>0 and all(Ids_to_close) is not None: 
            [self.close_position(*i) for i in Ids_to_close if i[0] is not False] 
        

    def set_pool(self, position):
        """
        Met à jour les balances après l'ouverture ou la fermeture d'une position.
        
        Parameters:
            position (polars.DataFrame): Informations sur la position ouverte ou fermée.
        """

        if position['state'].item() == 'Opening':
            signe_open = 1
            self.pool['crypto_balance']+=position['qty'].item() * position['signe_buy'].item() * signe_open
            self.pool['money_balance']-=position['qty'].item()*position['entryprice'].item() * position['signe_buy'].item() * signe_open
        elif position['state'].item() == 'Closing' :
            signe_open = -1
            self.pool['crypto_balance']+=position['qty'].item() * position['signe_buy'].item() * signe_open
            self.pool['money_balance']-=position['qty'].item()* self.current_data[self.CloseCol] * position['signe_buy'].item() * signe_open

###
#Open positions
#
    def open_conditions_check(self,i=0 ,orders_types = ['buy_orders','sell_orders']):
        for order_type in orders_types:
            condition_open = self.orders[order_type][0]['open_condition'](self.orders,order_type, self.current_data, self.struct,self.data_n_1[self.CloseCol])
            if (condition_open == 'BUY'  and self.pool['money_balance']>self.orders[order_type][0]['level']*self.orders[order_type][0]['orders_params']['qty']) \
                or (condition_open == 'SELL' and self.pool['crypto_balance']>self.orders[order_type][0]['orders_params']['qty'])\
                and i<10:
                self.open_position(order_type, Order_pos = 0)
                # self.open_conditions_check(i+1)

    def open_position(self,order_type, Order_pos = 0):
        
        """
        Ouvre une nouvelle position de trading et l'ajoute à la liste des positions ouvertes.
        Met à jour la pool (set_pool) et log la position ouverte (log_position)
        
        Parameters:
            position_args (dict): Paramètres de la position (prix d'entrée, quantité, type d'ordre, etc.).
                {'timestamp':timestamp,
                'entryprice':float,
                'qty':float,
                'is_buy':bool,
                'leverage':float,
                'take_profit':float,
                'stop_loss':float,
                'close_condition' : function}
        
        Returns:
            int: Identifiant de la position ouverte.

        """
        position_args = self.orders[order_type][Order_pos]['orders_params']
        position_args['timestamp'] = int(self.current_data[self.TimeCol])
        position_args['entryprice'] = self.current_data[self.CloseCol]
        position_args['close_condition'] = self.orders[order_type][Order_pos]['close_condition']
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
        self.log_position(position_args, order_type)
        self.old_log_position(current_position)
        #SET ORDERS
        self.orders=self.strategy.update_grid(self.current_data[self.CloseCol])
        return self.id_position

###
#Close positions
#

    def close_position(self, id, justif):
        """
        Ferme une position identifiée par son ID , met à jour la pool (set_pool) et log la position fermée (log_position).
        
        Parameters:
            id (int): Identifiant de la position à fermer.
            justif (str): Justification de la fermeture.
        """
        close_position = self.positions.filter(pl.col("id") == id)
        log_infos={'Position_ID' : id+1,
                   'BackTest_ID' : self.id,
                   'OrderId' : 'null',
                   'Grid_ID' : 'null',
                   'EventData_Time' : self.data[self.index][self.TimeCol],
                   'EventCode' : justif,
                   'PositionClosePrice' : self.current_data[self.CloseCol],
                   'CryptoBalance' : self.pool['crypto_balance'],
                   'MoneyBalance' : self.pool['money_balance'],
                   'PositionQty' : close_position['qty'].item(),}
        
        self.logger({'Position':log_infos})
        close_position = close_position.with_columns(state=pl.lit('Closing')) #Ajouter étape de log du prix de closing
        close_position = close_position.with_columns(justif=pl.lit(justif))
        close_position = close_position.with_columns(close_price=pl.lit(self.current_data[self.CloseCol]))
        close_position = close_position.with_columns(pl.lit(int(self.current_data[self.TimeCol])).alias("timestamp"))
        self.positions = self.positions.filter(pl.col("id") != id)
        self.set_pool(close_position)
        self.old_log_position(close_position)

###
#Fonctions de log
#
    def log_position(self, position_args, order_type=None):
        OrderId = 'null'
        if order_type is not None : 
            if order_type == 'buy_orders': justif = 'OPEN BUY'
            elif order_type == 'sell_orders': justif = 'OPEN SELL'
            OrderId = self.orders[order_type][0]['index']
            Time = position_args['timestamp']
            Quantity = position_args['qty']
            EntryPrice = position_args['entryprice']
        else : 
            justif = position_args['justif'].item()
            Time = position_args['timestamp'].item()
            Quantity = position_args['qty'].item()
            EntryPrice = position_args['entryprice'].item()


        self.pos_log = {'Position_ID' :  self.id_position, 
                        'OrderId' : OrderId,
                        'Grid_ID': self.orders['metadatas']['grid_index'],
                        'EventData_Time' : Time,
                        'BackTest_ID' : self.id,
                        'EventCode' : justif,
                        'PositionQty' : Quantity,
                        'PositionClosePrice' : EntryPrice,
                        'CryptoBalance' : self.pool['crypto_balance'],
                        'MoneyBalance' : self.pool['money_balance']}
        

        self.logger({'Position':self.pos_log})


    def log_orders(self):
        Grid_Id = self.orders['metadatas']['grid_index']
        for all_orders in self.orders['buy_orders']+self.orders['sell_orders']:
            if all_orders['orders_params']['is_buy'] is True:  OrderType = 'BUY'
            else: OrderType = 'SELL'
            # A wrapper
            OrdersInfos = {'Order_ID' : all_orders['index'],
            'Grid_ID'   : Grid_Id,
            'OrderTime' : self.current_data[self.TimeCol],
            'OrderType' : OrderType,
            'OrderPrice' : all_orders['level'],
            'OrderQuantity' : all_orders['orders_params']['qty'],
            'OrderLeverage' : all_orders['orders_params']['leverage'],
            'OrderTakeProfit' : all_orders['orders_params']['take_profit'],
            'OrderStopLoss' : all_orders['orders_params']['stop_loss'],
            'OrderStatus' : all_orders['orders_params']['state'],
            'OrderJustif' : all_orders['orders_params']['justif']}
            self.logger({'Order':OrdersInfos})
        self.orders_n_1 = self.orders.copy() 

    def old_log_position(self, position):
        """
        Enregistre les changements d'état des positions dans un fichier CSV.
        
        Parameters:
            position (polars.DataFrame): Informations sur la position à enregistrer.
        """
        info = list(position.rows()[0])
        print(info)
        for i in [self.pool['crypto_balance'],self.pool['money_balance']]:
            info.append(i)

        with open(self.position_event, 'a') as f:
            f.write('\n'+','.join([str(i) for i in info if not callable(i)]))
        



def get_symbol_from_path(path):
    """
    Extrait le symbole du nom de fichier.
    
    Parameters:
        path (str): Chemin du fichier.
        
    Returns:
        str: Symbole extrait du nom de fichier.
    """
    file_name = os.path.basename(path)
    symbol = file_name.split('_')[2].split('.')[0]
    return symbol



######
##
######
#     print(f"Order type : {order_type}",
#           f'\n Condition open : {condition_open}', 
#           f"\n Money balance : {self.pool['money_balance']}",
#           f"\n Crypto Balance : {self.pool['crypto_balance']}",
#           f"\n Buy amount : {self.orders[order_type][0]['level']*self.orders[order_type][0]['orders_params']['qty']}",
#           f"\n Quantity : {self.orders[order_type][0]['orders_params']['qty']}",
#           f"\n Buy Result : {condition_open == 'BUY' and self.pool['money_balance']>self.orders[order_type][0]['level']*self.orders[order_type][0]['orders_params']['qty']}",
#           f"\n Sell Result : {(condition_open == 'SELL' and self.pool['crypto_balance']>self.orders[order_type][0]['orders_params']['qty'])}")