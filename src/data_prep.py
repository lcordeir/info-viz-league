import pandas as pd
import numpy as np

from os import path as pt
import os

REDUCE = True

ds_names = ["bans","gold","kills","matchinfo","monsters","structures"]
print(os.getcwd())
# Load all the datasets
print("Reading csv files")
bans = pd.read_csv(pt.join("data","bans.csv"))
gold = pd.read_csv(pt.join("data","gold.csv"))
kills = pd.read_csv(pt.join("data","kills.csv"))
matchinfo = pd.read_csv(pt.join("data","matchinfo.csv"))
monsters = pd.read_csv(pt.join("data","monsters.csv"))
structures = pd.read_csv(pt.join("data","structures.csv"))
champ_ids = pd.read_csv(pt.join("data","champ_ids.csv"))

# All
## IDs
### Clean matchinfo
"""Amongst the oddities in the dataset, there were match entries with an associated address, but missing data like player names (some being '=' the others NaN).
Or missing team tags. The addresses links are to websites which are no longer kept up (domain changes and some data being archived over the years).
We drop these rows before creating the ids. Once we set the ids to other dfs we only keep the rows fitting an associated address and thus game. Automatically dropping the related rows in other dfs."""
matchinfo = matchinfo.dropna() # match_ids based on matchinfo
### Create ids
print("Creating match ids")
match_ids = matchinfo["Address"].reset_index()
match_ids = match_ids.rename(columns={"index":"match_id"})
### Assign ids
data_dfs = [bans,gold,kills,matchinfo,monsters,structures]
for i in range(len(data_dfs)):
    data_dfs[i]=data_dfs[i].merge(match_ids, on="Address",how="inner") # Ensure rows without association to address to match_id are dropped
    data_dfs[i].drop(columns=["Address"],inplace=True)
bans,gold,kills,matchinfo,monsters,structures = data_dfs
## Cardinality
print("Creating Cardinality")
monsters.loc[:,'cardinality'] = monsters.sort_values("Time").groupby("match_id").cumcount()
kills.loc[:,'cardinality'] = kills.sort_values("Time").groupby("match_id").cumcount()
structures.loc[:,'cardinality'] = structures.sort_values("Time").groupby("match_id").cumcount()
## Side
print("Cleaning 'Team'")
kills.loc[:,'Team'] = kills.loc[:,'Team'].apply(lambda x: 'RED' if x[0]=='r' else 'BLUE')
monsters.loc[:,'Team'] = monsters.loc[:,'Team'].apply(lambda x: 'RED' if x[0]=='r' else 'BLUE')
structures.loc[:,'Team'] = structures.loc[:,'Team'].apply(lambda x: 'RED' if (x[0]=='r' or x[0]=='R') else 'BLUE')

# Matchinfo
## Add bans
print("Adding bans to matchinfo")
bans.loc[:,'Team'] = bans.loc[:,'Team'].apply(lambda x: 'red' if x[0]=='r' else 'blue')
bans = bans.rename(columns={"ban_1":"Ban1","ban_2":"Ban2","ban_3":"Ban3","ban_4":"Ban4","ban_5":"Ban5"})
bans = bans.drop_duplicates().pivot(index='match_id',columns='Team',values=["Ban1","Ban2","Ban3","Ban4","Ban5"])
bans.columns = bans.columns.map(lambda col: f"{col[1]}{col[0]}")
matchinfo = matchinfo.merge(bans,on='match_id')
## Team Tags fully capitalized
matchinfo.loc[:,'blueTeamTag'] = matchinfo['blueTeamTag'].str.upper()
matchinfo.loc[:,'redTeamTag'] = matchinfo['redTeamTag'].str.upper()
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
print("Cleaning kills")
kills = kills.dropna(subset=['Victim']) # On Victim, because (although unclear) victim could die from neutral entity. Assists can and may be NaN
kills = kills[kills['Killer'] != 'TooEarly'] # Special case
kills.loc[:,'x_pos'] = pd.to_numeric(kills.loc[:,'x_pos'],errors='coerce') # Convert kill positions to numbers, coerce will convert or if not possible replace with NaN
kills.loc[:,'y_pos'] = pd.to_numeric(kills.loc[:,'y_pos'],errors='coerce') # Convert kill positions to numbers, coerce will convert or if not possible replace with NaN
## Team tags
print("Adding Killer/Victim Team tags & cleaning player names")
kills = kills.merge(matchinfo.reset_index()[['match_id', 'blueTeamTag', 'redTeamTag']], on='match_id', how='left') # Merge kills with team tags based on match_id
kills.loc[:,'Killer_Team'] = np.where(kills['Team'] == 'BLUE', kills['blueTeamTag'], kills['redTeamTag']) # Assign Killer_Team based on 'Team' column
kills.loc[:,'Victim_Team'] = np.where(kills['Team'] == 'BLUE', kills['redTeamTag'], kills['blueTeamTag']) # Assign Victim_Team based on 'Team' column
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
        kills.loc[:,col] = kills.apply(lambda row: extract_username(row[col], row['Victim_Team']), axis=1)
    else:
        kills.loc[:,col] = kills.apply(lambda row: extract_username(row[col], row['Killer_Team']), axis=1)
    kills.loc[:,col] = kills[col].str.lower().map(most_common_variants) # Keep only most recurring variatnt of username


# Monsters
## Subtype
print("Separating monster Subtypes")
monsters = monsters.dropna()
monsters.loc[:,'Subtype'] = monsters.loc[:,'Type'].apply(lambda x: x.split('_')[0] if 'DRAGON' in x and '_' in x else None)
monsters.loc[:,'Type'] = monsters.loc[:,'Type'].apply(lambda x: 'DRAGON' if 'DRAGON' in x else x)
drake_rename = {'FIRE':'INFERNAL','EARTH':'MOUNTAIN','WATER':'OCEAN','AIR':'CLOUD'}
monsters.loc[:,'Subtype'] = monsters['Subtype'].apply(lambda x: drake_rename[x] if x in drake_rename.keys() else x)
monsters.loc[:,'type_cardinality'] = monsters.sort_values("Time").groupby(["match_id","Type"]).cumcount().astype(int)


# Structures
## Lane/Type
print("Cleaning structure Lanes and Types")
structures = structures.dropna()
structures.loc[:,'Lane'] = structures.loc[:,'Lane'].apply(lambda x: x.split('_')[0])
structures.loc[:,'Type'] = structures.loc[:,'Type'].apply(lambda x: x.split('_')[0])
structures.loc[:,'type_cardinality'] = structures.sort_values("Time").groupby(["match_id","Type"]).cumcount().astype(int) # Specific for Nexus Tower assignation countW
# Boolean mask where Type is "NEXUS"
nexus_mask = structures['Type'] == 'NEXUS'
# Set 'Lane' to "UPPER" or "LOWER" based on even/odd type_cardinality
structures.loc[nexus_mask, 'Lane'] = np.where(
    structures.loc[nexus_mask, 'type_cardinality'] % 2 == 0,
    'UPPER',
    'LOWER'
)

# Champ IDs
## All capitalize
champ_ids['NAME'] = champ_ids['NAME'].str.capitalize()
champ_ids.loc[champ_ids["NAME"]=="Nunu&willump","NAME"] = "Nunu"
champ_ids.loc[champ_ids["NAME"]=="Dr.mundo","NAME"] = "Drmundo"


def reduce_dataset(df, ids):
    return df[df["match_id"].isin(ids)]

if REDUCE:
    print("Reducing datasets")
    r_matchinfo = matchinfo[matchinfo["Year"] >= 2017]
    r_matchids = r_matchinfo["match_id"]
    r_kills = reduce_dataset(kills, r_matchids)
    r_struct = reduce_dataset(structures, r_matchids)
    r_monsters = reduce_dataset(monsters, r_matchids)
    r_gold = reduce_dataset(gold, r_matchids)

    print("Saving modified csvs")
    r_gold.to_csv(pt.join("data","gold_mod_r.csv"))
    r_kills.to_csv(pt.join("data","kills_mod_r.csv"))
    r_matchinfo.to_csv(pt.join("data","matchinfo_mod_r.csv"))
    r_monsters.to_csv(pt.join("data","monsters_mod_r.csv"))
    r_struct.to_csv(pt.join("data","structures_mod_r.csv"))

else:
    # Save csvs
    print("Saving modified csvs")
    gold.to_csv(pt.join("data","gold_mod.csv"))
    kills.to_csv(pt.join("data","kills_mod.csv"))
    matchinfo.to_csv(pt.join("data","matchinfo_mod.csv"))
    monsters.to_csv(pt.join("data","monsters_mod.csv"))
    structures.to_csv(pt.join("data","structures_mod.csv"))
champ_ids.to_csv(pt.join("data","champ_ids_mod.csv"),index=False)