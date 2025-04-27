from dash import Dash, dcc, html, Input, State, Output, Patch, callback
import plotly.graph_objects as go
import json

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
fig.add_shape(
    type="line",
    x0=1,  # Début de la ligne
    y0=33.7,  # Valeur y de la ligne
    x1=90,  # Fin de la ligne (peut être ajustée selon les données)
    y1=33.7,
    xref="paper",
    yref="y",
    line=dict(color="Red", width=2)
)

app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='test_figure', figure = fig),
    html.Button("Print fig data", id="test_button", n_clicks=0)
])

@app.callback(Input('test_button', 'n_clicks'),
              State('test_figure', 'figure'))
def print_figure(n_clicks, figure):
    print(figure['layout'].keys())
    #print(json.dumps(figure, indent=4))
    #print(figure['layout']['xaxis'])


app.run(debug=True)

"""
patched_figure['layout']['shapes'].append({'type':'line',
                                       'name':f'position_{id}',
                                       'x0':position_event['timestamp'],
                                       'x1': '9999-12-31T00:00:00',
                                       'xref':'x',
                                       'y0':position_event['entryprice'],
                                       'y1':position_event['entryprice'],
                                       'yref':'y',
                                       'line':{
                                           'color':'Red',
                                           'width':2
                                       }})

"""