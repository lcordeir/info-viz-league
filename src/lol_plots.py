
import pandas as pd

import numpy as np

import plotly as plt
import plotly.express as px
import plotly.graph_objs as go

from typing import Optional, List
import os

from utils import format_time, encode_image_to_base64

MAPICONS_PATH = pt.join("ressources","mapicons")

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

def get_kill_plot(df: pd.DataFrame) -> go.Figure:
    assist_columns = ["Assist_1", "Assist_2", "Assist_3", "Assist_4"]
    assists = df.apply(lambda x: combine_assists(x, assist_columns), axis=1)
    formatted_time = df['Time'].apply(lambda x: format_time(float(x)))
    fig = px.scatter(
        data_frame=df,
        x=df['x_pos'],
        y=df['y_pos'],
        title="Deaths",
        width=800,
        height=800,
        #color=df['Team'].apply(lambda x: 'RED' if x=='BLUE' else 'BLUE'), # Binds colour to victim (flip), more intuitive for the one looking
        color='Team',
        color_discrete_map={'RED':'blue','BLUE':'red'},
        labels={'Team':'Team','BLUE': 'Red', 'RED': 'Blue'},
        hover_name='Victim',
        hover_data={
            'x_pos': False,
            'y_pos': False,
            'Team': False,
            'At ': formatted_time,
            'Killer': True,
            'Assists': assists,
        }
    )
    fig.update_traces(marker=dict(size=15))
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

def create_timeline(df: pd.DataFrame, hover_labels: List[str], x_tol: float, y_step: float) -> go.Figure:
    """ Creates a timeline using df's data, df needs columns: 'Time' and 'icon_name'.
    Labels to show when hovering given separately. x_tol is the tolerance given to insert on the same line, y_step is to climb on y axis. 
    """
    fig = go.Figure()
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
                yref="paper",
                sizex=1,
                sizey=1,
                xanchor="center",
                yanchor="top",
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
                marker=dict(size=30, color='rgba(0,0,0,0)'),  # invisible
                hoverinfo='text',
                text=hover_labels,
                showlegend=False
            ))

    fig.update_layout(
        xaxis=dict(
            range=[df['Time'].min() - 1, df['Time'].max() + 1],  # pad the view
            #title="Time",
            showline=True,
            showticklabels=True,
            tickmode='auto',
        ),
        yaxis=dict(
            visible=False,
        ),
        margin=dict(t=40, b=40), # TODO: DETERMINED BY DASH?
        height=200, # TODO: DETERMINED BY DASH?
    )


def get_monsters_timeline(df: pd.DataFrame) -> go.Figure:
    """ Creates a timeline of killed neutral objectives over time. 
    Should receive the data for a single match, or aggregated data"""
    hover_labels = [f"At: {format_time(row['Time'])}" for _, row in df.iterrows()]
    # Team column is killer team
    df['icon_name'] = df['Team'] + '_' + np.where(df['Subtype'].notna(), df['Subtype'], df['Type']) # TODO: Do in preprocessing?
    return create_timeline(df, hover_labels, 0.33, 0.4)

def get_structures_timeline(df: pd.DataFrame) -> go.Figure:
    """ Creates a timeline of destroyed structures over time. 
    Should receive the data for a single match, or aggregated data"""
    df['Time'].astype(float,False)
    
    # Team column is destroyer team -> destroyed (Blue turret destroyed)
    df['icon_name'] = f"{df['Team'].replace({'BLUE': 'RED', 'RED': 'BLUE'})}_{np.where(df['Type'] == 'INHIBITOR', 'INHIBITOR', 'TURRET')}"
    hover_labels = [f"{row['Lane'] if "NEXUS" not in row['Type'] else row['Type'][:-1]+" "+row['Type'][-1]} {"Turret" if row['Type']!="INHIBITOR" else row['Type']}<br>At: {format_time(row['Time'])}" for _, row in df.iterrows()]
    return create_timeline(df, hover_labels, 0.25, 0.33)