# components/kills_tab.py
from dash import html, dcc


def minutes_to_label(mins):
    if mins % 5 == 0:
        return f"{int(mins)}m"
    return ""

# Generate marks from min to max (e.g., 0 to 60)
marks = {i: minutes_to_label(i) for i in range(0, 61)}  # 0 to 60 minutes



def kills_tab_layout():
    return html.Div([
        html.Div([
            dcc.Graph(id="map-graph", style={"flex": "2"}),
            html.Div(id="event-list", style={
                "flex": "1", "overflowY": "auto", "maxHeight": "600px"
            }),
        ], style={"display": "flex", "gap": "20px"}),

        html.Div([
            dcc.Graph(
                id="timeline-fig",
                config={"displayModeBar": False},
                style={
                    "height": "100px",  # Set the height of the timeline graph to make it visually appropriate
                    "marginTop": "10px",  # Add margin to the top for spacing
                    "padding": "0 1%"  # Add padding to the left and right sides
                }
            ),
            dcc.RangeSlider(
                min=0, max=60, step=1, value=[0, 60],
                id="time-slider",
                tooltip={"placement": "bottom"},
                marks=marks  # your formatted time labels
            ),
            
            dcc.Checklist(id="team-filter",
                          options=[{"label": "Blue", "value": "Blue"}, {"label": "Red", "value": "Red"}],
                          value=["Blue", "Red"], inline=True),
            dcc.RadioItems(id="map-style",
                           options=[{"label": "Heatmap", "value": "Heatmap"},
                                    {"label": "Satellite", "value": "Satellite"},
                                    {"label": "Schematic", "value": "Schematic"}],
                           value="Schematic", inline=True)
        ], style={"padding": "0 10px"}),  # Additional padding for the whole section
        
        # html.Div([
        #     html.Div([
        #         dcc.Graph(id="kill-podium", style={"height": "500px"})
        #     ], style={"width": "48%", "display": "inline-block"}),

        #     html.Div([
        #         dcc.Graph(id="assist-podium", style={"height": "500px"})
        #     ], style={"width": "48%", "display": "inline-block", "float": "right"}),
        # ], style={"marginTop": "40px"})
        html.Div([
    html.Div([
        dcc.Graph(
            id="kill-podium",
            style={"height": "500px"},
            config={"staticPlot": True, "displayModeBar": False}
        )
    ], style={"width": "48%", "display": "inline-block"}),

    html.Div([
        dcc.Graph(
            id="assist-podium",
            style={"height": "500px"},
            config={"staticPlot": True, "displayModeBar": False}
        )
    ], style={"width": "48%", "display": "inline-block", "float": "right"}),
], style={"marginTop": "40px"})

    ])
