import os
import sys
import keyboard
import json
import pandas as pd
import polars as pl
import threading
from datetime import datetime
import plotly.graph_objects as go
import dash
from dash import Dash, dcc, html, Input, State, Output, Patch, callback
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
load_dotenv()
WD = os.getenv('WD')
sys.path.append(WD)

from config import REPORTING_LOG_PATH
from pages import display_live, display_kpi, display_graph
from src.OPE.MakeGrid import Grid_Maker
from src.OPE.strategies.strategy_DumbStrat import Strategy
from src.OPE.BackTest import baktest
from DataIterator import DataIterator
from KPIComputer import KPIComputer


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# app.layout = html.Div([
#     dbc.Tabs(
#         [
#         dbc.Tab(label='LIVE', tab_id='tab-1'),
#         dbc.Tab(label='AFTER', tab_id='tab-2')
#         ]
#     )
#     ]),
#     dcc.Store(id='store_speed', data=1.0),
#     dcc.Store(id='store_backtest_running', data=False),
#     dcc.Store(id='store_pause', data=True),
#     dcc.Store(id='store_current_data', data={}),
#     dcc.Store(id='store_open_positions', data={}),
#     dcc.Interval(id='refresh_live', interval = 1000, n_intervals=0, disabled=True),
#     html.Div(id="tab_content", children=display_live())
# ])
backtest_dirs = os.listdir(REPORTING_LOG_PATH)
app.layout = dbc.Container(
    [
        html.H1("REPORTING"),
        dcc.Dropdown(id = 'dropdown_backtest', options=backtest_dirs, value = ""),
        dbc.Tabs(
            children = [
                dbc.Tab(label='LIVE', tab_id='tab-1'),
                dbc.Tab(label='KPI', tab_id='tab-2'),
                dbc.Tab(label='GRAPH', tab_id='tab-3')
            ],
            id="tabs",
            active_tab="tab-1"
        ),
        dcc.Store(id='store_speed', data=1.0),
        dcc.Store(id='store_backtest_running', data=False),
        dcc.Store(id='store_pause', data=True),
        dcc.Store(id='store_current_data', data={}),
        dcc.Store(id='store_open_positions', data={}),
        dcc.Store(id='store_kpi',data={}),
        dcc.Interval(id='refresh_live', interval = 1000, n_intervals=0, disabled=True),
        html.Div(id="tab_content", children = display_live())
    ]
)


@app.callback(Output("tab_content", "children"), 
        Input("tabs", "active_tab"),
        State('store_kpi','data'),
        prevent_initial_call=True)
def render_tab(tab_id, kpi_data):
    """
    Défini le contenu des différents tabs
    """
    print(tab_id)
    if tab_id == "tab-1":
        return html.Div(display_live())

    elif tab_id == "tab-2":
        return html.Div(display_kpi(kpi_computer.Categories))
    
    elif tab_id == 'tab-3':
        return html.Div(display_graph(kpi_computer.fig_equity))
    else:
        raise ValueError
    

@app.callback(Input('dropdown_backtest', 'value'),
              prevent_initial_call=True)
def choose_bt(backtest_id):
    """
    """
    print(backtest_id)
    global kpi_computer
    kpi_computer = KPIComputer(REPORTING_LOG_PATH, backtest_id)
    





@app.callback(Output('store_backtest_running', 'data'),
            Input('ok_backtest', 'n_clicks'),
            [State('dropdown_backtest', 'value'),
            State('store_pause', 'data'),
            State('store_backtest_running', 'data'),
            State('data_every_items', 'value')],
            prevent_initial_call=True)
def confirm_live_bt(n_clicks, dropdown_value, pause, bt_running, every):
    """
    
    """
 
    if pause is True and bt_running is False:
  
        backtest_path = REPORTING_LOG_PATH
        print(backtest_path)
        global di
        di = DataIterator(backtest_path, every)

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
    
    if bt_running:
        if pause:
            #C'est pauser -> reprendre
            pause = False
            print('RESUME')
            di.resume()
        elif not pause:
            #Ca tourne -> pauser
            pause = True
            print('PAUSE')
            di.pause()
    else:
        raise dash.exceptions.PreventUpdate

    return pause, pause 

# @app.callback(Input('candlestick_chart', 'figure'))
# def test_figure(fig_data):
#     print(fig_data['data'])
    

@app.callback(Output('candlestick_chart', 'figure', allow_duplicate=True),
               Input('store_current_data', 'data'),
               State('candlestick_chart', 'figure'),
               prevent_initial_call=True)
def update_graph(new_data, fig_data):
    """
    """

    fig_data = fig_data['data']
    #print(fig_data)
    fig_data_names = [trace['name'] for trace in fig_data]
    print(fig_data_names)

    patched_figure = Patch()
    patched_figure['data'][0]['x'].append(new_data['Open time'][0])
    patched_figure['data'][0]['open'].append(new_data['Open'][0])
    patched_figure['data'][0]['high'].append(new_data['High'][0])
    patched_figure['data'][0]['low'].append(new_data['Low'][0])
    patched_figure['data'][0]['close'].append(new_data['Close'][0])
 
    update_position_event(new_data, patched_figure, fig_data_names)

    return patched_figure

def update_position_event(new_data, patched_figure, fig_data_names):
    """
    """

    
    def open_position(position_event):
        """
        
        """
        id = position_event.pop('id')
        patched_figure['data'].append({'type':'scatter',
                                       'name':f'position_{id}',
                                       'x':[position_event['timestamp'], position_event['timestamp'] + pd.to_timedelta(di.every)],
                                       'y':[position_event['entryprice'], position_event['entryprice']],
                                       'mode':'lines'})

    
    def prolong_open_positions(data_index):
        """
        """
        patched_figure['data'][data_index]['x'][1] = datetime.fromisoformat(new_data['Open time'][0]) + pd.to_timedelta(di.every)

    def closing_position(data_index, position_event, no_open=False):
        if not no_open:
            #position_event ne contient qu'une seule ligne
            patched_figure['data'][data_index]['name'] = f'closed_position_{position_event["id"]}'
            patched_figure['data'][data_index]['x'][1] = position_event['timestamp']
            patched_figure['data'][data_index]['y'][1] = position_event['close_price']
        elif no_open:
            #position_event contient deux lignes, une d'open et l'autre de close
            opening_position = position_event.filter(pl.col("state") == 'Opening')
            closing_position = position_event.filter(pl.col("state") == 'Closing')
            print({'type':'scatter',
                                       'name':f'closed_position_{closing_position["id"]}',
                                       'x':[opening_position['timestamp'], closing_position['timestamp']],
                                       'y':[opening_position['entryprice'], closing_position['close_price']],
                                       'mode':'lines'})
            patched_figure['data'].append({'type':'scatter',
                                       'name':f'closed_position_{closing_position["id"]}',
                                       'x':[opening_position['timestamp'].item(), closing_position['timestamp'].item()],
                                       'y':[opening_position['entryprice'].item(), closing_position['close_price'].item()],
                                       'mode':'lines'})


    if any(name.startswith('position') for name in fig_data_names):
        for fig_data_index, name in enumerate(fig_data_names):
            if name.startswith('position'):
                prolong_open_positions(fig_data_index)

    if di.position_event.select(pl.col("timestamp").dt.strftime('%Y-%m-%dT%H:%M:%S').is_in([new_data['Open time'][0]])).to_series().any():
        
        positions_event = di.position_event.filter(pl.col('timestamp').dt.strftime('%Y-%m-%dT%H:%M:%S')==new_data['Open time'][0])
        print(positions_event)

        ids_with_two_occurrences = (
                    positions_event.clone().group_by("id")
                    .count()
                    .filter(pl.col("count") == 2)
                    .select("id")
                    .to_series()
                    .to_list()
                )
        if ids_with_two_occurrences != []:
            double_positions_event = positions_event.filter(pl.col('id').is_in(ids_with_two_occurrences))
            positions_event = positions_event.filter(~pl.col('id').is_in(ids_with_two_occurrences)) 
            print('AAA', double_positions_event)
        else :
            double_positions_event = None

        #Si il n'y qu'un évènement par position et par timeframe
        print(positions_event)
        for position_event in positions_event.iter_rows(named=True):
            #print(position_event)
            if position_event['state'] == 'Closing':
                print('BBBC', positions_event)
                fig_data_index = fig_data_names.index(f'position_{position_event["id"]}')
                closing_position(fig_data_index, position_event)
            if position_event['state'] == 'Opening':
                print('BBBO', positions_event)
                open_position(position_event)

        # Si il y a 2 évènements par position et par timeframe, 
        # alors on doit fermer la position avant qu'elle soit ouverte
        # puisque les deux évènements se produisent en même temps
        if double_positions_event is not None:
            for position_id in ids_with_two_occurrences:
                double_position_event_for_id = double_positions_event.filter(pl.col("id") == position_id)
                print('CCC', double_position_event_for_id)
                closing_position(fig_data_index, double_position_event_for_id, no_open=True)
                



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
    money_balance = 1000
    crypto_balance = 0.107
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
    #-1,1511776434000,null,null,null,null,null,null,null,INIT,IS,null,107,1000000


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
