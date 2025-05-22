from dash import Input, Output, State, callback, html
import pandas as pd
import plotly.graph_objects as go
from os import path as pt
import base64
import os
import json
from layout.main_menu import MATCHINFO_DF, KILLS_DF, STRUCTURES_DF, MONSTERS_DF, GOLD_DF, CHAMP_IDS_DF
from lol_plots import *

@callback(
    [
        Output("winrate-plot", "figure"),
        Output("champrates-plot", "figure"),
        Output("objective-plot", "figure"),
        Output("first-drake-plot", "figure"),
        Output("top-kills-plot", "figure"),
        Output("gold-plot", "figure"),

         ],
    [
        Input("filter_games", "selectedRows"),
        # Input("stored_games_filtered", "selectedRows"),

     ]
)
# def update_plots(time_range, map_style, team_filter, match_records):
def update_plots(match_records):
    if match_records is None or len(match_records) == 0:
        print("no games selected")    
        return (go.Figure(), ) * 6
    
    n_games = len(match_records)

    match_ids = list(pd.DataFrame.from_records(match_records)["match_id"])

    # == Get filtered data
    filtered_matchinfo = MATCHINFO_DF[MATCHINFO_DF.index.isin(match_ids)]
    kills = KILLS_DF[KILLS_DF["match_id"].isin(match_ids)]
    structures = STRUCTURES_DF[STRUCTURES_DF["match_id"].isin(match_ids)]
    gold = GOLD_DF[GOLD_DF["match_id"].isin(match_ids)]
    monsters = MONSTERS_DF[MONSTERS_DF["match_id"].isin(match_ids)]

    if n_games == 1:
        # Win rates single game
        blue_team = filtered_matchinfo["blueTeamTag"].values[0]
        red_team = filtered_matchinfo["redTeamTag"].values[0]

        cols = MATCHINFO_DF[['blueTeamTag', 'redTeamTag']].to_numpy()
        mask = ( (cols == blue_team).any(axis=1) ) & ( (cols == red_team).any(axis=1) )
        filtered_df = MATCHINFO_DF[mask]
        scores = get_team_scores(filtered_df, blue_team, red_team)
        wr_fig = get_2teams_winrate(blue_team, red_team, filtered_matchinfo, scores)

        # Champ rates single game
        pick_rate, win_rate, ban_rate = get_champ_rates(filtered_matchinfo)
        champ_plot = get_champ_rates_plots(pick_rate, win_rate, ban_rate, CHAMP_IDS_DF)
        #champ_plot = get_champs_posbans(filtered_matchinfo, CHAMP_IDS_DF)
    else: 
        wr_fig = get_win_rate(filtered_matchinfo)
        pick_rate, win_rate, ban_rate = get_champ_rates(filtered_matchinfo)
        champ_plot = get_champ_rates_plots(pick_rate, win_rate, ban_rate, CHAMP_IDS_DF)

    # Top 3 plots (two plots in one)
    top_killers = get_top_killers(kills)
    top_deaths = get_top_deaths(kills)
    top_fig = podium_dual_figure(top_killers, "Top 3 Killers", top_deaths, "Top 3 Deaths")

    return (wr_fig,
            champ_plot,
            get_objective_distribution(monsters), 
            get_first_Drake_avg(monsters), 
            top_fig,
            plot_gold_over_time(gold)
            )