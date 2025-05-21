from dash import Input, Output, State, callback, html
import pandas as pd
import plotly.graph_objects as go
from os import path as pt
import base64
import os
import json
from layout.main_menu import MATCHINFO_DF, KILLS_DF, STRUCTURES_DF, MONSTERS_DF, BANS_DF, GOLD_DF

@callback(
    [
        Output("map-graph", "figure"),
        Output("timeline-fig", "figure"),
        Output("event-list", "children"),
     ],
    [
        Input("time-slider", "value"),
        Input("map-style", "value"),
        Input("team-filter", "value"),
        # Input("filtered_match_info", "data"),
        Input("filter_games", "selectedRows"),
        # Input("stored_games_filtered", "selectedRows"),

     ]
)
def update_map(time_range, map_style, team_filter, match_records):
# def update_map(time_range, map_style, team_filter, match_records, games):

    # print("===========")
    # print(games)
    # print("///////////")

    if map_style == "Schematic":
        map_image_path = "ressources/SummonersRift.webp"
    elif map_style == "Satellite":
        map_image_path = "ressources/satellite.jpeg"
    else:
        map_image_path = "ressources/SummonersRift.webp"

    if match_records is None or len(match_records) == 0:
        print("no games selected")    
        return generate_kills_map(pd.DataFrame(), map_image_path), go.Figure(), html.Div()
    
    # print("games selected:")    
    # print(match_records)
    match_ids = list(pd.DataFrame.from_records(match_records)["match_id"])
    # print(match_ids)
    # == Get filtered data
    filtered_matchinfo = MATCHINFO_DF[MATCHINFO_DF.index.isin(match_ids)]
    
    kills = KILLS_DF[KILLS_DF["match_id"].isin(match_ids)]
    kills = kills[
        (kills["Time"] >= time_range[0]) &
        (kills["Time"] <= time_range[1]) &
        (kills["Team"].isin(team_filter))
    ]

    structures = STRUCTURES_DF[STRUCTURES_DF["match_id"].isin(match_ids)]
    structures = structures[
        (structures["Time"] >= time_range[0]) &
        (structures["Time"] <= time_range[1]) &
        (structures["Team"].isin(team_filter))
    ]

    monsters = MONSTERS_DF[MONSTERS_DF["match_id"].isin(match_ids)]
    monsters = monsters[
        (monsters["Time"] >= time_range[0]) &
        (monsters["Time"] <= time_range[1]) &
        (monsters["Team"].isin(team_filter))
    ]

    # print(df.head())
    # print(df.__len__())

    # == Map 
    kills_map = generate_kills_map(kills, map_image_path)

    # == Timeline with kills
    timeline_fig = generate_kill_timeline(kills)

    print(monsters.head())

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


    return kills_map, timeline_fig, event_list

    
def generate_kills_map(kills, image_path):
    # Import image (for some reason, directly putting the path does not load the image)
    # image_path = "ressources/SummonersRift.webp"
    encoded_image = base64.b64encode(open(image_path, 'rb').read()).decode()

    fig = go.Figure()
    fig.add_layout_image(
            dict(
                # source="ressources/SummonersRift.webp",
                source="data:image/webp;base64," + encoded_image,
                x=0,
                y=16000,
                xref="x",
                yref="y",
                sizex=16000,
                sizey=16000,
                opacity=0.5,
                layer="below"
        )
    )

    for _, kill in kills.iterrows():
        # print(f"X: {kill['x_pos']}")
        # print(f"Y: {kill['y_pos']}")
        fig.add_trace(go.Scatter(
            x=[kill["x_pos"]],
            y=[kill["y_pos"]],
            mode="markers",
            marker=dict(
                size=10,
                color="blue" if kill["Team"] == "BLUE" else "red",
                symbol="x"
            ),
            name=f"{kill['Killer']} killed {kill['Victim']}",
            text=f"Time: {kill['Time']}s\nKiller: {kill['Killer']}\nVictim: {kill['Victim']}",
            hoverinfo="text"
        ))

    fig.update_layout(
        xaxis=dict(
            range=[0, 16000],
            constrain='domain',     # Keep aspect ratio when resizing
            showgrid=False,
            zeroline=False,
            scaleanchor="y",
            scaleratio=1
        ),
        yaxis=dict(
            range=[0, 16000],
            constrain='domain',     # Keep aspect ratio when resizing
            showgrid=False,
            zeroline=False
        ),
        title="League of Legends Kill Map",
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        width=650,
        height=650,
        dragmode="zoom",            # Enable zoom and pan
    )

    fig.update_layout(
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[dict(
                label="Reset View",
                method="relayout",
                args=[
                    {
                        "xaxis.range[0]": 0,
                        "xaxis.range[1]": 16000,
                        "yaxis.range[0]": 0,
                        "yaxis.range[1]": 16000,
                        # Include a dummy toggle to force rerender
                        "uirevision": True
                    }
                ]
            )],
            x=0.01,
            y=0.99,
            xanchor="left",
            yanchor="top"
        )]
    )


    fig.update_layout(
        modebar_remove=["autoscale"],  # Remove default autoscale button
    )


    return fig

def generate_kill_timeline(kills_df):
    # Group by time (rounded or binned if needed)
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=kills_df["Time"],
        y=[1] * len(kills_df),  # just show dots at y=1
        mode="markers",
        marker=dict(
            size=16,
            line=dict(width=1),  # Makes the line thick enough to see
            # color=np.where(kills_df["Team"] == "Red", "red", "blue"),
            color = ["red" if team == "RED" else "blue" for team in kills_df["Team"]],
            symbol="line-ns-open"
        ),
        hovertext=kills_df.apply(lambda row: f"{row['Killer']} → {row['Victim']} ({row['Time']:.2f}m)", axis=1),
        hoverinfo="text",
        showlegend=False
    ))

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(range=[0, 60], visible=False),
        yaxis=dict(visible=False),
        height=100,
        # margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        dragmode=False,
        )
    
    fig.update_layout(
        xaxis=dict(
            range=[0, 60],  # Same as the slider range
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False
        )
    )

    return fig