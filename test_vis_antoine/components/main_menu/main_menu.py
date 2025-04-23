from dash import html, dcc
from components.map.map_tab import map_tab_layout

def create_layout():
    return html.Div([
        dcc.Tabs(id="tabs", value="map", style={"height": "50px", "overflowY": "auto"}, children=[
            dcc.Tab(label="Map", value="map"),
            dcc.Tab(label="Test", value="test"),
        ]),
        html.Div(id="tab-content")
    ],
                    
    style={"height": "20px"})
