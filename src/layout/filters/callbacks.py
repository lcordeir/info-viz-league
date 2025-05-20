
# TODO les callbacks vont appeler des fonctions qui vont ouptut le df avec des filtres, pas besoin d'avoir le df ici
# TODO p-ê store les df filtrés dans des dcc.Store (unn dcc.Store par type de filtre?)
# TODO => plutot tout filtrer sur match_infos (p-ê dans un dcc.Store) et ensuite faire une intersection avec les autres df
import pandas as pd
from typing import List, Dict, Any
from os import path as pt
from dash import Dash, html, dcc, dash_table, Input, Output, State, callback, no_update
import plotly.express as px

@callback(
    Output("stored_intermediate_match_info", 'data'),
    Output("match_info_columns", 'data'),
    Input('filter_year', 'value'),
    Input('filter_season', 'value'),
    Input('filter_league', 'value'),
    Input('filter_type', 'value'),
)
def store_intermediate_df(filter_year, filter_season, filter_league, filter_type):
    df = pd.read_csv(pt.join("data","matchinfo_mod.csv"))

    df = df[df['Season'].isin(filter_season)]
    df = df[df['Year'].isin(filter_year)]
    df = df[df['League'].isin(filter_league)]
    df = df[df['Type'].isin(filter_type)]

    return df.to_records(index=False), df.columns

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
)
def reset_metadata_filters(n_clicks, filter_year_options, filter_season_options, filter_league_options, filter_type_options):
    return filter_year_options, filter_season_options, filter_league_options, filter_type_options


@callback(
    Output("filter_team_player_position", "rowData"),
    Input("stored_intermediate_match_info", 'data'),
    State("match_info_columns", 'data')
)
def combine_team_player_position(intermediate_records, cols) -> pd.DataFrame:
    """
    Creates a new dataframe where each row contains a team, player and position
    """
    df = pd.DataFrame.from_records(intermediate_records, columns=cols)
    
    added_players = set()
    records = [] # TODO si ça fonctionne de le mettre en df, je peux juste return les records
    for index, row in df.iterrows():
        blue_team = row['blueTeamTag']
        red_team = row['redTeamTag']

        blue_top = row['blueTop']
        blue_jungle = row['blueJungle']
        blue_middle = row['blueMiddle']
        blue_adc = row['blueADC']
        blue_support = row['blueSupport']

        if (blue_team, blue_top, "Top") not in added_players:
            records.append((blue_team, blue_top, 'Top'))
            added_players.add((blue_team, blue_top, "Top"))
        if (blue_team, blue_jungle, "Jungle") not in added_players:
            records.append((blue_team, blue_jungle, 'Jungle'))
            added_players.add((blue_team, blue_jungle, "Jungle"))
        if (blue_team, blue_middle, "Middle") not in added_players:
            records.append((blue_team, blue_middle, 'Middle'))
            added_players.add((blue_team, blue_middle, "Middle"))
        if (blue_team, blue_adc, "ADC") not in added_players:
            records.append((blue_team, blue_adc, 'ADC'))
            added_players.add((blue_team, blue_adc, "ADC"))
        if (blue_team, blue_support, "Support") not in added_players:
            records.append((blue_team, blue_support, 'Support'))
            added_players.add((blue_team, blue_support, "Support"))

        red_top = row['redTop']
        red_jungle = row['redJungle']
        red_middle = row['redMiddle']
        red_adc = row['redADC']
        red_support = row['redSupport']

        if (red_team, red_top, "Top") not in added_players:
            records.append((red_team, red_top, 'Top'))
            added_players.add((red_team, red_top, "Top"))
        if (red_team, red_jungle, "Jungle") not in added_players:
            records.append((red_team, red_jungle, 'Jungle'))
            added_players.add((red_team, red_jungle, "Jungle"))
        if (red_team, red_middle, "Middle") not in added_players:
            records.append((red_team, red_middle, 'Middle'))
            added_players.add((red_team, red_middle, "Middle"))
        if (red_team, red_adc, "ADC") not in added_players:
            records.append((red_team, red_adc, 'ADC'))
            added_players.add((red_team, red_adc, "ADC"))
        if (red_team, red_support, "Support") not in added_players:
            records.append((red_team, red_support, 'Support'))
            added_players.add((red_team, red_support, "Support"))
    
    df = pd.DataFrame.from_records(records, columns=["Teams", "Players", "Position"])
    return df.to_dict("records")

@callback(
    Output("filter_games", "rowData"),
    # Output("filter_games", "selectedRows"),
    Input("stored_intermediate_match_info", 'data'),
    State("match_info_columns", 'data')
)
def get_games(intermediate_records, cols):
    df = pd.DataFrame.from_records(intermediate_records, columns=cols)
    # TODO rajouter le gold et le nombre de kills dans match_info pour faire comme ce que Loïc à envoyer
    df = df[["match_id", "Year", "League", "Season", "Type", "bResult", "blueTeamTag", "redTeamTag", "rResult", "gamelength"]]
    return df.to_dict("records")# , df.to_dict("records")

@callback(
    Output("stored_filtetered_match_info", "data"),
    Input("filter_games", "selectedRows"),
    Input("filter_team_player_position", "selectedRows")
)
def store_filtered_match_info(games_rows, teams_rows):
    print(type(games_rows))
    if isinstance(games_rows, list):
        print(len(games_rows))

    return