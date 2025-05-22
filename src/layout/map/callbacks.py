from dash import Input, Output, callback, html
import pandas as pd
from os import path as pt
import plotly.graph_objects as go


from layout.main_menu import MATCHINFO_DF, KILLS_DF, STRUCTURES_DF, MONSTERS_DF
from map_plots import get_map_timeline_mplot

@callback(
    [
        Output("map-graph", "figure"),
        Output("event-list", "children"),
     ],
    [
        Input("time-slider", "value"),
        Input("map-style", "value"),
        Input("filter_games", "selectedRows"),
        Input("stored_games_filtered", "data"),

     ]
)
def update_map(time_range, map_style,match_records, storedg):

    if match_records == None:
        return go.Figure(), html.Div()

    heatmap = map_style == "Heatmap"

    match_ids = list(pd.DataFrame.from_records(match_records)["match_id"])

    # == Get filtered data
    filtered_matchinfo = MATCHINFO_DF[MATCHINFO_DF.index.isin(match_ids)]
    
    kills = KILLS_DF[KILLS_DF["match_id"].isin(match_ids)]
    structures = STRUCTURES_DF[STRUCTURES_DF["match_id"].isin(match_ids)]
    monsters = MONSTERS_DF[MONSTERS_DF["match_id"].isin(match_ids)]



    # == List of events/games
    if len(match_ids) == 0:
        print("no games selected")    
    elif len(match_ids) == 1:
        kills["source"] = "kills"
        structures["source"] = "structures"
        monsters["source"] = "monsters"
        combined = pd.concat([kills, structures, monsters]).sort_values("Time")
        # One match, so add game events
        event_list = []
        for _, row in combined.iterrows():
            event = None

            if row["source"] == "kills":
                event = html.Div([
                    html.Strong(f"{row['Killer']}"),
                    " killed ",
                    html.Strong(f"{row['Victim']}"),
                    f" at {row['Time']:.2f}m"
                ], style={
                "border": "1px solid #ccc",
                "borderRadius": "8px",
                "padding": "10px",
                "marginBottom": "10px",
                "backgroundColor": "#f9f9f9",
                "boxShadow": "2px 2px 5px rgba(0, 0, 0, 0.05)"
            })

            elif row["source"] == "structures":
                type_name = row['Type'] if pd.notna(row['Type']) else ""
                event = html.Div([
                    "Team ",
                    html.Strong(f"{row['Team']}"),
                    " destroyed the ",
                    html.Strong(f"{type_name} tower"),
                    f" at {row['Time']:.2f}m"
                ], style={
                "border": "1px solid #ccc",
                "borderRadius": "8px",
                "padding": "10px",
                "marginBottom": "10px",
                "backgroundColor": "#f9f9f9",
                "boxShadow": "2px 2px 5px rgba(0, 0, 0, 0.05)"
            })
                
            elif row["source"] == "monsters":
                subtype = f"{row.get('Subtype', '')} " if pd.notna(row.get('Subtype', None)) else ""
                type_name = row['Type'] if pd.notna(row['Type']) else ""
                event = html.Div([
                    "Team ",
                    html.Strong(f"{row['Team']}"),
                    " killed the ",
                    html.Strong(f"{subtype}{type_name}"),
                    f" at {row['Time']:.2f}m"
                ], style={
                "border": "1px solid #ccc",
                "borderRadius": "8px",
                "padding": "10px",
                "marginBottom": "10px",
                "backgroundColor": "#f9f9f9",
                "boxShadow": "2px 2px 5px rgba(0, 0, 0, 0.05)"
            })


            if event is not None:
                event_list.append(event)
            event_list = event_list
    else:
        # Multiple matches, so show list of matches
        event_list = [
            html.Div([
                "[",
                html.Strong(f"{row['blueTeamTag']}"),
                " VS ",
                html.Strong(f"{row['redTeamTag']}"),
                "] at ",
                html.Strong(f"{row['League']}"),
                " League during the ",
                html.Strong(f"{row['Season']}"),
                " season of ",
                html.Strong(f"{row['Year']}"),
            ], style={
                "border": "1px solid #ccc",
                "borderRadius": "8px",
                "padding": "10px",
                "marginBottom": "10px",
                "backgroundColor": "#f9f9f9",
                "boxShadow": "2px 2px 5px rgba(0, 0, 0, 0.05)"
            })
            for _, row in filtered_matchinfo.drop_duplicates(subset="match_id").iterrows()
        ]

    kills_map = get_map_timeline_mplot(kills, monsters, structures, time_range, heatmap)

    return kills_map,  event_list