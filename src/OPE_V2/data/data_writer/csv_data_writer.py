import os
from dotenv import load_dotenv

from bot.order.order import Order
from bot.position.position import Position
from  event.event import EventType, EventDispatcher, Event
from backtest import Backtest


load_dotenv()
WD = os.getenv('WD')

dir = f"{WD}src/OPE_V2/data/BOT_OPE_DATA"

class CSVDataWriter:

    METADATA = {

        'ORDER' : ['OrderId', 'OrderEventTimestamp', 'OrderEventType', 'OrderSide', 'OrderLevel','OrderAssetQty','OrderLeverage','OrderTakeprofitPrice','OrderStoplossPrice','OperationalTimestamp'],
        'POSITION' : ['PositionId', 'OrderId', 'PositionEventTimestamp', 'PositionEventType', 'PositionSide', 'PositionEntryPrice', 'PositionAssetQty', 'PositionLeverage', 'PositionTakeprofitPrice', 'PositionStoplossPrice', 'PositionClosePrice', 'PositionCloseType', 'OperationalTimestamp'],
        'BACKTEST' : ['BacktestId','HistoricalStartTimestamp','HistoricalEndTimestamp','Symbol','StrategyName','StrategyType','StrategyParams','InitialMoney','OperationalTimestamp']
    }
    EVENTS = [EventType.INIT_BACKTEST,
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
            'PositionId': position.id,
            'OrderId': position.order_id,
            'PositionEventTimestamp' : position.position_event_timestamp,
            'PositionEventType' : position.position_event,
            'PositionSide' : position.side,
            'PositionEntryPrice' : position.entry_price,
            'PositionAssetQty' : position.asset_qty,
            'PositionLeverage' : position.leverage,
            'PositionTakeprofitPrice' : position.tp_price,
            'PositionStoplossPrice' : position.sl_price,
            'PositionClosePrice' : position.close_price,
            'PositionCloseType' : position.close_type,
            'OperationalTimestamp' : event.timestamp
        }
    
    def mapping_backtest(self, event : Event) -> dict:
        backtest : Backtest = event.data
        return {
            'BacktestId' : backtest.id,
            'HistoricalStartTimestamp' : backtest.historical_start_timestamp,
            'HistoricalEndTimestamp' : backtest.historical_end_timestamp,
            'Symbol' : backtest.pair,
            'StrategyName' : backtest.strategy_name,
            'StrategyType' : backtest.strategy_type,
            'StrategyParams' : backtest.strategy_params,
            'InitialMoney' : backtest.initial_money,
            'OperationalTimestamp' : backtest.technical_start_timestamp

        }
    
    def log(self, event : Event) -> None:

        obj = event.data
        if obj.__class__ == Order:
            key = 'ORDER'
            map = self.mapping_order(event)
        elif obj.__class__ == Position:
            key = 'POSITION'
            map = self.mapping_position(event)
        elif obj.__class__ == Backtest:
            key = 'BACKTEST'
            map = self.mapping_backtest(event)

        with open (self.files_path[key], 'a') as f:
            f.write('\n'+self.sep.join([str(map[column]) for column in self.METADATA[key]]))
            f.close()


