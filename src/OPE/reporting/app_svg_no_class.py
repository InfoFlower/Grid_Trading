import os
import sys
import keyboard
import json
import pandas as pd
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
    dcc.Store(id='store_open_positions', data={}),
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
        position_event_path = REPORTING_LOG_PATH+f'{dropdown_value}/position_event.csv'

        global di
        di = DataIterator(data_path, items_value, position_event_path)

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

@app.callback(Input('store_current_data', 'data'),
              State('candlestick_chart', 'figure'))
def test_figure(data, fig_data):
    #print(fig_data)
    pass
    

@app.callback(Output('candlestick_chart', 'figure', allow_duplicate=True),
               Input('store_current_data', 'data'),
               State('store_open_positions', 'data'),
               prevent_initial_call=True)
def update_graph(new_data, open_positions):
    """
    """

    patched_figure = Patch()

    patched_figure['data'][0]['x'].append(new_data['Open time'][0])
    patched_figure['data'][0]['open'].append(new_data['Open'][0])
    patched_figure['data'][0]['high'].append(new_data['High'][0])
    patched_figure['data'][0]['low'].append(new_data['Low'][0])
    patched_figure['data'][0]['close'].append(new_data['Close'][0])
    #patched_figure['layout']['xaxis']['range'][-1] = new_data['Open time'][0] +
 
    patched_figure = update_position_event(new_data, open_positions, patched_figure)

    return patched_figure

def update_position_event(new_data, open_positions, patched_figure):
    """
    """

    def open_position(position_event, open_positions, patched_figure):
        """
        
        """
        id = position_event.pop('id')
        #open_positions[id] = position_event
        #print(go.Scatter(x=[position_event['timestamp']], y=[position_event['entryprice']], mode='lines', name=f'position_{id}'))
        patched_figure['data'].append({'type':'scatter',
                                       'name':f'position_{id}',
                                       'x':[position_event['timestamp'], position_event['timestamp'] + pd.to_timedelta(di.every)],
                                       'y':[position_event['entryprice'], position_event['entryprice']],
                                       'mode':'lines'})

        return patched_figure

    if di.position_event.select(pl.col("timestamp").dt.strftime('%Y-%m-%dT%H:%M:%S').is_in([new_data['Open time'][0]])).to_series().any():
        #print(di.position_event)
        
        positions_event = di.position_event.filter(pl.col('timestamp').dt.strftime('%Y-%m-%dT%H:%M:%S')==new_data['Open time'][0])
        #print(di.position_event)
        for position_event in positions_event.iter_rows(named=True):
            #print(position_event)
            if position_event['justif'] == 'Opening':
                patched_figure = open_position(position_event, open_positions, patched_figure)

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
    #create_run_backtest()


"""
from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objects as go
from dash_extensions.enrich import DashProxy, Patch
import polars as pl
import numpy as np
from datetime import timedelta

# Sample data generator
timestamps = pl.date_range("2024-01-01", "2024-01-20", interval="1d")
prices = np.random.rand(len(timestamps)) * 100

df = pl.DataFrame({
    "timestamp": timestamps,
    "price": prices
})

# Simulated trading positions
# You would dynamically update this in real use
positions = {
    1: {"id": 1, "y": 50, "x_start": timestamps[2], "active": True},
    2: {"id": 2, "y": 75, "x_start": timestamps[5], "active": True},
    3: {"id": 3, "y": 65, "x_start": timestamps[7], "active": False},  # Closed
}

# Dashboard
app = DashProxy(__name__)
app.layout = html.Div([
    html.Button("Update Chart", id="btn"),
    dcc.Graph(
        id="graph",
        figure=go.Figure()
    )
])

@app.callback(
    Output("graph", "figure", allow_duplicate=True),
    Input("btn", "n_clicks"),
    prevent_initial_call=True
)
def update_chart(n):
    patch = Patch()

    # Get latest timestamp (simulate new candle)
    current_x = df["timestamp"][min(n + 9, len(df) - 1)]  # iterate slowly

    # Start fresh for the patch
    patch["data"] = []

    # Add candlestick trace (optional if already present)
    patch["data"] += [go.Scatter(
        x=df["timestamp"][:n+10],
        y=df["price"][:n+10],
        mode="lines+markers",
        name="Price"
    )]

    # Add/Update position lines
    for pos in positions.values():
        if not pos["active"]:
            continue  # skip closed positions
        x0 = pos["x_start"]
        x1 = current_x
        y = pos["y"]
        patch["data"] += [go.Scatter(
            x=[x0, x1],
            y=[y, y],
            mode="lines",
            line=dict(dash="dash", width=2),
            name=f"Position {pos['id']}"
        )]

    return patch

if __name__ == "__main__":
    app.run_server(debug=True)

"""
