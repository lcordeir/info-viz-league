from dash import html, dcc
import dash_ag_grid as dag
from typing import List
from layout.filters.filtering import get_unique_values
from layout.filters.filtering import combine_team_player_position

def filters_layout() -> List: 
    return [
        filters_metadata(),
        filters_team_player_position(),
        filter_champions(),
        filter_games(),
        html.Button('Reset all filters', id='filters_all_reset', n_clicks=0, style={'margin': '10px'}),
    ]

def filters_metadata() -> html.Div:
    unique_years = get_unique_values('Year')
    unique_seasons = get_unique_values('Season')
    unique_leagues = get_unique_values('League')
    unique_types = get_unique_values('Type')

    return \
        html.Div([
            html.Details([
                html.Summary(html.B('Choose data to analyse')),
                html.Table([
                    # TODO changer tous les radioitems pour recevoir les options et value depuis un callback
                    html.Tr([
                        html.Td([html.B("Year"), dcc.Checklist(unique_years, unique_years, id='filter_year', inline=True)]),
                        html.Td([html.B("Season"), dcc.Checklist(unique_seasons, unique_seasons, id='filter_split', inline=True)])
                    ]),
                    html.Tr([
                        html.Td([html.B("League"), dcc.Checklist(unique_leagues, unique_leagues, id='filter_region', inline=True)]),
                        html.Td([html.B("Type"), dcc.Checklist(unique_types, unique_types, id='filter_type', inline=True)])
                    ])
                ], style = {'width': '100%',
                            'textAlign': 'left', 
                }),
                html.Button('Reset filters', id='filters_metadata_reset', n_clicks=0, style={'margin': '10px'}),
            ], open=True),
        ])


def filters_team_player_position() -> html.Div:
    df = combine_team_player_position()

    columnDefs = [
        {
            "headerName": "Teams",
            "field": "Teams",
            "filter": "agSetColumnFilter",
        },
        {
            "headerName": "Players",
            "field": "Players",
            "filter": "agSetColumnFilter",
        },
        {
            "headerName": "Position",
            "field": "Position",
            "filter": "agSetColumnFilter",
        },
    ]

    defaultColDef = {"flex": 1, "filter": True}

    grid = dag.AgGrid(
        id="filter_team_player_position",
        rowData=df.to_dict("records"),
        columnDefs=columnDefs,
        defaultColDef=defaultColDef,
        dashGridOptions={"sideBar": "filters"},
        style={"height": 300},
    )

    return \
        html.Div([
            html.Details([
                html.Summary('Filter by Teams, Players and Positions'),
                grid
            ], open=True),
        ])

def filter_champions() -> html.Div:
    return \
        html.Div([
            html.Details([
                html.Summary('Filter by champions'),
                html.Div([
                    "TODO"
                ]),
                html.Button('Reset filters', id='filters_champions_reset', n_clicks=0, style={'margin': '10px'}),
            ], open=False),
        ])

def filter_games() -> html.Div:
    return \
        html.Div([
            html.Details([
                html.Summary('Filter by games'),
                html.Div([
                    "TODO"
                ]),
                html.Button('Reset filters', id='filters_games_reset', n_clicks=0, style={'margin': '10px'}),
            ], open=False),
        ])