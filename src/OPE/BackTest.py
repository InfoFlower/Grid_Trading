import os
import polars as pl
import time
import shutil
from dotenv import load_dotenv
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
    BACKTEST_ID = 0
    def __init__(self, data_path, strategy, money_balance, crypto_balance, log_path, TimeCol='Open Time',CloseCol='Close', time_4_epoch=50000):
        self.id = self.__class__.BACKTEST_ID + 1

        #PATHS
        #TODO : Ajouter une classe Logger qui s'occupe de toutes les logs
        self.log_path = log_path
        self.backtest_log_path = self.log_path+f'{self.id}/'
        self.data_hist=self.backtest_log_path+'data.csv'
        self.positions_hist=self.backtest_log_path+'positions.csv'
        self.orders_hist=self.backtest_log_path+'orders.json'
        self.sio_time=self.backtest_log_path+'sio_time.csv'

        #Vide le repertoire de log des backtest
        #A mieux gérer dans le future, juste pour dev
        for file_name in os.listdir(self.log_path):
            shutil.rmtree(self.log_path+str(file_name))
    
        os.mkdir(self.backtest_log_path)#TODO : utils create_directory

        self.data = pl.read_csv(data_path, truncate_ragged_lines=True)
        self.data[['Open time','Open','High','Low','Close']].write_csv(self.data_hist)

        with open(self.positions_hist, 'w') as f:f.write('id,timestamp,entryprice,qty,is_buy,signe_buy,leverage,take_profit,stop_loss,state,justif,close_price,crypto_balance,money_balance')
        with open(self.sio_time,'w') as f:f.write('epoch,total_of_lines,prct_of_run,time_between_epoch,time_from_start,epoch_size')
        # with open(self.orders_hist, 'w', encoding='utf-8') as f:
        #     f.write('[')

        self.data = self.data[['Open time','Close']]
        self.data = self.data.to_numpy()

        
        # faire une structure? #TODO CARRÉMENT FAIRE DES STRUCTURES
        self.start_time = time.time()
        self.step_time_n_1 = self.start_time
        self.length_of_data = len(self.data)
        self.time_4_epoch = time_4_epoch

        self.TimeCol = TimeCol
        self.CloseCol = CloseCol
        self.strategy = strategy
        
        self.id_position = 0
        self.positions = pl.DataFrame()
        self.orders=self.strategy(self.data[0][self.CloseCol])
        self.pool={'money_balance' : money_balance, 
                   'crypto_balance' : crypto_balance}
        
        
    
    def __iter__(self):
        """
        Initialise l'index de l'itération.
        
        Returns:
            self: L'instance elle-même pour l'itération.
        """
        self.index = 0  # Reset index for iteration
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
        if self.index < len(self.data)-1:
            self.index += 1
            self.current_data = self.data[self.index]
            #TODO : une fonction qui permet d'envoyer les infos du backtest vers reporting (self.current_data, self.orders, self.positions, self.pool)
            self.check_time_conformity()
            self.trigger()
            return self.current_data
        else:
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
        self.log_time()
        a=self.data_n_1[self.TimeCol]
        b=self.current_data[self.TimeCol]
        dif=a-b
        dif=dif.item()
        if abs(dif)>5000 :raise ValueError(f"Time between two data is too long : {dif}")

    def trigger(self):
        """
        Détermine si une position doit être ouverte ou fermée selon la stratégie en cours.
        """
        
        condition_open_buy = self.orders['buy_orders'][0]['open_condition'](self.orders, self.current_data[self.CloseCol], self.data_n_1[self.CloseCol])
        if condition_open_buy == 'BUY' and self.pool['money_balance']>self.orders['buy_orders'][0]['level']*self.orders['buy_orders'][0]['orders_params']['qty']:
            params = self.orders['buy_orders'][0]['orders_params']
            params['timestamp'] = self.current_data[self.TimeCol]
            params['entryprice'] = self.current_data[self.CloseCol]
            params['close_condition'] = self.orders['buy_orders'][0]['close_condition']
            self.open_position(params)
            self.orders=self.strategy.update_grid(self.current_data[self.CloseCol]) #Ajouter kwargs

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

    def open_position(self,position_args):
        
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

#Classe log

    def close_position(self, id, justif):
        """
        Ferme une position identifiée par son ID , met à jour la pool (set_pool) et log la position fermée (log_position).
        
        Parameters:
            id (int): Identifiant de la position à fermer.
            justif (str): Justification de la fermeture.
        """
        print('CLOSE POSITION')
        close_position = self.positions.filter(pl.col("id") == id)
        close_position = close_position.with_columns(state=pl.lit('Closing')) #Ajouter étape de log du prix de closing
        close_position = close_position.with_columns(justif=pl.lit(justif))
        close_position = close_position.with_columns(close_price=pl.lit(self.current_data[self.CloseCol]))
        self.positions = self.positions.filter(pl.col("id") != id)

        self.set_pool(close_position)
        self.log_position(close_position)

    def log_time(self):
        """
        Log les statistiques temporelles pour chaque epoch.
        """
        if self.index%self.time_4_epoch==0:
            current_time=time.time()
            prct_of_run=self.index/self.length_of_data
            epoch=self.index/self.time_4_epoch
            time_between_epoch=current_time-self.step_time_n_1
            time_from_start=current_time-self.start_time
            print(f'\n',f'EPOCH : {epoch}  \n NUMBER OF LINES : {self.index}\n PRCT OF RUN : {prct_of_run} \n TIME BETWEEN EPOCH : {time_between_epoch} \n TIME FROM START : {time_from_start} \n EPOCH SIZE : {self.time_4_epoch}',f'\n'*2,'#'*20)
            with open(self.sio_time,'a') as f : f.write(f'\n{epoch},{self.index},{prct_of_run},{time_between_epoch},{time_from_start},{self.time_4_epoch}')
            self.step_time_n_1=time.time()

    
    def log_position(self, position):
        """
        Enregistre les changements d'état des positions dans un fichier CSV.
        
        Parameters:
            position (polars.DataFrame): Informations sur la position à enregistrer.
        """
        print('LOG POSITION')
        info = list(position.rows()[0])
        for i in [self.pool['crypto_balance'],self.pool['money_balance']]:
            info.append(i)

        with open(self.positions_hist, 'a') as f:
            f.write('\n'+','.join([str(i) for i in info if not callable(i)]))