import os
from dotenv import load_dotenv

load_dotenv()
WD = os.getenv('WD')

dir = f"{WD}src/OPE_V2/data/BOT_OPE_DATA"

class CSVDataWriter:

    DATA_STRUCTURE = {

        'ORDER' : ['OrderId', 'OrderEventTimestamp', 'OrderEventType', 'OrderSide', 'OrderLevel','OrderAssetQty','OrderLeverage','OrderTakeprofitPrice','OrderStoplossPrice','CreatedAt','ExecutedAt', 'OperationnalTimestamp'],
        'POSITION' : ['PositionId', 'OrderId', 'PositionEventTimestamp', 'PositionEventType', 'PositionSide', 'PositionAssetQty', 'PositionLeverage', 'PositionTakeprofitPrice', 'PositionStoplossPrice', 'PositionEntryPrice', 'PositionClosePrice', 'PositionCloseType', 'OperationnalTimestamp']

    }

    def __init__(self, event_dispatcher, output_dir=dir, sep=',', append=False):
        """
        """
        self.files_path = {}
        self.event_dispatcher = event_dispatcher
        #self.output_dir = output_dir

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for filename in self.DATA_STRUCTURE:
            self.files_path[filename] = f"{output_dir}/{filename}.csv"
            
            if not os.path.exists(self.files_path[filename]) or append is False:
                with open(self.files_path[filename], 'w') as f:
                    f.write(sep.join(self.DATA_STRUCTURE[filename]))
                    f.close()

#csv_data_writer = CSVDataWriter()