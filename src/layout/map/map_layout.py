from dash import html, dcc

def minutes_to_label(mins):
    if mins % 5 == 0:
        return f"{int(mins)}m"
    return ""

# Generate marks from min to max (e.g., 0 to 60)
marks = {i: minutes_to_label(i) for i in range(0, 61)}  # 0 to 60 minutes



def map_layout() -> list:
    return [
        html.Div([
            # Container with relative positioning
            html.Div([
                # Full-size map graph
                dcc.Graph(id="map-graph", style={
                    "height": "100vh",
                    "width": "100%",
                }),

                # Overlaid event list
                html.Div(id="event-list", style={
                    "position": "absolute",
                    "top": "20px",  # padding from top
                    "right": "20px",  # padding from right
                    "height": "50vh",
                    "width": "10vw",  # or adjust as needed
                    "overflowY": "auto",
                    "backgroundColor": "rgba(255, 255, 255, 0.9)",  # semi-transparent
                    "border": "1px solid #ccc",
                    "padding": "10px",
                    "zIndex": 10,  # ensure it's above the graph
                    "borderRadius": "8px"
                }),
            ], style={"position": "relative"}),
        ]),
    
        html.Div([
            html.Div([

                # SLIDER
                dcc.RangeSlider(
                    min=0, max=60, step=1, value=[0, 60],
                    id="time-slider",
                    tooltip={"placement": "bottom"},
                    marks=marks  # your formatted time labels
                ),
            ], style={}),
                
                # MAP STYLE RADIO
                dcc.RadioItems(id="map-style",
                            options=[{"label": "Heatmap", "value": "Heatmap"},
                                        {"label": "Satellite", "value": "Satellite"},
                                        {"label": "Schematic", "value": "Schematic"}],
                            value="Schematic", inline=True)
            ], style={"padding": "0 10px"}),

    ]