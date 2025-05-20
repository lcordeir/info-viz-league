import pandas as pd
import numpy as np

from os import path as pt
import os

ds_names = ["bans","gold","kills","matchinfo","monsters","structures"]
print(os.getcwd())
# Load all the datasets
bans = pd.read_csv(pt.join("data","bans.csv"))
gold = pd.read_csv(pt.join("data","gold.csv"))
kills = pd.read_csv(pt.join("data","kills.csv"))
matchinfo = pd.read_csv(pt.join("data","matchinfo.csv"))
monsters = pd.read_csv(pt.join("data","monsters.csv"))
structures = pd.read_csv(pt.join("data","structures.csv"))

# All
## IDs
### Clean mathcinfo
"""Amongst the oddities in the dataset, there were match entries with an associated address, but missing data like player names (some being '=' the others NaN).
Or missing team tags. The addresses links are to websites which are no longer kept up (domain changes and some data being archived over the years).
We drop these rows before creating the ids. Once we set the ids to other dfs we only keep the rows fitting an associated address and thus game. Automatically dropping the related rows in other dfs."""
matchinfo = matchinfo.dropna() # match_ids based on matchinfo
### Create ids
match_ids = matchinfo["Address"].reset_index()
match_ids = match_ids.rename(columns={"index":"match_id"})
### Assign ids
data_dfs = [bans,gold,kills,matchinfo,monsters,structures]
for i in range(len(data_dfs)):
    data_dfs[i]=data_dfs[i].merge(match_ids, on="Address",how="inner") # Ensure rows without association to address to match_id are dropped
    data_dfs[i].drop(columns=["Address"],inplace=True)
bans,gold,kills,matchinfo,monsters,structures = data_dfs
## Cardinality
monsters['cardinality'] = monsters.sort_values("Time").groupby("match_id").cumcount()
kills['cardinality'] = kills.sort_values("Time").groupby("match_id").cumcount()
structures['cardinality'] = structures.sort_values("Time").groupby("match_id").cumcount()
## Side
kills['Team'] = kills.loc[:,'Team'].apply(lambda x: 'RED' if x[0]=='r' else 'BLUE')
monsters['Team'] = monsters.loc[:,'Team'].apply(lambda x: 'RED' if x[0]=='r' else 'BLUE')
structures['Team'] = structures.loc[:,'Team'].apply(lambda x: 'RED' if (x[0]=='r' or x[0]=='R') else 'BLUE')

# Matchinfo
## Add bans
bans['Team'] = bans['Team'].apply(lambda x: 'red' if x[0]=='r' else 'blue')
bans = bans.rename(columns={"ban_1":"Ban1","ban_2":"Ban2","ban_3":"Ban3","ban_4":"Ban4","ban_5":"Ban5"})
bans = bans.drop_duplicates().pivot(index='match_id',columns='Team',values=["Ban1","Ban2","Ban3","Ban4","Ban5"])
bans.columns = bans.columns.map(lambda col: f"{col[1]}{col[0]}")
matchinfo = matchinfo.merge(bans,on='match_id')
## Team Tags fully capitalized
matchinfo['blueTeamTag'] = matchinfo['blueTeamTag'].str.upper()
matchinfo['redTeamTag'] = matchinfo['redTeamTag'].str.upper()
## Normalize player names (Some have varying capitalization)
player_cols = matchinfo.iloc[:,9::2].iloc[:,:10].columns
all_usernames = pd.Series(pd.unique(matchinfo[player_cols].values.ravel())).dropna()
most_common_variants = ( # Map lowercased usernames to their most common variant
    all_usernames.groupby(all_usernames.str.lower())
    .agg(lambda x: x.value_counts().idxmax())
    .to_dict())
for col in player_cols:
    matchinfo[col] = matchinfo[col].str.lower().map(most_common_variants) # Keep only most recurring variatnt of username

# Kills
## Position
kills = kills.dropna(subset=['Victim']) # On Victim, because (although unclear) victim could die from neutral entity. Assists can and may be NaN
kills = kills[kills['Killer'] != 'TooEarly'] # Special case
kills.loc[:,'x_pos'] = pd.to_numeric(kills.loc[:,'x_pos'],errors='coerce') # Convert kill positions to numbers, coerce will convert or if not possible replace with NaN
kills.loc[:,'y_pos'] = pd.to_numeric(kills.loc[:,'y_pos'],errors='coerce') # Convert kill positions to numbers, coerce will convert or if not possible replace with NaN
## Team tags
kills = kills.merge(matchinfo.reset_index()[['match_id', 'blueTeamTag', 'redTeamTag']], on='match_id', how='left') # Merge kills with team tags based on match_id
kills['Killer_Team'] = np.where(kills['Team'] == 'BLUE', kills['blueTeamTag'], kills['redTeamTag']) # Assign Killer_Team based on 'Team' column
kills['Victim_Team'] = np.where(kills['Team'] == 'BLUE', kills['redTeamTag'], kills['blueTeamTag']) # Assign Victim_Team based on 'Team' column
kills.drop(columns=['blueTeamTag', 'redTeamTag'], inplace=True)
## Player names
def extract_username(full_str, team_tag):
    if pd.isna(full_str): # Assists can be NaN. At this point no Killer/Victim/Time is NaN (verified)
        return full_str
    
    parts = full_str.split(" ")
    if len(parts) < 2:
        return full_str  # Unusual format, return as-is (team tag missing)
    if parts[0].upper() == team_tag:
        return " ".join(parts[1:]) # First part is team tag, return rest
    else:
        return full_str  # Assume already a username
cols_to_clean = ['Killer', 'Victim', 'Assist_1', 'Assist_2', 'Assist_3', 'Assist_4']
for col in cols_to_clean:
    if 'Victim' in col:
        kills[col] = kills.apply(lambda row: extract_username(row[col], row['Victim_Team']), axis=1)
    else:
        kills[col] = kills.apply(lambda row: extract_username(row[col], row['Killer_Team']), axis=1)
    kills[col] = kills[col].str.lower().map(most_common_variants) # Keep only most recurring variatnt of username


# Monsters
## Subtype
monsters = monsters.dropna()
monsters['Subtype'] = monsters.loc[:,'Type'].apply(lambda x: x.split('_')[0] if 'DRAGON' in x and '_' in x else None)
monsters['Type'] = monsters.loc[:,'Type'].apply(lambda x: 'DRAGON' if 'DRAGON' in x else x)
drake_rename = {'FIRE':'INFERNAL','EARTH':'MOUNTAIN','WATER':'OCEAN','AIR':'CLOUD'}
monsters['Subtype'] = monsters['Subtype'].apply(lambda x: drake_rename[x] if x in drake_rename.keys() else x)


# Structures
## Lane/Type
structures = structures.dropna()
structures.loc[:,'Lane'] = structures.loc[:,'Lane'].apply(lambda x: x.split('_')[0])
structures.loc[:,'Type'] = structures.loc[:,'Type'].apply(lambda x: x.split('_')[0])
structures['type_cardinality'] = structures.sort_values("Time").groupby(["match_id","Type"]).cumcount().astype(int) # Specific for Nexus Tower assignation countW
# Boolean mask where Type is "NEXUS"
nexus_mask = structures['Type'] == 'NEXUS'
# Set 'Lane' to "UPPER" or "LOWER" based on even/odd type_cardinality
structures.loc[nexus_mask, 'Lane'] = np.where(
    structures.loc[nexus_mask, 'type_cardinality'] % 2 == 0,
    'UPPER',
    'LOWER'
)


# Save csvs
bans.to_csv(pt.join("data","bans_mod.csv"))
gold.to_csv(pt.join("data","gold_mod.csv"))
kills.to_csv(pt.join("data","kills_mod.csv"))
matchinfo.to_csv(pt.join("data","matchinfo_mod.csv"))
monsters.to_csv(pt.join("data","monsters_mod.csv"))
structures.to_csv(pt.join("data","structures_mod.csv"))