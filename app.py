
from dash import Dash, html, dcc, callback, Output, Input, State
from dash.dash_table import DataTable
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px


external_stylesheets = [
    dbc.themes.BOOTSTRAP, 
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    ]
app = Dash(__name__, external_stylesheets=external_stylesheets)

##############
# data model #
##############

df_faithful = pd.read_csv("data/faithful.csv")

FAITHFUL_LOOKUP = {
    "eruptions" : {"id":"eruptions", "name":"Eruption Time (mins)"},
    "waiting" : {"id":"waiting", "name":"Waiting Time (mins)"},
}

# Define style arguments for the sidebar. 
# We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "36rem",
    "padding": "3rem 1rem",
    "background-color": "#f8f9fa",
}

# Define styles for the main content position it to the right of the 
# sidebar and add some padding.
CONTENT_STYLE = {
    "margin-left": "8rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}



def transform_slider_value(value):
    """Converts linear slider position into geometric value"""
    return 1 / 2**value


###############
# layout view #
###############

app.layout = dbc.Container([
    html.Div([
        html.H2("Data Sample App", className="display-4"),
        html.Hr(),
        html.Div([
            dbc.Label("Sample proportion:"),
            dcc.Slider(
                # min = 0, max = 1.0, 
                step = None,
                marks={i:f"1/{(2**i)}" for i in range(8)},
                value = 0,
                id='sample-prop-slider'
            ),
            html.P([], id="sample-prop-text-out"),
            html.Br(),
            dbc.Label("Fill colour:"),
            dcc.Dropdown(
                id="colour-dropdown",
                options = [
                    {"label":"Orange", "value":"orange"},
                    {"label":"Dark Orange", "value":"darkorange"},
                    {"label":"Coral", "value":"coral"},
                    {"label":"Orange Red", "value":"orangered"},
                ],
                value = "coral",
            ),
            html.Br(),
            dbc.Label("Download Sample CSV:"),
            html.Button("Download", id="button-download-sample"),
            dcc.Download(id="download-sample-df"),
        ]),
        html.Hr(),
        html.P(
            "Each time the size of the sample is changed, a new dataset is "
            "generated. This sample is fed into multiple outputs by storing "
            "the data in the browser. This allows it to be shared between " 
            "multiple outputs without being re-generated, and hence re-sampled "
            "for each one. This ensures that the "
            "same sample is shown in the graph, the table, and downloaded. "
        ),
        html.Hr(),
    ], style = SIDEBAR_STYLE),
    html.Div([
        # dcc.Store stores the intermediate sampled data
        dcc.Store(id='intermediate-sample-data'),
        dbc.Row([
            dbc.Col([
                dbc.Card(dbc.CardBody([
                    dcc.Graph(figure={}, id="scatter-graph")
                ]))
            ], width=12, align="center"),
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H4("Sample data:", className="card-text"),
                        dbc.Row([
                            dbc.Col(width=3),
                            dbc.Col([], id="datatable-out", style={"align":"center"}),
                            dbc.Col(width=3),
                        ])
                    ], style={
                        'textAlign': 'left',
                        "margin-left":"20px",
                        "margin-right":"20px"
                    })
                )
            ], width=12, align="center")
        ]),
    ], style=CONTENT_STYLE)
])

########################
# callbacks controller #
########################

# use browser Store to store intermediate values
@app.callback(
    Output('intermediate-sample-data', 'data'), 
    Input('sample-prop-slider', 'value')
)
def get_sample_data(proportion_slider_val):
    proportion = transform_slider_value(proportion_slider_val)
    df = df_faithful.sample(frac = proportion)
    # data must be stored as json
    return df.to_json(date_format='iso', orient='split')

@app.callback(
    Output('sample-prop-text-out', 'children'),
    Input('sample-prop-slider', 'value')
)
def display_value(value):
    transformed_value = transform_slider_value(value)
    text = (
        f"Sampled {transformed_value*df_faithful.shape[0]//1:0.0f} rows of "
        f"{df_faithful.shape[0]:0.0f} rows ({100*transformed_value:.1f}%)"
    )
    return text

@callback(
    Output("download-sample-df", "data"),
    Input("button-download-sample", "n_clicks"),
    # use state to unlink dependency 
    #   - will not trigger download when data changes 
    State("intermediate-sample-data", "data"),
    prevent_initial_call=True,
)
def download_sample_df(n_clicks, json_df_sample):
    # data from store is json
    df = pd.read_json(json_df_sample, orient='split')
    return dcc.send_data_frame(df.to_csv, "sample_download.csv", index = False)

@callback(
    Output("scatter-graph", "figure"),
    [
        Input("intermediate-sample-data", "data"),
        Input("colour-dropdown", "value"),
        # use state to unlink dependency - doesn't matter too much here
        #   as this is an input of an input here. 
        State("sample-prop-slider", "value"),
    ]
)
def update_graph(json_df_sample, colour, proportion_slider_val):
    proportion = transform_slider_value(proportion_slider_val)
    # data from store is json
    df = pd.read_json(json_df_sample, orient='split')
    if df.shape[0] <= 0:
        raise PreventUpdate
    title = (f"Plot of {FAITHFUL_LOOKUP['eruptions']['name']} against "
             f"{FAITHFUL_LOOKUP['waiting']['name']} for a sample of "
             f"{100*proportion:.1f}%. "
             f"<br><sup>Source: Old Faithful Gyser Dataset.</sup>")
    fig = px.scatter(
        df, x="waiting", y="eruptions",
        template="simple_white",
        color_discrete_sequence=[colour],
        title=title,
        )
    fig.update_layout(
        xaxis_title=FAITHFUL_LOOKUP['waiting']['name'],
        yaxis_title=FAITHFUL_LOOKUP['eruptions']['name'],
        xaxis_range=[40,100],
        yaxis_range=[0.5,6],
    )
    return fig

@callback(
    Output("datatable-out", "children"),
    Input("intermediate-sample-data", "data"),
)
def update_datatable(json_df_sample):
    # data from store is json
    df = pd.read_json(json_df_sample, orient='split')
    if df.shape[0] <= 0:
        raise PreventUpdate
    dt = DataTable(
        data = df.to_dict("records"),
        columns = [
            FAITHFUL_LOOKUP[col] for col in df_faithful.columns
        ],
        page_size=8, 
        fill_width=True,
        style_cell={
            'padding-right': '10px',
            'padding-left': '10px',
            'text-align': 'center',
            'marginLeft': 'auto',
            'marginRight': 'auto'
        },
        style_table={'overflowX': 'auto'},
    ),
    return dt

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
