######################################################################################################################################
########################                           MAKE GRID FOR GRID TRADING                        #################################
######################################################################################################################################

######################################################################################################################################
#                            
#                                            STRUCTURE OF THE BASIC_GRID GRID
#                       
#                                            grid_origin: float, the price of the first order
#                                            prct_of_intervall : float, the percentage of the price between orders
#                                            nb_orders : int, the number of orders to make
#
######################################################################################################################################
import json

class Grid_Maker:
    """
    Classe permettant de créer la grille de grid trading.\n

    Arguments:
        - grid_type : Le type de grille
        - grid_name : Le nom de la grille
        - write_path : Le chemin relatif vers lequel on log les grilles

    Attributes:
        - grid_type : grid_type
        - index : Identifiant de la grille, initialisé à 0
        - write_path :  write_path+grid_name+'.json'
    
    Methods:
        - __call__() : Crée une nouvelle grille de type self.grid_type
        - update_grid(args) : inutile
        - make_order(i,args,params) : Construit un ordre de type buy or sell (params[is_buy])
        - Make_Basic_Grid(args) : Construit une grille de type 'BasicGrid'
        - log_grid(grid) : Enregistre la création d'une grille et append dans un .json
    """
    def __init__(self, grid_type, grid_name, write_path='data/trade_history/grid/'):
        self.order_index=0
        self.grid_type = grid_type
        self.index=0
        #Changer le nom du self.write_path pour self.grid_path ou qqchose de ce genre
        self.write_path = write_path+grid_name+'.json'
        with open(self.write_path, 'w', encoding='utf-8') as f:
            f.write('[')

    def __call__(self, args):
        """
        Incrémente l'identifiant de la grille et\n
        Crée une nouvelle grille associée au grid_type.\n

        Arguments:
            - args (dict) : arguments de la grille et des ordres qu'elle contient

        Returns:
            - Make_Basic_Grid(args) (dict)
        """
        self.index+=1
        if self.grid_type == 'BasicGrid':
            return self.Make_Basic_Grid(args)
        elif self.grid_type == 'HedgingGrid':
            return self.Make_Hedging_Grid(args)
        else:
            raise ValueError(f"Unknown grid type: {self.grid_type}")

    def update_grid(self,args):
        """
        ici aucune utilité, faire des grilles (donc strat avec besoin pour implémentation).\n
        """
        pass


    def make_order(self,intervall,args,params, need_signed=True):
        """
        Retourne un ordre au niveau i pour un type d'ordre (params : buy or sell) et les args 
        """
        self.order_index+=1
        signe_buy=-1
        if need_signed: 
            if params['is_buy']:signe_buy=1
        return {'index':self.order_index,'level' : args['grid_origin']-signe_buy*args['grid_origin']*(intervall*args['prct_of_intervall']),
                        'orders_params' : params,
                        'open_condition' : args['open_condition'],
                        'close_condition' : args['close_condition'],
                        'justif' : params['justif'],
                        'state' : 'open'}
        
    def Make_Basic_Grid(self,args):
        """
        Crée une grille simple, espacement linéaire des ordres autour de l'origine\n
        Même nb_orders pour les ordres d'achats et les ordres de ventes.\n

        Arguments: 
            - args (dict) : 'BasicGrid' args
                - grid_origin (float) : Origine de la grille ,entre les sell_orders et les buy_orders
                - prct_of_intervall (float):  Pourcentage d'écart entre chaque ordre
                - nb_orders (int) : Nombre d'ordre à créer à l'achat et à la vente
                - orders_params (dict) : Paramètres des ordres
                    - qty (float) : Quantité de BTC à faire rentrer en position
                    - is_buy (bool) : Ordre à l'achat ou à la vente
                    - leverage (float) : Multiple de levier à appliquer
                    - take_profit (float) : Pourcentage de gain
                    - stop_loss (float) : Pourcentage de perte
                    - justif (str) : Justification de la prise de position de l'ordre
                - open_condition (function) : Fonction de condition d'ouverture de l'ordre
                - closing_condition (function) : Fonction de condition de fermeture de l'ordre
        Returns:
            - grid (dict) : 
                - index (int) : identifiant de la grille
                - origin (float) : Origine de la grille ,entre les sell_orders et les buy_orders
                - sell_orders (list) : Liste des ordres de ventes
                - buy_orders (list) : Liste des ordres d'achats
        """
        buy_params = args['orders_params'].copy()
        buy_params['is_buy'] = True
        buy_orders = [self.make_order(i,args,buy_params) for i in range(1, args['nb_orders']+1)]

        sell_params = args['orders_params'].copy()
        sell_params['is_buy'] = False
        sell_orders = [self.make_order(i,args,sell_params) for i in range(1, args['nb_orders']+1)]
        
        grid={'index':self.index,
              'origin':args['grid_origin'].item(),
                'sell_orders': sell_orders,
                'buy_orders' : buy_orders}
        
        self.log_grid(grid)

        return grid

    def Make_Hedging_Grid(self, args):
        """
        """
        buy_params = args['orders_params'].copy()
        buy_params['is_buy'] = True
        buy_orders = [self.make_order(i, args, buy_params) for i in (-1, 1)]

        sell_params = args['orders_params'].copy()
        sell_params['is_buy'] = False
        sell_orders = [self.make_order(i, args, buy_params) for i in (-1, 1)]

        grid={'index':self.index,
              'origin':args['grid_origin'].item(),
                'sell_orders': sell_orders,
                'buy_orders' : buy_orders}
        self.log_grid(grid)
        return grid
                        
    #TODO : Ajouter une classe Logger qui s'occupe de toutes les logs
    def log_grid(self, grid):
        """
        Enregistre l'objet grille précédemment créer dans un fichier .json
        
        Parameters:
            grid (dict): Informations sur la grille
        """
        def clean_order(orders):
            orders_list = []
            for order in orders:
                orders_list.append({k:v for k, v in order.items() if not callable(v)})
            return orders_list
        clean_grid = grid.copy()
        buy_orders = clean_grid['buy_orders'].copy()
        sell_orders = clean_grid['sell_orders'].copy()
        str_function_buy_orders = clean_order(buy_orders)
        str_function_sell_orders = clean_order(sell_orders)
        clean_grid['buy_orders'] = str(str_function_buy_orders)
        clean_grid['sell_orders'] = str(str_function_sell_orders)
        with open(self.write_path, 'a', encoding='utf-8') as f:
            if self.index != 1 :f.write(f'\n,')   
            json.dump(clean_grid, f, ensure_ascii=False, indent=4)

        