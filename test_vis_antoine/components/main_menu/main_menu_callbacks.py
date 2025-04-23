from dash import Input, Output, callback, html
from components.map.map_tab import map_tab_layout
from components.test.test_tab import test_tab_layout
# from components.utils import load_data, filter_data
# from components.plots import generate_kill_map, generate_kill_timeline
import json
import os
import pandas as pd


@callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value')
)
def render_content(tab):
    if tab == 'map':
        return map_tab_layout()
    elif tab == 'test':
        return test_tab_layout()