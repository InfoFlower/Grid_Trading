from Strategy_template import Strategy

class StrategyHedging(Strategy):

    """"""

    # Conditions for orders
    def close_condition(self, position, current_n, current_n_struct,price_n_1):
        """
        Définit la condition de fermeture d'une position.\n
        Si la condition est rempli retourne l'id de cette position.\n

        Dans ce cas, on teste juste si le prix a passé un palier de TP ou SL

        Arguments:
            - position (dict) : Position à tester
            - price_n (float) : Prix au niveau n de l'itération
            - price_n_1 (float) : Prix au niveau n-1 de l'itération
        
        Returns:
            - (int, str) : Si la position doit être fermée
            - (False, False) : Si la position reste ouverte
        """
        # if position['is_buy']:
        #     #Pas de stoploss :stop_loss_price = position['entryprice']*(1-position['stop_loss'])
        #     take_profit_price = position['entryprice']*(1+position['take_profit'])
        #     if price_n >= take_profit_price and price_n_1 < take_profit_price : 
        #         return (position['id'], 'TAKEPROFIT BUY')
        
        # if position['is_buy'] is False:
        #     take_profit_price = position['entryprice']*(1-position['take_profit'])
        #     if price_n <= take_profit_price and price_n_1 > take_profit_price : 
        #         return (position['id'], 'TAKEPROFIT SELL')


        # price_n_1 = float(price_n_1)
        # price_n=float(current_n[current_n_struct['CloseCol']])
        # High_n = current_n[current_n_struct['HighCol']]
        # Low_n = current_n[current_n_struct['LowCol']]
        # if position['is_buy']:
        #     stop_loss_price = position['entryprice']*(1-position['stop_loss'])
        #     take_profit_price = position['entryprice']*(1+position['take_profit'])
        #     if   (price_n <= stop_loss_price and price_n_1 >stop_loss_price) or  Low_n <= stop_loss_price <= High_n: 
        #         return (position['id'], 'STOPLOSS BUY')
        #     elif price_n >= take_profit_price and price_n_1 < take_profit_price or  Low_n <= take_profit_price <= High_n: 
        #         return (position['id'], 'TAKEPROFIT BUY')
        
        # if position['is_buy']==False:
        #     stop_loss_price = position['entryprice']*(1+position['stop_loss'])
        #     take_profit_price = position['entryprice']*(1-position['take_profit'])
        #     if (price_n >=  stop_loss_price and price_n_1 <stop_loss_price) or  Low_n <= stop_loss_price <= High_n:
        #         return (position['id'], 'STOPLOSS SELL')
        #     elif (price_n <= take_profit_price and price_n_1 > take_profit_price) or  Low_n <= take_profit_price <= High_n:  
        #         return (position['id'], 'TAKEPROFIT BUY')
        # return False, False

        price_n_1 = float(price_n_1)
        price_n = float(current_n[current_n_struct['CloseCol']])
        High_n = current_n[current_n_struct['HighCol']]
        Low_n = current_n[current_n_struct['LowCol']]
        if position['is_buy']:
            take_profit_price = position['entryprice']*(1+position['take_profit'])
            if price_n >= take_profit_price and price_n_1 < take_profit_price or  Low_n <= take_profit_price <= High_n: 
                return (position['id'], 'TAKEPROFIT BUY')
            
        if position['is_buy'] is False:
            take_profit_price = position['entryprice']*(1-position['take_profit'])
            if (price_n <= take_profit_price and price_n_1 > take_profit_price) or  Low_n <= take_profit_price <= High_n:  
                return (position['id'], 'TAKEPROFIT SELL')
            
        return False, False

    def open_condition(self, orders, price_n, price_n_1):
        """
        Définit la condition d'ouverture des ordres les plus proches du prix.\n
        Teste donc 1 ordre d'achat et 1 ordre de vente.\n
        On ne peut pas ouvrir les deux ordres en même temps.\n

        Arguments:
            - orders (dict) : Ordre à tester 
            - price_n (float) : Prix au niveau n de l'itération
            - price_n_1 (float) : Prix au niveau n-1 de l'itération

        Returns:
            - str : Si ordre à ouvrir
            - False : Sinon
        """
        price_n = float(price_n)
        price_n_1 = float(price_n_1)
        if orders['buy_orders'][0]['level']>=price_n and orders['buy_orders'][0]['level']<price_n_1 :return "BUY"
        if orders['sell_orders'][0]['level']<=price_n and orders['sell_orders'][0]['level']>price_n_1 :return "SELL"
        return False