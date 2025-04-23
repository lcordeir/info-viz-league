from dash import html, dcc

def minutes_to_label(mins):
    if mins % 5 == 0:
        return f"{int(mins)}m"
    return ""

# Generate marks from min to max (e.g., 0 to 60)
marks = {i: minutes_to_label(i) for i in range(0, 61)}  # 0 to 60 minutes



def map_tab_layout():
    return html.Div([
        html.Div([
            dcc.Graph(id="map-graph"),
            html.Div([
                html.Details([
                    html.Summary(html.B('Choose data to analyse')),
                    html.Table([# TODO changer tous les radioitems pour recevoir les options et value depuis un callback
                        html.Tr([
                            html.Td([html.B("Year"), dcc.RadioItems(['2018', '2019','...'], '2018', id='year_map_filter', inline=True)]),
                            html.Td([html.B("Split"), dcc.RadioItems(['Spring', 'Summer'], 'Spring', id='split_map_filter', inline=True)])
                        ]),
                        html.Tr([
                            html.Td([html.B("Region"), dcc.RadioItems(['NALCS', 'EULCS', '...'], 'NALCS', id='region_map_filter', inline=True)]),
                            html.Td([html.B("Type"), dcc.RadioItems(['Season', 'Playoffs','...'], 'Season', id='type_map_filter', inline=True)])
                        ])
                    ])
                ], open=True),
                html.Details([
                    html.Summary('Filter by Team(s)/Player(s)/Position(s)'),
                    html.Div([
                        "TODO"
                    ]),
                ], open=False),
                html.Details([
                    html.Summary('Filter by champions'),
                    html.Div([
                        "TODO"
                    ]),
                ], open=False),
                html.Details([
                    html.Summary('Filter by games'),
                    html.Div([
                        "TODO"
                    ]),
                ], open=False)
            ]),
        ], style={"display": "flex", "gap": "20px"}),

        html.Div([
        #     dcc.Graph(
        #         id="timeline-fig",
        #         config={"displayModeBar": False},
        #         style={
        #             "height": "100px",  # Set the height of the timeline graph to make it visually appropriate
        #             "marginTop": "10px",  # Add margin to the top for spacing
        #             "padding": "0 1%"  # Add padding to the left and right sides
        #         }
        #     ),
        #     dcc.RangeSlider(
        #         min=0, max=60, step=1, value=[0, 60],
        #         id="time-slider",
        #         tooltip={"placement": "bottom"},
        #         marks=marks  # your formatted time labels
        #     ),
            
        #     dcc.Checklist(id="team-filter",
        #                   options=[{"label": "Blue", "value": "Blue"}, {"label": "Red", "value": "Red"}],
        #                   value=["Blue", "Red"], inline=True),
        #     dcc.RadioItems(id="map-style",
        #                    options=[{"label": "Heatmap", "value": "Heatmap"},
        #                             {"label": "Satellite", "value": "Satellite"},
        #                             {"label": "Schematic", "value": "Schematic"}],
        #                    value="Schematic", inline=True)
        ], style={"padding": "0 10px"})  # Additional padding for the whole section
    ])
