import os
import sys
import keyboard
import polars as pl
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback
from dotenv import load_dotenv
load_dotenv()
WD = os.getenv('WD')
ETL_folder_relative = os.path.dirname(WD)
sys.path.append(ETL_folder_relative)


import src.OPE.MakeGrid as MakeGrid
from src.OPE.strategies.strategy_DumbStrat import Strategy
from src.OPE.BackTest import baktest


app = Dash(__name__)

init_state = {"Running": True, "Speed": 1.0}

app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='LIVE', value='tab-1'),
        dcc.Tab(label='AFTER', value='tab-2')
    ]),
    dcc.Store(id='sim_state', data=init_state),
    html.Div(id="tab_content")
])

@callback(
        Output("tab_content", "children"), 
        Input("tabs", "value")
        )
def render_tab(value_tab):
    """
    Défini le contenu des différents tabs
    """
    print('lala')
    if value_tab == "tab-1":
        #TODO : mettre ces returns dans des fichiers différents
        return html.Div([
            html.H1("LIVE"),
            html.Button("Pause/Reprendre", id="pause-button", n_clicks=0),
            html.Div(id="status", children="Simulation en cours")
        ])
    elif value_tab == "tab-2":
        return html.Div([
            html.H1("AFTER"),
            dcc.Interval(id="interval", interval=1000, n_intervals=0)
        ])
    else:
        raise ValueError

@callback(Output("status", "children"), Input("pause-button", "n_clicks"), prevent_initial_call=True, suppress_callback_exceptions=True) 
def toggle_pause(n_clicks):
    """
    """
    print('pause')
    print(running)
    running = not running
    return running

def run_backtest():
    """
    Crée une instance de BackTest
    et run la strategy associée
    """
    GridType = 'BasicGrid'
    GridName='GridPoc'
    grid_maker = MakeGrid.Grid_Maker(GridType, GridName)

    StratName = 'DumbStrat'
    strategy = Strategy(StratName, grid_maker)

    data_path = f'{WD}/data/OPE_DATA/data_raw_BTCUSDT_176.csv'
    money_balance = 10000
    crypto_balance = 100
    TimeCol = 0
    CloseCol = 1
    bktst=baktest(data_path, strategy, money_balance,crypto_balance,TimeCol,CloseCol,time_4_epoch=500000)
    for _ in bktst:
        pass
    with open(bktst.strategy.grid_maker.write_path, 'a') as f:f.write(']')
            




if __name__ == "__main__":
    run_backtest()


