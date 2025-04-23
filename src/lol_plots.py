
import pandas as pd
import plotly as plt
import plotly.express as px
import plotly.graph_objs as go
from typing import Optional, List
from os import path as pt

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
            source=encode_image_to_base64(f"{pt.join(MAPICONS_PATH,elem)}.png"),
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


def get_structures_timeline(df: pd.DataFrame) -> go.Figure:
    """ Creates a timeline of destroyed structures over time. Should receive the data for a single match."""
    df['Time'].astype(float,False)
    fig = px.scatter(
        data_frame=df,
        x='Time',
        y=[""] * len(df),  # Keeps all points on a horizontal line
        color='Team',
        symbol='Type',
    )
    fig.update_traces(marker=dict(size=15))

    return fig