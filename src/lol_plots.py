
import pandas as pd

import numpy as np

import plotly as plt
import plotly.express as px
import plotly.graph_objs as go

from typing import Optional, List
import os, math

from utils import format_time, encode_image_to_base64

MAPICONS_PATH = os.path.join("ressources","mapicons")

# === MAP ===

def add_map_bg(fig: go.Figure) -> go.Figure:
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

def combine_assists(row: pd.Series, assist_cols: List[str]) -> Optional[str]:
    assists = [str(row[col]) for col in assist_cols if pd.notna(row[col])]
    return ", ".join(assists) if assists else None

def get_kill_plot_single(df: pd.DataFrame) -> go.Figure:
    assist_columns = ["Assist_1", "Assist_2", "Assist_3", "Assist_4"]
    df['hover_labels'] = [f"<b>{row['Victim']}</b><br>By: {row['Killer']}<br>Assisted by: {combine_assists(row, assist_columns)}<br>At: {format_time(row['Time'])}" for _, row in df.iterrows()]
    red_team = np.where(df['Team']=="BLUE",df['Victim_Team'],df['Killer_Team'])[0] # Data being "kills", Team colour relates to killer team. More intuitive for user to have the victim's colour -> "A blue player died there"
    blue_team = np.where(df['Team']=="RED",df['Victim_Team'],df['Killer_Team'])[0]
    fig = px.scatter(
        data_frame=df,
        x=df['x_pos'],
        y=df['y_pos'],
        title="Deaths",
        width=800,
        height=800,
        color='Victim_Team',
        color_discrete_map={blue_team:'blue',red_team:'red'},
        labels={'Victim_Team':'Team'},
        custom_data=['hover_labels'],  # Pass hover_labels as custom_data
    )
    fig.update_traces(
        marker=dict(size=15),
        hovertemplate="%{customdata[0]}<extra></extra>"  # Use only the value from custom_data
        )
    df.drop(columns=['hover_labels'],inplace=True)
    return fig

def get_kill_plot_aggregate(df: pd.DataFrame, heatmap_binsize: int) -> go.Figure:
    df_div = df.copy()
    df_div['x_pos'] = (df_div['x_pos']/df['x_pos'].max()*heatmap_binsize).apply(math.floor)
    df_div['y_pos'] = (df_div['y_pos']/df['y_pos'].max()*heatmap_binsize).apply(math.floor)
    df_div = df_div.groupby(['x_pos', 'y_pos', 'Team']).agg(count=('Time', 'count'),avg_time=('Time', 'mean')).reset_index()
    df_div['Team'] = np.where(df_div['Team'] == 'BLUE', "Red Side", " Blue Side")
    df_div['hover_labels'] = [f"<b>Count: {row['count']}</b><br>At: {format_time(row['avg_time'])}" for _, row in df_div.iterrows()]
    fig = px.scatter(
        data_frame=df_div,
        y=df_div['y_pos'],
        x=df_div['x_pos'],
        title="Deaths",
        width=800,
        height=800,
        color='Team',
        #color_discrete_map={'RED':'blue','BLUE':'red'},
        size='count',
        custom_data=['hover_labels'],  # Pass hover_labels as custom_data
    )
    fig.update_traces(
        hovertemplate="%{customdata[0]}<extra></extra>"  # Use only the value from custom_data
        )
    return fig

def get_kill_plot(df: pd.DataFrame, heatmap_binsize: int = 25) -> go.Figure:
    if df['match_id'].unique().size == 1: fig = get_kill_plot_single(df)
    else: fig = get_kill_plot_aggregate(df, heatmap_binsize)
    add_map_bg(fig)
    return fig

def get_kill_heatmap(df: pd.DataFrame, heatmap_binsize: int):
    fig=px.density_heatmap(
        x=df['x_pos'],
        y=df['y_pos'],
        nbinsx=heatmap_binsize, # Define "size" of blocks
        nbinsy=heatmap_binsize,
        title="Kills",
        width=800,
        height=800,
        color_continuous_scale='Viridis'
        )
    add_map_bg(fig)
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

# TODO: Might have to give 'x_size' in function of highest Time value of any timeline data
def create_timeline(df: pd.DataFrame, hover_labels: List[str]) -> go.Figure:
    """ Creates a timeline using df's data, df needs columns: 'count', 'Time' and 'icon_name'.
    Labels to show when hovering given separately.
    """
    fig = go.Figure()
    
    x_size = df['Time'].max() + 1
    
    tot_count = df['count'].sum()
    df['size'] = x_size/100+10*(df['count']/tot_count)  # Base size related with x axis and scales with proportion
    max_s_icon = df['size'].max()

    # x_tol defines when a neighbouring icon is to be offset by y_step. Both in funciton of icon size
    x_tol = max_s_icon*0.15
    y_step = max_s_icon

    y_values = []
    previous_x = -100
    previous_y = y_step
    # Add one image per event
    for _, row in df.iterrows():
        img_path = f'../ressources/mapicons/{row['icon_name']}.png'
        x = row['Time']
        if x-(previous_x+x_tol) < 0: y = previous_y+y_step
        else: y = y_step
        if os.path.exists(img_path):
            fig.add_layout_image(
                source=encode_image_to_base64(img_path),
                x=x,
                y=y,
                xref="x",
                yref="y",
                sizex=row['size'],
                sizey=row['size'],
                xanchor="center",
                yanchor="middle",
                layer="above"
            )
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
    fig.update_layout(
        xaxis=dict(
            range=[0, x_size],  # pad the view: game time
            #title="Time",
            showline=False,
            showticklabels=True,
            tickmode='auto',
        ),
        yaxis=dict(
            range=[0, max(y_values)+max_s_icon],  # pad the view: consider icon size
            visible=True,
            showline=True,
            showticklabels=False,
            tickvals=np.unique(y_values),   # To put horizontal lines at level of icons
        ),
        margin=dict(t=40, b=40), # TODO: DETERMINED BY DASH?
        height=200, # TODO: DETERMINED BY DASH?
    )
    return fig

def get_monsters_timeline(df: pd.DataFrame) -> go.Figure:
    """ Creates a timeline of killed neutral objectives over time. 
    Should receive the data for a single match, or aggregated data"""
    # Team column is killer team
    if df['match_id'].unique().size > 1:
        # Do not consider Subtype in aggregate, because too much detail
        g_df = df.groupby(['Type','type_cardinality','Team']).aggregate(count=('Type','size'),Time=('Time','mean')).sort_values('Time').reset_index()
        g_df['icon_name'] = g_df['Team'] + '_' + g_df['Type'] # TODO: Do in preprocessing?
        hover_labels = [f"<b>{row['Type']}</b><br>At: {format_time(row['Time'])}<br>Count: {row['count']}" for _, row in g_df.iterrows()]
    else: 
        g_df = df
        g_df['count'] = 1
        g_df['icon_name'] = df['Team'] + '_' + np.where(df['Subtype'].notna(), df['Subtype'], df['Type']) # TODO: Do in preprocessing?
        hover_labels = [f"<b>{row['Type']}</b><br>At: {format_time(row['Time'])}" for _, row in g_df.iterrows()]
    return create_timeline(g_df, hover_labels)

def get_structures_timeline(df: pd.DataFrame) -> go.Figure:
    """ Creates a timeline of destroyed structures over time. 
    Should receive the data for a single match, or aggregated data"""
    df['Time'].astype(float,False)
    g_df = df.groupby(['Type','Lane','Team']).aggregate(count=('Type','size'),Time=('Time','mean')).sort_values('Time').reset_index()
    # Team column is destroyer team -> destroyed (Blue turret destroyed)    
    g_df['icon_name'] = g_df['Team'].replace({'BLUE': 'RED', 'RED': 'BLUE'}) + '_' + np.where(g_df['Type'] == 'INHIBITOR', 'INHIBITOR', 'TURRET')
    hover_labels = [f"<b>{row['Lane']} {f"{row['Type']} Turret" if row['Type']!="INHIBITOR" else row['Type']}</b><br>At: {format_time(row['Time'])}{"<br>Count: "+str(row['count']) if df['match_id'].unique().size > 1 else ""}" for _, row in g_df.iterrows()]
    return create_timeline(g_df, hover_labels)