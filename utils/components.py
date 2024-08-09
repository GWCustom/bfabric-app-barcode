import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd
import dash_table

DEVELOPER_EMAIL = "griffin@gwcustom.com"

button_style = {"min-width":"100%","max-width":"100%","font-size":"20px"}

default_sidebar = [
    
    dcc.Dropdown(
        id='order_input',
        placeholder='Select order',
        style=button_style,
    ),
    html.P(),
    dbc.Button('Load / Reload', id='load-val', n_clicks=0, style=button_style),
    html.P(),
    html.P(),
    dbc.Button('Swap Indices', id='swap', n_clicks=0, style=button_style, color='secondary'),
    html.P(),
    dbc.Button('RevComp index 1', id='RC1', n_clicks=0, style=button_style, color='secondary'),
    html.P(),
    dbc.Button('RevComp index 2', id='RC2', n_clicks=0, style=button_style, color='secondary'),
    html.P(),
    dbc.Button('RevSeq index 1', id='RS1', n_clicks=0, style=button_style, color='secondary'),
    html.P(),
    dbc.Button('RevSeq index 2', id='RS2', n_clicks=0, style=button_style, color='secondary'),
    html.P(),
    dbc.Button('Trim index 1', id='Tr1', n_clicks=0, style=button_style, color='secondary'),
    html.P(),
    dbc.Button('Trim index 2', id='Tr2', n_clicks=0, style=button_style, color='secondary'),
    html.P(),
    dbc.Button('Set index 1', id='Set1', n_clicks=0, style=button_style, color='secondary'),
    html.P(),
    dbc.Button('Set index 2', id='Set2', n_clicks=0, style=button_style, color='secondary'),
    html.P(),
    dcc.Input(
        id="reset_value",
        placeholder="reset value",
        style={**button_style, **{'color':'black'}}
    ),
    html.P(),
    dbc.Button('Clear DMX barcodes', id='reset', n_clicks=0, style=button_style),
    html.P(),
    dbc.Button('check / uncheck all', id='check', n_clicks=0, style=button_style),
    html.P(),
    dbc.Button('Update Bfabric', id='update', n_clicks=0, color='danger', style=button_style),
]

no_auth = [
    html.P("You are not currently logged into an active session. Please log into bfabric to continue:"),
    html.A('Login to Bfabric', href='https://fgcz-bfabric.uzh.ch/bfabric/')
]

expired = [
    html.P("Your session has expired. Please log into bfabric to continue:"),
    html.A('Login to Bfabric', href='https://fgcz-bfabric.uzh.ch/bfabric/')
]

no_entity = [
    html.P("There was an error fetching the data for your entity. Please try accessing the applicaiton again from bfabric:"),
    html.A('Login to Bfabric', href='https://fgcz-bfabric.uzh.ch/bfabric/')
]

dev = [html.P("This page is under development. Please check back later."),html.Br(),html.A("email the developer for more details",href="mailto:"+DEVELOPER_EMAIL)]

auth = [
    html.Div(
        id="auth-div",
        children=[
            html.Div(
                id="graph_header"
            ),
            html.Div(
                id="div-graphs-bc",
                children=[
                    dash_table.DataTable(
                        id="barcode_table",
                        data = pd.DataFrame().to_dict('records'),
                        columns = [],
                    )
                ],
                style={"max-width":"70vw", "margin-left":"2vw", "margin-top":"2vh", "overflow-y":"scroll", "max-height":"60vh"}
            )
        ]
    )
]