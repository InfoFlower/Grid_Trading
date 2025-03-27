from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import polars as pl
import keyboard

class Reporting:
    """
    """
    def __init__(self):
        self.app = Dash(__name__)
        self.running = True
        self.speed = 1.0
        self.app.layout = html.Div([
            dcc.Tabs(id='tabs', value='tab-1', children=[
                dcc.Tab(label='LIVE', value='tab-1'),
                dcc.Tab(label='AFTER', value='tab-2')
            ]),
            html.Div(id="tab-content")
        ])

        self.app.callback(Output("tab-content", "children"), Input("tabs", "value"))(self.render_tab)

    def render_tab(self, value_tab):
        if value_tab == "tab-1":
            #TODO : mettre ces returns dans des fichier différents
            return html.Div([
                html.H1("LIVE"),
                html.Button("Pause/Reprendre", id="pause-button", n_clicks=0),
                html.P("Ici, on affichera les stats de la stratégie.")
            ])
        elif value_tab == "tab-2":
            return html.Div([
                html.H1("AFTER"),
                dcc.Interval(id="interval", interval=1000, n_intervals=0),
                html.Div(id="status", children="Simulation en cours")
            ])
        else:
            raise ValueError

    def start(self):
        self.app.run(debug=True)



if __name__ == "__main__":
    dashboard = Reporting()
    dashboard.start()


