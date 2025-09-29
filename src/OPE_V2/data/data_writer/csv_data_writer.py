import os
from dotenv import load_dotenv

from bot.order.order import Order
from bot.position.position import Position
from event.event import EventType, EventDispatcher, Event
from backtest import Backtest
from portfolio.portfolio import Portfolio


load_dotenv()
WD = os.getenv('WD')

dir = f"{WD}src/OPE_V2/data/BACKTEST_OPE_DATA"

class CSVDataWriter:

    METADATA = {
        'BACKTEST' : ['BacktestId', 'TradingSessionType', 'HistoricalStartTimestamp','HistoricalEndTimestamp','Symbol',
                      'StrategyName','StrategyType',#'StrategyParams',
                      'InitialMoney','OperationalStartTimestamp'],
        'ORDER' : ['BacktestId', 'OrderId', 'OrderEventTimestamp', 'OrderEventType',
                   'OrderSide', 'OrderLevel','OrderAssetQty', 'OrderLeverage',
                   'OrderTakeprofitPrice','OrderStoplossPrice','OperationalTimestamp'],
        'POSITION' : ['BacktestId', 'PositionId', 'OrderId', 'PositionEventTimestamp', 'PositionEventType', 
                      'PositionSide', 'PositionMargin', 'PositionEntryPrice', 'PositionAssetQty', 'PositionLeverage', 
                      'PositionTakeprofitPrice', 'PositionStoplossPrice', 
                      'PositionClosePrice', 'PositionCloseType', 'OperationalTimestamp'],
        'PORTFOLIO' : ['BacktestId', 'PortfolioEventTimestamp', 'PortfolioEventType',
                       'CashBalance', 'OrderLongAsset', 'OrderShortAsset',
                        'PositionLongAsset', 'PositionShortAsset','OperationalTimestamp']
    }
    EVENTS = [EventType.INIT_BACKTEST,
              EventType.INIT_PORTFOLIO,
              EventType.UPDATE_PORTFOLIO,
              EventType.ORDER_EXECUTED,
              EventType.ORDER_CREATED,
              EventType.ORDER_CANCELLED,
              EventType.POSITION_CANCELLED,
              EventType.POSITION_CLOSED,
              EventType.POSITION_OPENED]

    def __init__(self, event_dispatcher : EventDispatcher, output_dir=dir, sep=',', append=False):
        """
        """
        self.sep = sep
        self.files_path = {}
        self.event_dispatcher = event_dispatcher
        #self.output_dir = output_dir

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for filename in self.METADATA:
            self.files_path[filename] = f"{output_dir}/{filename}.csv"
            
            if not os.path.exists(self.files_path[filename]) or append is False:
                with open(self.files_path[filename], 'w') as f:
                    f.write(sep.join(self.METADATA[filename]))
                    f.close()

        for event_type in self.EVENTS:
            event_dispatcher.add_listeners(event_type, self.log)

        

    def mapping_order(self, event : Event) -> dict:

        order : Order = event.data
        return {
            'BacktestId' : self.backtest_id,
            'OrderId': order.id,
            'OrderEventTimestamp' : order.order_event_timestamp,
            'OrderEventType' : order.order_event,
            'OrderSide' : order.side,
            'OrderLevel' : order.level,
            'OrderAssetQty' : order.asset_qty,
            'OrderLeverage' : order.leverage,
            'OrderTakeprofitPrice' : order.tp_price,
            'OrderStoplossPrice' : order.sl_price,
            'OperationalTimestamp' : event.timestamp
        }
    
    def mapping_position(self, event : Event) -> dict:

        position : Position = event.data
        return {
            'BacktestId' : self.backtest_id,
            'PositionId': position.id,
            'OrderId': position.order_id,
            'PositionEventTimestamp' : position.position_event_timestamp,
            'PositionEventType' : position.position_event,
            'PositionSide' : position.side,
            'PositionMargin' : position.margin,
            'PositionEntryPrice' : position.entry_price,
            'PositionAssetQty' : position.asset_qty,
            'PositionEntryValue' : position.value(position.entry_price),
            'PositionLeverage' : position.leverage,
            'PositionTakeprofitPrice' : position.tp_price,
            'PositionStoplossPrice' : position.sl_price,
            'PositionClosePrice' : position.close_price,
            'PositionCloseValue' : position.value(position.close_price),
            'PositionClosePnl': position.pnl(position.close_price),
            'PositionCloseType' : position.close_type,
            'OperationalTimestamp' : event.timestamp
        }
    
    def mapping_backtest(self, event : Event) -> dict:
        backtest : Backtest = event.data
        return {
            'BacktestId' : backtest.id,
            'TradingSessionType': "BACKTEST",
            'HistoricalStartTimestamp' : backtest.historical_start_timestamp,
            'HistoricalEndTimestamp' : backtest.historical_end_timestamp,
            'Symbol' : backtest.pair,
            'StrategyName' : backtest.strategy_name,
            'StrategyType' : backtest.strategy_type,
            #'StrategyParams' : backtest.strategy_params,
            'InitialMoney' : backtest.initial_money,
            'OperationalStartTimestamp' : event.timestamp

        }
    
    def mapping_portfolio(self, event : Event) -> dict:
        portfolio : Portfolio = event.data
        return {
            'BacktestId':self.backtest_id,
            'PortfolioEventTimestamp': portfolio.portfolio_event_timestamp,
            'PortfolioEventType' : portfolio.portfolio_event_type,
            'CashBalance' : portfolio.portfolio_balance.cash_balance,
            'OrderLongAsset' : portfolio.portfolio_balance.orders.long,
            'OrderShortAsset' : portfolio.portfolio_balance.orders.short,
            'PositionLongAsset' : portfolio.portfolio_balance.positions.long,
            'PositionShortAsset' : portfolio.portfolio_balance.positions.short,
            'OperationalTimestamp' : event.timestamp
        }
    def log(self, event : Event) -> None:

        obj = event.data
        if obj.__class__ == Backtest:
            key = 'BACKTEST'
            self.backtest_id = obj.id
            map = self.mapping_backtest(event)
        elif obj.__class__ == Portfolio:
            key = 'PORTFOLIO'
            map = self.mapping_portfolio(event)
        elif obj.__class__ == Order:
            key = 'ORDER'
            map = self.mapping_order(event)
        elif obj.__class__ == Position:
            key = 'POSITION'
            map = self.mapping_position(event)

        with open (self.files_path[key], 'a') as f:
            f.write('\n'+self.sep.join([str(map[column]) for column in self.METADATA[key]]))
            f.close()


