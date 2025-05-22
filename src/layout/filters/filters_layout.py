from dash import html, dcc
import dash_ag_grid as dag
from typing import List
from layout.filters.callbacks import get_metadata_df

def filters_layout() -> List[html.Div]: 
    return [
        filters_metadata(),
        dcc.Store(id='stored_metadata_filtered'),
        dcc.Store(id='metadata_filtered_columns'),
        filters_team_player_position(),
        dcc.Store(id='stored_team_player_position_filtered'),
        dcc.Store(id='team_player_position_filtered_columns'),
        dcc.Store(id='stored_match_ids'),
        # filter_champions(),
        filter_games(),
        dcc.Store(id='stored_games_filtered'),
        dcc.Store(id='games_filtered_columns'),
        html.Button('Reset all filters', id='filters_all_reset', n_clicks=0, style={'margin': '10px'}),
    ]

def filters_metadata() -> html.Div: # TODO changer les checbox en ag grid pour toujours simplement filtrer sur les match_id
    columnDefs = [
        {
            "headerName": "Year",
            "field": "Year",
            "filter": "agSetColumnFilter",
        },
        {
            "headerName": "Season",
            "field": "Season",
            "filter": "agSetColumnFilter",
        },
        {
            "headerName": "League",
            "field": "League",
            "filter": "agSetColumnFilter",
        },
        {
            "headerName": "Type",
            "field": "Type",
            "filter": "agSetColumnFilter",
        },
    ]

    defaultColDef = {"flex": 1, "filter": True}

    grid = dag.AgGrid(
        enableEnterpriseModules=True,
        id="filter_metadata",
        rowData=get_metadata_df(),
        columnDefs=columnDefs,
        defaultColDef=defaultColDef,
        dashGridOptions={"sideBar": "filters", "suppressRowClickSelection": True, "animateRows": False},
        style={"height": 300}, # TODO changer la taille des rows pour qu'elles soient plus fines
    )

    return \
        html.Div([
            html.Details([
                html.Summary(html.B('Choose data to analyse')),
                grid,
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
                grid,
                html.Button('Reset filters', id='filters_team_player_position_reset', n_clicks=0, style={'margin': '10px'}),
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
                grid,
                html.Button('Reset filters', id='filters_games_reset', n_clicks=0, style={'margin': '10px'}),
            ], open=True),
        ])