from dash import Dash, dcc, html, Input, Output, State, callback
import plotly.express as px
import polars as pl
import functools
import keyboard

class Reporting:
    """
    """
    #state_struct = ["Running", "Speed", "Current_data"]
    state_init = {"Running" : True, "Speed" : 1.0, "Current_data" : [], 'n_clicks':0}
    def __init__(self, ):
        self.app = Dash(__name__)
        self.state = self.state_init
        # self.running = True
        # self.speed = 1.0
        # self.current_data = []
        print("ll")
        self.app.layout = html.Div([
            dcc.Store(id='sim_state', data=[self.state]),
            dcc.Tabs(id='tabs', value='tab-1', children=[
                dcc.Tab(label='LIVE', value='tab-1'),
                dcc.Tab(label='AFTER', value='tab-2')
            ]),
            html.Div(id="tab_content")
        ])

        #self.app.callback(Output("tab_content", "children"), Input("tabs", "value"))(self.render_tab)
        self.callbacks()

    

    def callbacks(self):
        """
        
        """
        print('call')
        self.app.callback(
            Output("sim_state", "data"),
            Input("pause_button", "n_clicks"),
            State("sim_state", "data")
        )(functools.partial(self.toggle_pause))
        
        self.app.callback(
            Output("tab_content", "children"),
            Input("tabs", "value")
        )(functools.partial(self.render_tab))
        
    def render_tab(self, value_tab):
        """
        Défini le contenu des différents tabs
        """
        print('tab')
        if value_tab == "tab-1":
            #TODO : mettre ces returns dans des fichiers différents
            return html.Div([
                html.H1("LIVE"),
                html.Button("Pause/Reprendre", id="pause_button", n_clicks=0),
                html.Div(id="status", children="Simulation en cours")
            ])
        elif value_tab == "tab-2":
            return html.Div([
                html.H1("AFTER"),
                dcc.Interval(id="interval", interval=1000, n_intervals=0),
                html.P("fdbfdngbvfdkh")
                
            ])
        else:
            raise ValueError
 
    def toggle_pause(self, n_clicks, store):
        """
        """
        print('store :', store)
        print('n_clicks :', n_clicks)
        self.state['Running'] = not store[0]['Running']
        self.state['n_clicks'] = store[0]['n_clicks']+1
        return [self.state]
        
        
        
    def get_infos_from_backtest(self, ):
        """
        """

    


    def start(self):
        self.app.run(debug=True)



if __name__ == "__main__":
    dashboard = Reporting()
    dashboard.start()


