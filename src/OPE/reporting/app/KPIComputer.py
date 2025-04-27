import os
import polars as pl
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px
from dotenv import load_dotenv
from config import REPORTING_LOG_PATH
from KPI_CATEGORIES import CATEGORIES
pl.Config.set_tbl_cols(20)
pl.Config.set_tbl_rows(500)
load_dotenv()
WD = os.getenv('WD')


class KPIComputer:
    """
    
    """


    def __init__(self, REPORTING_LOG_PATH, backtest_id):
        """
        """
        ###### A utiliser avec le Logger ######

        # self.data = pl.read_csv(f'{REPORTING_LOG_PATH}/Data.csv')
        # #TODO self.data : filter between startTime et endTime

        # self.position_event = pl.read_csv(f'{REPORTING_LOG_PATH}/Position.csv')
        # self.position_event = self.position_event.filter(pl.col('BackTest_ID')==backtest_id)

        # self.backtest = pl.read_csv(f'{REPORTING_LOG_PATH}/BackTest.csv')
        # self.backtest = self.backtest.filter(pl.col('BackTest_ID')==backtest_id)

        ###### A utiliser avec les anciens logs ######
        self.old_data = pl.read_csv(f'{WD}data/DATA_RAW_S_ORIGIN/data_raw_BTCUSDT.csv', truncate_ragged_lines=True)
        print(self.old_data.head(5))
        self.old_position_event = pl.read_csv(f'{REPORTING_LOG_PATH}/{backtest_id}/position_event.csv')
        print(self.old_position_event.head(5))
        self.Categories = CATEGORIES
        
        
        
        ###### Transformation du dataframe, calcul equity, dradown etc... ######
        
        self.old_equity()
        print(self.old_position_value.head())
        self.old_drawdown()
        print('drawdown fini')
        self.old_returns()
        print('returns fini')
        self.old_Categories()
        print('categories fini')
        self.old_graphe_equity()
        print('fig equity fini')

    ###### OLD TRANSFORMATION ######
    def old_equity(self):
        """
        """
        # print(self.old_data.head())
        # print(self.old_position_event.head())

        old_left_merged_data_x_posevent = self.old_data.join(self.old_position_event, left_on='Open time', right_on='timestamp', how = 'left')
        old_left_merged_data_x_posevent = old_left_merged_data_x_posevent.with_columns(
            [
                (pl.col('crypto_balance').fill_null(strategy='forward')).alias('crypto_balance'),
                (pl.col('money_balance').fill_null(strategy='forward')).alias('money_balance')
            ]
        )
        
        #old_left_merged_data_x_posevent.with_columns([pl.col("")])
        self.old_position_value = old_left_merged_data_x_posevent.with_columns(
            [
                (pl.col('Close')*pl.col('crypto_balance') + pl.col('money_balance')).alias('Equity')
            ]
        ).select(
            ["Open time", "Open", "High", "Low", "Close", "crypto_balance", "money_balance", "Equity"]
        )
        

    def old_drawdown(self):
        """
        """
        
        position_value = self.old_position_value.clone()
        
        position_value = position_value.with_columns([
            pl.col('Equity').cum_max().alias("high_water_mark")
        ]) 
        
        position_value = position_value.with_columns([
            ((pl.col("Equity")-pl.col("high_water_mark"))/pl.col("high_water_mark")).alias('Drawdown')
        ])
        self.old_position_value = position_value.select(
            ["Open time", "Open", "High", "Low", "Close", "crypto_balance", "money_balance", "Equity", "Drawdown"]
            )
    def old_returns(self):
        """
        """
        position_value = self.old_position_value.clone()
        position_value = position_value.with_columns([
            ((pl.col("Equity") / pl.col("Equity").shift(1)) - 1).alias("Returns")
        ])
        self.old_position_value = position_value

        

    ###### OLD CATEGORIES  ######
    def old_Categories(self):
        """
        """
        self.Categories['RENTABILITE'] = {
                                        "Total Return": self.old_Total_Return(),
                                        "Annualized Return": self.old_Annualized_Return(),
                                        "Win Rate": self.old_Win_Rate()
                                        }
        self.Categories['RISQUE'] = {
                                    "Max Drawdown": self.old_Max_Drawdown(),
                                    "Returns Volatility": self.old_Volatility(),
                                    "Sharpe Ratio": self.old_Sharpe_Ratio()
                                    }
        #old_Max_Drawdown

    ###### OLD KPI  ###### 
    def old_Total_Return(self):
        """
        Pourcentage de gain total (sur tout le backtest)
        -> Float
        """
        print(self.old_position_value.head())
        ic = self.old_position_value['Equity'][0]
        print(ic)
        fc = self.old_position_value['Equity'][-1]
        print(fc)
        total_return = (fc - ic)/ic
        return total_return

    def old_Annualized_Return(self):
        """
        Pourcentage de gain annualisé
        (CAGR)
        """


        tmin = datetime.fromtimestamp(self.old_data.select(pl.col("Open time").min()).item()/1000)
        tmax = datetime.fromtimestamp(self.old_data.select(pl.col("Open time").max()).item()/1000)
        delta = relativedelta(tmax, tmin)

        t = delta.years + delta.months/12 + delta.days/365.25 + delta.hours/8766 + delta.minutes/525960 + delta.seconds/31557600
        
        ic = self.old_position_value['Equity'][0]*2

        fc = self.old_position_value['Equity'][-1]*2

        try:
            return (fc/ic)**(1/t)-1
        except :
            return f"OverflowError : Période trop courte {delta}"


    def old_Win_Rate(self):
        """
        Win Rate (Pourcentage)
        """
        nbWin = self.old_position_event.filter(pl.col('justif').str.contains("TAKEPROFIT")).shape[0]
        nbLoss = self.old_position_event.filter(pl.col('justif').str.contains("STOPLOSS")).shape[0]
        return nbWin/(nbWin+nbLoss)*100
    
    def old_Max_Drawdown(self):
        """
        Min(Drawdown)
        
        """
        return self.old_position_value['Drawdown'].min()
    
    def old_Volatility(self):
        """
        Ecart type des rendements
        #Donnée par secondes
        """
        return self.old_position_value['Returns'].std()
    
    def old_Expected_Return(self):
        """
        """
        return self.old_position_value['Returns'].mean()
    
    def old_Sharpe_Ratio(self):
        """
        """
        return self.old_Expected_Return()/self.old_Volatility()
    
    ###### OLD GRAPHE ######
    def old_graphe_equity(self):
        fig = px.line(self.old_position_value, x='Open time', y='Equity')
        print(fig)
        self.fig_equity = fig
        


    











    ###### FONCTION RENTABILITE ######

    def Total_Return(self):
        """
        Pourcentage de gain total (sur tout le backtest)
        -> Float
        """
        ic = self.backtest['InitialCapital'].item()
        fc = self.backtest['FinalCapital'].item()
        return (fc - ic)/ic
    
    def Annualized_Return(self):
        """
        Pourcentage de gain annualisé
        (CAGR)
        """
        t = 1 #TODO t durée en année -> 6mois = 0.5
        ic = self.backtest['InitialCapital'].item()
        fc = self.backtest['FinalCapital'].item()
        annualized_return = (fc/ic)**(1/t)-1

    def Monthly_Return(self):
        pass

    def Win_Rate(self):
        """
        Win Rate
        """
        nbWin = self.position_event.filter(pl.col('CloseReason').str.contains("TAKEPROFIT")).shape[0]
        nbLoss = self.position_event.filter(pl.col('CloseReason').str.contains("STOPLOSS")).shape[0]
        wr = nbWin/(nbWin+nbLoss)*100

    ###### FONCTION RISQUE ######
    def Max_Drawdown(self):
        """
        """





# def main():

#     kpiComputer = KPIComputer(REPORTING_LOG_PATH, 1)
#     position_value = kpiComputer.old_position_value.head(10)
#     total_return = kpiComputer.old_Total_Return()
#     annualized_return = kpiComputer.old_Annualized_Return()
#     win_rate = kpiComputer.old_Win_Rate()
#     max_drawdown = kpiComputer.old_Max_Drawdown()
#     sharpe_ratio = kpiComputer.old_Sharpe_Ratio()
#     volatility = kpiComputer.old_Volatility()
#     categories = kpiComputer.Categories
#     print('position_value', position_value)
#     print('annualized_return', annualized_return)
#     print('total_return', total_return)
#     print('win_rate', win_rate)
#     print('max_drawdown', max_drawdown)
#     print('categories', categories)
#     print('volatility', volatility)
#     print('sharpe_ratio', sharpe_ratio)

if __name__ == "__main__":
    #main()
    pass

