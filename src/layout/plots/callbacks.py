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
        # Output("map-graph", "figure"),
        # Output("timeline-fig", "figure"),
        # Output("event-list", "children"),
        Output("kill-plot", "figure"),
        Output("heatmap-plot", "figure"),
        Output("objective-plot", "figure"),
        Output("first-drake-plot", "figure"),
        Output("timeline-monsters-plot", "figure"),
        Output("timeline-structures-plot", "figure"),
        Output("timeline-kills-plot", "figure"),
        Output("map-timeline-mplot", "figure"),
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
    
    # print("games selected:")    
    # print(match_records)
    match_ids = list(pd.DataFrame.from_records(match_records)["match_id"])
    # print(match_ids)
    # == Get filtered data
    filtered_matchinfo = MATCHINFO_DF[MATCHINFO_DF.index.isin(match_ids)]
    
    kills = KILLS_DF[KILLS_DF["match_id"].isin(match_ids)]
    # kills = kills[
    #     (kills["Time"] >= time_range[0]) &
    #     (kills["Time"] <= time_range[1]) &
    #     (kills["Team"].isin(team_filter))
    # ]

    structures = STRUCTURES_DF[STRUCTURES_DF["match_id"].isin(match_ids)]
    # structures = structures[
    #     (structures["Time"] >= time_range[0]) &
    #     (structures["Time"] <= time_range[1]) &
    #     (structures["Team"].isin(team_filter))
    # ]

    monsters = MONSTERS_DF[MONSTERS_DF["match_id"].isin(match_ids)]
    # monsters = monsters[
    #     (monsters["Time"] >= time_range[0]) &
    #     (monsters["Time"] <= time_range[1]) &
    #     (monsters["Team"].isin(team_filter))
    # ]

    return (get_kill_plot(kills),
            get_kill_heatmap(kills, heatmap_binsize=100), 
            get_objective_distribution(monsters), 
            get_first_Drake_avg(monsters), 
            get_monsters_timeline(monsters, x_size=100),
            get_structures_timeline(structures, x_size=100),
            get_kills_timeline(kills),
            get_map_timeline_mplot(kills, monsters, structures, filtered_matchinfo)
            
            )
    # if len(match_ids) == 1:
    #     return (get_kill_plot_single(kills), )
    # else:
    #     return (get_kill_plot_aggregate(kills), )
