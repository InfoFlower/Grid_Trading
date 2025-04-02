from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import polars as pl
import keyboard


app = Dash(__name__)

global running

running = True
speed = 1.0

app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='LIVE', value='tab-1'),
        dcc.Tab(label='AFTER', value='tab-2')
    ]),
    html.Div(id="tab-content")
])

#app.callback(Output("tab-content", "children"), Input("tabs", "value"))(render_tab)

@callback(
        Output("tab-content", "children"), 
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

@callback(Output("status", "children"), Input("pause-button", "n_clicks")) 
def toggle_pause(n_clicks):
    """
    """
    print('pause')
    print(running)
    running = not running
    return running
            




if __name__ == "__main__":
    app.run(debug=True)


