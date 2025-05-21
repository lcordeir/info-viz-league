
import pandas as pd

import numpy as np

import plotly as plt
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from typing import Optional, List
import os, math

from utils import format_time, encode_image_to_base64

MAPICONS_PATH = os.path.join("ressources","MAPICONS")

# === MAP ===

def add_map_bg(fig: go.Figure) -> go.Figure:
    """Modifies a figure to add the map as a background to it."""
    fig.update_traces(opacity=0.66)
    fig.update_layout(
        images=[
            dict(
                source="..\\ressources\\SummonersRift.webp",  # Path or URL to the PNG/SVG image
                xref="paper",  # Coordinates system: 'paper' means relative to the paper's area
                yref="paper",
                x=0,  # Positioning the image
                y=1,  # Positioning the image
                sizex=1,  # Image width as a fraction of plot area
                sizey=1,  # Image height as a fraction of plot area
                opacity=0.3,  # Image transparency (0 = fully transparent, 1 = fully opaque)
                layer="below"  # Ensures the image stays below the plot
            )
        ],
    )
    return fig

def get_map_bg(xref: str="paper", yref: str="paper", size: int=1) -> dict:
    """Creates a dict containing the information relating to the map background to add on the map"""
    return dict(
        source="..\\ressources\\SummonersRift.webp",  # Path or URL to the PNG/SVG image
        xref=xref,  # Coordinates system: 'paper' means relative to the paper's area
        yref=yref,
        x=0,  # Positioning the image
        y=0,  # Positioning the image
        sizex=size,  # Adjust based on your coordinate system
        sizey=size,
        xanchor="left",
        yanchor="bottom",
        sizing="stretch",  # Or "contain", "fill"
        opacity=0.3,  # Image transparency (0 = fully transparent, 1 = fully opaque)
        layer="below"  # Ensures the image stays below the plot
    )

def combine_assists(row: pd.Series, assist_cols: List[str]) -> Optional[str]:
    assists = [str(row[col]) for col in assist_cols if pd.notna(row[col])]
    return ", ".join(assists) if assists else None

def get_kill_plot(df: pd.DataFrame, heatmap_binsize: int = 25) -> go.Figure:
    """Calls create_kill_plot after processing the df further."""
    if df['match_id'].unique().size == 1:
        df_g = df.copy()    # To avoid warning
        coord_suffix = ""

        assist_columns = ["Assist_1", "Assist_2", "Assist_3", "Assist_4"]
        hover_labels = [f"<b>{row['Victim']}</b><br>By: {row['Killer']}<br>Assisted by: {combine_assists(row, assist_columns)}<br>At: {format_time(row['Time'])}" for _, row in df_g.iterrows()]

        blue_team = df_g.loc[df_g['Team'] == 'BLUE', 'Killer_Team'].iloc[0] # Note, killer perspective, so BLUE means blue killer and red victim
        red_team = df_g.loc[df_g['Team'] == 'BLUE', 'Victim_Team'].iloc[0]

        df_g.loc[:,'Team'] = np.where(df_g['Team'] == 'BLUE', red_team, blue_team) # Invert color on the map, more user friendly if a dot fits the player who died
        df_g.loc[:,'count'] = 1 # Just to be consistent with the aggregated version and have a "count" column for the size
        team_name_col=[(red_team,'red'),(blue_team,'blue')]
    else: 
        coord_suffix = "bin_"
        x_max = df['x_pos'].max()
        y_max = df['y_pos'].max()
        df['bin_x_pos'] = (df['x_pos']/x_max*heatmap_binsize).apply(math.floor) # Scalow down into bins
        df['bin_y_pos'] = (df['y_pos']/y_max*heatmap_binsize).apply(math.floor)

        df_g = df.groupby(['bin_x_pos', 'bin_y_pos', 'Team']).agg(count=('Time', 'count'),avg_time=('Time', 'mean')).reset_index()

        df_g['bin_x_pos'] = df_g['bin_x_pos']*(x_max / heatmap_binsize) # Rescale the coords to original size, to be consistent with scaling between single and aggregate
        df_g['bin_y_pos'] = df_g['bin_y_pos']*(y_max / heatmap_binsize)

        df_g['Team'] = np.where(df_g['Team'] == 'BLUE', "Red Side", "Blue Side")
        hover_labels = [f"<b>Count: {row['count']}</b><br>At: {format_time(row['avg_time'])}" for _, row in df_g.iterrows()]
        team_name_col=[("Red Side", "red"), ("Blue Side", "blue")]
    return create_kill_plot(df_g, team_name_col, hover_labels, coord_suffix)

def create_kill_plot(df_g: pd.DataFrame, team_name_col: List[(str)], hover_labels: List[str], coord_suffix: str) -> go.Figure:
    max_size = df_g['count'].max()
    # Create figure
    fig = go.Figure()
    for team_name, color in team_name_col:
        team_data = df_g[df_g['Team'] == team_name]
        fig.add_trace(
            go.Scatter(
                x=team_data[coord_suffix+'x_pos'],
                y=team_data[coord_suffix+'y_pos'],
                mode='markers',
                name=team_name,
                legendgroup=team_name,  # Link traces with same team
                marker=dict(size=30*team_data.loc[:,'count']/max_size, color=color),
                hoverinfo='text',
                text=hover_labels,
                showlegend=True
            )
        )
    return fig


def get_kill_heatmap(df: pd.DataFrame, heatmap_binsize: int) -> go.Figure:
    fig = go.Figure()
    heatmap = go.Histogram2d(
        x=df['x_pos'],
        y=df['y_pos'],
        nbinsx=heatmap_binsize,
        nbinsy=heatmap_binsize,
        colorscale='Viridis',
        opacity=0.6,
        colorbar=dict(
            title='Kill Density',
            x=0.80,           # Move the colorbar horizontally (0=left, 1=right)
            y=0.80,           # Move it vertically (1 is top, 0 is bottom)
            len=0.5,          # Shorten it to only cover the map row
            thickness=30,     # Width of the bar
            xanchor='left'    # Anchors the x-position
    ))
    fig.add_trace(heatmap) 
    return fig

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

# == TIMELINES ==
def set_timeline_margins_scale(fig: go.Figure, x_size: int):
    xaxis_common = {
        "range": [0, x_size],
        "showline": False,
        "showticklabels": True,
        "tickmode": "auto",
        "col": 1,  # all xaxes are in column 1
        "matches":'x2'
    }
    for row in range(2, 5):
        fig.update_xaxes(row=row, **xaxis_common)
    fig.update_layout(
        margin=dict(l=60, r=60, t=50, b=50), # TODO: DETERMINED BY DASH?
        height=1500, # TODO: DETERMINED BY DASH?
        plot_bgcolor='rgba(0,0,0,0)',  # transparent background for all plots
    )

def create_timeline(df: pd.DataFrame, hover_labels: List[str], x_size: int, xyref_nb: str = "") -> go.Figure:
    """ Creates a timeline using df's data, df needs columns: 'count', 'Time' and 'icon_name'.
    Labels to show when hovering given separately.
    """
    fig = go.Figure()
    
    tot_count = df['count'].sum()
    df['size'] = x_size/100+10*(df['count']/tot_count)  # Base size related with x axis and scales with proportion
    max_s_icon = df['size'].max()

    # x_tol defines when a neighbouring icon is to be offset by y_step. Both in funciton of icon size
    x_tol = max_s_icon*0.15
    y_step = max_s_icon

    y_values = []
    previous_x = -100
    previous_y = y_step

    layout_images = []
    # Add one image per event
    for _, row in df.iterrows():
        img_path = f'../ressources/mapicons/{row['icon_name']}.png'
        x = row['Time']
        if x-(previous_x+x_tol) < 0: y = previous_y+y_step
        else: y = y_step
        if os.path.exists(img_path):
            layout_images.append(dict(
                source=encode_image_to_base64(img_path),
                x=x,
                y=y,
                xref="x"+xyref_nb,
                yref="y"+xyref_nb,
                sizex=row['size'],
                sizey=row['size'],
                xanchor="center",
                yanchor="middle",
                layer="above"
            ))
        else: # TODO: EXCEPTION HANDLING? 
            print(f"Image not found: {img_path}")
        # Keep track of y positioning
        previous_x = x
        previous_y = y
        y_values.append(y)
    fig.add_trace(go.Scatter(
                x=df['Time'],
                y=y_values,
                mode='markers',
                marker=dict(size=df['size'], color='rgba(0,0,0,0)'),  # invisible
                hoverinfo='text',
                text=hover_labels,
                showlegend=False
            ))
    #set_timeline_margins_scale(fig, x_size, [0, max(y_values)+max_s_icon], np.unique(y_values))
    return fig, np.unique(y_values), max(y_values)+max_s_icon, layout_images

def get_monsters_timeline(df: pd.DataFrame, x_size: int) -> go.Figure:
    """ Creates a timeline of killed neutral objectives over time. 
    Should receive the data for a single match, or aggregated data"""
    # Team column is killer team
    if df['match_id'].unique().size > 1:
        # Do not consider Subtype in aggregate, because too much detail
        g_df = df.groupby(['Type','type_cardinality','Team']).aggregate(count=('Type','size'),Time=('Time','mean')).sort_values('Time').reset_index()
        g_df.loc[:,'icon_name'] = g_df['Team'] + '_' + g_df['Type'] # TODO: Do in preprocessing?
        hover_labels = [f"<b>{row['Type']}</b><br>At: {format_time(row['Time'])}<br>Count: {row['count']}" for _, row in g_df.iterrows()]
    else: 
        g_df = df.copy()
        g_df.loc[:,'count'] = 1
        g_df.loc[:,'icon_name'] = df['Team'] + '_' + np.where(df['Subtype'].notna(), df['Subtype'], df['Type']) # TODO: Do in preprocessing?
        hover_labels = [f"<b>{row['Type']}</b><br>At: {format_time(row['Time'])}" for _, row in g_df.iterrows()]
    return create_timeline(g_df, hover_labels, x_size, "3") # xyref is the 3rd subplot

def get_structures_timeline(df: pd.DataFrame, x_size: int) -> go.Figure:
    """ Creates a timeline of destroyed structures over time. 
    Should receive the data for a single match, or aggregated data"""
    df['Time'].astype(float,False)
    g_df = df.groupby(['Type','Lane','Team']).aggregate(count=('Type','size'),Time=('Time','mean')).sort_values('Time').reset_index()
    # Team column is destroyer team -> destroyed (Blue turret destroyed)    
    g_df.loc[:,'icon_name'] = g_df['Team'].replace({'BLUE': 'RED', 'RED': 'BLUE'}) + '_' + np.where(g_df['Type'] == 'INHIBITOR', 'INHIBITOR', 'TURRET')
    hover_labels = [f"<b>{row['Lane']} {f"{row['Type']} Turret" if row['Type']!="INHIBITOR" else row['Type']}</b><br>At: {format_time(row['Time'])}{"<br>Count: "+str(row['count']) if df['match_id'].unique().size > 1 else ""}" for _, row in g_df.iterrows()]
    return create_timeline(g_df, hover_labels, x_size, "4") # xyref is the 4th subplot

def create_kills_timeline(df: pd.DataFrame, team_name_col: List[(str)], hover_labels: List[str]) -> go.Figure:
    """ Creates a timeline using df's data, df needs columns: 'count', 'Time' and 'icon_name'.
    Labels to show when hovering given separately.
    """

    fig = go.Figure()
    y_mod = 0
    max_size = df['count'].max()
    for team_name, color in team_name_col:
        team_data = df[df['Team'] == team_name]
        y_mod += 1

        fig.add_trace(
            go.Scatter(
                x=team_data['Time'],
                y=np.zeros(team_data.shape[0])+y_mod,
                mode='markers',
                name=team_name,
                legendgroup=team_name,  # Link traces with same team
                marker=dict(size=30*team_data['count']/max_size, sizemin=6,color=color),
                hoverinfo='text',
                text=hover_labels,
                showlegend=False
            )
        )

    #set_timeline_margins_scale(fig, x_size, [0,2], np.ones(df.shape[0]))
    return fig, [1,2], 3

def get_kills_timeline(df: pd.DataFrame) -> go.Figure:
    """ Creates a timeline of killed neutral objectives over time. 
    Should receive the data for a single match, or aggregated data"""
    # Team column is killer team
    if df['match_id'].unique().size == 1:
        df_g = df.copy()    # To avoid warning

        assist_columns = ["Assist_1", "Assist_2", "Assist_3", "Assist_4"]
        hover_labels = [f"<b>{row['Victim']}</b><br>By: {row['Killer']}<br>Assisted by: {combine_assists(row, assist_columns)}<br>At: {format_time(row['Time'])}" for _, row in df_g.iterrows()]

        blue_team = df_g.loc[df_g['Team'] == 'BLUE', 'Killer_Team'].iloc[0] # Note, killer perspective, so BLUE means blue killer and red victim
        red_team = df_g.loc[df_g['Team'] == 'BLUE', 'Victim_Team'].iloc[0]

        df_g.loc[:,'Team'] = np.where(df_g['Team'] == 'BLUE', red_team, blue_team) # Invert color on the map, more user friendly if a dot fits the player who died
        df_g.loc[:,'count'] = 1 # Just to be consistent with the aggregated version and have a "count" column for the size
        team_name_col=[(red_team,'red'),(blue_team,'blue')]
    else: 
        # Do not consider Subtype in aggregate, because too much detail
        df_g = df.groupby(['cardinality','Team']).aggregate(count=('Team','count'),Time=('Time','mean')).sort_values('Time').reset_index()
        hover_labels = [f"Count: {row['count']}<br>At: {format_time(row['Time'])}<br>Cardinality: {row['cardinality']}" for _, row in df_g.iterrows()]
        df_g.loc[:,'Team'] = np.where(df_g['Team'] == 'BLUE', "Red Side", "Blue Side")
        team_name_col=[("Red Side", "red"), ("Blue Side", "blue")]
    return create_kills_timeline(df_g, team_name_col, hover_labels)

def get_map_timeline_mplot(dfkills, dfmons, dfstruct, matchinfo):
    """Creates subplots for map and timelines"""
    # TODO: get timeframe filter and apply
    # time_filtered_kills = filtered_kills.applytimefilter
    # TODO: get whether heatmap or scatter, note if single match heatmap looks bad
    heatmap = False
    # TODO: get binsize from selector? We can fix it at 50, or fix at 25/50 for normal map and 100 for heatmap
    binsize = 50

    # Fix preliminary values
    map_size = 14650 # This is how it is
    row_h = [0.6,0.13,0.13,0.14] # Give priority to map

    # Compute xaxis size based on my gamelength of !filtered! data
    x_size = matchinfo['gamelength'].max() + 1  # TODO: REPLACE THIS WITH MAX X + 1 IF TIMEFILTER

    # Create the traces
    if heatmap:
        fig1 = get_kill_heatmap(dfkills, binsize)   # recommend 100 (50 OK), else ugly
    else:
        fig1 = get_kill_plot(dfkills, binsize)  # reccommend 50 max else laggy
    fig2,fig2_yvals,fig2_y_max = get_kills_timeline(dfkills)
    fig3,fig3_yvals,fig3_y_max, fig3imgs = get_monsters_timeline(dfmons, x_size)
    fig4,fig4_yvals,fig4_y_max, fig4imgs = get_structures_timeline(dfstruct, x_size)

    # create subplots
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=False,
        row_heights=row_h,
        vertical_spacing=0.1,
        subplot_titles=("Map", "Kills Timeline", "Monsters Timeline", "Structures Timeline")
    )

    # Add figure 1 (map) to subplots
    for trace in fig1.data:
        fig.add_trace(trace, row=1, col=1)
    # Enforce square map (equal unit scale)
    fig1_axis_common = {"showline": False, "showticklabels": False, "row":1, "col":1, "showgrid":False}
    fig.update_yaxes(range=[0, map_size], **fig1_axis_common)
    fig.update_xaxes(range=[0, map_size], scaleanchor='y', **fig1_axis_common)
    map_bg_img = get_map_bg("x1","y1",map_size) # Dict to be added to list of images set alter

    # yaxis related settings that are fix for timelines
    timeline_axes_common = {"visible":True, "showline":True, "linecolor":'gray',"gridcolor":'gray',"showticklabels":False, "col":1, "autorange":False, "fixedrange":True}

    # Add figure 2 (kills timeline)
    for trace in fig2.data:
        fig.add_trace(trace, row=2, col=1)
    fig.update_yaxes(
        range=[0,fig2_y_max],  # pad the view: consider icon size
        tickvals=fig2_yvals,   # To put horizontal lines at level of icons
        row=2, **timeline_axes_common
    )
    # Add figure 3 (monsters timeline)
    for trace in fig3.data:
        fig.add_trace(trace, row=3, col=1)
    fig.update_yaxes(
        range=[0,fig3_y_max],  # pad the view: consider icon size
        tickvals=fig3_yvals,   # To put horizontal lines at level of icons
        row=3, **timeline_axes_common
    )
    # Add figure 4 (structures timeline)
    for trace in fig4.data:
        fig.add_trace(trace, row=4, col=1)
    fig.update_yaxes(
        range=[0,fig4_y_max],  # pad the view: consider icon size
        tickvals=fig4_yvals,   # To put horizontal lines at level of icons
        row=4, **timeline_axes_common
    )

    fig.layout.images = fig3imgs+fig4imgs+[map_bg_img]  # Add images, monster, structure icons and map bg
    set_timeline_margins_scale(fig, x_size)

    return fig