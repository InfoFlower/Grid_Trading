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

    def __init__(self, backtest):
        self.app = Dash(__name__)
        self.state = self.state_init
        self.backtest = backtest
        # self.running = True
        # self.speed = 1.0
        # self.current_data = []
        self.app.layout = html.Div([
            dcc.Store(id='store_current_data', data = []),#Définir data = [self.backtest.current_data]
            dcc.Store(id='sim_state', data=[self.state]),
            #dcc.Interval(id='interval_get_data', interval=1, n_intervals=0),
            #dcc.Interval(id='interval_update_chart', interval= ),
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

        # self.app.callback(
        #     Output("store_current_data", "data"),
        #     Input("interval_get_data", "n_intervals")
        # )(functools.partial(self.get_backtest_data))

        self.app.callback(
            Output("status", "children"),
            Input("store_current_data", "data")
        )(functools.partial(self.get_backtest_data))
        
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
                html.Div(id="status", children="Simulation en cours") #str(self.backtest.current_data)
            ])
        elif value_tab == "tab-2":
            return html.Div([
                html.H1("AFTER"),
                html.P("fdbfdngbvfdkh")   
            ])
        else:
            raise ValueError
    
    def get_backtest_data(self, n_intervals):
        """
        """
        current_data = 0
        if self.backtest.current_data is not None:
            current_data = self.backtest.current_data
        else :
            current_data = 0
            print('lol')
        return current_data
 
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


