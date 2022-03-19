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
from dash.exceptions import PreventUpdate

import plotly.express as px

import plotly.graph_objs as go


import numpy as np
import pandas as pd

import base64
import os
import io

import datetime

from card_format import Card_format

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
    def build_tabs_card(self):
        return html.Div(
            id='tabs-card',
            className='tabs_card',
            children=[
                dcc.Tabs(
                    id='app-tabs-card',
                    value='tab1-card',
                    className='custom-tabs-card',
                    children=[
                        dcc.Tab(
                            id='Specs-tab',
                            label='Frente do cartão',
                            value='tab1-card',
                            className='custom-tab',
                            selected_className='custom-tab--selected',
                        ),
                        dcc.Tab(
                            id='Control-chart-tab',
                            label='Fundo do Cartão',
                            value='tab2-card',
                            className='custom-tab',
                            selected_className='custom-tab--selected',
                        )
                    ]
                )
            ]
        )

    def transforme_df(self, df):
        df['Data de Nascimento'].apply(lambda x: pd.to_datetime(x))
        df['Carimbo de data/hora'] =df['Carimbo de data/hora'].apply(lambda x: x.replace('/', '-'))
        df['Carimbo de data/hora'] = pd.to_datetime(df['Carimbo de data/hora'], format='%Y-%m-%d %H:%M:%S PM GMT-3')
        
        df.rename(columns={'Local de conversão': 'conversão'}, inplace=True)
        
        #df.drop(["Faixa Etária"], axis=1, inplace=True)
        
        df['idade'] = self.current_year - pd.DatetimeIndex(df['Data de Nascimento']).year
        
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
                                            min_date_allowed=self.df['Carimbo de data/hora'].min(),
                                            max_date_allowed=self.df['Carimbo de data/hora'].max(),
                                            initial_visible_month=self.df['Carimbo de data/hora'].min(),
                                            date=self.df['Carimbo de data/hora'].min(),
                                            display_format='MMMM D, YYYY',
                                            style={'border':'0px solid black'}
                                        ),
                                        html.P('Data Final'),
                                        dcc.DatePickerSingle(
                                            id='date-fim-picker',
                                            min_date_allowed=self.df['Carimbo de data/hora'].min(),
                                            max_date_allowed=self.df['Carimbo de data/hora'].max(),
                                            initial_visible_month=self.df['Carimbo de data/hora'].max(),
                                            date=self.df['Carimbo de data/hora'].max(),
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
    
    def build_front_of_card(self):
        return dbc.Card(id='front-of-card',children=[
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label('Nome:',style={'display':'inline-block','margin-right':20})
                            ], md=2),
                            dbc.Col([
                                dcc.Input(id='nome', type='text', placeholder='', style={'display':'inline-block', 'border': '1px solid black', 'size': '40'}),
                            ], md=4)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Label('Atividade:',style={'display':'inline-block','margin-right':20})
                            ], md=2),
                            dbc.Col([
                                dcc.Input(id='atividade', type='text', placeholder='', style={'display':'inline-block', 'border': '1px solid black'}),
                            ], md=4),
                            dbc.Col([
                                html.Label('Nascimento:',style={'display':'inline-block','margin-right':20})
                            ], md=2),
                            dbc.Col([
                                dcc.Input(id='nascimento', type='text', placeholder='', style={'display':'inline-block', 'border': '1px solid black'}),
                            ], md=1)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Label('DOC. Identidade:',style={'display':'inline-block','margin-right':20})
                            ], md=2),
                            dbc.Col([
                                dcc.Input(id='identidade', type='text', placeholder='', style={'display':'inline-block', 'border': '1px solid black'}),
                            ], md=4),
                            dbc.Col([
                                html.Label('CPF:',style={'display':'inline-block','margin-right':20})
                            ], md=2),
                            dbc.Col([
                                dcc.Input(id='cpf', type='text', placeholder='', style={'display':'inline-block', 'border': '1px solid black'}),
                            ], md=1)
                        ])
                    ])
                ])
    def build_card_background(self):
        return dbc.Card(id='card-background', children=[
            dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label('Pai:',style={'display':'inline-block','margin-right':20})
                            ], md=2),
                            dbc.Col([
                                dcc.Input(id='pai', type='text', placeholder='', style={'display':'inline-block', 'border': '1px solid black'}),
                            ], md=4)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Label('Mãe:',style={'display':'inline-block','margin-right':20})
                            ], md=2),
                            dbc.Col([
                                dcc.Input(id='mae', type='text', placeholder='', style={'display':'inline-block', 'border': '1px solid black'}),
                            ], md=4)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Label('Naturalidade:',style={'display':'inline-block','margin-right':20})
                            ], md=2),
                            dbc.Col([
                                dcc.Input(id='naturalidade', type='text', placeholder='', style={'display':'inline-block', 'border': '1px solid black'}),
                            ], md=4),
                            dbc.Col([
                                html.Label('Sexo:',style={'display':'inline-block','margin-right':20})
                            ], md=2),
                            dbc.Col([
                                dcc.Input(id='sexo', type='text', placeholder='', style={'display':'inline-block', 'border': '1px solid black'}),
                            ], md=1)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Label('Conversão:',style={'display':'inline-block','margin-right':20})
                            ], md=2),
                            dbc.Col([
                                dcc.Input(id='conversao', type='text', placeholder='', style={'display':'inline-block', 'border': '1px solid black'}),
                            ], md=4),
                            dbc.Col([
                                html.Label('Batismo Águas:',style={'display':'inline-block','margin-right':20})
                            ], md=2),
                            dbc.Col([
                                dcc.Input(id='batismo-aguas', type='text', placeholder='', style={'display':'inline-block', 'border': '1px solid black'}),
                            ], md=1)
                        ])
                    ])
            ])
    
    def build_member_control(self):
        return dbc.Row([
            dbc.Col([
                dcc.Interval(
                            id="interval-component-card",
                            interval=2 * 1000,  # in milliseconds
                            n_intervals=50,  # start at batch 50
                            disabled=True,
                ),
                self.build_tabs_card(),
                dbc.Row(id='app-card'),
                dcc.Store(id="n-interval-stage-card", data=50),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.Button('Gerar Imagens',id='button-img', n_clicks=0)
                    ]),
                    dbc.Col(
                        html.Button('Gerar Imagens',id='button-img-fundo', n_clicks=0)
                    )
                ]),
                html.Br(),
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div(
                                    html.Img(id='cartao-frente', src=app.get_asset_url('cartao_frente.jpeg'), style={'height':'210px', 'width':'290px'})
                                ),
                            ], md=6),
                            dbc.Col([
                                html.Div(
                                    html.Img(id='cartao-fundo', src=app.get_asset_url('cartao_fundo.jpeg'), style={'height':'210px', 'width':'290px'})
                                ),
                            ], md=6)
                        ])
                    ])
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(html.Button('Gerar PDF',id='button-pdf', n_clicks=0), md=2),
                    dbc.Col(html.Label(id='label-pdf-gerado'), md=3)
                ])
            ]),
            dbc.Col([
                html.H2('Tabelas com informações')
            ])
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
            
            elif tab_switch == "tab2":
                return (
                    #html.Div(
                    #    id="status-container",
                    #    children=[
                    
                    self.build_member_control(),
                    
                    #    ],
                    #),
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
            [Output("app-card", "children"), Output("interval-component-card", "n_intervals")],
            [Input("app-tabs-card", "value")],
            [State("n-interval-stage-card", "data")],
        )
        def render_tab_content(tab_switch, stopped_interval):
            if tab_switch == "tab1-card":
                return self.build_front_of_card(), stopped_interval
            
            elif tab_switch == "tab2-card":
                return self.build_card_background(), stopped_interval
        
        # Update interval
        @app.callback(
            Output("n-interval-stage-card", "data"),
            [Input("app-tabs-card", "value")],
            [
                State("interval-component-card", "n_intervals"),
                State("interval-component-card", "disabled"),
                State("n-interval-stage", "data"),
            ],
        )
        def update_interval_state(tab_switch, cur_interval, disabled, cur_stage):
            if disabled:
                return cur_interval
        
            if tab_switch == "tab1-card":
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
            new_db = self.df[(self.df['Carimbo de data/hora'] >= select_date_ini) & (self.df['Carimbo de data/hora'] <= select_date_fin)]
            
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
            
        @app.callback(
            Output('cartao-frente', 'src'),
            Input('button-img', 'n_clicks'),
            prevent_initial_call=True,
        )
        def btn_generate_image(n_clickes):
            card = Card_format()
            data = {
                'name':"ANDRE LUIZ PIRES GUIMARAES",
                'cargo': "DIACONO",
                'data_nascimento': '15/07/1997',
                'emisao_card':'14/03/2022',
                'venci_card': '12/03/2027',
                'rg':'15648154-15',
                'cpf':'703.455.081-65'
            }
            card.editImage('database/modelos/cartao_frente.jpeg', 'database/modelos/fundo_frente.jpg', data)
            #card.editImageFundo('assets/cartao_fundo.jpeg', 'assets/fundo_fundo.jpg')
            
            #Rotacionar imagem
            card.trataImage("database/modelos/fundo_frente.jpg")
            #card.trataImage("assets/fundo_fundo.jpg", False)
            del card
            img_filename = 'database/modelos/fundo_frente.jpg'
            encoded_image = base64.b64encode(open(img_filename, 'rb').read())
            
            return 'data:image/jpg;base64,{}'.format(encoded_image.decode())
        
        @app.callback(
            Output('cartao-fundo', 'src'),
            Input('button-img-fundo', 'n_clicks'),
            prevent_initial_call=True,
        )
        def btn_generate_image(n_clickes):
            card = Card_format()
            data = {
                'nome_pai':'RAMILTON RIBEIRO GUIMARAES',
                'nome_mae':'JUCELIA PEREIRA PIRES',
                'nacionalidade':'BRASILEIRO',
                'sexo': 'MASCULINO',
                'conversao':'15/04/2012',
                'batismo':'15/02/2014'
            }
            card.editImageFundo('database/modelos/cartao_fundo.jpeg', 'database/modelos/fundo_fundo.jpg', data)
            
            #Rotacionar imagem
            #card.trataImage("assets/fundo_frente.jpg")
            card.trataImage("database/modelos/fundo_fundo.jpg", False)
            del card
            
            img_filename = 'database/modelos/fundo_fundo.jpg'
            encoded_image = base64.b64encode(open(img_filename, 'rb').read())
            
            return 'data:image/jpg;base64,{}'.format(encoded_image.decode())
        
        @app.callback(
            Output('label-pdf-gerado', 'children'),
            Input('button-pdf', 'n_clicks'),
            prevent_initial_call=True,
        )
        def btn_generate_image(n_clickes):
            if n_clickes is None:
                raise PreventUpdate
            else:
                card = Card_format()
                card.generate_pdf('database/modelos/fundo_frente.jpg','database/modelos/fundo_fundo.jpg')
                
                return 'pdf gerado com sucesso!'
            
        
    #def app_init(self):
    #    #self.callbacks(self.app)
    #    self.app.run_server(debug=True, host='localhost')
        
if __name__ == "__main__":
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
    app.config['suppress_callback_exceptions']=True
    tesete =DashBoard_forms(app)
    app.run_server(debug=True, host='localhost', use_reloader = True)
    