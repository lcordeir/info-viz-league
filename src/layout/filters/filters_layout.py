from dash import html, dcc

def filters_layout() -> list: 
    return [
        html.Details([
            html.Summary(html.B('Choose data to analyse')),
            html.Table([
                # TODO changer tous les radioitems pour recevoir les options et value depuis un callback
                # TODO changer les boutons pour qu'ils puissent recevoir plus que une seule valeur
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
    ]