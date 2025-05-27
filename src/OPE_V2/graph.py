import os
import plotly.graph_objects as go
import polars as pl
from dotenv import load_dotenv

load_dotenv()
WD = os.getenv('WD')


file_path=f'{WD}data/OPE_DATA/DATA_RAW_S_ORIGIN_test_code/data_raw_BTCUSDT_176.csv'
data = pl.read_csv(file_path, truncate_ragged_lines=True)

fig = go.Figure(data=[go.Candlestick(x=data['Open time'],
                                        open=data['Open'],
                                        high=data['High'],
                                        low=data['Low'],
                                        close=data['Close'])])

#Open time,Open,High,Low,Close,
fig.show()