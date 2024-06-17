#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, dash_table, no_update
import plotly.express as px
import dash
import io
import base64

# Cargar los datos del archivo CSV
df_customers = pd.read_csv("clustered_df.csv")
df_state = pd.read_csv("state.csv")
df_industry = pd.read_csv("industry.csv")

# Función para reemplazar guiones bajos con espacios
def format_label(label):
    return label.replace('_', ' ').capitalize()

# Inicializar la aplicación Dash con hojas de estilo externas
external_stylesheets = [
    'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'
]

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label=format_label('Customer Database'), children=[
            html.Div([
                html.H1(format_label("Customer Database"), style={'text-align': 'center'}),
                html.Div([
                    html.Label(format_label('Customer ID:')),
                    dcc.Input(id='customer-id-input', type='text', style={'margin-right': '10px'}),
                    html.Button(format_label('Search'), id='search-button', n_clicks=0, style={'background-color': '#4CAF50', 'color': 'white', 'font-weight': 'bold', 'margin-right': '10px'}),
                    html.Button(format_label('Clear'), id='clear-button', n_clicks=0, style={'background-color': '#f44336', 'color': 'white', 'font-weight': 'bold'}),
                    dcc.Upload(
                        id='upload-data',
                        children=html.Button('Upload File', style={'background-color': '#2196F3', 'color': 'white', 'font-weight': 'bold', 'margin-left': '10px'}),
                        multiple=False
                    )
                ], style={'padding': '20px'}),
                dash_table.DataTable(
                    id='table',
                    columns=[
                        {'name': format_label('Customer State'), 'id': 'customer_state'},
                        {'name': format_label('Industry'), 'id': 'product_category_name'},
                        {'name': format_label('Customer Value'), 'id': 'customer_lifetime_value'},
                        {'name': format_label('Cluster'), 'id': 'cluster'},
                        {'name': format_label('Average Price'), 'id': 'average_price'}
                    ],
                    data=[],
                    style_cell={
                        'textAlign': 'left',
                        'padding': '5px'
                    },
                    style_header={
                        'backgroundColor': '#4CAF50',
                        'fontWeight': 'bold',
                        'color': 'white'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(240, 240, 240)'
                        },
                        {
                            'if': {'row_index': 'even'},
                            'backgroundColor': 'rgb(255, 255, 255)'
                        }
                    ],
                    style_as_list_view=True
                ),
                html.Div(id='upload-error', style={'color': 'red', 'margin-top': '10px'})
            ])
        ]),
        dcc.Tab(label=format_label('Graphs'), children=[
            html.Div([
                html.H1(format_label("Graphs"), style={'text-align': 'center'}),
                dcc.Graph(id='cluster-pie-chart'),
                dcc.Graph(id='average-price-bar-chart'),
                dcc.Graph(id='customer-value-bar-chart')
            ])
        ]),
        dcc.Tab(label=format_label('State Data'), children=[
            html.Div([
                html.H1(format_label("State Data"), style={'text-align': 'center'}),
                html.Div([
                    html.Label(format_label('State:')),
                    dcc.Dropdown(
                        id='state-dropdown',
                        options=[{'label': state, 'value': state} for state in df_state['customer_state'].unique()],
                        value=df_state['customer_state'].unique()[0]
                    )
                ], style={'padding': '20px'}),
                dcc.Graph(id='state-count-industry-bar-chart'),
                dcc.Graph(id='state-average-price-bar-chart')
            ])
        ]),
        dcc.Tab(label=format_label('Industry Data'), children=[
            html.Div([
                html.H1(format_label("Industry Data"), style={'text-align': 'center'}),
                html.Div([
                    html.Label(format_label('Industry:')),
                    dcc.Dropdown(
                        id='industry-dropdown',
                        options=[{'label': format_label(industry), 'value': industry} for industry in df_industry['product_category_name'].unique()],
                        value=df_industry['product_category_name'].unique()[0]
                    )
                ], style={'padding': '20px'}),
                dcc.Graph(id='industry-count-state-bar-chart'),
                dcc.Graph(id='industry-average-price-bar-chart')
            ])
        ])
    ])
])

def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return pd.read_excel(io.BytesIO(decoded))

@app.callback(
    [Output('table', 'data'), Output('cluster-pie-chart', 'figure'), Output('average-price-bar-chart', 'figure'), Output('customer-value-bar-chart', 'figure'), Output('upload-error', 'children')],
    [Input('search-button', 'n_clicks'), Input('clear-button', 'n_clicks'), Input('upload-data', 'contents')],
    [State('customer-id-input', 'value'), State('table', 'data')]
)
def update_table_and_graphs(search_clicks, clear_clicks, uploaded_file, customer_id, current_table_data):
    ctx = dash.callback_context

    if not ctx.triggered:
        return no_update, no_update, no_update, no_update, ''

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    global df_customers

    if button_id == 'clear-button':
        return [], px.pie(), px.bar(), px.bar(), ''

    error_message = ''

    if button_id == 'upload-data' and uploaded_file is not None:
        uploaded_df = parse_contents(uploaded_file)
        if 'customer_id' not in uploaded_df.columns:
            error_message = 'Error: The uploaded file does not contain a "customer_id" column.'
            return no_update, no_update, no_update, no_update, error_message
        new_ids = uploaded_df['customer_id'].astype(str).tolist()
        query = df_customers[df_customers['customer_id'].astype(str).isin(new_ids)]
    else:
        query = df_customers.copy()

        if customer_id:
            query = query[query['customer_id'].astype(str).str.strip() == customer_id.strip()]

    new_data = query[['customer_state', 'product_category_name', 'customer_lifetime_value', 'cluster', 'average_price']].to_dict('records')

    if button_id == 'search-button' or (button_id == 'upload-data' and uploaded_file is not None):
        combined_data = current_table_data + new_data if current_table_data else new_data

        data = pd.DataFrame(combined_data)

        cluster_pie_chart = px.pie(data, names='cluster', title='Cluster Distribution', template='plotly_dark')
        
        average_price_data = data.groupby('product_category_name')['average_price'].mean().reset_index()
        average_price_bar_chart = px.bar(average_price_data, x='product_category_name', y='average_price', title='Average Price per Industry', template='plotly_dark')
        
        customer_value_data = data.groupby('product_category_name')['customer_lifetime_value'].mean().reset_index()
        customer_value_bar_chart = px.bar(customer_value_data, x='product_category_name', y='customer_lifetime_value', title='Customer Value per Industry', template='plotly_dark')

        return combined_data, cluster_pie_chart, average_price_bar_chart, customer_value_bar_chart, error_message

    return no_update, no_update, no_update, no_update, error_message

@app.callback(
    [Output('state-count-industry-bar-chart', 'figure'), Output('state-average-price-bar-chart', 'figure')],
    [Input('state-dropdown', 'value')]
)
def update_state_graphs(state):
    filtered_df = df_state[df_state['customer_state'] == state]

    count_industry_bar_chart = px.bar(filtered_df, x='product_category_name', y='Count_industry', title=f'Count of Industries in {state}', template='plotly_dark')
    average_price_bar_chart = px.bar(filtered_df, x='product_category_name', y='Average Price per state', title=f'Average Price in {state} by Industry', template='plotly_dark')

    return count_industry_bar_chart, average_price_bar_chart

@app.callback(
    [Output('industry-count-state-bar-chart', 'figure'), Output('industry-average-price-bar-chart', 'figure')],
    [Input('industry-dropdown', 'value')]
)
def update_industry_graphs(industry):
    filtered_df = df_industry[df_industry['product_category_name'] == industry]

    count_state_bar_chart = px.bar(filtered_df, x='customer_state', y='Count_state', title=f'Count of States for {format_label(industry)}', template='plotly_dark')
    average_price_bar_chart = px.bar(filtered_df, x='customer_state', y='Average Price per state', title=f'Average Price for {format_label(industry)} by State', template='plotly_dark')

    return count_state_bar_chart, average_price_bar_chart

if __name__ == '__main__':
    app.run_server(debug=True)




# In[ ]:




