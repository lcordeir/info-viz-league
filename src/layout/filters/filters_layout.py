from dash import html, dcc
import dash_ag_grid as dag
from typing import List
from layout.filters.filtering import get_unique_values

def filters_layout() -> List: 
    return [
        filters_metadata(),
        dcc.Store(id='stored_intermediate_match_info'),
        dcc.Store(id='match_info_columns'),
        filters_team_player_position(),
        # filter_champions(),
        filter_games(),
        dcc.Store(id='stored_filtetered_match_info'),
        html.Button('Reset all filters', id='filters_all_reset', n_clicks=0, style={'margin': '10px'}),
    ]

def filters_metadata() -> html.Div:
    unique_years = sorted(get_unique_values('Year'))
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
                        html.Td([html.B("Season"), dcc.Checklist(unique_seasons, unique_seasons, id='filter_season', inline=True)])
                    ]),
                    html.Tr([
                        html.Td([html.B("League"), dcc.Checklist(unique_leagues, unique_leagues, id='filter_league', inline=True)]),
                        html.Td([html.B("Type"), dcc.Checklist(unique_types, unique_types, id='filter_type', inline=True)])
                    ])
                ], style = {'width': '100%',
                            'textAlign': 'left', 
                }),
                html.Button('Reset filters', id='filters_metadata_reset', n_clicks=0, style={'margin': '10px'}),
            ], open=True),
        ])


def filters_team_player_position() -> html.Div:
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
        enableEnterpriseModules=True,
        id="filter_team_player_position",
        # rowData=df.to_dict("records"),
        columnDefs=columnDefs,
        defaultColDef=defaultColDef,
        dashGridOptions={"sideBar": "filters", "suppressRowClickSelection": True, "animateRows": False},
        style={"height": 300}, # TODO changer la taille des rows pour qu'elles soient plus fines
    )

    return \
        html.Div([
            html.Details([
                html.Summary('Filter by Teams, Players and Positions'),
                grid
            ], open=False),
        ])

# def filter_champions() -> html.Div:
#     return \
#         html.Div([
#             html.Details([
#                 html.Summary('Filter by champions'),
#                 html.Div([
#                     "TODO"
#                 ]),
#                 html.Button('Reset filters', id='filters_champions_reset', n_clicks=0, style={'margin': '10px'}),
#             ], open=False),
#         ])

def filter_games() -> html.Div:
    columnDefs = [
        {
            "headerName": "Match nr.",
            "field": "match_id",
            "checkboxSelection": True,
            "headerCheckboxSelection": True,
        },
        {
            "headerName": "Year",
            "field": "Year",
        },
        {
            "headerName": "League",
            "field": "League",
        },
        {
            "headerName": "Season",
            "field": "Season",
        },
        {
            "headerName": "Type",
            "field": "Type",
        },
        {
            "headerName": "Game length",
            "field": "gamelength",
        },
        {
            "headerName": "Blue result",
            "field": "bResult",
        },
        {
            "headerName": "Blue team",
            "field": "blueTeamTag",
        },
        {
            "headerName": "Red team",
            "field": "redTeamTag",
        },
        {
            "headerName": "Red result",
            "field": "rResult",
        },
    ]

    defaultColDef = {"flex": 1, "filter": True}
    defaultColDef = {
        "flex": 1,
        "filter": True,
    }

    grid = dag.AgGrid(
        enableEnterpriseModules=True,
        id="filter_games",
        # rowData=df.to_dict("records"),
        columnDefs=columnDefs,
        defaultColDef=defaultColDef,
        dashGridOptions={"rowSelection": "multiple", "suppressRowClickSelection": True, "animateRows": False},
        style={"height": 300}, # TODO changer la taille des rows pour qu'elles soient plus fines
    )

    return \
        html.Div([
            html.Details([
                html.Summary('Filter by games'),
                grid
            ], open=True),
        ])