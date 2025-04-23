# components/layout.py
from dash import html, dcc
from components.kills_tab import kills_tab_layout  # 👈 no circular import now

def create_layout():
    return html.Div([
        dcc.Tabs(id="tabs", value="kills", style={"height": "50px", "overflowY": "auto"}, children=[
            dcc.Tab(label="Kills", value="kills"),
            dcc.Tab(label="Gold", value="gold"),
            dcc.Tab(label="Structures", value="structures"),
            dcc.Tab(label="Monsters", value="monsters"),
        ]),
        html.Div(id="tab-content", children=kills_tab_layout())  # default

    ],
                    
    style={"height": "20px"})
