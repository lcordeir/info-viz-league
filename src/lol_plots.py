
import pandas as pd

import numpy as np

import plotly as plt
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from typing import Optional, List
import os, math

from utils import format_time, encode_image_to_base64

MAPICONS_PATH = os.path.join("ressources","mapicons")

# === General Plots ==

def get_objective_distribution(monsters: pd.DataFrame, normalized: bool=True) -> go.Figure:
    """Returns a stacked barchart of monster type distribution by cardinality.
    Takes monsters df as input and boolean to normalize data or not."""
    # Count monsters by type for each cardinality
    grouped_counts = monsters.groupby(['cardinality', 'Type']).aggregate(count=('Type','size'),avg_time=('Time','mean')).reset_index()
    grouped_counts['avg_time_str'] = grouped_counts['avg_time'].apply(format_time)
    if normalized:
        grouped_counts['percent'] = grouped_counts['count'] / grouped_counts.groupby('cardinality')['count'].transform('sum')
        grouped_counts['percent_str'] = (grouped_counts['percent'] * 100).map("{:.2f}%".format)
        labels = {'cardinality': 'Cardinality', 'percent_str': 'Percentage', 'count':'Count', 'avg_time_str':'Average Time'}
        hover_data={'cardinality': True, 'percent':False, 'percent_str': True, 'count': True, 'Type': True, 'avg_time_str':True}
        y='percent'
    else:
        labels = {'cardinality': 'Cardinality', 'count': 'Count', 'avg_time_str':'Average Time'}
        hover_data={'cardinality': True, 'Type': True, 'count': True, 'avg_time_str':True}
        y='count'

    fig = px.bar(
        grouped_counts,
        x='cardinality',
        y=y,
        color='Type',
        title='Distribution of Types by Cardinality',
        labels=labels,
        hover_data=hover_data,
        barmode='stack'
    )
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None
    )
    return fig

def get_first_Drake_avg(monsters: pd.DataFrame) -> go.Figure:
    """Plots the average time of the first drake of any subtype done in a game. Show certain subtypes are prioritized."""
    time_monst=monsters.loc[monsters.groupby(['match_id','Type'])['Time'].idxmin()].groupby(['Subtype']).aggregate({'Time':'mean'}).sort_values('Time').reset_index()
    time_monst_cols = {'INFERNAL':'red','OCEAN':'blue','CLOUD':'yellow','MOUNTAIN':'green'} 
    fig=px.bar(time_monst,
            x="Subtype",
            y="Time",
            color="Subtype",
            width=500,
            color_discrete_map=time_monst_cols)
    # Rename y-axis
    fig.update_traces(width=0.85)\
        .update_xaxes(showticklabels=False)\
        .update_layout(showlegend=False,
                       yaxis_title='Average time for first clear',)
    # Add icons to graph
    for elem in time_monst['Subtype']:
        fig.add_layout_image(
            # Could do encorde for all in advance and cache
            source=encode_image_to_base64(f"{os.path.join(MAPICONS_PATH,elem)}.png"),
            x=elem,
            y=0.05,  # Right at x-axis
            xref="x",
            yref="paper",
            sizex=0.5,
            sizey=0.1,
            xanchor="center",
            yanchor="top",
            layer="above"
        )
    return fig

# Win rates

def get_win_rate(matchinfo: pd.DataFrame) -> go.Figure:
    """Returns overall winrate of received matchinfo df"""
    wins=matchinfo.loc[:,['bResult','rResult']].sum()
    d = {"WIN RATE BLUE":wins['bResult']/wins.sum()*100,"WIN RATE RED":wins['rResult']/wins.sum()*100}
    fig = px.bar(
        x=d.keys(),
        y=d.values(),
        color=d.keys(),
        width=500,
        color_discrete_map=dict(zip(d.keys(), ('blue', 'red')))
    )

    fig.update_traces(
        width=0.75,
        hovertemplate="%{y:.1f}%",  # Custom hover text
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title=None,
        yaxis_title=None
    )
    return fig

def get_team_scores(matchinfo: pd.DataFrame, blue_team: str, red_team: str) -> dict:
    """Computes total scores of blue and red team in df. df should be matchinfo"""
    teams = [blue_team, red_team]
    scores = {}
    for team in teams:
        blue_score = matchinfo.loc[matchinfo['blueTeamTag'] == team, 'bResult'].sum()
        red_score = matchinfo.loc[matchinfo['redTeamTag'] == team, 'rResult'].sum()
        total_score = blue_score + red_score
        scores[team] = total_score
    return scores

def get_2teams_winrate(blue_team: str, red_team: str, row: pd.DataFrame, scores: dict) -> go.Figure:
    """Creates boxplot of winrates capped to indicate winning team. Called when a single game is selected.
    TODO (OPT): Consider multiple games of one team."""
    # Extract values
    blue_score = scores[blue_team]
    red_score = scores[red_team]
    total = blue_score + red_score

    # Compute win ratios
    blue_pct = blue_score / total * 100
    red_pct = red_score / total * 100

    # Determine winner
    if row['bResult'].values[0] > row['rResult'].values[0]: 
        winner = blue_team  
    else: 
        winner = red_team

    # Define colors
    team_colors = {
        blue_team: {
            'low': f"rgba(0, 0, 255, 0.4)",     # light blue
            'full': f"rgba(0, 0, 255, 1.0)"      # strong blue
        },
        red_team: {
            'low': f"rgba(255, 0, 0, 0.4)",     # light red
            'full': f"rgba(255, 0, 0, 1.0)"      # strong red
        }
    }

    fig = go.Figure()
    for team, pct in [(blue_team, blue_pct), (red_team, red_pct)]:
        fig.add_trace(go.Bar(
            x=[team],
            y=[pct],
            marker_color=team_colors[team]['low'],
            name=team,
            hovertemplate=f"{team} Win Rate: {pct:.1f}%",
            showlegend=False
        ))
        # Add full saturation bar only if this team won the current match
        if team == winner:
            fig.add_trace(go.Bar(
                x=[team],
                y=[2],  # a small height just to cap the top
                marker_color=team_colors[team]['full'],
                name=f"{team} (won)",
                hoverinfo="skip",
                showlegend=False
            ))
    fig.update_layout(
        barmode='stack',
        xaxis_title=None,
        yaxis_title=None,
        title="All Time Win Rates",
        margin=dict(t=40),
        yaxis_range=[0, 100],
    )
    return fig


# Top 3 plots
def podium_figure(series, title):
    n = len(series)
    if n == 0:
        fig = go.Figure()
        fig.update_layout(
            title=title,
            xaxis=dict(showticklabels=False),
            yaxis=dict(showticklabels=False),
            showlegend=False,
            plot_bgcolor="white",
            hovermode=False,
            dragmode=False,
            annotations=[
                dict(
                    text="Not enough data",
                    x=0.5, y=0.5,
                    xref="paper", yref="paper",
                    showarrow=False,
                    font=dict(size=24)
                )
            ]
        )
        return fig

    # Podium positions: left = #2, center = #1, right = #3
    positions = [1, 0, 2]  # Indexes in value_counts()
    labels = ["#2", "#1", "#3"]
    colors = ["silver", "gold", "#cd7f32"]
    heights = [13, 20, 8]

    data = []
    for pos, label, color, height in zip(positions, labels, colors, heights):
        if pos < n:
            data.append({
                "label": label,
                "name": series.index[pos],
                "color": color,
                "height": height
            })

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[d["label"] for d in data],
        y=[d["height"] for d in data],
        text=[d["name"] for d in data],
        textfont=dict(size=20),
        textposition="inside",
        marker_color=[d["color"] for d in data],
        width=[1] * len(data)
    ))

    fig.update_layout(
        title=title,
        xaxis=dict(
            showticklabels=True,
            tickfont=dict(size=32)
        ),
        yaxis=dict(showticklabels=False),
        showlegend=False,
        bargap=0.5,
        plot_bgcolor="white",
        hovermode=False,
        dragmode=False
    )
    fig.update_traces(hoverinfo="skip")

    return fig


def get_top_killers(kills_df):
    top_kills = kills_df["Killer"].value_counts().nlargest(3)
    return podium_figure(top_kills, "Top 3 Killers")


def get_top_assisters(kills_df):
    assist_cols = [col for col in kills_df.columns if col.startswith("Assist_")]
    top_assists = kills_df[assist_cols].stack().value_counts().nlargest(3)
    return podium_figure(top_assists, "Top 3 Assisters")


def get_top_deaths(kills_df):
    top_deaths = kills_df["Victim"].value_counts().nlargest(3)
    return podium_figure(top_deaths, "Top 3 Deaths")

