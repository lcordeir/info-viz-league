import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def generate_kill_map(kills, map_style="Schematic", team_filter=["Blue", "Red"]):

    # Map Image Source
    if map_style == "Heatmap":
        # map_image = "https://i.sstatic.net/cPVCwl.jpg"
        map_image = "/assets/heatmap.webp"
    elif map_style == "Satellite":
        # map_image = "https://i.imgur.com/ObEp8yn.jpg"
        # map_image = "https://i.imgur.com/cP9aXpq.jpeg"
        # map_image = "https://i.imgur.com/etO73Wl.jpeg"
        map_image = "/assets/satellite.jpeg"
    else:
        # map_image = "https://preview.redd.it/fgrxon2d9km71.png?width=750&format=png&auto=webp&s=6e0157b2ec829080cb4f137c1e9aa99a3f0f30cd"
        map_image = "/assets/schematic.webp"
    
    print(f"Using map image: {map_image}")
    
    # Create the plot
    fig = go.Figure()

    # Add the map image as the background (fixed axes)
    fig.add_layout_image(
        dict(
            source=map_image,
            x=0,
            y=16000,
            xref="x",
            yref="y",
            sizex=16000,  # Adjusted to fit the map's scale (lower values)
            sizey=16000,  # Adjusted to fit the map's scale (lower values)
            opacity=0.5,
            layer="below"
        )
    )

    # print(len(kills))
    # Add kill points on top of the map
    for _, kill in kills.iterrows():
        # print(f"X: {kill['x']}")
        # print(f"Y: {kill['y']}")
        fig.add_trace(go.Scatter(
            x=[kill["x"]],
            y=[kill["y"]],
            mode="markers",
            marker=dict(
                size=10,
                color="red" if kill["Team"] == "Red" else "blue",
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
            color=np.where(kills_df["Team"] == "Red", "red", "blue"),
            symbol="line-ns-open"
        ),
        hovertext=kills_df.apply(lambda row: f"{row['Killer']} → {row['Victim']} ({row['Time']:.2f}m)", axis=1),
        hoverinfo="text",
        showlegend=False
    ))

    fig.update_layout(
        xaxis=dict(range=[0, 60]),
        yaxis=dict(visible=False),  # hide y-axis
        height=100,
        margin=dict(l=0, r=0, t=30, b=0),
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


def generate_podium(kills_df):
    # Count kills and assists
    top_kills = kills_df["Killer"].value_counts().nlargest(3)
    assist_cols = [col for col in kills_df.columns if col.startswith("Assist_")]
    top_assists = kills_df[assist_cols].stack().value_counts().nlargest(3)

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

    return (
        podium_figure(top_kills, "Top 3 Killers"),
        podium_figure(top_assists, "Top 3 Assisters")
    )

