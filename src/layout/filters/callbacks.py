import pandas as pd
from typing import List, Dict, Any
from os import path as pt
from dash import Dash, html, dcc, dash_table, Input, Output, State, callback, no_update
import plotly.express as px

# @callback(
#     Output('filter_year', 'value'),
#     Output('filter_season', 'value'),
#     Output('filter_league', 'value'),
#     Output('filter_type', 'value'),
#     Input('filters_metadata_reset', "n_clicks"),
#     State('filter_year', 'options'),
#     State('filter_season', 'options'),
#     State('filter_league', 'options'),
#     State('filter_type', 'options'),
#     prevent_initial_call=True
# )
# def reset_metadata_filters(n_clicks, filter_year_options, filter_season_options, filter_league_options, filter_type_options):
#     return filter_year_options, filter_season_options, filter_league_options, filter_type_options

def get_metadata_df():
    """
    Returns the match_info dataframe
    """
    df = pd.read_csv(pt.join("data","matchinfo_mod.csv"))
    return df.to_dict("records")


@callback(
    Output("stored_metadata_filtered", 'data'),
    Output("metadata_filtered_columns", 'data'),
    Input("filter_metadata", "virtualRowData"),
    prevent_initial_call=True
)
def store_metadata_df(filtered_rows):
    if len(filtered_rows) == 0:
        return no_update, no_update
    metadata_df = pd.DataFrame.from_dict(filtered_rows)
    return metadata_df.to_records(index=False), metadata_df.columns


@callback(
    Output("filter_team_player_position", "rowData"),
    Output("stored_match_ids", 'data'),
    Input("stored_metadata_filtered", 'data'),
    State("metadata_filtered_columns", 'data'),
    prevent_initial_call=True
)
def update_team_player_position(intermediate_records, cols):
    """
    Creates a new dataframe where each row contains a team, player and position
    """
    if len(intermediate_records) == 0:
        return no_update, no_update
    df = pd.DataFrame.from_records(intermediate_records, columns=cols)
    
    match_id_dict = dict()
    for index, row in df.iterrows():
        match_id = row['match_id']

        blue_team = row['blueTeamTag']
        red_team = row['redTeamTag']

        blue_top = row['blueTop']
        blue_jungle = row['blueJungle']
        blue_middle = row['blueMiddle']
        blue_adc = row['blueADC']
        blue_support = row['blueSupport']

        if (blue_team, blue_top, "Top") not in match_id_dict:
            match_id_dict[(blue_team, blue_top, "Top")] = {match_id}
        else:
            match_id_dict[(blue_team, blue_top, "Top")].add(match_id)
        if (blue_team, blue_jungle, "Jungle") not in match_id_dict:
            match_id_dict[(blue_team, blue_jungle, "Jungle")] = {match_id}
        else:
            match_id_dict[(blue_team, blue_jungle, "Jungle")].add(match_id)
        if (blue_team, blue_middle, "Middle") not in match_id_dict:
            match_id_dict[(blue_team, blue_middle, "Middle")] = {match_id}
        else:
            match_id_dict[(blue_team, blue_middle, "Middle")].add(match_id)
        if (blue_team, blue_adc, "ADC") not in match_id_dict:
            match_id_dict[(blue_team, blue_adc, "ADC")] = {match_id}
        else:
            match_id_dict[(blue_team, blue_adc, "ADC")].add(match_id)
        if (blue_team, blue_support, "Support") not in match_id_dict:
            match_id_dict[(blue_team, blue_support, "Support")] = {match_id}
        else:
            match_id_dict[(blue_team, blue_support, "Support")].add(match_id)

        red_top = row['redTop']
        red_jungle = row['redJungle']
        red_middle = row['redMiddle']
        red_adc = row['redADC']
        red_support = row['redSupport']
        
        if (red_team, red_top, "Top") not in match_id_dict:
            match_id_dict[(red_team, red_top, "Top")] = {match_id}
        else:
            match_id_dict[(red_team, red_top, "Top")].add(match_id)
        if (red_team, red_jungle, "Jungle") not in match_id_dict:
            match_id_dict[(red_team, red_jungle, "Jungle")] = {match_id}
        else:
            match_id_dict[(red_team, red_jungle, "Jungle")].add(match_id)
        if (red_team, red_middle, "Middle") not in match_id_dict:
            match_id_dict[(red_team, red_middle, "Middle")] = {match_id}
        else:
            match_id_dict[(red_team, red_middle, "Middle")].add(match_id)
        if (red_team, red_adc, "ADC") not in match_id_dict:
            match_id_dict[(red_team, red_adc, "ADC")] = {match_id}
        else:
            match_id_dict[(red_team, red_adc, "ADC")].add(match_id)
        if (red_team, red_support, "Support") not in match_id_dict:
            match_id_dict[(red_team, red_support, "Support")] = {match_id}
        else:
            match_id_dict[(red_team, red_support, "Support")].add(match_id)
        
    records = list(match_id_dict.keys())
    df = pd.DataFrame.from_records(records, columns=["Teams", "Players", "Position"])

    match_id_list = []
    for item in match_id_dict.items():
        match_id_list.append((item[0], tuple(item[1])))
    match_id_tuple = tuple(match_id_list)

    return df.to_dict("records"), match_id_tuple


@callback(
    Output("stored_team_player_position_filtered", 'data'),
    Output("team_player_position_filtered_columns", 'data'),
    Input("filter_team_player_position", "virtualRowData"),
    State("stored_metadata_filtered", 'data'),
    State("metadata_filtered_columns", 'data'),
    State("stored_match_ids", "data"),
    prevent_initial_call=True
)
def store_team_player_position_df(filtered_rows, intermediate_records, cols, match_id_list):
    if len(filtered_rows) == 0:
        return no_update, no_update
    if len(intermediate_records) == 0:
        return no_update, no_update
    
    team_player_position_df = pd.DataFrame.from_dict(filtered_rows)
    metadata_df = pd.DataFrame.from_records(intermediate_records, columns=cols)
    
    match_id_dict = dict()
    for item in match_id_list:
        match_id_dict[tuple(item[0])] = tuple(item[1])

    match_ids = [] # list of match_ids that appear in the filtered team_player_position_df
    for index, row in team_player_position_df.iterrows():
        key = (row['Teams'], row['Players'], row['Position'])
        if key in match_id_dict:
            match_ids.extend(match_id_dict[key])
    match_ids = list(set(match_ids))
    print("match_id" ,len(match_ids))
    
    filtered_metadata_df = metadata_df[metadata_df['match_id'].isin(match_ids)]

    # all_positions = team_player_position_df["Position"].unique() # TODO le filtre sur les positions ne sert à rien, comment filtrer sur les positions dans le plots? 
    return filtered_metadata_df.to_records(index=False), filtered_metadata_df.columns

@callback(
    Output("filter_games", "rowData"),
    Input("stored_team_player_position_filtered", 'data'),
    State("team_player_position_filtered_columns", 'data'),
    prevent_initial_call=True
)
def get_games(team_player_position_records, cols):
    if len(team_player_position_records) == 0:
        return no_update
    df = pd.DataFrame.from_records(team_player_position_records, columns=cols)
    # TODO rajouter le gold et le nombre de kills dans match_info pour faire comme ce que Loïc à envoyer
    # df = df[["match_id", "Year", "League", "Season", "Type", "bResult", "blueTeamTag", "redTeamTag", "rResult", "gamelength"]]
    return df.to_dict("records")

@callback(
    Output("stored_games_filtered", "data"),
    Output("games_filtered_columns", "data"),
    Input("filter_games", "selectedRows"),
    prevent_initial_call=True
)
def store_filtered_match_info(games_rows):
    print(len(games_rows))
    if len(games_rows) > 0:
        df = pd.DataFrame.from_dict(games_rows)
        return df.to_records(index=False), df.columns
    else:
        # print("No games selected")
        return no_update, no_update