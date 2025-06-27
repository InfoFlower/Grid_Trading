import os
from datetime import datetime
from dotenv import load_dotenv
import polars as pl
load_dotenv()
WD = os.getenv('WD')


from data.data_provider.csv_data_provider import CSVDataProvider
from strategy.strategy import Strategy, StrategyType
from portfolio.portfolio import Portfolio
from event.event import EventDispatcher, Event, EventType

class Backtest:

    BACKTEST_OPE_DATA = f"{WD}src/OPE_V2/data/BACKTEST_OPE_DATA/"


    # id : int
    # label_id : str
    # historical_start_timestamp : int  -- data_provider
    # historical_end_timestamp : int  -- data_provider
    # pair : str -- data_provider
    # strategy_name : str -- strategy
    # strategy_type : str -- strategy
    # strategy_params : str -- strategy (user)
    # initial_money : float -- strategy (user)
    # technical_start_timestamp : datetime
    # technical_end_timestamp : datetime

    def __init__(self, data_provider : CSVDataProvider,
                strategy : Strategy, 
                portfolio : Portfolio,
                event_dispatcher : EventDispatcher) -> None:
        
        self.event_dispatcher = event_dispatcher
        self.data_provider = data_provider

        self.id : int = 0 #SHA1
        self.label_id : str = "AAA"
        self.historical_start_timestamp : int = data_provider.initial_data['TimeCol']
        self.historical_end_timestamp : int = data_provider.last_data['TimeCol']
        self.pair : str = data_provider.pair
        self.strategy_name : str = strategy.strategy_name
        self.strategy_type : StrategyType = strategy.strategy_type
        self.strategy_params : dict = strategy.params
        self.initial_money : float = portfolio.initial_cash
        self.technical_start_timestamp : datetime = datetime.now()
        #self.technical_end_timestamp : datetime = datetime.now()

        event_dispatcher.add_listeners(EventType.END_BACKTEST, self.compute_kpi)

        event_dispatcher.dispatch(Event(
                            type = EventType.INIT_BACKTEST,
                            data = self,
                            timestamp = datetime.now()
                        ))
        
    def compute_kpi(self, event : Event):
        print("BACKTEST TERMINÉ")

        #self.load_data()
        #self.mapping_position_1()

        #self.returns().balance().pnl()

        #self.graph()
    ################################################################################
    #########################       SQL LITE ????     ##############################
    #####################     METTRE DANS AUTRE FICHIER     ########################
    ################################################################################
    
    ##### LOAD DATA #####
    def load_data(self):
        self.data = self.data_provider.data.clone().select(['TimeCol', 'OpenCol','CloseCol','LowCol','HighCol'])
        self.order = pl.read_csv(f"{self.BACKTEST_OPE_DATA}ORDER.csv")
        self.position = pl.read_csv(f"{self.BACKTEST_OPE_DATA}POSITION.csv")
        print(self.position.__class__)
        self.portfolio = pl.read_csv(f"{self.BACKTEST_OPE_DATA}PORTFOLIO.csv")
    
    ##### TRANSFORM TABLES #####
    def mapping_position_1(self):
        self.position_open_to_close = self.position.clone().\
            filter(pl.col("PositionEventType")=="EventType.POSITION_OPENED").\
            select(
                ["BacktestId","PositionId","OrderId","PositionEventTimestamp","PositionEventType",
            "PositionSide","PositionMargin","PositionEntryPrice","PositionAssetQty","PositionEntryValue",
            "PositionLeverage","PositionTakeprofitPrice","PositionStoplossPrice"]
            ).join(
            self.position.clone().\
            filter(pl.col("PositionEventType")=="EventType.POSITION_CLOSED").\
            select(
                ["PositionId","PositionEventTimestamp", "PositionEventType", "PositionClosePrice", "PositionCloseValue", "PositionClosePnl", "PositionCloseType"]
            ),
            left_on="PositionId", right_on="PositionId", how="left"
            ).\
            rename(mapping = {"PositionEventTimestamp":"PositionOpenEventTimestamp",
                                "PositionEventTimestamp_right":"PositionCloseEventTimestamp"}).\
            drop(["PositionEventType", "PositionEventType_right"])
        
        with pl.Config(tbl_cols=19, tbl_rows=12):
            print(self.position_open_to_close.columns)





    ##### ADD COLUMNS #####
    def returns(self):

        self.data = self.data.with_columns(pl.col("CloseCol").pct_change().alias("Returns"))
        return self

    def balance(self):
        self.data = self.data.join(
            self.portfolio.select(["PortfolioEventTimestamp", "CashBalance"]),
            left_on="TimeCol", right_on="PortfolioEventTimestamp", how="left"
                            ).group_by("TimeCol", maintain_order=True).tail(1
                            ).with_columns(
                                [pl.col("CashBalance").fill_null(strategy='forward').alias("CashBalance")]
                            )
        return self

    def pnl(self):
        print(self.position_open_to_close)
        ctx = pl.SQLContext(DATA=self.data, POSITION_OC=self.position_open_to_close)
        result = ctx.execute("""
                SELECT * 
                FROM  DATA
                LEFT JOIN POSITION_OC ON DATA.TimeCol >= POSITION_OC.PositionOpenEventTimestamp AND DATA.TimeCol <= POSITION_OC.PositionCloseEventTimestamp
        """).collect()
        
        with pl.Config(tbl_cols=20):
            print(result.head())

    def graph(self):

        import matplotlib.pyplot as plt
        plt.plot(self.data["TimeCol"].to_numpy(),self.data["CashBalance"].to_numpy())
        plt.show()



    
    