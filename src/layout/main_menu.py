from dash import html, dcc
from layout.filters.filters_layout import filters_layout
from layout.map.map_layout import map_layout
from layout.plots.plots_layout import plots_layout

from utils import resource_path

import pandas as pd
from os import path as pt


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


# GLOBAL DATAFRAMES
MATCHINFO_DF = pd.read_csv(resource_path(pt.join('data', 'matchinfo_mod.csv')), index_col=0)
KILLS_DF = pd.read_csv(resource_path(pt.join('data', 'kills_mod.csv')))
STRUCTURES_DF =  pd.read_csv(resource_path(pt.join('data', 'structures_mod.csv')))
MONSTERS_DF =  pd.read_csv(resource_path(pt.join('data', 'monsters_mod.csv')))
GOLD_DF =  pd.read_csv(resource_path(pt.join('data', 'gold_mod.csv')))
CHAMP_IDS_DF = pd.read_csv(resource_path(pt.join('data', 'champ_ids_mod.csv')))
