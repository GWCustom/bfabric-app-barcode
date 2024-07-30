from dash import Input, Output, State, html, dcc
import dash_bootstrap_components as dbc
import dash
import json
import pandas as pd
import os
import utils.bfab_utils as fns
# import bfabric
from utils import auth_utils, components

from dash import callback_context as ctx
import dash_table

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
                        html.Div(
                            children=[html.P(id="page-title",children=[str("Barcode Manipulation Dashboard")], style={"font-size":"40px", "margin-left":"20px", "margin-top":"10px"})],
                            style={"margin-top":"0px", "min-height":"80px","height":"6vh","border-bottom":"2px solid #d4d7d9"}
                        )
                    )
                ),
                dbc.Row(
                    id="page-content-main",
                    children=[
                        dbc.Col(
                            html.Div(
                                id="sidebar",
                                children=components.default_sidebar,
                                style={"border-right": "2px solid #d4d7d9", "height": "100%", "padding": "20px", "font-size": "20px"}
                            ),
                            xl=2, lg=2, md=3, sm=3, xs=4
                        ),
                        dbc.Col(
                            dcc.Loading(
                                html.Div(
                                    id="page-content",
                                    children=components.no_auth + [
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
                                    ],style={"margin-top":"2vh", "margin-left":"2vw", "font-size":"20px"},
                                ),
                            # width=9,
                            ),
                        )
                    ],
                    style={"margin-top": "0px", "min-height": "40vh"}
                ),
            ], style={"width":"100vw"},  
            fluid=True
        ),
        dcc.Loading(
            [
                dcc.Store(id='token', storage_type='session'), # Where we store the actual token
                dcc.Store(id='entity', storage_type='session'), # Where we store the entity data retrieved from bfabric
                dcc.Store(id='token_data', storage_type='session'), # Where we store the token auth response
                dcc.Store(id='original'),
                dcc.Store(id='edited'),
                dcc.Store(id='order-number'),
                dcc.Store(id='selectedRows', data=[0]),
                dcc.Store(id='dummy-trigger'),
            ],
        )
    ],style={"width":"100vw", "overflow-x":"hidden", "overflow-y":"scroll"}
)

@app.callback(output=Output('selectedRows', 'data'),
              inputs=[Input('barcode_table', 'selected_rows')])
def selection(dat):
    # print(dat)
    return dat


@app.callback(output=Output("graph_header",'children'),
              inputs=[Input('yes', 'n_clicks'),
                      Input('no', 'n_clicks')],
              state=[State('edited', 'data'),
                     State('selectedRows', 'data')])
def confirm(yes, no, data, sel):
    try:
        df = pd.read_json(data, orient='split')
        df = df.iloc[sel, :]
        button_clicked = ctx.triggered_id
        if button_clicked == 'yes' and yes > 0:
            print("QUEUEING")
            print(df)
            # q.enqueue(
            #     fns.update_bfabric, 
            #     kwargs={
            #         "df":df,
            #     }
            # )

            # if len(response[1]) != 0:
            header = html.H1("Bfabric Updating...Probably wait 2 min and then do what you gotta do. ",style={'color': 'red', 'fontSize': 40, 'textAlign':'center'})

            # os.system("rm temporary.csv")

        elif button_clicked == 'no':
            header = html.H1("Bfabric NOT Updated...Refresh page to continue",style={'color': 'white', 'fontSize': 40, 'textAlign':'center'})
            os.system("rm temporary.csv")

        else:
            header = []
    except:
        header = []
    return header

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
                }
            )

    button_clicked = ctx.triggered_id

    print(another)

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
                }
            )

    if button_clicked != "update":
        return send
    else:
        header = html.Div(
            id="AreYouSure",
            children=[
                html.H4("Are you sure you want to update bfabric? (only selected samples will be updated)"),
                dbc.Button('Update', id='yes', n_clicks=0, color='warning'),
                dbc.Button('Cancel', id='no', n_clicks=0, color='secondary'),
                html.Br(),
                html.P(),
                send
            ]
        )
        return header


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
        return pd.DataFrame().to_json(date_format='iso', orient='split')
    

@app.callback(output=Output('original','data'),
              inputs=[Input('load-val', 'n_clicks')],
              state=[State('order_input', 'value'),
                     State('original', 'data'),
                     State('order-number', 'data'),
                     State('token', 'data')])
def load_new_table(load_reload, order_number, old, order, token):

    tdata = json.loads(auth_utils.token_to_data(token))
    wrapper = auth_utils.token_response_to_bfabric(tdata)

    if type(order_number) != type(None) and type(order) != type(None):
        if load_reload <= 1 or int(order_number) != int(list(pd.read_json(order, orient='split')['order_number'])[0]):
            df = fns.get_dataset(order_number, wrapper)
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
        Output('reset', 'disabled'),
        Output('update', 'disabled'),
        Output('check', 'disabled'),
    ],
    [
        Input('url', 'search'),
    ]
)
def display_page(url_params):
    
    base_title = "Barcode Manipulation Dashboard"

    if not url_params:
        return None, None, None, components.no_auth, base_title, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True
    
    token = "".join(url_params.split('token=')[1:])
    tdata_raw = auth_utils.token_to_data(token)
    
    if tdata_raw:
        if tdata_raw == "EXPIRED":
            return None, None, None, components.expired, base_title, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True

        else: 
            tdata = json.loads(tdata_raw)
    else:
        return None, None, None, components.no_auth, base_title, True, True, True, True, True, True, True, True, True, True, True, True, True, True
    
    if tdata:
        entity_data = json.loads(auth_utils.entity_data(tdata))
        page_title = f"{base_title} - {tdata['entityClass_data']} - {entity_data['name']} ({tdata['environment']} System)" if tdata else "Bfabric App Interface"

        if not tdata:
            return token, None, None, components.no_auth, page_title, True, True, True, True, True, True, True, True, True, True, True, True, True, True
        
        elif not entity_data:
            return token, None, None, components.no_entity, page_title, True, True, True, True, True, True, True, True, True, True, True, True, True
        
        else:
            if not DEV:
                return token, tdata, entity_data, components.auth, page_title, False, False, False, False, False, False, False, False, False, False, False, False, False, False
            else: 
                return token, tdata, entity_data, components.dev, page_title, True, True, True, True, True, True, True, True, True, True, True, True, True, True
    else: 
        return None, None, None, components.no_auth, base_title, True, True, True, True, True, True, True, True, True, True, True, True, True, True


@app.callback(
    Output('order_input', 'options'),
    Input('token', 'data')
)
def startup_function(token): 

    ids = []
    token_data = json.loads(auth_utils.token_to_data(token))
    Bfab = auth_utils.token_response_to_bfabric(token_data)
    res = Bfab.read_object(endpoint="run", obj={"id":token_data['entity_id_data']})
    orders = res[0].container
    for elt in orders:
        if elt._classname == "order":
            ids.append(elt._id)
        
    return [{'label': elt, 'value': elt } for elt in ids]


@app.callback(output=Output('edited','data'),
              inputs=[Input('load-val','n_clicks'),
                      Input('original', 'data'),
                      Input('update','n_clicks'),
                      Input('reset','n_clicks'),
                      Input('Set1','n_clicks'),
                      Input('Set2','n_clicks'),
                      Input('RC1','n_clicks'),
                      Input('RC2','n_clicks'),
                      Input('RS1','n_clicks'),
                      Input('RS2','n_clicks'),
                      Input('swap','n_clicks'),
                      Input('Tr1','n_clicks'),
                      Input('Tr2','n_clicks'),
                      Input("graph_header", "children")
                      ],state=[State('reset_value', 'value'),
                      State('edited', 'data'),
                      State('selectedRows', 'data')])
def barcode_table(load_button,orig,update_button,clear_dmx_barcodes,Set1,Set2,RevComp1,RevComp2,RevSeq1,RevSeq2,swap,tr1,tr2,GH,reset_barcode,loader,sel):

    send = html.Div()

    button_clicked = ctx.triggered_id

    if button_clicked == "load-val":
        return orig

    # df=pd.read_csv('temporary.csv')
    try:
        df = pd.read_json(loader, orient='split')
    except:
        df = pd.DataFrame()
    try:
        if button_clicked == 'RC1':
            df['Barcode 1'] = [fns.RC(list(df['Barcode 1'])[i]) if i in sel else list(df['Barcode 1'])[i] for i in range(len(list(df['Barcode 1'])))]
        if button_clicked == 'RC2':
            df['Barcode 2'] = [fns.RC(list(df['Barcode 2'])[i]) if i in sel else list(df['Barcode 2'])[i] for i in range(len(list(df['Barcode 2'])))]
        if button_clicked == 'RS1':
            df['Barcode 1'] = [fns.RS(list(df['Barcode 1'])[i]) if i in sel else list(df['Barcode 1'])[i] for i in range(len(list(df['Barcode 1'])))]
        if button_clicked == 'RS2':
            df['Barcode 2'] = [fns.RS(list(df['Barcode 2'])[i]) if i in sel else list(df['Barcode 2'])[i] for i in range(len(list(df['Barcode 2'])))]
        if button_clicked == 'Tr1':
            df['Barcode 1'] = [str(list(df['Barcode 1'])[i])[:-1] if i in sel else list(df['Barcode 1'])[i] for i in range(len(list(df['Barcode 1'])))]
        if button_clicked == 'Tr2':
            df['Barcode 2'] = [str(list(df['Barcode 2'])[i])[:-1] if i in sel else list(df['Barcode 2'])[i] for i in range(len(list(df['Barcode 2'])))]

        if button_clicked == 'swap': #### TODO Fix for selections:
            new_bc1 = []
            new_bc2 = []
            for i in range(len(list(df['Barcode 1']))):
                if i in sel:
                    new_bc1.append(list(df['Barcode 2'])[i])
                    new_bc2.append(list(df['Barcode 1'])[i])
                else:
                    new_bc2.append(list(df['Barcode 2'])[i])
                    new_bc1.append(list(df['Barcode 1'])[i])
            df['Barcode 1'] = new_bc1
            df['Barcode 2'] = new_bc2
            # placeholder = list(df['Barcode 1'])[:]
            # df['Barcode 1'] = df['Barcode 2']
            # df['Barcode 2'] = placeholder
        if button_clicked == 'Set1':
            if type(None) != type(reset_barcode):
                df['Barcode 1'] = [reset_barcode if i in sel else list(df['Barcode 1'])[i] for i in range(len(list(df['Barcode 1'])))]
            else:
                df['Barcode 1'] = ["" for i in list(df['Barcode 1'])]
        if button_clicked == 'Set2':
            if type(None) != type(reset_barcode):
                df['Barcode 2'] = [reset_barcode if i in sel else list(df['Barcode 2'])[i] for i in range(len(list(df['Barcode 2'])))]
            else:
                df['Barcode 2'] = ["" if i in sel else list(df['Barcode 2'])[i] for i in range(len(list(df['Barcode 2'])))]
        return df.to_json(date_format='iso', orient='split')

    except:
        return orig

if __name__ == '__main__':
    app.run_server(debug=False, port=PORT, host=HOST)