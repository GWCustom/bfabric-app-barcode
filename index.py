from dash import Input, Output, State, html, dcc
import dash_bootstrap_components as dbc
import dash
import json
import pandas as pd
import os
import utils.bfab_utils as fns
from datetime import datetime as dt
from utils.objects import Logger

import bfabric
from utils import auth_utils, components

from dash import callback_context as ctx
from dash import dash_table

import asyncio
import threading

if os.path.exists("./PARAMS.py"):
    try:
        from PARAMS import PORT, HOST, DEV
    except:
        PORT = 8050
        HOST = 'localhost'
        DEV = True
else:
    PORT = 8050
    HOST = 'localhost'
    DEV = True
    

def run_async_in_background(coroutine_func, *args):
    def start_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    new_loop = asyncio.new_event_loop()
    t = threading.Thread(target=start_loop, args=(new_loop,))
    t.start()

    future = asyncio.run_coroutine_threadsafe(coroutine_func(*args), new_loop)
    return future

####### Main components of a Dash App: ########
# 1) app (dash.Dash())
# 2) app.layout (html.Div())
# 3) app.callback()

#################### (1) app ####################
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

#################### (2) app.layout ####################

app.layout = html.Div(
    children=[
        dcc.Location(
            id='url',
            refresh=False
        ),
        html.Div(
            [
                
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Update B-Fabric")),
                        dbc.ModalBody("Confirm barcode update in B-Fabric for selected samples?"),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Confirm Update", id="yes", className="ms-auto", n_clicks=0
                            )
                        ),
                    ],
                    id="modal",
                    is_open=False,
                ),
            ]
        ),
        dbc.Container(
            children=[    
                dbc.Row(
                    dbc.Col(
                        html.Div(
                            className="banner",
                            children=[
                                html.Div(
                                    children=[
                                        html.P(
                                            'Barcode Manipulation Dashboard',
                                            style={'color':'#ffffff','margin-top':'15px','height':'80px','width':'100%',"font-size":"40px","margin-left":"20px"}
                                        )
                                    ],
                                    style={"background-color":"#000000", "border-radius":"10px"}
                                ),
                            ],
                        ),
                    ),
                ),
                dbc.Row(
                    dbc.Col(
                        [
                            html.Div(
                                children=[
                                    html.P(
                                        id="page-title",
                                        children=[
                                            str(" ")
                                        ], 
                                        style={
                                            "font-size":"40px", 
                                            "margin-left":"20px", 
                                            "margin-top":"10px"
                                        }
                                    ),
                                    
                                ] ,
                                style={"margin-top":"0px", "min-height":"80px","height":"6vh","border-bottom":"2px solid #d4d7d9"}
                            )
                        ]+ components.alerts
                    )
                ),
                components.tabs,
            ], style={"width":"100vw"},  
            fluid=True
        ),
        dcc.Store(id='transformations_applied_store', data = [], storage_type='session'),
    ],style={"width":"100vw", "overflow-x":"hidden"}#, "overflow-y":"scroll"}
)

@app.callback(output=Output('selectedRows', 'data'),
              inputs=[Input('barcode_table', 'selected_rows')])
def selection(dat):
    # print(dat)
    return dat


@app.callback(
    Output("modal", "is_open"),
    [Input("update", "n_clicks"), Input("yes", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    output=[
        Output("alert-fade", "is_open"),
        Output("alert-fade-2", "is_open"),
        Output("alert-fade-3", "is_open"),
        Output("transformations_applied_store", "data", allow_duplicate=True),
    ],
    inputs=[
        Input('yes', 'n_clicks')
    ],
    state=[
        State('edited', 'data'),
        State('selectedRows', 'data'),
        State('token', 'data'),
        State('transformations_applied_store', 'data')
    ],
    prevent_initial_call=True
)
def confirm(yes, data, sel, token, transformations):

    updated, queued, not_updated = False, False, False
    token_data = json.loads(auth_utils.token_to_data(token))
    environ = token_data.get('environment', 'TEST') 
    environ = environ.upper()

    L = Logger(
    jobid = token_data.get('jobId', None),
    username= token_data.get("user_data", "None"),
    environment= token_data.get("environment", "None"))

    if not data:
        L.log_operation("Error", "An error occured while updating the barcodes in B-Fabric.", params=None, flush_logs=True)
        return not_updated, queued, updated, transformations

    try:
        df = pd.read_json(data, orient='split')
        df = df.iloc[sel, :]
        button_clicked = ctx.triggered_id

        if button_clicked == 'yes' and yes > 0:

            # Here we update using the gfeeder credentials, since the user rarely has 
            # Sufficient permissions to edit the objects. 
            SUPERUSER = bfabric.Bfabric.from_config(config_env=environ)

            # now we make fns.update_bfabric call, but do not await it. . . run asyncronously. 
            # asyncio.run(fns.update_bfabric(df, SUPERUSER))
            run_async_in_background(fns.update_bfabric, df, SUPERUSER, token_data, transformations)
            # fns.update_bfabric(df, SUPERUSER) 
            updated = True

            transformations = []

        
    except Exception as e:
        print("-----------ERROR-----------")
        print(e) 

        not_updated = True

    return updated, queued, not_updated, transformations

@app.callback(output=Output('div-graphs-bc', 'children'),
              inputs=[Input('edited', 'data'),
                      Input('update', 'n_clicks'),
                      Input('selectedRows', 'data'),
                      Input('check', 'n_clicks')])
def display_graph(data, update_button, another, check):

    df = pd.read_json(data, orient='split')

    if df.empty:
        return dash_table.DataTable(
                [],
                [],
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(220, 220, 220)',
                    }
                ],
                style_cell={'padding':'10px'},
                style_data={
                    'color': 'black',
                    'backgroundColor': 'white'
                },
                style_header={
                    'backgroundColor': 'rgb(210, 210, 210)',
                    'color': 'black',
                    'fontWeight': 'bold'
                },
                
            )

    button_clicked = ctx.triggered_id

    if button_clicked == "check":
        if type(another) == type(None):
            rows = []
        else:
            tmp = [i for i in range(len(df[list(df.columns)[0]]))]
            for elt in another:
                tmp.remove(elt)
            rows = tmp
    else:
        if type(another) == type(None):
            
            rows = [i for i in range(len(df[list(df.columns)[0]]))]

        else:
            rows = another

    send = dash_table.DataTable(
                id="barcode_table",
                data=df.to_dict("records"),
                columns=[{"name": i, "id": i} for i in df.columns],
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(220, 220, 220)',
                    }
                ],
                row_selectable="multi",
                selected_rows=rows,
                # selected_rows = another,
                style_cell={'padding':'10px'},
                style_data={
                    'color': 'black',
                    'backgroundColor': 'white'
                },
                style_header={
                    'backgroundColor': 'rgb(210, 210, 210)',
                    'color': 'black',
                    'fontWeight': 'bold'
                },
                
            )

    if button_clicked != "update":
        return send
    else:
        return []


@app.callback(output=Output('order-number','data'),
              inputs=[Input('load-val', 'n_clicks')],
              state=[State('order_input', 'value'),
                     State('order-number', 'data')])
def load_new_order(load_reload, order_number, old):

    if type(order_number) != type(None):
        if load_reload <= 1:
            df = pd.DataFrame({"order_number":[order_number],"index":["index"]})
            return df.to_json(date_format='iso', orient='split')
        else:
            df = pd.read_json(old, orient='split')
            return df.to_json(date_format='iso', orient='split')
    else:
        return pd.DataFrame({"order_number":[],"index":[]}).to_json(date_format='iso', orient='split')
    

@app.callback(
    [
        Output("alert-fade-bug", "is_open"),
        Output("alert-fade-bug-fail", "is_open")
    ],
    [
        Input("submit-bug-report", "n_clicks")
    ],
    [
        State("token", "data"),
        State("entity", "data"),
        State("bug-description", "value")
    ],
    prevent_initial_call=True
)
def submit_bug_report(n_clicks, token, entity_data, bug_description):

    if token: 
        token_data = json.loads(auth_utils.token_to_data(token))
    else:
        token_data = ""

    jobId = token_data.get('jobId', None)
    username = token_data.get("user_data", "None")

    L = Logger(
    jobid = token_data.get('jobId', None),
    username= token_data.get("user_data", "None"),
    environment= token_data.get("environment", "None"))

    if n_clicks:
        L.log_operation("bug report", "Initiating bug report submission process.", params=None, flush_logs=False)
        try:
            sending_result = auth_utils.send_bug_report(
                token_data=token_data,
                entity_data=entity_data,
                description=bug_description
            )

            if sending_result:
                L.log_operation("bug report", f"Bug report successfully submitted. | DESCRIPTION: {bug_description}", params=None, flush_logs=True)
                return True, False
            else:
                L.log_operation("bug report", "Failed to submit bug report!", params=None, flush_logs=True)
                return False, True
        except:
            L.log_operation("bug report", "Failed to submit bug report!", params=None, flush_logs=True)
            return False, True

    return False, False


@app.callback(output=Output('original','data'),
              inputs=[Input('load-val', 'n_clicks')],
              state=[State('order_input', 'value'),
                     State('original', 'data'),
                     State('order-number', 'data'),
                     State('token', 'data')])
def load_new_table(load_reload, order_number, old, order, token):
    if token:
        tdata = json.loads(auth_utils.token_to_data(token))
    else: 
        return None
    wrapper = auth_utils.token_response_to_bfabric(tdata)

    if order_number is not None and order is not None:
        if load_reload <= 1 or int(order_number) != int(list(pd.read_json(order, orient='split')['order_number'])[0]):
            df = fns.get_dataset(order_number, wrapper, tdata)
            return df.to_json(date_format='iso', orient='split')
        else:
            df = pd.read_json(old, orient='split')
            return df.to_json(date_format='iso', orient='split')
    else:
        return pd.DataFrame().to_json(date_format='iso', orient='split')


@app.callback(
    [
        Output('token', 'data'),
        Output('token_data', 'data'),
        Output('entity', 'data'),
        Output('page-content', 'children'),
        Output('page-title', 'children'),
        Output('load-val', 'disabled'),
        Output('swap', 'disabled'),
        Output('RC1', 'disabled'),
        Output('RC2', 'disabled'),
        Output('RS1', 'disabled'),
        Output('RS2', 'disabled'),
        Output('Tr1', 'disabled'),
        Output('Tr2', 'disabled'),
        Output('Set1', 'disabled'),
        Output('Set2', 'disabled'),
        Output('reset_value', 'disabled'),
        Output('yes', 'disabled'),
        Output('update', 'disabled'),
        Output('check', 'disabled'),
        Output('session-details', 'children'),
    ],
    [
        Input('url', 'search'),
    ]
)
def display_page(url_params):
    
    base_title = ""
    session_details = [html.P("No session details available")]

    if not url_params:
        return None, None, None, components.no_auth, base_title, *(True for _ in range(14)), session_details
    
    token = "".join(url_params.split('token=')[1:])
    tdata_raw = auth_utils.token_to_data(token)
    
    if tdata_raw:
        if tdata_raw == "EXPIRED":
            return None, None, None, components.expired, base_title, *(True for _ in range(14)), session_details
        else: 
            tdata = json.loads(tdata_raw)
    else:
        return None, None, None, components.no_auth, base_title, *(True for _ in range(14)), session_details
    
    if tdata:
        entity_data = json.loads(auth_utils.entity_data(tdata))
        page_title = f"{tdata['entityClass_data']} - {entity_data['name']}" if tdata else "B-Fabric App Interface"

        if not tdata:
            return token, None, None, components.no_auth, page_title, *(True for _ in range(14)), session_details
        
        elif not entity_data:
            return token, None, None, components.no_entity, page_title, *(True for _ in range(14)), session_details
        
        else:
            if not DEV:
                session_details = [
                    html.P([
                        html.B("Entity Name: "), entity_data['name'],
                        html.Br(),
                        html.B("Entity Class: "), tdata['entityClass_data'],
                        html.Br(),
                        html.B("Environment: "), tdata['environment'],
                        html.Br(),
                        html.B("Entity ID: "), tdata['entity_id_data'],
                        html.Br(),
                        html.B("User Name: "), tdata['user_data'],
                        html.Br(),
                        html.B("Session Expires: "), tdata['token_expires'],
                        html.Br(),
                        html.B("Current Time: "), str(dt.now().strftime("%Y-%m-%d %H:%M:%S"))
                    ])
                ]
                return token, tdata, entity_data, components.auth, page_title, *(False for _ in range(14)), session_details
            else: 
                return token, tdata, entity_data, components.dev, page_title, *(True for _ in range(14)), session_details
    else: 
        return None, None, None, components.no_auth, base_title, *(True for _ in range(14)), session_details


@app.callback(
    Output('order_input', 'options'),
    Input('token', 'data')
)
def startup_function(token): 

    if token:
        token_data = json.loads(auth_utils.token_to_data(token))
    else: 
        return []
    
    L = Logger(
    jobid = token_data.get('jobId', None),
    username= token_data.get("user_data", "None"),
    environment= token_data.get("environment", "None"))

    Bfab = auth_utils.token_response_to_bfabric(token_data)

    #res = Bfab.read(endpoint="run", obj={"id":token_data['entity_id_data']}, max_results=None)

    res = L.logthis(
        api_call=Bfab.read,
        endpoint="run",
        obj={"id":token_data['entity_id_data']},
        max_results=None,
        flush_logs = False,
    )

    orders = [
        item['id'] for item in res[0].get('container')
        if item.get('classname') == 'order'
    ]

    L.log_operation("order input", f"Orders {orders} loaded successfully.", flush_logs=True)
        
    return [{'label': f'Order {order_id}', 'value': order_id} for order_id in orders]


@app.callback(
    output=[
        Output('edited', 'data'),
        Output('transformations_applied_store', 'data', allow_duplicate=True)
    ],
    inputs=[
        Input('load-val', 'n_clicks'),
        Input('original', 'data'),
        Input('update', 'n_clicks'),
        Input('Set1', 'n_clicks'),
        Input('Set2', 'n_clicks'),
        Input('RC1', 'n_clicks'),
        Input('RC2', 'n_clicks'),
        Input('RS1', 'n_clicks'),
        Input('RS2', 'n_clicks'),
        Input('swap', 'n_clicks'),
        Input('Tr1', 'n_clicks'),
        Input('Tr2', 'n_clicks'),
    ],
    state=[
        State('reset_value', 'value'),
        State('edited', 'data'),
        State('selectedRows', 'data'),
        State('transformations_applied_store', 'data')
    ],
    prevent_initial_call=True
)
def barcode_table(load_button, orig, update_button, Set1, Set2, RevComp1, RevComp2, RevSeq1, RevSeq2, swap, tr1, tr2, reset_barcode, loader, sel, transformations_applied):
    send = html.Div()

    button_clicked = ctx.triggered_id
    if button_clicked == "load-val":
        return orig, transformations_applied

    try:
        df = pd.read_json(loader, orient='split')
    except:
        df = pd.DataFrame()

    try:
        if button_clicked == 'RC1':
            df['Barcode 1'] = [fns.RC(list(df['Barcode 1'])[i]) if i in sel else list(df['Barcode 1'])[i] for i in range(len(list(df['Barcode 1'])))]
            transformations_applied.append("RevComp index 1")
            print(transformations_applied)
        if button_clicked == 'RC2':
            df['Barcode 2'] = [fns.RC(list(df['Barcode 2'])[i]) if i in sel else list(df['Barcode 2'])[i] for i in range(len(list(df['Barcode 2'])))]
            transformations_applied.append("RevComp index 2")
            print(transformations_applied)
        if button_clicked == 'RS1':
            df['Barcode 1'] = [fns.RS(list(df['Barcode 1'])[i]) if i in sel else list(df['Barcode 1'])[i] for i in range(len(list(df['Barcode 1'])))]
            transformations_applied.append("RevSeq index 1")
            print(transformations_applied)
        if button_clicked == 'RS2':
            df['Barcode 2'] = [fns.RS(list(df['Barcode 2'])[i]) if i in sel else list(df['Barcode 2'])[i] for i in range(len(list(df['Barcode 2'])))]
            transformations_applied.append("RevSeq index 2")
            print(transformations_applied)
        if button_clicked == 'Tr1':
            df['Barcode 1'] = [str(list(df['Barcode 1'])[i])[:-1] if i in sel else list(df['Barcode 1'])[i] for i in range(len(list(df['Barcode 1'])))]
            transformations_applied.append("Trim index 1")
        if button_clicked == 'Tr2':
            df['Barcode 2'] = [str(list(df['Barcode 2'])[i])[:-1] if i in sel else list(df['Barcode 2'])[i] for i in range(len(list(df['Barcode 2'])))]
            transformations_applied.append("Trim index 2")
        if button_clicked == 'swap':#### TODO Fix for selections:
            new_bc1, new_bc2 = [], []
            for i in range(len(list(df['Barcode 1']))):
                if i in sel:
                    new_bc1.append(list(df['Barcode 2'])[i])
                    new_bc2.append(list(df['Barcode 1'])[i])
                else:
                    new_bc2.append(list(df['Barcode 2'])[i])
                    new_bc1.append(list(df['Barcode 1'])[i])
            df['Barcode 1'], df['Barcode 2'] = new_bc1, new_bc2
            # placeholder = list(df['Barcode 1'])[:]
            # df['Barcode 1'] = df['Barcode 2']
            # df['Barcode 2'] = placeholder
            transformations_applied.append("Swap Indices")
        if button_clicked == 'Set1':
            if type(None) != type(reset_barcode):
                df['Barcode 1'] = [reset_barcode if i in sel else list(df['Barcode 1'])[i] for i in range(len(list(df['Barcode 1'])))]
            else:
                df['Barcode 1'] = ["" for _ in list(df['Barcode 1'])]
            transformations_applied.append("Set index 1")
        if button_clicked == 'Set2':
            if type(None) != type(reset_barcode):
                df['Barcode 2'] = [reset_barcode if i in sel else list(df['Barcode 2'])[i] for i in range(len(list(df['Barcode 2'])))]
            else:
                df['Barcode 2'] = ["" if i in sel else list(df['Barcode 2'])[i] for i in range(len(list(df['Barcode 2'])))]
            transformations_applied.append("Set index 2")
        return df.to_json(date_format='iso', orient='split'), transformations_applied

    except Exception as e:
        #Add Log and User Error?
        print("Error occurred:", e)
        return orig, transformations_applied


if __name__ == '__main__':
    app.run_server(debug=False, port=PORT, host=HOST)
