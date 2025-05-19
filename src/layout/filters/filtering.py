import pandas as pd
from typing import List, Dict, Any
from os import path as pt

def get_unique_values(column: str) -> List[str]: # TODO vérifier si c'est tjs un str ou parfois un int
    """
    Get unique values from a specific column in the DataFrame.
    """
    if column in ['Year', 'Season', 'League', 'Type']:
        path = pt.join('data', 'matchinfo_mod.csv')
    elif column in ['blueTeamTag', 'redTeamTag']: # même chose qu'au dessus
        path = pt.join('data', 'matchinfo_mod.csv')
    df = pd.read_csv(path)
    return df[column].unique().tolist()

def combine_team_player_position() -> pd.DataFrame:
    """
    Creates a new dataframe where each row contains a team, player and position
    """
    df = pd.read_csv(pt.join("data","matchinfo_mod.csv"))
    
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

    return pd.DataFrame.from_records(records, columns=["Teams", "Players", "Position"])