from dash import html, dcc

def minutes_to_label(mins):
    if mins % 5 == 0:
        return f"{int(mins)}m"
    return ""

# Generate marks from min to max (e.g., 0 to 60)
marks = {i: minutes_to_label(i) for i in range(0, 91)}  # 0 to 90 minutes - Really shouldn't be hardcoded, but low priority now



def map_layout() -> list:
    return [
        html.Div([
            html.Div([

                # SLIDER
                dcc.RangeSlider(
                    min=0, max=90, step=1, value=[0, 90],
                    id="time-slider",
                    tooltip={"placement": "bottom"},
                    marks=marks  # your formatted time labels
                ),
            ], style={
                "position": "relative"}),
            # Container with relative positioning
            html.Div([
                # Full-size map graph
                dcc.Graph(id="map-graph", style={
                    "height": "100vh",
                    "width": "100%",
                }),

                 html.Div([
                    dcc.RadioItems(
                        id="map-style",
                        options=[
                            {"label": "Heatmap", "value": "Heatmap"},
                            # {"label": "Satellite", "value": "Satellite"},
                            {"label": "Schematic", "value": "Schematic"}
                        ],
                        value="Schematic",
                        inline=True,
                        style={"marginBottom": "1vh"}  # spacing below radios
                    ),

                    html.Div(id="event-list", style={
                        "overflowY": "auto",
                        "maxHeight": "37vh"
                    }),
                ], style={
                    "position": "absolute",
                    "top": "20px",
                    "right": "20px",
                    "height": "40vh",
                    "width": "10vw",
                    "overflowY": "auto",
                    "backgroundColor": "rgba(255, 255, 255, 0.9)",
                    "border": "1px solid #ccc",
                    "padding": "10px",
                    "zIndex": 10,
                    "borderRadius": "8px"
                }),
            ], style={"position": "relative"}),
        ]),

    ]