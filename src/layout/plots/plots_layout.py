from dash import html, dcc


def plots_layout() -> list:
    return [
        html.Div([
            html.Div(dcc.Graph(id="winrate-plot", style={"width": "100%"}, config={'displayModeBar': False}), style={"flex": "1", "minWidth": "45%"}),
            html.Div(dcc.Graph(id="champrates-plot", style={"width": "100%"}, config={}), style={"flex": "1", "minWidth": "45%"}),
            html.Div(dcc.Graph(id="objective-plot", style={"width": "100%"}, config={}), style={"flex": "1", "minWidth": "45%"}),
            html.Div(dcc.Graph(id="first-drake-plot", style={"width": "100%"}, config={'staticPlot': True}), style={"flex": "1", "minWidth": "45%"}),
            html.Div(dcc.Graph(id="top-kills-plot", style={"width": "100%"}, config={'displayModeBar': False, 'staticPlot': True}), style={"flex": "1", "minWidth": "45%"}),
            html.Div(dcc.Graph(id="gold-plot", style={"width": "100%"}, config={'displayModeBar': False}), style={"flex": "1", "minWidth": "45%"})
        ], style={
            "display": "flex",
            "flexWrap": "wrap",
            "gap": "20px",
            "justifyContent": "space-between",
            "maxWidth": "100vw",
            "padding": "10px",
            "boxSizing": "border-box",
            # Optional scroll control:
            "overflowY": "auto",
            "overflowX": "hidden"
        })
    ]
