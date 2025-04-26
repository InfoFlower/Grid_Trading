import polars as pl
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px
from config import REPORTING_LOG_PATH
from KPI_CATEGORIES import CATEGORIES
pl.Config.set_tbl_cols(20)
pl.Config.set_tbl_rows(500)


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
        self.old_data = pl.read_csv(f'{REPORTING_LOG_PATH}/{backtest_id}/data.csv')
        self.old_position_event = pl.read_csv(f'{REPORTING_LOG_PATH}/{backtest_id}/position_event.csv')
        self.Categories = CATEGORIES
        
        
        
        ###### Transformation du dataframe, calcul equity, dradown etc... ######
        self.old_equity()
        self.old_drawdown()

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
        self.position_value = old_left_merged_data_x_posevent.with_columns(
            [
                (pl.col('Close')*pl.col('crypto_balance') + pl.col('money_balance')).alias('Equity')
            ]
        ).select(
            ["Open time", "Open", "High", "Low", "Close", "crypto_balance", "money_balance", "Equity"]
        )

    def old_drawdown(self):
        """
        """
        position_value = self.position_value.clone()
        position_value = position_value.with_columns([
            pl.col('Equity').cum_max().alias("high_water_mark")
        ]) 
        position_value = position_value.with_columns([
            (pl.col("Equity")-pl.col("high_water_mark"))/pl.col("high_water_mark").alias('Drawdown')
        ])
        self.position_value = position_value.select([
            ["Open time", "Open", "High", "Low", "Close", "crypto_balance", "money_balance", "Equity", "Drawdown"]
        ])

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
                                    "Volatilité": 0.0,
                                    "Sharpe Ratio": 0.0
                                    }
        #old_Max_Drawdown

    ###### OLD KPI  ###### 
    def old_Total_Return(self):
        """
        Pourcentage de gain total (sur tout le backtest)
        -> Float
        """
        ic = self.old_position_event['money_balance'][0]*2
        fc = self.old_position_event['money_balance'][-1]*2
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
        
        ic = self.old_position_event['money_balance'][0]*2

        fc = self.old_position_event['money_balance'][-1]*2

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
        
        """
        return self.position_value['Drawdown'].min()
    
    ###### OLD GRAPHE ######
    def old_graphe_equity(self):
        fig = px.line(self.position_value, x='Open time', y='Equity')
        fig.show()


    











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





def main():

    kpiComputer = KPIComputer(REPORTING_LOG_PATH, 1)
    total_return = kpiComputer.old_Total_Return()
    annualized_return = kpiComputer.old_Annualized_Return()
    win_rate = kpiComputer.old_Win_Rate()
    max_drawdown = kpiComputer.old_Max_Drawdown()
    print('Position value', kpiComputer.position_value.head(10))
    print('annualized_return', annualized_return)
    print('total_return', total_return)
    print('win_rate', win_rate)
    print('max_drawdown', max_drawdown)

if __name__ == "__main__":
    main()

