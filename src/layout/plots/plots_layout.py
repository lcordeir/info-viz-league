from dash import html, dcc

# def plots_layout() -> list:
#     return [
#         html.Div([
#             html.Div(dcc.Graph(id="kill-plot", style={"width": "100%"}), style={"flex": "1"}),
#             html.Div(dcc.Graph(id="heatmap-plot", style={"width": "100%"}), style={"flex": "1"})
#         ], style={
#             "display": "flex",
#             "flexDirection": "row",  # Two columns
#             "gap": "20px",
#             "width": "100%"
#         })
#     ]

# def plots_layout() -> list:
#     return [
#         html.Div([
#             html.Div(dcc.Graph(id="kill-plot", style={"width": "100%", "height": "100%"}), style={"flex": "1"}),
#             html.Div(dcc.Graph(id="heatmap-plot", style={"width": "100%", "height": "100%"}), style={"flex": "1"}),
#             html.Div(dcc.Graph(id="objective-plot", style={"width": "100%", "height": "100%"}), style={"flex": "1"}),
#             html.Div(dcc.Graph(id="first-drake-plot", style={"width": "100%", "height": "100%"}), style={"flex": "1"}),
#             html.Div(dcc.Graph(id="timeline-monsters-plot", style={"width": "100%", "height": "100%"}), style={"flex": "1"}),
#             html.Div(dcc.Graph(id="timeline-structures-plot", style={"width": "100%", "height": "100%"}), style={"flex": "1"}),
#             html.Div(dcc.Graph(id="timeline-kills-plot", style={"width": "100%", "height": "100%"}), style={"flex": "1"}),
#         ], style={
#             "display": "flex",
#             "flexDirection": "row",
#             "gap": "20px",
#             "maxWidth": "100vw",     # limit width to viewport width
#             "maxHeight": "90vh",     # limit height to 90% of viewport height
#             "overflow": "auto",      # scrollbars if needed
#             "padding": "10px",
#             "boxSizing": "border-box"
#         })
#     ]

def plots_layout() -> list:
    return [
        html.Div([
            html.Div(dcc.Graph(id="winrate-plot", style={"width": "100%", "height": "100%"},config={'displayModeBar': False,}), style={"flex": "1", "minWidth": "45%"}),
            html.Div(dcc.Graph(id="heatmap-plot", style={"width": "100%", "height": "100%"},config={'displayModeBar': False, 'staticPlot': True }), style={"flex": "1", "minWidth": "45%"}), ###
            html.Div(dcc.Graph(id="objective-plot", style={"width": "100%", "height": "100%"},config={}), style={"flex": "1", "minWidth": "45%"}),
            html.Div(dcc.Graph(id="first-drake-plot", style={"width": "100%", "height": "100%"},config={'staticPlot': True }), style={"flex": "1", "minWidth": "45%"}),
            html.Div(dcc.Graph(id="top-kills-plot", style={"width": "100%", "height": "100%"},config={'displayModeBar': False, 'staticPlot': True }), style={"flex": "1", "minWidth": "45%"}), ###
            html.Div(dcc.Graph(id="top-deaths-plot", style={"width": "100%", "height": "100%"},config={'displayModeBar': False}), style={"flex": "1", "minWidth": "45%"}), ###
            html.Div(dcc.Graph(id="timeline-kills-plot", style={"width": "100%", "height": "100%"},config={'displayModeBar': False, 'staticPlot': True }), style={"flex": "1", "minWidth": "45%"}), ###
            html.Div(dcc.Graph(id="map-timeline-mplot", style={"width": "100%", "height": "100%"},config={'displayModeBar': False, 'staticPlot': True }), style={"flex": "1", "minWidth": "45%"}), ###
        ], style={
            "display": "flex",
            "flexWrap": "wrap",
            "gap": "20px",
            "justifyContent": "space-between",
            "maxWidth": "100vw",
            "maxHeight": "90vh",
            "overflowY": "auto",
            "padding": "10px",
            "boxSizing": "border-box"
        })
    ]
