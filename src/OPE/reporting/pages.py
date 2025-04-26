import os 
from dash import dcc, html
import plotly.graph_objects as go
from config import REPORTING_LOG_PATH
import dash_bootstrap_components as dbc

backtest_dirs = os.listdir(REPORTING_LOG_PATH)
def display_live():
    """

    """
    fig = go.Figure(
        go.Candlestick(
            x=[],
            open=[],
            high=[],
            low=[],
            close=[],
            name='candle_chart'
        )
    )

    

    return [
            html.H1("LIVE"),
            #dcc.Dropdown(id = 'dropdown_backtest', options=backtest_dirs, value = backtest_dirs[0]),
            dcc.RadioItems(id='data_every_items',options=[
                                            {'label': '1m', 'value': '1m'},
                                            {'label': '5m', 'value': '5m'},
                                            {'label': '15m', 'value': '15m'},
                                            {'label': '30m', 'value': '30m'},
                                            {'label': '1h', 'value': '1h'},
                                            {'label': '4h', 'value': '4h'},
                                            {'label': '1d', 'value': '1d'}],
                                            value='5m'),
            html.Button("Confirmer backtest", id='ok_backtest', n_clicks=0),
            html.Button("Pause/Reprendre", id="pause_button", n_clicks=0),
            dcc.Graph(id='candlestick_chart', figure=fig)
            ]

def display_kpi(kpi_data):
    """
    """
    
    

    def create_card(title, indicators):
        return dbc.Card(
            [
                dbc.CardHeader(title, className="text-white bg-primary"),
                dbc.CardBody(
                    [html.P(f"{k}: {v}", className="card-text") for k, v in indicators.items()]
                ),
            ],
            className="mb-4 shadow",
            style={"borderRadius": "12px", "minHeight": "200px"},
            
        )
    
    return dbc.Container(
    [
        html.H1("Reporting de stratégie de trading", className="my-4 text-center"),

        dbc.Row([
            dbc.Col(create_card("📈 Rentabilité", kpi_data['RENTABILITE']), md=4),
            dbc.Col(create_card("⚠️ Risque", kpi_data['RISQUE']), md=4),
            dbc.Col(create_card("⚖️ Efficacité", kpi_data['EFFICACITE']), md=4),
        ]),
        dbc.Row([
            dbc.Col(create_card("🧪 Robustesse", kpi_data['ROBUSTESSE']), md=6),
            dbc.Col(create_card("🔁 Stabilité", kpi_data['STABILITE']), md=6),
        ])
    ],
    fluid=True,
    id = 'container_KPI'
)

def display_graph(fig):
    """
    """
    print(fig)
    return dbc.Container(
        dcc.Graph(id='equity_chart', figure=fig)
    )