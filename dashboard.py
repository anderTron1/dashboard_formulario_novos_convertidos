#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 07:51:50 2022

@author: andre
"""

import dash
from dash import dcc
from dash import html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import plotly.express as px

import plotly.graph_objs as go


import numpy as np
import pandas as pd

import base64
import os
import io

import datetime

class BaseBlock:
    def __init__(self, app=None):
        self.app = app
    
        self.currentDateTime = datetime.datetime.now()
        self.date = self.currentDateTime.date()
        self.current_year = self.date.year
        
        self.UPLOAD_DIRECTORY = 'database'
        
        self.df = pd.read_csv(self.UPLOAD_DIRECTORY+'/database.csv')

        self.transforme_df(self.df)
        
        self.select_sex_columns = ['Masculino','Feminino']

        self.select_faixa_etaria_columns = ['Criança', 'Adolecente', 'Jovem','Adulto']
        
        self.select_conver = self.df['conversão'].drop_duplicates().values
        
        self.select_irmao_que = self.df['Esta sendo'].drop_duplicates().values
        
        self.select_type = [
            'Sexo', 'Estado Civil', 'Faixa Etária', 'Esta sendo', 'conversão'
        ]
        
        self.select_plot = [
            'Grafico de barras',
            'Grafico de espalhamento',
            'Grafico de pizza',
        ]
        
        
        self.quant = self.df.Sexo.value_counts()
    
        if self.app is not None and hasattr(self, 'callbacks'):
            self.callbacks(self.app)
            
    def build_tabs(self):
        return html.Div(
            id='tabs',
            className='tabs',
            children=[
                dcc.Tabs(
                    id='app-tabs',
                    value='tab2',
                    className='custom-tabs',
                    children=[
                        dcc.Tab(
                            id='Specs-tab',
                            label='Novos Convertidos',
                            value='tab1',
                            className='custom-tab',
                            selected_className='custom-tab--selected',
                        ),
                        dcc.Tab(
                            id='Control-chart-tab',
                            label='Controle de Membros',
                            value='tab2',
                            className='custom-tab',
                            selected_className='custom-tab--selected',
                        )
                    ]
                )
            ]
        )

    def transforme_df(self, df):
        df['Data de Nascimento'].apply(lambda x: pd.to_datetime(x))
        df['fixa preenchida no dia'].apply(lambda x: pd.to_datetime(x))
        print(self.df['fixa preenchida no dia'].min())
        print(self.df['fixa preenchida no dia'].max())
        df.rename(columns={'Local de conversão': 'conversão'}, inplace=True)
        
        #df.drop(["Faixa Etária"], axis=1, inplace=True)
        
        df['idade'] = self.current_year - pd.DatetimeIndex(df['Data de Nascimento']).year
        print(df['idade'])
        
        df['Faixa Etária'] = None
        
        df.loc[df.idade < 12, 'Faixa Etária'] = 'Criança'
        df.loc[(df.idade >= 12) & (df.idade < 16), 'Faixa Etária'] = 'Adolecente'
        df.loc[(df.idade >= 16) & (df.idade <= 30), 'Faixa Etária'] = 'Jovem'
        df.loc[df.idade > 30, 'Faixa Etária'] = 'Adulto'


        '''fig2 = go.Figure(layout={'template': 'plotly_dark'})
        fig2.add_trace(go.Bar(x=quant.keys(), y=quant))
        fig2.update_layout(
            paper_bgcolor='#242424',
            plot_bgcolor='#242424',
            autosize=True,
            margin=dict(l=10, r=10, t=10, b=10)
        )'''
        
        '''fig = go.Figure(layout={'template': 'plotly_dark'})
        fig.add_trace()'''

    def plot_pip(self,data):
        fig = go.Figure(layout={'template': 'plotly_dark'},
                         data=[go.Pie(labels=data.keys(), values=data.values, textinfo='label+percent',
                        insidetextorientation='radial')])
        return fig 
    def plot_bar(self,data):
        fig = go.Figure(layout={'template': 'plotly_dark'},
                                 data=[go.Bar(x=data.keys(), y=data)])
        return fig    
      
    def plot_scatter(self,data):
        fig = go.Figure(layout={'template': 'plotly_dark'},
                                 data=[go.Scatter(x=data.keys(), y=data)])
        return fig 
    
    def update_table(self,new_data):
        new_data = new_data[['Nome', 'Telefone', 'Estado Civil', 'Esta sendo', 'conversão']]
        tab = dash_table.DataTable(
                         id='table',
                         columns=[{'id':i, 'name': i} for i in new_data.columns],
                         data=new_data.to_dict('records'),
                         page_size=8,
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
    
    def parse_contents(self, contents, filename):
        content_type, content_string = contents.split(',')
    
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                df_loaded = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                self.transforme_df(df_loaded)
                '''elif 'xls' in filename:
                # Assume that the user uploaded an excel file
                new_df = pd.read_excel(io.BytesIO(decoded))'''
                
                df_new = pd.concat([self.df, df_loaded])
                df_new.drop_duplicates(subset='Nome', inplace=True)
                
                df_new.to_csv(self.UPLOAD_DIRECTORY + '/database.csv')
                print(df_new)
                
                self.df = df_new
                
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.' + str(e)
            ])
        return html.Div(['Arquivo carregado... Atualize a pagina'])
    
    def build_banner(self):
        return html.Div(
            id="banner",
            className="banner",
            children=[
                html.Div(
                    html.Img(id='log', src=app.get_asset_url('ciadseta.png'))
                ),
                dbc.Col([
                    dbc.Row([
                        html.H3('CONTROLE DE INFORMAÇÕES DE IRMÃOS')  
                    ]),
                    dbc.Row([
                        html.H5('ASSEMBLEIA DE DEUS CIADSETA')  
                    ]),
                ])
            ],
        )
    
    def new_converts(self):
        return dbc.Row([
                dbc.Col([            
                    dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                        dbc.Row([
                                            dbc.Col([                                    
                                                html.Div([
                                                    html.P('Selecione os dados que deseja plotar:', style={'margin-top': '25px'}),
                                                    dcc.Dropdown(id='location-dropdown-select',
                                                                 options=[{'label': i, 'value':i} for i in self.select_type],
                                                                 style={'margin-top':'10px'}
                                                                 ),
                                                    
                                                ])
                                            ]),
                                            dbc.Col([                                    
                                                html.Div([
                                                    html.P('Selecione a forma que deseja plotar:', style={'margin-top': '25px'}),
                                                    dcc.Dropdown(id='location-dropdown-select-plot',
                                                                 options=[{'label': i, 'value':i} for i in self.select_plot],
                                                                 style={'margin-top':'10px'}
                                                                 ),
                                                    
                                                ])
                                            ])
                                        ]),
                                ]),
                                html.Div([
                                        html.P('Analise grafica:', style={'margin-top': '25px'}),
                                        dcc.Graph(id='line-graph')#, figure=fig2)
                                ]) 
                            ], color='light', outline=True, style={'margin-top': '10px',
                                                                   'box-shadow': '0 4px 4px 0 rgb(0,0,0,0.15), 0 4px 20px 0 rgba(0,0,0,0.19'}
                            )
                    ], md=12),#total da largura 
                                                                        
                ], md=6, style={'padding':'15px'}),
                                                                   
                dbc.Col([
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.P('Data inicio'),
                                        dcc.DatePickerSingle(
                                            id='date-inicio-picker',
                                            min_date_allowed=self.df['fixa preenchida no dia'].min(),
                                            max_date_allowed=self.df['fixa preenchida no dia'].max(),
                                            initial_visible_month=self.df['fixa preenchida no dia'].min(),
                                            date=self.df['fixa preenchida no dia'].min(),
                                            display_format='MMMM D, YYYY',
                                            style={'border':'0px solid black'}
                                        ),
                                        html.P('Data Final'),
                                        dcc.DatePickerSingle(
                                            id='date-fim-picker',
                                            min_date_allowed=self.df['fixa preenchida no dia'].min(),
                                            max_date_allowed=self.df['fixa preenchida no dia'].max(),
                                            initial_visible_month=self.df['fixa preenchida no dia'].max(),
                                            date=self.df['fixa preenchida no dia'].max(),
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
                                                 options=[{'label': i, 'value':i} for i in self.select_sex_columns],
                                                 style={'margin-top':'10px'}
                                     ),
                                    html.P('Faixa Étaria:'),
                                    dcc.Dropdown(id='location-dropdown_faix',
                                                 options=[{'label': i, 'value':i} for i in self.select_faixa_etaria_columns],
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
                                                 options=[{'label': i, 'value':i} for i in self.select_conver],
                                                 style={'margin-top':'10px'}
                                     ),
                                    html.P('Imrão que:'),
                                    dcc.Dropdown(id='location-dropdown_que',
                                                 options=[{'label': i, 'value':i} for i in self.select_irmao_que],
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
                    html.Div(id='output-data-upload'),
                    html.Br(),
                    html.Div(
                        id='update-table',
                    ),
                    html.H5(id='cont-data')
                    
                ], md=6, style={'padding':'15px'})
                                    
                
            ])
    
class DashBoard_forms(BaseBlock):
    #instalação do dash
    def callbacks(self, app):
        
        '''fig2 = go.Figure(layout={'template': 'plotly_dark'})
        fig2.add_trace(go.Bar(x= self.quant.keys(), y = self.quant))
        fig2.update_layout(
            paper_bgcolor='#242424',
            plot_bgcolor='#242424',
            autosize=True,
            margin=dict(l=10, r=10, t=10, b=10)
        )'''
        # dbc.Container(
        app.layout = html.Div(
                id='app-container',
                children=[
                    dbc.Row([
                        self.build_banner()
                    ]),
                    dbc.Row([
                        self.build_tabs(),
                        dcc.Interval(
                            id="interval-component",
                            interval=2 * 1000,  # in milliseconds
                            n_intervals=50,  # start at batch 50
                            disabled=True,
                        ),
                        html.Div(id="app-content"),
                        
                        #state=[State("value-setter-store", "data")]
                        dcc.Store(id="n-interval-stage", data=50),
                    ])
                ]
            #fluid=True
            )
                   
        @app.callback(
            [Output("app-content", "children"), Output("interval-component", "n_intervals")],
            [Input("app-tabs", "value")],
            [State("n-interval-stage", "data")],
        )
        def render_tab_content(tab_switch, stopped_interval):
            if tab_switch == "tab1":
                return self.new_converts(), stopped_interval
            return (
                html.Div(
                    id="status-container",
                    children=[
                        html.H2('Em construçao')
                        
                    ],
                ),
                stopped_interval,
            )
        # Update interval
        @app.callback(
            Output("n-interval-stage", "data"),
            [Input("app-tabs", "value")],
            [
                State("interval-component", "n_intervals"),
                State("interval-component", "disabled"),
                State("n-interval-stage", "data"),
            ],
        )
        def update_interval_state(tab_switch, cur_interval, disabled, cur_stage):
            if disabled:
                return cur_interval
        
            if tab_switch == "tab1":
                return cur_interval
            return cur_stage
        
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
                if select in self.select_type:
                    fig2 = self.plot_pip(self.df[select].value_counts())
                    
            elif plot_type == 'Grafico de barras':
                if select in self.select_type:
                    fig2 = self.plot_bar(self.df[select].value_counts())
            elif plot_type == 'Grafico de espalhamento':
                if select in self.select_type:
                    fig2 = self.plot_scatter(self.df[select].value_counts())
                    
                    
            fig2.update_layout(
                paper_bgcolor='#242424',
                plot_bgcolor='#242424',
                autosize=True,
                margin=dict(l=10, r=10, t=10, b=10)
            )
                    
            return fig2   
    

        @app.callback(
            Output('download-excel', 'data'),
            Input('button-save-excel', 'n_clicks'),
            prevent_initial_call=True,
        )
        def save_table(n_clickes):
            new_data = self.df[['Nome', 'Telefone', 'Estado Civil', 'Faixa Etária', 'Rua', 'Bairro', 'Número', 'Ponto de Referência', 'conversão']]
            
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
            new_db = self.df[(self.df['fixa preenchida no dia'] >= select_date_ini) & (self.df['fixa preenchida no dia'] <= select_date_fin)]
            
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
            
            return self.update_table(new_db), 'Quantidade de registro conforme a filtragem: {}'.format(cont)

        @app.callback(Output('output-data-upload', 'children'),
                      Input('upload-data', 'contents'),
                      State('upload-data', 'filename')
        )
        def update_output(list_of_contents, list_of_names):
            if list_of_contents is not None:
                children = [
                    self.parse_contents(c, n) for c, n in zip(list_of_contents, list_of_names)]
                return children

    #def app_init(self):
    #    #self.callbacks(self.app)
    #    self.app.run_server(debug=True, host='localhost')
        
if __name__ == "__main__":
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
    app.config['suppress_callback_exceptions']=True
    tesete =DashBoard_forms(app)
    app.run_server(debug=True, host='localhost')
    