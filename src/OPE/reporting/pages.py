import os 
import dash
from dash import Dash, dcc, html, Input, State, Output, callback
import plotly.graph_objects as go
from config import REPORTING_LOG_PATH

backtest_dirs = os.listdir(REPORTING_LOG_PATH)
def display_page1():
    """
    
    """
    return [
            html.H1("LIVE"),
            dcc.Dropdown(id = 'dropdown_backtest', options=backtest_dirs, value = backtest_dirs[0]),
            dcc.RadioItems(id='data_every_items',options=[
                                            {'label': '1m', 'value': '1m'},
                                            {'label': '5m', 'value': '5m'},
                                            {'label': '15m', 'value': '15m'},
                                            {'label': '30m', 'value': '30m'},
                                            {'label': '1h', 'value': '1h'},
                                            {'label': '4h', 'value': '4h'},
                                            {'label': '1d', 'value': '1d'}],
                                            value='5m'),
            html.Button("Confirmer backtest", id='ok_backtest', n_clicks=0),
            html.Button("Pause/Reprendre", id="pause_button", n_clicks=0),
            dcc.Graph(id='candlestick_chart', figure={'data':[
                                                {'type': 'candlestick',
                                                'name':'candle_chart', 
                                                'x': [],               
                                                'open': [],
                                                'high': [],
                                                'low': [],
                                                'close': []}
                                                ]
                                            }
                                        )
                                    ]