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
                style={
                    "max-width":"70vw", 
                    "margin-left":"2vw", 
                    "margin-top":"2vh", 
                    # "overflow-y":"scroll", 
                    "max-height":"60vh"
                }
            )
        ]
    )
]

alerts = [
    dcc.Loading(
        [
            dbc.Alert(
                "Sample barcodes in bfabric have been updated",
                id="alert-fade",
                dismissable=True,
                is_open=False,
                color="success",
                style={"max-width":"50vw", "margin":"10px"}
            ),
            dbc.Alert(
                "Sample updates in bfbric have been queued. Please wait for the update to complete (up to 1 minute)",
                id="alert-fade-2",
                dismissable=True,
                color="info",
                is_open=False,
                style={"max-width":"50vw", "margin":"10px"}
            ),
            dbc.Alert(
                "An error occured while updating the barcodes in bfabric. Please try again.\n if the issue persists, please fill out and submit a bug report.",
                id="alert-fade-3",
                dismissable=True,
                color="danger",
                is_open=False,
                style={"max-width":"50vw", "margin":"10px"}
            ),
            dbc.Alert(
                "You're bug report has been submitted. Thanks for helping us improve!",
                id="alert-fade-bug",
                dismissable=True,
                is_open=False,
                color="info",
                style={"max-width":"50vw", "margin":"10px"}
            ),
            dbc.Alert(
                "Failed to submit bug report! Please email the developers directly at the email below!",
                id="alert-fade-bug-fail", 
                dismissable=True,
                is_open=False, 
                color="danger",
                style={"max-width":"50vw", "margin":"10px"}
            ),
        ]
    )
]

empty_sidebar = []


tab3_content = dbc.Row(
    id="page-content-main",
    children=[
        dbc.Col(
            html.Div(
                id="sidebar",
                children=default_sidebar,
                style={
                    "border-right": "2px solid #d4d7d9", 
                    "max-height": "65vh", 
                    "padding": "20px", 
                    "font-size": "20px",
                    "overflow-y":"scroll",
                }
            ),
            xl=2, lg=3, md=3, sm=3, xs=4
        ),
        dbc.Col(
            [
                dcc.Loading(
                    [
                        dcc.Store(id='token', storage_type='session'), # Where we store the actual token
                        dcc.Store(id='entity', storage_type='session'), # Where we store the entity data retrieved from bfabric
                        dcc.Store(id='token_data', storage_type='session'), # Where we store the token auth response
                        dcc.Store(id='original', storage_type='memory'),
                        dcc.Store(id='edited', storage_type='memory'),
                        dcc.Store(id='order-number', storage_type='session'),
                        dcc.Store(id='selectedRows', data=[0], storage_type='memory'),
                        dcc.Store(id='dummy-trigger', storage_type='session'),
                    ],
                ),
                dcc.Loading(
                    html.Div(
                        id="page-content",
                        children=no_auth + [
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
                                        style={
                                            "max-width":"70vw", 
                                            "margin-left":"2vw", 
                                            "margin-top":"2vh", 
                                            "overflow-y":"scroll", 
                                            "max-height":"60vh"
                                        }
                                    )
                                ]
                            )
                        ],style={
                            "margin-top":"2vh", 
                            "margin-left":"2vw", 
                            "font-size":"20px",
                            "overflow-y":"scroll",
                        },
                    ),
                # width=9,
                )
            ],
        )
    ],
    style={"margin-top": "0px", "min-height": "40vh", "height":"70vh", "max-height":"70vh"}
),

docs_tab = dbc.Row(
        id="page-content-docs",
        children=[
            dbc.Col(
                html.Div(
                    id="sidebar_docs",
                    children=empty_sidebar,
                    style={"border-right": "2px solid #d4d7d9", "height": "100%", "padding": "20px", "font-size": "20px"}
                ),
                width=3,
            ),
            dbc.Col(
                [html.Div(
                    id="page-content-docs-children",
                    children=[
                        html.H2("Welcome to The Barcode Dashboard"),
                        html.P([
                            "This app serves as a user interface for updating barcodes of run samples within bfabric."
                        ]),
                        html.Br(),
                        html.H4("Developer Info"),
                        html.P([
                            "This app was written by Griffin White, for the FGCZ. If you wish to report a bug, please use the \"bug reports\" tab. If you wish to contact the developer for other reasons, please use the email:",
                            html.A(" griffin@gwcustom.com", href="mailto:griffin@gwcustom.com"),
                        ]),
                        html.Br(),

                        html.H4("Some Notes on this App\'s Functionality"),
                        html.P([
                            """
                            This app is designed to allow users to update the barcodes of samples
                            in bfabric. """
                        ]),
                        html.Br(),
                        html.P([
                            """

                            This app communicates with the bfabric API to fetch and save data in bfabric.
                            However the bfabric API currently does not support updating whitespace as barcodes.
                            It is therfore impossible to set a barcode to an empty string, or a space (for instance). 
                            In cases where clearing out a barcode is imperative for successful demultiplexing, I reccomend 
                            setting the barcode to a placeholder value such as 'G', and then demultiplexing 
                            using the draugrUI with an additional barcode mismatch. 
                            """
                        ]),
                        html.Br(),
                        html.P("""
                            \n\n
                            The app uses in-memory storage to make it simple to reset the barcodes to their initial state (by simply refreshing the page).
                            However, this means that the app will not remember the state of the barcodes if the page is refreshed. 
                            Only refresh the page after you have saved the barcodes in bfabric, or if you wish to reset the barcodes to their initial state.
                            """
                        ),
                        html.H4("Update Barcodes Tab"),
                        html.P([
                            html.B(
                                "Load / Reload --"
                            ), " Load the order you'd like to update barcodes for.",
                            html.Br(),html.Br(),
                            html.B(
                                "Swap Indices --"
                            ), " Swap the indices of the selected rows.",
                            html.Br(),html.Br(),
                            html.B(
                                "RevComp index 1 --"
                            ), " Reverse complement the first index of the selected rows.",
                            html.Br(),html.Br(),
                            html.B(
                                "RevComp index 2 --"
                            ), " Reverse complement the second index of the selected rows.",
                            html.Br(),html.Br(),
                            html.B(
                                "RevSeq index 1 --"
                            ), " Reverse the sequence of the first index of the selected rows.",
                            html.Br(),html.Br(),
                            html.B(
                                "RevSeq index 2 --"
                            ), " Reverse the sequence of the second index of the selected rows.",
                            html.Br(),html.Br(),
                            html.B(
                                "Trim index 1 --"
                            ), " Trim the first index of the selected rows.",
                            html.Br(),html.Br(),
                            html.B(
                                "Trim index 2 --"
                            ), " Trim the second index of the selected rows.",
                            html.Br(),html.Br(),
                            html.B(
                                "Set index 1 --"
                            ), " Set the first index of the selected rows to a specific value.",
                            html.Br(),html.Br(),
                            html.B(
                                "Set index 2 --"
                            ), " Set the second index of the selected rows to a specific value.",
                            html.Br(),html.Br(),
                            html.B(
                                "Reset Value"
                            ), " -- Set the value to reset the selected rows to.",
                            html.Br(),html.Br(),
                            html.B(
                                "Check / Uncheck All --"
                            ), " Check or uncheck all rows.",
                            html.Br(),html.Br(),
                            html.B(
                                "Update Bfabric --"
                            ), " Update the barcodes of the selected rows in bfabric."
                        ], style={"margin-left": "2vw"}),
                        html.Br(),            
                        ], style={"margin-left": "2vw"}),
                        html.H4("Report a Bug Tab"),
                        html.P([
                            "If you encounter a bug while using this app, please fill out a bug report in the \"Report a Bug\" tab, so that it can be addressed by the developer."
                    ],
                    style={"margin-top":"2vh", "margin-left":"2vw", "padding-right":"40px"},
                ),],
                width=9,
            ),
        ],
    style={"margin-top": "0px", "min-height": "40vh", "height":"70vh", "max-height":"70vh", "overflow-y":"scroll", "padding-right":"40px", "padding-top":"20px"}
)

report_bug_tab = dbc.Row(
    id="page-content-bug-report",
    children=[
        dbc.Col(
            html.Div(
                id="sidebar_bug_report",
                children=empty_sidebar,
                style={"border-right": "2px solid #d4d7d9", "height": "100%", "padding": "20px", "font-size": "20px"}
            ),
            width=3,
        ),
        dbc.Col(
            html.Div(
                id="page-content-bug-report-children",
                children=[
                    html.H2("Report a Bug"),
                    html.P([
                        "Please use the form below to report a bug in the Draugr UI. If you have any questions, please email the developer at ",
                        html.A(" griffin@gwcustom.com", href="mailto:griffin@gwcustom.com"),
                    ]),
                    html.Br(),
                    html.H4("Session Details: "),
                    html.Br(),
                    html.P(id="session-details", children="No Active Session"),
                    html.Br(),
                    html.H4("Bug Description"),
                    dbc.Textarea(id="bug-description", placeholder="Please describe the bug you encountered here.", style={"width": "100%"}),
                    html.Br(),
                    dbc.Button("Submit Bug Report", id="submit-bug-report", n_clicks=0, style={"margin-bottom": "60px"}),
                    html.Br(),
                ],
                style={"margin-top":"2vh", "margin-left":"2vw", "font-size":"20px", "padding-right":"40px"},
            ),
            width=9,
        ),
    ],
    style={"margin-top": "0px", "min-height": "40vh"}
)


tabs = dbc.Tabs(
    [
        dbc.Tab(docs_tab, label="Documentation"),
        dbc.Tab(tab3_content, label="Update Barcodes"),
        dbc.Tab(report_bug_tab, label="Report a Bug"),
    ]
)