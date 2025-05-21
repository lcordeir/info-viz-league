# components/callbacks.py
from dash import Input, Output, callback, html
from components.kills_tab import kills_tab_layout
from components.utils import load_data, filter_data
from components.plots import generate_kill_map, generate_kill_timeline, generate_podium
import json
import os
import pandas as pd


def get_kills_data():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'kills.csv')
    kills_data = pd.read_csv(file_path)
    # return kills_data
    return kills_data.sample(n=100, random_state=42) # Temporary random subset, team filter should be added later

# Assuming you have a filter function like this:
def filter_data(df, kill_time_range, team_filter):
    df = df.copy()
    df["Time"] = df["Time"].astype(float)
    df["x_pos"] = df["x_pos"].astype(float)
    df["y_pos"] = df["y_pos"].astype(float)

    # Map team names
    team_map = {"bKills": "Blue", "rKills": "Red"}
    df["Team"] = df["Team"].map(team_map)

    # Rename position columns if needed
    df = df.rename(columns={"x_pos": "x", "y_pos": "y"})
    print(df["Time"].min())
    print(df["Time"].max())
    return df[
        (df["Time"] >= kill_time_range[0]) &
        (df["Time"] <= kill_time_range[1]) &
        (df["Team"].isin(team_filter))
    ]

@callback(
    [Output("map-graph", "figure"),
     Output("event-list", "children"),
     Output("timeline-fig", "figure"),
     Output("kill-podium", "figure"),
     Output("assist-podium", "figure")
     ],
    [Input("time-slider", "value"),
     Input("team-filter", "value"),
     Input("map-style", "value")]
)
def update_map(kill_time_range, team_filter, map_style):
    # Get all kills from data source
    kills = get_kills_data()  # Make sure this function is implemented to return your full kills dataset
    
    # Filter data by the selected time range and teams
    filtered_kills = filter_data(kills, kill_time_range, team_filter)
    print(len(filtered_kills))

    # Generate the kill map with the selected style
    map_fig = generate_kill_map(filtered_kills, map_style, team_filter)
    timeline_fig = generate_kill_timeline(filtered_kills)
    fig_kills, fig_assists = generate_podium(filtered_kills)
    
    # Generate a list of kills as cards
    kill_list = [
        html.Div([
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
        for _, row in filtered_kills.iterrows()
    ]

    return map_fig, kill_list, timeline_fig, fig_kills, fig_assists
