from dash import Input, Output, State, callback, html
import pandas as pd
import plotly.graph_objects as go
from os import path as pt
import base64
import os
import json
from layout.main_menu import MATCHINFO_DF, KILLS_DF, STRUCTURES_DF, MONSTERS_DF, BANS_DF, GOLD_DF
from lol_plots import *

@callback(
    [
        Output("winrate-plot", "figure"),
        Output("objective-plot", "figure"),
        Output("first-drake-plot", "figure"),
         ],
    [
        # Input("filtered_match_info", "data"),
        Input("filter_games", "selectedRows"),
        # Input("stored_games_filtered", "selectedRows"),

     ]
)
# def update_plots(time_range, map_style, team_filter, match_records):
def update_plots(match_records):
    if match_records is None or len(match_records) == 0:
        print("no games selected")    
        return (go.Figure(), ) * 8
    

    match_ids = list(pd.DataFrame.from_records(match_records)["match_id"])

    # == Get filtered data
    filtered_matchinfo = MATCHINFO_DF[MATCHINFO_DF.index.isin(match_ids)]
    
    kills = KILLS_DF[KILLS_DF["match_id"].isin(match_ids)]

    structures = STRUCTURES_DF[STRUCTURES_DF["match_id"].isin(match_ids)]


    monsters = MONSTERS_DF[MONSTERS_DF["match_id"].isin(match_ids)]

    if len(match_records) == 1:
        blue_team = filtered_matchinfo["blueTeamTag"].values[0]
        red_team = filtered_matchinfo["redTeamTag"].values[0]

        cols = MATCHINFO_DF[['blueTeamTag', 'redTeamTag']].to_numpy()
        mask = ( (cols == blue_team).any(axis=1) ) & ( (cols == red_team).any(axis=1) )
        filtered_df = MATCHINFO_DF[mask]
        scores = get_team_scores(filtered_df, blue_team, red_team)
        wr_fig = get_2teams_winrate(blue_team, red_team, filtered_matchinfo, scores)
    else: wr_fig = get_win_rate(filtered_matchinfo)


    return (wr_fig,
            get_objective_distribution(monsters), 
            get_first_Drake_avg(monsters), 
            )