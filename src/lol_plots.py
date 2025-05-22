
import pandas as pd

import numpy as np

import plotly as plt
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from typing import Optional, List
import os, math

from utils import format_time, encode_image_to_base64, generate_shades_plotly

MAPICONS_PATH = os.path.join("ressources","mapicons")
CHAMP_ICONS_LINK = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/" # Append champion id

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
def podium_dual_figure(series1, title1, series2, title2):
    # Helper to prepare data for podium bars (top 3)
    def prepare_podium_data(series):
        n = len(series)
        if n == 0:
            return []
        positions = [1, 0, 2]  # Podium order: #2, #1, #3
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
        return data

    data1 = prepare_podium_data(series1)
    data2 = prepare_podium_data(series2)

    # If no data in both, show one subplot with annotation
    if not data1 and not data2:
        fig = make_subplots(rows=1, cols=1)
        fig.add_annotation(
            text="Not enough data",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=24)
        )
        fig.update_layout(
            plot_bgcolor="white",
            dragmode=False,
            hovermode=False,
            xaxis=dict(showticklabels=False),
            yaxis=dict(showticklabels=False)
        )
        return fig

    fig = make_subplots(rows=1, cols=2, subplot_titles=[title1, title2])

    # Add bars for series1 (left subplot)
    if data1:
        fig.add_trace(go.Bar(
            x=[d["label"] for d in data1],
            y=[d["height"] for d in data1],
            text=[d["name"] for d in data1],
            textfont=dict(size=20),
            textposition="inside",
            marker_color=[d["color"] for d in data1],
            width=[1]*len(data1),
            hoverinfo='skip'
        ), row=1, col=1)
    else:
        fig.add_annotation(
            text="Not enough data",
            x=0.5, y=0.5,
            xref="x domain", yref="y domain",
            showarrow=False,
            font=dict(size=20),
            row=1, col=1
        )

    # Add bars for series2 (right subplot)
    if data2:
        fig.add_trace(go.Bar(
            x=[d["label"] for d in data2],
            y=[d["height"] for d in data2],
            text=[d["name"] for d in data2],
            textfont=dict(size=20),
            textposition="inside",
            marker_color=[d["color"] for d in data2],
            width=[1]*len(data2),
            hoverinfo='skip'
        ), row=1, col=2)
    else:
        fig.add_annotation(
            text="Not enough data",
            x=0.5, y=0.5,
            xref="x domain", yref="y domain",
            showarrow=False,
            font=dict(size=20),
            row=1, col=2
        )

    fig.update_layout(
        showlegend=False,
        bargap=0.5,
        plot_bgcolor="white",
        dragmode=False,
        hovermode=False,
        xaxis=dict(tickfont=dict(size=32), showticklabels=True),
        xaxis2=dict(tickfont=dict(size=32), showticklabels=True),
        yaxis=dict(showticklabels=False),
        yaxis2=dict(showticklabels=False)
    )

    return fig


def get_top_killers(kills_df):
    top_kills = kills_df["Killer"].value_counts().nlargest(3)
    return top_kills

def get_top_deaths(kills_df):
    top_deaths = kills_df["Victim"].value_counts().nlargest(3)
    return top_deaths


# Gold
def plot_gold_over_time(gold_df):
    # Get the relevant rows
    goldred = gold_df[gold_df["Type"] == "goldred"].iloc[0]
    goldblue = gold_df[gold_df["Type"] == "goldblue"].iloc[0]
    golddiff = gold_df[gold_df["Type"] == "golddiff"].iloc[0]

    # Extract valid minute columns
    minute_cols = [col for col in gold_df.columns if col.startswith("min_") and pd.notna(goldred[col])]
    minutes = [int(col.split("_")[1]) for col in minute_cols]

    goldred_values = goldred[minute_cols].astype(float).values
    goldblue_values = goldblue[minute_cols].astype(float).values
    golddiff_values = golddiff[minute_cols].astype(float).values

    # Create hover text
    red_hover = [f"Minute {m}<br>Red: {r:,.0f}<br>Diff: {d:+,.0f}" 
                 for m, r, d in zip(minutes, goldred_values, golddiff_values)]
    blue_hover = [f"Minute {m}<br>Blue: {b:,.0f}<br>Diff: {d:+,.0f}" 
                  for m, b, d in zip(minutes, goldblue_values, golddiff_values)]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=minutes,
        y=goldred_values,
        name="Red Team Gold",
        line=dict(color="red"),
        hoverinfo="text",
        text=red_hover
    ))

    fig.add_trace(go.Scatter(
        x=minutes,
        y=goldblue_values,
        name="Blue Team Gold",
        line=dict(color="blue"),
        hoverinfo="text",
        text=blue_hover
    ))

    fig.update_layout(
        title="Gold Over Time per Team",
        xaxis=dict(title="Minute", range=[0, max(minutes)]),
        yaxis_title="Gold",
        plot_bgcolor="white",
        hovermode="closest"  # default hover behavior
    )

    fig.update_layout(
    xaxis=dict(
        showgrid=True,
        gridcolor='lightgray',
        gridwidth=1,
        griddash='dot'
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='lightgray',
        gridwidth=1,
        griddash='dot'
    )
)

    return fig

# === Champion Pick/Ban/Win rates ===

def get_champ_rates(matchinfo: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Computes the champion winrates"""
    ban_cols = ["blueBan1","blueBan2","blueBan3","blueBan4","blueBan5","redBan1","redBan2","redBan3","redBan4","redBan5"]
    pick_cols = ["blueTopChamp","blueJungleChamp","blueMiddleChamp","blueADCChamp","blueSupportChamp","redTopChamp","redJungleChamp","redMiddleChamp","redADCChamp","redSupportChamp"]
    n_games = matchinfo.shape[0]
    # List all pick columns
    blue_cols = pick_cols[:5]
    red_cols = pick_cols[5:]

    # Count wins per side
    blue_wins = matchinfo.loc[matchinfo['bResult'] == 1, blue_cols].stack().value_counts()
    red_wins = matchinfo.loc[matchinfo['rResult'] == 1, red_cols].stack().value_counts()
    # Combine both
    champion_wins = blue_wins.add(red_wins, fill_value=0).astype(int)

    ban_rates = matchinfo[ban_cols].stack().value_counts()/n_games*100
    pick_rates = matchinfo[pick_cols].stack().value_counts()/n_games*100
    win_rates = (champion_wins/pick_rates).sort_values(ascending=False)

    return pick_rates[:5], win_rates[:5], ban_rates[:5]

def get_image_paths(champ_names: List[str], champ_ids: pd.DataFrame) -> List[str]:
    """Return a list of champion icon URLs based on champion names."""
    sel_champ_ids = [champ_ids.loc[champ_ids['NAME'] == name, 'ID'].values[0] for name in champ_names]
    return [f"{CHAMP_ICONS_LINK}{id}.png" for id in sel_champ_ids]

def get_champ_rates_plots(pick_df: pd.DataFrame, win_df: pd.DataFrame, ban_df: pd.DataFrame, champ_ids: pd.DataFrame) -> go.Figure:
    """Creates subplots with champion pick ban and winrates"""

    fig = make_subplots(
        rows=1, cols=3,
        shared_xaxes=False,
        column_widths=[00.33,0.33,0.34],
        vertical_spacing=0.1,
        subplot_titles=("Pick Rates", "Win rates", "Ban rates"),
        specs=[[{}, {}, {}]]
    )

    # Create single bar traces
    pick_trace = create_champ_rate_trace(pick_df, colour="#004ac0")
    win_trace = create_champ_rate_trace(win_df, colour="#009e00")
    ban_trace = create_champ_rate_trace(ban_df, colour="#ff0000", ban=True)

    # Add traces to subplots
    fig.add_trace(pick_trace, row=1, col=1)
    fig.add_trace(win_trace, row=1, col=2)
    fig.add_trace(ban_trace, row=1, col=3)


    # Add images for each subplot
    pick_names = pick_df.index.tolist()
    pick_img_paths = get_image_paths(pick_names, champ_ids)
    add_champion_images(fig, pick_df.index, pick_img_paths, "x1") # xref according to right subplot
    add_champion_images(fig, win_df.index, get_image_paths(win_df.index,champ_ids), "x2")
    add_champion_images(fig, ban_df.index, get_image_paths(ban_df.index,champ_ids), "x3")

    # Update layout
    fig.update_traces(width=0.85)
    fig.update_layout(
        showlegend=False,
        margin=dict(b=100),  # Make space for champ icons
    )
    fig.update_xaxes(showticklabels=False)
    return fig


def create_champ_rate_trace(df: pd.DataFrame, colour: str, ban: bool = False) -> go.Figure:
    """Creates a bar trace of champion pick/ban or winrates, should receive a df with the champion name as an index and their rate as sole values"""
    colours = generate_shades_plotly(colour, n_shades=df.shape[0])

    trace = go.Bar(
        x=df.index,
        y=df.values,
        marker_color=colours,
        width=0.75,
        hovertemplate="%{x}: %{y:.2f}%",
        showlegend=False
    )
    
    return trace

def add_champion_images(fig: go.Figure, champ_refs: List[str|float], img_paths: List[str], xref: str, y_shift: float|List[float]=-0.05, size: float=0.1):
    """Adds images under x-axis in a specific subplot column. champ_ref is a list either of champion names (to reference xref associated to champion) or a float value referring to an exact position"""
    if type(y_shift) is not list:
        y_shift = [y_shift for i in range(len(champ_refs))]
    for champ, path, y in zip(champ_refs, img_paths, y_shift):
        fig.add_layout_image(
            dict(
                source=path,
                xref=xref,
                yref="paper",
                x=champ,
                y=y,
                sizex=1,
                sizey=size,
                xanchor="center",
                yanchor="top",
                layer="above"
            )
        )

def get_champs_posbans():
    return None