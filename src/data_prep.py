import pandas as pd
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
### Create ids
match_ids = matchinfo["Address"].reset_index()
match_ids = match_ids.rename(columns={"index":"match_id"})
### Assign ids
data_dfs = [bans,gold,kills,matchinfo,monsters,structures]
for i in range(len(data_dfs)):
    data_dfs[i]=data_dfs[i].merge(match_ids, on="Address",how="left")
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


# Kills
## Position
kills = kills.dropna()
kills.loc[:,'x_pos'] = pd.to_numeric(kills.loc[:,'x_pos'],errors='coerce') # Convert kill positions to numbers, coerce will convert or if not possible replace with NaN
kills.loc[:,'y_pos'] = pd.to_numeric(kills.loc[:,'y_pos'],errors='coerce') # Convert kill positions to numbers, coerce will convert or if not possible replace with NaN

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
structures['type_cardinality'] = structures.sort_values("Time").groupby(["match_id","Type"]).cumcount().astype(int) # Specific for Nexus Tower assignation count
structures.loc[:,'Type'] = structures.apply(lambda row: f"NEXUS{row['type_cardinality'] % 2 + 1}" if row['Type'] == 'NEXUS' else row['Type'],axis=1)


# Save csvs
bans.to_csv(pt.join("data","bans_mod.csv"))
gold.to_csv(pt.join("data","gold_mod.csv"))
kills.to_csv(pt.join("data","kills_mod.csv"))
matchinfo.to_csv(pt.join("data","matchinfo_mod.csv"))
monsters.to_csv(pt.join("data","monsters_mod.csv"))
structures.to_csv(pt.join("data","structures_mod.csv"))