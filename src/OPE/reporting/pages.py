import os 
import dash
from dash import Dash, dcc, html, Input, State, Output, callback
from config import REPORTING_LOG_PATH

backtest_dirs = os.listdir(REPORTING_LOG_PATH)
def display_page1():
    """
    
    """
    return [
            html.H1("LIVE"),
            dcc.Dropdown(id = 'dropdown_backtest', options=backtest_dirs, value = backtest_dirs[0]),
            html.Button("Confirmer backtest", id='ok_backtest', n_clicks=0),
            html.Button("Pause/Reprendre", id="pause_button", n_clicks=0),
            dcc.Graph(id='candlestick_chart')
        ]