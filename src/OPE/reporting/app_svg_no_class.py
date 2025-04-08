import os
import sys
import keyboard
import polars as pl
import threading
import plotly.graph_objects as go
import dash
from dash import Dash, dcc, html, Input, State, Output, Patch, callback
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
load_dotenv()
WD = os.getenv('WD')
sys.path.append(WD)

from config import REPORTING_LOG_PATH
from pages import display_page1
from src.OPE.MakeGrid import Grid_Maker
from src.OPE.strategies.strategy_DumbStrat import Strategy
from src.OPE.BackTest import baktest
from DataIterator import DataIterator


app = Dash(__name__)

app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='LIVE', value='tab-1'),
        dcc.Tab(label='AFTER', value='tab-2')
    ]),
    dcc.Store(id='store_speed', data=1.0),
    dcc.Store(id='store_backtest_running', data=False),
    dcc.Store(id='store_pause', data=True),
    dcc.Store(id='store_current_data', data={}),
    dcc.Interval(id='refresh_live', interval = 1000, n_intervals=0, disabled=True),
    html.Div(id="tab_content", children=display_page1())
])

@app.callback(Output("tab_content", "children"), 
        Input("tabs", "value"),
        prevent_initial_call=True)
def render_tab(value_tab):
    """
    Défini le contenu des différents tabs
    """

    if value_tab == "tab-1":
        return html.Div(display_page1())

    elif value_tab == "tab-2":
        return html.Div([
            html.H1("AFTER"),
        ])
    else:
        raise ValueError
    
@app.callback(Output('store_backtest_running', 'data'),
            Input('ok_backtest', 'n_clicks'),
            [State('dropdown_backtest', 'value'),
            State('store_pause', 'data'),
            State('store_backtest_running', 'data'),
            State('data_every_items', 'value')],
            prevent_initial_call=True)
def choose_bt_dropdown(n_clicks, dropdown_value, pause, bt_running, items_value):
    """
    
    """
 
    if pause is True and bt_running is False:
            
        data_path = REPORTING_LOG_PATH+f'{dropdown_value}/data.csv'
        global di
        di = DataIterator(data_path, items_value)

        thread = threading.Thread(target=di.iterate)
        thread.start()

        bt_running = True
        
    else:
        dash.exceptions.PreventUpdate 
        
    return bt_running


@app.callback(Output('store_current_data', 'data'),
              Input('refresh_live', 'n_intervals'),
              prevent_initial_call=True)
def get_queue(n_intervals):

    if not di.data_queue.empty():
        queue_data = di.data_queue.get()
        
        return queue_data
    else:
        return dash.no_update
    

@app.callback([Output('store_pause', 'data'), 
           Output('refresh_live', 'disabled')],
           [Input('pause_button', 'n_clicks'),
            Input('store_backtest_running', 'data')],
           State('store_pause', 'data'),
           prevent_initial_call=True)
def pause(n_clicks, bt_running, pause):
    """
    """
    print('AVANT pause:',pause, 'n_clicks', n_clicks)
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
    print('APRES pause:',pause)
    return pause, pause

@app.callback(Output('candlestick_chart', 'figure', allow_duplicate=True),
               Input('store_current_data', 'data'),
               prevent_initial_call=True)
def update_graph(new_data):
    """
    """
    #print('GRAPH')
    #print('new_data : ', new_data)

    patched_figure = Patch()

    patched_figure['data'][0]['x'].append(new_data['Open time'][0])
    patched_figure['data'][0]['open'].append(new_data['Open'][0])
    patched_figure['data'][0]['high'].append(new_data['High'][0])
    patched_figure['data'][0]['low'].append(new_data['Low'][0])
    patched_figure['data'][0]['close'].append(new_data['Close'][0])

    return patched_figure




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


