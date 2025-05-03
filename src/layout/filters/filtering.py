import pandas as pd
from typing import List, Dict, Any
from os import path as pt

def get_unique_values(column: str) -> List[str]:
    """
    Get unique values from a specific column in the DataFrame.
    """
    if column in ['Year', 'Season', 'League', 'Type']:
        path = pt.join('data', 'matchinfo_mod.csv')
    elif column in ['Team', 'Player', 'Position']: # TODO p-ê pas correct
        path = pt.join('data', 'players_mod.csv')
    df = pd.read_csv(path)
    return df[column].unique().tolist()