from dash import Input, Output, callback, html
import json
import os
import pandas as pd

@callback(
    Output("year_map_filter", "options"),
    Input()
)
# TODO J'essaie d'avoir les années qui existent dans le dataset comme options pour le radioitem mais je ne sais pas comment faire
