
# TODO les callbacks vont appeler des fonctions qui vont ouptut le df avec des filtres, pas besoin d'avoir le df ici
# TODO p-ê store les df filtrés dans des dcc.Store (unn dcc.Store par type de filtre?)
# TODO => plutot tout filtrer sur match_infos (p-ê dans un dcc.Store) et ensuite faire une intersection avec les autres df
import pandas as pd
from typing import List, Dict, Any
from os import path as pt
from dash import Dash, html, dcc, dash_table, Input, Output, State, callback, no_update
import plotly.express as px

@callback(
    Output('filter_year', 'value'),
    Output('filter_season', 'value'),
    Output('filter_league', 'value'),
    Output('filter_type', 'value'),
    Input('filters_metadata_reset', "n_clicks"),
    State('filter_year', 'options'),
    State('filter_season', 'options'),
    State('filter_league', 'options'),
    State('filter_type', 'options'),
    prevent_initial_call=True
)
def reset_metadata_filters(n_clicks, filter_year_options, filter_season_options, filter_league_options, filter_type_options):
    return filter_year_options, filter_season_options, filter_league_options, filter_type_options

@callback(
    Output("stored_metadata_filtered", 'data'),
    Output("metadata_filtered_columns", 'data'),
    Input('filter_year', 'value'),
    Input('filter_season', 'value'),
    Input('filter_league', 'value'),
    Input('filter_type', 'value'),
)
def store_metadata_df(filter_year, filter_season, filter_league, filter_type):
    df = pd.read_csv(pt.join("data","matchinfo_mod.csv"))

    df = df[df['Season'].isin(filter_season)]
    df = df[df['Year'].isin(filter_year)]
    df = df[df['League'].isin(filter_league)]
    df = df[df['Type'].isin(filter_type)]

    return df.to_records(index=False), df.columns


@callback(
    Output("filter_team_player_position", "rowData"),
    Input("stored_metadata_filtered", 'data'),
    State("metadata_filtered_columns", 'data'),
    prevent_initial_call=True
)
def update_team_player_position(intermediate_records, cols):
    """
    Creates a new dataframe where each row contains a team, player and position
    """
    df = pd.DataFrame.from_records(intermediate_records, columns=cols)
    
    added_players = set()
    records = []
    for index, row in df.iterrows():
        match_id = row['match_id']

        blue_team = row['blueTeamTag']
        red_team = row['redTeamTag']

        blue_top = row['blueTop']
        blue_jungle = row['blueJungle']
        blue_middle = row['blueMiddle']
        blue_adc = row['blueADC']
        blue_support = row['blueSupport']

        if (blue_team, blue_top, "Top") not in added_players:
            records.append((match_id, blue_team, blue_top, 'Top'))
            added_players.add((blue_team, blue_top, "Top"))
        if (blue_team, blue_jungle, "Jungle") not in added_players:
            records.append((match_id, blue_team, blue_jungle, 'Jungle'))
            added_players.add((blue_team, blue_jungle, "Jungle"))
        if (blue_team, blue_middle, "Middle") not in added_players:
            records.append((match_id, blue_team, blue_middle, 'Middle'))
            added_players.add((blue_team, blue_middle, "Middle"))
        if (blue_team, blue_adc, "ADC") not in added_players:
            records.append((match_id, blue_team, blue_adc, 'ADC'))
            added_players.add((blue_team, blue_adc, "ADC"))
        if (blue_team, blue_support, "Support") not in added_players:
            records.append((match_id, blue_team, blue_support, 'Support'))
            added_players.add((blue_team, blue_support, "Support"))

        red_top = row['redTop']
        red_jungle = row['redJungle']
        red_middle = row['redMiddle']
        red_adc = row['redADC']
        red_support = row['redSupport']

        if (red_team, red_top, "Top") not in added_players:
            records.append((match_id, red_team, red_top, 'Top'))
            added_players.add((red_team, red_top, "Top"))
        if (red_team, red_jungle, "Jungle") not in added_players:
            records.append((match_id, red_team, red_jungle, 'Jungle'))
            added_players.add((red_team, red_jungle, "Jungle"))
        if (red_team, red_middle, "Middle") not in added_players:
            records.append((match_id, red_team, red_middle, 'Middle'))
            added_players.add((red_team, red_middle, "Middle"))
        if (red_team, red_adc, "ADC") not in added_players:
            records.append((match_id, red_team, red_adc, 'ADC'))
            added_players.add((red_team, red_adc, "ADC"))
        if (red_team, red_support, "Support") not in added_players:
            records.append((match_id, red_team, red_support, 'Support'))
            added_players.add((red_team, red_support, "Support"))
    
    df = pd.DataFrame.from_records(records, columns=["match_id", "Teams", "Players", "Position"])
    return df.to_dict("records")
    

@callback(
    Output("stored_team_player_position_filtered", 'data'),
    Output("team_player_position_filtered_columns", 'data'),
    Input("filter_team_player_position", "virtualRowData"),
    Input("stored_metadata_filtered", 'data'),
    State("metadata_filtered_columns", 'data'),
    prevent_initial_call=True
)
def store_team_player_position_df(filtered_rows, intermediate_records, cols):
    metadata_df = pd.DataFrame.from_records(intermediate_records, columns=cols)
    team_player_position_df = pd.DataFrame.from_dict(filtered_rows)

    if len(team_player_position_df.index) == 0:
        return intermediate_records, cols
    
    # match_ids = team_player_position_df["match_id"].unique()
    # filtered_metadata_df = metadata_df[metadata_df['match_id'].isin(match_ids)]
    # print(len(match_ids), len(filtered_metadata_df.index)) # TODO ne garde pas tous les match_ids, p-ê moyen de le faire fonctionner

    all_teams = team_player_position_df["Teams"].unique()
    all_players = team_player_position_df["Players"].unique()
    # all_positions = team_player_position_df["Position"].unique() # TODO le filtre sur les positions ne sert à rien, comment filtrer sur les positions dans le plots?

    filtered_metadata_df = metadata_df[metadata_df["blueTeamTag"].isin(all_teams) | metadata_df["redTeamTag"].isin(all_teams)]
    filtered_metadata_df = filtered_metadata_df[filtered_metadata_df["blueTop"].isin(all_players) |
                                                filtered_metadata_df["blueJungle"].isin(all_players) |
                                                filtered_metadata_df["blueMiddle"].isin(all_players) |
                                                filtered_metadata_df["blueADC"].isin(all_players) |
                                                filtered_metadata_df["blueSupport"].isin(all_players) |
                                                filtered_metadata_df["redTop"].isin(all_players) |
                                                filtered_metadata_df["redJungle"].isin(all_players) |
                                                filtered_metadata_df["redMiddle"].isin(all_players) |
                                                filtered_metadata_df["redADC"].isin(all_players) |
                                                filtered_metadata_df["redSupport"].isin(all_players)]    

    return filtered_metadata_df.to_records(index=False), filtered_metadata_df.columns

@callback(
    Output("filter_games", "rowData"),
    Input("stored_team_player_position_filtered", 'data'),
    State("team_player_position_filtered_columns", 'data'),
    prevent_initial_call=True
)
def get_games(team_player_position_records, cols):
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
    if len(games_rows) > 0:
        df = pd.DataFrame.from_dict(games_rows)
        return df.to_records(index=False), df.columns
    else:
        # print("No games selected")
        return [], []