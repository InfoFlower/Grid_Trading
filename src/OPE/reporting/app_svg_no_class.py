import os
import sys
import keyboard
import polars as pl
import threading
import plotly.graph_objects as go
import dash
from dash import Dash, dcc, html, Input, State, Output, callback
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
load_dotenv()
WD = os.getenv('WD')
sys.path.append(WD)


from src.OPE.MakeGrid import Grid_Maker
from src.OPE.strategies.strategy_DumbStrat import Strategy
from src.OPE.BackTest import baktest
from DataIterator import DataIterator


app = Dash(__name__)

#init_state = {"Running": False, "Speed": 1.0}

app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='LIVE', value='tab-1'),
        dcc.Tab(label='AFTER', value='tab-2')
    ]),
    dcc.Store(id='store_speed', data=1.0),
    dcc.Store(id='store_backtest_running', data=False),
    dcc.Store(id='store_pause', data=True),
    dcc.Store(id='store_current_data', data=[]),
    dcc.Interval(id='refresh_live', interval = 1000, n_intervals=0, disabled=True),
    html.Div(id="tab_content")
])

REPORTING_LOG_PATH = f'{WD}src/OPE/reporting/BACKTESTS/'

@callback(Output("tab_content", "children"), 
        Input("tabs", "value"))
def render_tab(value_tab):
    """
    Défini le contenu des différents tabs
    """
    print(value_tab)
    if value_tab == "tab-1":
        
        #TODO : mettre ces returns dans des fichiers différents
        return html.Div([
            html.H1("LIVE"),
            dcc.Dropdown(id = 'dropdown_backtest', options=os.listdir(REPORTING_LOG_PATH), value = 2),
            html.Button("Confirmer backtest", id='ok_backtest', n_clicks=0),
            html.Button("Pause/Reprendre", id="pause_button", n_clicks=0),
            dcc.Graph(id='candlestick_chart'),
            html.Div(id="status", children="Simulation en cours")
        ])
    elif value_tab == "tab-2":
        return html.Div([
            html.H1("AFTER"),
            dcc.Interval(id="interval", interval=1000, n_intervals=0)
        ])
    else:
        raise ValueError
    
@callback([Output('store_pause', 'data', allow_duplicate=True),
           Output('refresh_live', 'disabled', allow_duplicate=True),
           Output('store_backtest_running', 'data')],
        Input('ok_backtest', 'n_clicks'),
          State('dropdown_backtest', 'value'),
          State('store_pause', 'data'),
          State('store_backtest_running', 'data'),
           prevent_initial_call=True)
def choose_bt_dropdown(n_clicks, dropdown_value, pause, bt_running):
    """
    
    """
    if pause is True and bt_running is False:
        
        data_path = REPORTING_LOG_PATH+f'{dropdown_value}/data.csv'
        data = pl.read_csv(data_path)
        global di
        di = DataIterator(data)

        thread = threading.Thread(target=di.iterate)
        thread.start()
        
        pause = False
        bt_running = True
    else:
        dash.exceptions.PreventUpdate
    return pause, pause, bt_running


@callback(Input('refresh_live', 'n_intervals'))
def todo(n_intervals):#Update graph
    if not di.data_queue.empty():
        print("QUEUE")
        print(di.data_queue.get())
    else:
        print('empty')


@callback([Output('store_pause', 'data'), 
           Output('refresh_live', 'disabled')],
           Input('pause_button', 'n_clicks'),
           State('store_pause', 'data'),
           State('store_backtest_running', 'data'),
           prevent_initial_call=True)
def pause(n_clicks, pause, bt_running):
    """
    """
    if bt_running:
        if pause:
            #C'est pauser -> reprendre
            pause = False
            di.resume()
        elif not pause:
        #Ca tourne -> pauser
            pause = True
            di.pause()
    else:
        raise dash.exceptions.PreventUpdate
    
    return pause, pause
    




#Crée une instance de Backtest,
#A faire passer les arguments à travers une page 'Create Backtest' 
def create_run_backtest():
    """
    Crée une instance de BackTest
    et run la strategy associée
    """
    GridType = 'BasicGrid'
    GridName='GridPoc'
    grid_maker = Grid_Maker(GridType, GridName)

    StratName = 'DumbStrat'
    strategy = Strategy(StratName, grid_maker)

    data_path = f'{WD}/data/OPE_DATA/data_raw_BTCUSDT_176.csv'
    money_balance = 1000000
    crypto_balance = 107
    TimeCol = 0
    CloseCol = 1
    log_path = REPORTING_LOG_PATH
    bt = baktest(data_path, strategy, money_balance,crypto_balance,log_path,TimeCol,CloseCol,time_4_epoch=500000)

    for _ in bt:
        pass

    with open(bt.strategy.grid_maker.write_path, 'a') as f:f.write(']')
            




if __name__ == "__main__":
    app.run(debug=True)


