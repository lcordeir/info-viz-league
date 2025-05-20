import pandas as pd
from typing import List, Dict, Any
from os import path as pt

def get_unique_values(column: str) -> List[str]: # TODO vérifier si c'est tjs un str ou parfois un int
    """
    Get unique values from a specific column in the matchinfo file.
    """
    df = pd.read_csv(pt.join('data', 'matchinfo_mod.csv'))
    return df[column].unique().tolist()
