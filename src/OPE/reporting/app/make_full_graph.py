data_file = 'data_raw_BTCUSDT_175.csv'
order_file = 'src/OPE/reporting/data_logger/Order.csv'
import polars as pl
from dotenv import load_dotenv
import os
load_dotenv()
WD = os.getenv('WD')

def downsample_price_df(price_df, interval=10):
    return price_df.slice(0, price_df.height).filter(pl.arange(0, price_df.height) % interval == 0)


def get_data_graph(data_file, order_file, position_file):
    if len(data_file.split('_')) > 3:
        data_file_path = WD + 'data/OPE_DATA/DATA_RAW_S_ORIGIN_test_code/' + data_file
    else:
        data_file_path = WD + 'data/DATA_RAW_S_ORIGIN/' + data_file

    price_df = pl.read_csv(data_file_path, truncate_ragged_lines=True)
    price_df = price_df.with_columns([
        pl.col("Open time").cast(pl.Datetime).alias("Time")
    ])
    price_df = downsample_price_df(price_df, interval=1000)  # Keep every 10th row

    orders_df = pl.read_csv(order_file)
    orders_df = orders_df.with_columns([
        pl.col("OrderTime").cast(pl.Datetime).alias("OrderTime")
    ])

    positions_df = pl.read_csv('src/OPE/reporting/data_logger/Position.csv')
    positions_df = positions_df.with_columns([
        pl.col("EventData_Time").cast(pl.Datetime).alias("EventData_Time")
    ])

    price_data = price_df.select(["Time", "Close"]).to_dicts()
    orders_data = orders_df.select(["OrderTime", "OrderType", "OrderPrice"]).to_dicts()
    positions_data = positions_df.select(["EventData_Time", "EventCode", "PositionEntryPrice", "PositionClosePrice"]).to_dicts()

    return {
        "prices": price_data,
        "orders": orders_data,
        "positions": positions_data
    }