from dash import html, dcc
from layout.filters.filters_layout import filters_layout
from layout.map.map_layout import map_layout
from layout.plots.plots_layout import plots_layout

def create_layout():
    return html.Div([
        html.Div(
            id="filters", 
            children=filters_layout(), 
            style={
                'width': '100%',
                'textAlign': 'center', 
                # TODO les enfants ne garde pas le même style que cette div (pas au centre) voir si possible de le faire
            }
        ),
        html.Div([
            html.Div(id="map", 
                     children=map_layout(),
                     style={
                        'width': '50%',
            }),
            html.Div(id="plots", 
                     children=plots_layout(),
                     style={
                        'width': '50%',
            }),
        ], style={
            'display': 'flex'
        }),
        dcc.Store(id="filtered_match_info")
    ])