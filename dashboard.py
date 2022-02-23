#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 07:51:50 2022

@author: andre
"""

import dash
from dash import dcc
from dash import html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px

import plotly.graph_objs as go


import numpy as np
import pandas as pd

import PySimpleGUI as sg
import os

import datetime

currentDateTime = datetime.datetime.now()
date = currentDateTime.date()
current_year = date.year

df = pd.read_csv('database.csv')

print(df['Data de Nascimento'])
df['Data de Nascimento'].apply(lambda x: pd.to_datetime(x))
df.rename(columns={'Local de conversão': 'conversão'}, inplace=True)

#df.drop(["Faixa Etária"], axis=1, inplace=True)

df['idade'] = current_year - pd.DatetimeIndex(df['Data de Nascimento']).year

print(df['idade'])

df['Faixa Etária'] = None

df.loc[df.idade < 12, 'Faixa Etária'] = 'Criança'
df.loc[(df.idade >= 12) & (df.idade < 16), 'Faixa Etária'] = 'Adolecente'
df.loc[(df.idade >= 16) & (df.idade <= 30), 'Faixa Etária'] = 'Jovem'
df.loc[df.idade > 30, 'Faixa Etária'] = 'Adulto'

print(df['Faixa Etária'])

select_sex_columns = ['Masculino','Feminino']


select_faixa_etaria_columns = ['Criança', 'Adolecente', 'Jovem','Adulto']

select_conver = np.unique(df['conversão'])
select_irmao_que = np.unique(df['Esta sendo'])

select_type = [
    'Sexo', 'Estado Civil', 'Faixa Etária', 'Esta sendo', 'conversão'
]

select_plot = [
    'Grafico de barras',
    'Grafico de espalhamento',
    'Grafico de pizza',
]


quant = df.Sexo.value_counts()
print(quant)

fig2 = go.Figure(layout={'template': 'plotly_dark'})
fig2.add_trace(go.Bar(x=quant.keys(), y=quant))
fig2.update_layout(
    paper_bgcolor='#242424',
    plot_bgcolor='#242424',
    autosize=True,
    margin=dict(l=10, r=10, t=10, b=10)
)

'''fig = go.Figure(layout={'template': 'plotly_dark'})
fig.add_trace()'''


#instalação do dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

app.layout = dbc.Container(
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Img(id='log', src=app.get_asset_url('ciadseta.png'), height=160),
                    ], style={})
                ], md=5),
                dbc.Col([
                    html.Div([
                        html.H4('ASSEMBLEIA DE DEUS CIADSETA'),
                        html.H5('Formulario de novos convertidos')
                    ], style={})
                ], md=5)
            ]),            
            dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([                                    
                                        html.Div([
                                            html.P('Selecione os dados que deseja plotar:', style={'margin-top': '25px'}),
                                            dcc.Dropdown(id='location-dropdown-select',
                                                         options=[{'label': i, 'value':i} for i in select_type],
                                                         style={'margin-top':'10px'}
                                                         ),
                                            
                                        ])
                                    ]),
                                    dbc.Col([                                    
                                        html.Div([
                                            html.P('Selecione a forma que deseja plotar:', style={'margin-top': '25px'}),
                                            dcc.Dropdown(id='location-dropdown-select-plot',
                                                         options=[{'label': i, 'value':i} for i in select_plot],
                                                         style={'margin-top':'10px'}
                                                         ),
                                            
                                        ])
                                    ])
                                ]),
                        ]),
                        html.Div([
                                html.P('Analise grafica:', style={'margin-top': '25px'}),
                                dcc.Graph(id='line-graph', figure=fig2)
                        ]) 
                    ], color='light', outline=True, style={'margin-top': '10px',
                                                           'box-shadow': '0 4px 4px 0 rgb(0,0,0,0.15), 0 4px 20px 0 rgba(0,0,0,0.19'}
                    )
            ], md=12),#total da largura 
                                                                
        ], md=6, style={'padding':'15px'}),
                                                           
        dbc.Col([
            html.H3('FILTRAR INFORMAÇÕES'),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.P('Data inicio'),
                                dcc.DatePickerSingle(
                                    id='date-inicio-picker',
                                    min_date_allowed=df['fixa preenchida no dia'].min(),
                                    max_date_allowed=df['fixa preenchida no dia'].max(),
                                    initial_visible_month=df['fixa preenchida no dia'].min(),
                                    date=df['fixa preenchida no dia'].min(),
                                    display_format='MMMM D, YYYY',
                                    style={'border':'0px solid black'}
                                ),
                                html.P('Data Final'),
                                dcc.DatePickerSingle(
                                    id='date-fim-picker',
                                    min_date_allowed=df['fixa preenchida no dia'].min(),
                                    max_date_allowed=df['fixa preenchida no dia'].max(),
                                    initial_visible_month=df['fixa preenchida no dia'].max(),
                                    date=df['fixa preenchida no dia'].max(),
                                    display_format='MMMM D, YYYY',
                                    style={'border':'0px solid black'}
                                )
                        ])
                    ], color='light', outline=True, style={'margin-top': '10px',
                                                           'box-shadow': '0 4px 4px 0 rgb(0,0,0,0.15), 0 4px 20px 0 rgba(0,0,0,0.19'
                                                           })
                ], md=4),#total da largura 
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.P('Sexo:'),
                            dcc.Dropdown(id='location-dropdown_sex',
                                         options=[{'label': i, 'value':i} for i in select_sex_columns],
                                         style={'margin-top':'10px'}
                             ),
                            html.P('Faixa Étaria:'),
                            dcc.Dropdown(id='location-dropdown_faix',
                                         options=[{'label': i, 'value':i} for i in select_faixa_etaria_columns],
                                         style={'margin-top':'10px'}
                             )
                        ])
                    ], color='light', outline=True, style={'margin-top': '10px',
                                                           'box-shadow': '0 4px 4px 0 rgb(0,0,0,0.15), 0 4px 20px 0 rgba(0,0,0,0.19'
                                                           })
                ], md=4),#total da largura 
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.P('Conversão na:'),
                            dcc.Dropdown(id='location-dropdown_cong',
                                         options=[{'label': i, 'value':i} for i in select_conver],
                                         style={'margin-top':'10px'}
                             ),
                            html.P('Imrão que:'),
                            dcc.Dropdown(id='location-dropdown_que',
                                         options=[{'label': i, 'value':i} for i in select_irmao_que],
                                         style={'margin-top':'10px'}
                             )
                        ])
                    ], color='light', outline=True, style={'margin-top': '10px',
                                                           'box-shadow': '0 4px 4px 0 rgb(0,0,0,0.15), 0 4px 20px 0 rgba(0,0,0,0.19'
                                                           })
                ], md=4),#total da largura 
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Upload(id='upload-data',
                                   children=html.Button('Carregar arquivo', n_clicks=0),
                                   multiple=True)
                    ])
                ], md=4),
                
                dbc.Col([
                    html.Div([
                        html.Button('Baixar tabela',id='button-save-excel', n_clicks=0),
                        dcc.Download(id='download-excel'), 
                    ])
                ], md=4),                    
            ]),
            html.Br(),
            html.Div(
                id='update-table',
            ),
            html.H5(id='cont-data')
            
        ], md=6, style={'padding':'15px'})
                            
        
    ])
, fluid=True)
       
def plot_pip(data):
    fig = go.Figure(layout={'template': 'plotly_dark'},
                     data=[go.Pie(labels=data.keys(), values=data.values, textinfo='label+percent',
                    insidetextorientation='radial')])
    return fig 
def plot_bar(data):
    fig = go.Figure(layout={'template': 'plotly_dark'},
                             data=[go.Bar(x=data.keys(), y=data)])
    return fig    
  
def plot_scatter(data):
    fig = go.Figure(layout={'template': 'plotly_dark'},
                             data=[go.Scatter(x=data.keys(), y=data)])
    return fig 
                              
@app.callback(
    Output('line-graph', 'figure'),
    [Input('location-dropdown-select-plot', 'value'),
     Input('location-dropdown-select', 'value')
     ]
)                                                           
def plot_graph(plot_type, select):
    
    fig2 = go.Figure(layout={'template': 'plotly_dark'})
    
    if plot_type == 'Grafico de pizza':
        #fig2 = go.Figure(layout={'template': 'plotly_dark'}, data=[go.Pie()])
        if select in select_type:
            fig2 = plot_pip(df[select].value_counts())
            
    elif plot_type == 'Grafico de barras':
        if select in select_type:
            fig2 = plot_bar(df[select].value_counts())
    elif plot_type == 'Grafico de espalhamento':
        if select in select_type:
            fig2 = plot_scatter(df[select].value_counts())
            
            
    fig2.update_layout(
        paper_bgcolor='#242424',
        plot_bgcolor='#242424',
        autosize=True,
        margin=dict(l=10, r=10, t=10, b=10)
    )
            
    return fig2

def update_table(new_data):
    new_data = new_data[['Nome', 'Telefone', 'Estado Civil', 'Esta sendo', 'conversão']]
    tab = dash_table.DataTable(
                     id='table',
                     columns=[{'id':i, 'name': i} for i in new_data.columns],
                     data=new_data.to_dict('records'),
                     style_header={
                                    'backgroundColor': 'rgb(30, 30, 30)',
                                    'color': 'white',
                                    'fontWeight': 'bold'
                                    },
                     style_data={
                                'backgroundColor': 'rgb(50, 50, 50)',
                                'color': 'white',
                                'fontWeight': 'bold'
                                },
                         )
    return tab

@app.callback(
    Output('download-excel', 'data'),
    Input('button-save-excel', 'n_clicks'),
    prevent_initial_call=True,
)
def save_table(n_clickes):
    new_data = df[['Nome', 'Telefone', 'Estado Civil', 'Rua', 'Bairro', 'Número', 'Ponto de Referência']]
    
    return dcc.send_data_frame(new_data.to_excel, "Novos_Convertidos.xlsx", sheet_name="Sheet_name_1", 
                               index=False)

@app.callback(
    [
     Output('update-table', 'children'),
     Output('cont-data', 'children')
    ],
    [
     Input('date-inicio-picker', 'date'),
     Input('date-fim-picker', 'date'),
     Input('location-dropdown_sex', 'value'),
     Input('location-dropdown_faix', 'value'),
     Input('location-dropdown_cong', 'value'),
     Input('location-dropdown_que', 'value'),
     
    ]
)
def update_graphs_table(select_date_ini, select_date_fin,select_sex, select_faix, select_conv, select_type_conv):
    new_db = df[(df['fixa preenchida no dia'] >= select_date_ini) & (df['fixa preenchida no dia'] <= select_date_fin)]
    
    dic = {
        'Sexo': select_sex,
        'Faixa Etária': select_faix,
        'conversão':select_conv,
        'Esta sendo': select_type_conv
        }
    
    for key, value in dic.items():
        if value != None:
            new_db = new_db[new_db[key] == value]
    
    cont = len(new_db)
    
    return update_table(new_db), 'Quantidade de registro conforme a filtragem: {}'.format(cont)

if __name__ == "__main__":
    app.run_server(debug=True, host='localhost')