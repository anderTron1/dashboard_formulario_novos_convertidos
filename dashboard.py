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

import pandas as pd
from datetime import timedelta, date

class BaseBlock:
    def __init__(self, app=None):
        self.app = app
    
        self.currentDateTime = datetime.datetime.now()
        self.date = self.currentDateTime.date()
        self.current_year = self.date.year
        
        self.UPLOAD_DIRECTORY = 'assets/'
        
        self.df = pd.read_csv(self.UPLOAD_DIRECTORY+'database.csv')
        self.df_new_selected = None
        self.df_members = pd.read_csv(self.UPLOAD_DIRECTORY+'cadastro de membros.csv')

        self.transforme_df(self.df)
        #self.transforme_df_new_members(self.df_members)
        
        self.select_sex_columns = ['Masculino','Feminino']

        self.select_faixa_etaria_columns = ['Criança', 'Adolecente', 'Jovem','Adulto']
        
        self.select_conver = self.df['conversão'].drop_duplicates().values
        
        self.select_irmao_que = self.df['Esta sendo'].drop_duplicates().values
        
        self.name_img_member = None
        
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
    
    def convert_date(self, df, columns, format_date_current, format_date_final):
        df[columns] = pd.to_datetime(df[columns], format=format_date_current)
        df[columns] = df[columns].dt.strftime(format_date_final)

    def transforme_df(self, df, transforme_data=True):
        df['Data de Nascimento'].apply(lambda x: pd.to_datetime(x))
        
        
        df['Carimbo de data/hora'] =df['Carimbo de data/hora'].apply(lambda x: x.replace('/', '-'))
        df['Carimbo de data/hora'] = pd.to_datetime(df['Carimbo de data/hora'], format='%d-%m-%Y %H:%M:%S')
            
        #print(df['Carimbo de data/hora'])
        df['Carimbo de data/hora'] = df['Carimbo de data/hora'].dt.strftime('%Y-%m-%d %H:%M:%S')
        #print('\n\n',df['Carimbo de data/hora'])
        #print(df['Carimbo de data/hora']
        
        #df['Carimbo de data/hora'] =df['Carimbo de data/hora'].apply(lambda x: x.replace('/', '-'))
        
        #print(df['Carimbo de data/hora'][0].find('PM GMT-3'))
        #if df['Carimbo de data/hora'][0].find('PM GMT-3') != -1:
        #     df['Carimbo de data/hora'] = pd.to_datetime(df['Carimbo de data/hora'], format='%Y-%m-%d %H:%M:%S PM GMT-3')
        #else:
        #df['Carimbo de data/hora'] = pd.to_datetime(df['Carimbo de data/hora'], format='%Y-%m-%d %H:%M:%S')
        
        if transforme_data:
            df.rename(columns={'Local de conversão': 'conversão'}, inplace=True)
                        
            df['idade'] = self.current_year - pd.DatetimeIndex(df['Data de Nascimento']).year
            
            df['Faixa Etária'] = None
            
            df.loc[df.idade < 12, 'Faixa Etária'] = 'Criança'
            df.loc[(df.idade >= 12) & (df.idade < 16), 'Faixa Etária'] = 'Adolecente'
            df.loc[(df.idade >= 16) & (df.idade <= 30), 'Faixa Etária'] = 'Jovem'
            df.loc[df.idade > 30, 'Faixa Etária'] = 'Adulto'

    """def transforme_df_new_members(self, df_new_members):
        
        self.convert_date(df_new_members, columns='Data de Nascimento', format_date_current='%Y-%m-%d', format_date_final='%d/%m/%Y')
        self.convert_date(df_new_members, columns='Data do batismo nas águas', format_date_current='%Y-%m-%d', format_date_final='%d/%m/%Y')
        self.convert_date(df_new_members, columns='Data de Admissão', format_date_current='%Y-%m-%d', format_date_final='%d/%m/Y')"""

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
    
    def update_table(self,id_table, new_data):
        tab = dash_table.DataTable(
                         id=id_table,
                         columns=[{'id':i, 'name': i, "hideable": True} for i in new_data.columns],
                         data=new_data.to_dict('records'),
                         page_size=8,
                         editable=False,              # allow editing of data inside all cells
                         row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                        
                         style_header={
                                        'backgroundColor': 'rgb(30, 30, 30)',
                                        'color': 'white',
                                        'fontWeight': 'bold',
                                        },
                         style_data={
                                    'backgroundColor': 'rgb(50, 50, 50)',
                                    'color': 'white',
                                    'fontWeight': 'bold',
                                    },
                             ),                        
        return tab
    
    def parse_contents(self, contents, filename, name_database, transforme_data = True):
        content_type, content_string = contents.split(',')
    
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                df_loaded = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                #print(transforme_data, name_database)
                self.transforme_df(df_loaded, transforme_data)
                
                df_new = pd.concat([self.df, df_loaded])
                
                df_new['Carimbo de data/hora'] =df_new['Carimbo de data/hora'].apply(lambda x: x.replace('-', '/'))
                df_new['Carimbo de data/hora'] = pd.to_datetime(df_new['Carimbo de data/hora'], format='%Y-%m-%d %H:%M:%S')
            
                #print(df['Carimbo de data/hora'])
                df_new['Carimbo de data/hora'] = df_new['Carimbo de data/hora'].dt.strftime('%d/%m/%Y %H:%M:%S')
                
                df_new.drop_duplicates(subset='Nome', inplace=True)
                
                df_new.to_csv(self.UPLOAD_DIRECTORY + name_database)

                self.df = pd.read_csv(self.UPLOAD_DIRECTORY+name_database)
                
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.' + str(e)
            ])
        return html.Div(['Arquivo carregado, a pagina será atualizada...'])
    
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
                                            display_format='DD, MMMM YYYY',
                                            style={'border':'0px solid black'}
                                        ),
                                        html.P('Data Final'),
                                        dcc.DatePickerSingle(
                                            id='date-fim-picker',
                                            min_date_allowed=self.df['Carimbo de data/hora'].min(),
                                            max_date_allowed=self.df['Carimbo de data/hora'].max(),
                                            initial_visible_month=self.df['Carimbo de data/hora'].max(),
                                            date=self.df['Carimbo de data/hora'].max(),
                                            display_format='DD, MMMM YYYY',
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
                                dcc.Input(id='nome', type='text', value='', style={'display':'inline-block', 'border': '1px solid black', 'size': '40'}),
                            ], md=4)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Label('Atividade:',style={'display':'inline-block','margin-right':20})
                            ], md=2),
                            dbc.Col([
                                dcc.Input(id='atividade', type='text', value='', style={'display':'inline-block', 'border': '1px solid black'}),
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
                        ]),
                    ]),
                    dcc.Link(id='linke-img', href=''),
                    html.Div(id='path-image')
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
                            disabled=False,
                ),
                self.build_tabs_card(),
                dbc.Row(id='app-card'),
                dcc.Store(id="n-interval-stage-card", data=50),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.Button('Gerar Imagens',id='button-img', n_clicks=1)
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
            ], style={'margin': '1.5em'}),
            dbc.Col([
                dcc.Input(id='nome-membro', type='text', placeholder='', style={'display':'inline-block', 'border': '1px solid black'}),
                #html.Div(
                html.H3('Tabela de membros'),
                dbc.Row([
                    html.Div([
                              dcc.Upload(id='upload-data-table-members',
                                           children=html.Button('Carregar novos dados', n_clicks=0),
                                           multiple=True)
                            ])
                ]),
                html.Div(id='output-data-upload-table-member'),
                html.Br(),
                dbc.Row(id='update-table-members'),
                #    ),
                html.H5(id='cont-data-members')
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
                    ], style={'width': '99%'})
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
        def render_tab_content_member(tab_switch, stopped_interval):
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
        def update_interval_state_card(tab_switch, cur_interval, disabled, cur_stage):
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
            new_data = self.df_new_selected[['Nome', 'Telefone', 'Estado Civil', 'Faixa Etária', 'Rua', 'Bairro', 'Número', 'Ponto de Referência', 'conversão']]
            
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
            
            new_data = new_db[['Nome', 'Telefone', 'Estado Civil', 'Esta sendo', 'conversão']]
            self.df_new_selected = new_db
            return self.update_table('table-table',new_data), 'Quantidade de registro conforme a filtragem: {}'.format(cont)
        
        @app.callback(
            [
             Output('update-table-members', 'children'), 
             Output('cont-data-members', 'children')
            ],
            Input('nome-membro', 'value')
            
        )
        def update_graphs_table_members(nome_membro):
            new_db = self.df_members 
            
            cont = len(new_db)
            
            new_data = new_db[['Nome do Membro', 'Celular', 'Cargo Ministerial']]
            
            return self.update_table('table-table-members',new_data), 'Quantidade de registro conforme a filtragem: {}'.format(cont)

        @app.callback(
            [Output('nome', 'value'),
             Output('atividade', 'value'),
             Output('nascimento', 'value'),
             Output('identidade', 'value'),
             Output('cpf', 'value'),
             Output('linke-img', 'href'),
             Output('path-image', 'children')
             ],
            Input('table-table-members', 'derived_virtual_selected_rows'),
            prevent_initial_call=True,
        )
        def select_element_table_member_front(active_cell):
            
            name = ''
            atividade = ''
            nascimento =  ''
            identidade = ''
            cpf = ''
            link = ''
            path_img = ''
            
            if active_cell is None:
                active_cell = []
                
            
            if active_cell != []:
                #active_row_id = active_cell if active_cell else None
                datas = self.df_members.loc[active_cell[0]]
                
                name = str(datas['Nome do Membro'])
                self.name_img_member = name
                atividade = str(datas['Cargo Ministerial'])
                nascimento =  str(datas['Data de Nascimento'])
                identidade = str(datas['RG'])
                cpf = str(datas['CPF'])
                link = datas['Foto do membro']
                
                path_img = (
                    html.Label('Salve a imagem do link acima neste diretorio:'),
                    dcc.Input(id='path-img-member', type='text', value=os.path.abspath('database/imagens_membros'))
                )
                
            return name, atividade, nascimento, identidade, cpf, link, path_img
        
        @app.callback(
            [Output('pai', 'value'),
             Output('mae', 'value'),
             Output('naturalidade', 'value'),
             Output('sexo', 'value'),
             Output('conversao', 'value'),
             Output('batismo-aguas', 'value')
             ],
            Input('table-table-members', 'derived_virtual_selected_rows'),
            prevent_initial_call=True,
        )
        def select_element_table_member_verse(active_cell):
            
            pai = ''
            mae = ''
            naturalidade =  ''
            sexo = ''
            conversao = ''
            batismo = ''
            
            if active_cell is None:
                active_cell = []
                
            
            if active_cell != []:
                #active_row_id = active_cell if active_cell else None
                datas = self.df_members.loc[active_cell[0]]
                
                pai = str(datas['Nome do pai'])
                mae = str(datas['Nome da Mãe'])
                naturalidade =  str(datas['Naturalidade'])
                sexo = str(datas['Sexo'])
                conversao = str(datas['Data de Admissão'])
                batismo = str(datas['Data do batismo nas águas'])
                
            return pai, mae, naturalidade, sexo, conversao, batismo
            
            
        @app.callback(Output('output-data-upload', 'children'),
                      Input('upload-data', 'contents'),
                      State('upload-data', 'filename')
        )
        def update_output(list_of_contents, list_of_names):
            if list_of_contents is not None:
                children = [
                    self.parse_contents(c, n, name_database) for c, n, name_database in zip(list_of_contents, list_of_names, ['database.csv'])]
                return children
            
        
        @app.callback(Output('output-data-upload-table-member', 'children'),
                      Input('upload-data-table-members', 'contents'),
                      State('upload-data-table-members', 'filename')
        )
        def update_output_members(list_of_contents, list_of_names):
            if list_of_contents is not None:
                transform_date = [False]
                children = [
                    self.parse_contents(c, n, name_database, transform) for c, n, name_database, transform, in zip(list_of_contents, list_of_names, ['cadastro de membros.csv'], transform_date)]
                return children
            
        @app.callback(
            Output('cartao-frente', 'src'),
            [Input('button-img', 'n_clicks'),
             State('nome', 'value'),
             State('atividade', 'value'),
             State('nascimento', 'value'),
             State('identidade', 'value'),
             State('cpf', 'value')
            ],
            
            prevent_initial_call=True,
        )
        def btn_generate_image(n_clickes, 
                               value_name,
                               value_atividade,
                               value_nasc,
                               value_ident,
                               value_cpf):
            card = Card_format()
            
            current_date = date.today()
            current_date = current_date.strftime('%d/%m/%Y')
            
            #sum_date = current_date + timedelta(days=10)
            sum_date = pd.to_datetime(current_date) + pd.DateOffset(years=5)
            
            sum_date = sum_date.strftime('%d/%m/%Y')
            
            #if n_clickes == 1:
            data = {
                'name':value_name,
                'cargo': value_atividade,
                'data_nascimento': value_nasc,
                'emisao_card':str(current_date),
                'venci_card': str(sum_date),
                'rg':value_ident,
                'cpf':value_cpf
            }
            card.editImage('database/modelos/cartao_frente.jpeg', 'database/modelos/fundo_frente.jpg', data)
            #card.editImageFundo('assets/cartao_fundo.jpeg', 'assets/fundo_fundo.jpg')
            
            #Rotacionar imagem
            card.trataImage("database/modelos/fundo_frente.jpg", img_member=self.name_img_member)
            #card.trataImage("assets/fundo_fundo.jpg", False)
            del card
            img_filename = 'database/modelos/fundo_frente.jpg'
            encoded_image = base64.b64encode(open(img_filename, 'rb').read())
            
            return 'data:image/jpg;base64,{}'.format(encoded_image.decode())
        
        @app.callback(
            Output('cartao-fundo', 'src'),
            [
                Input('button-img-fundo', 'n_clicks'),
                State('pai', 'value'),
                State('mae', 'value'),
                State('naturalidade', 'value'),
                State('sexo', 'value'),
                State('conversao', 'value'),
                State('batismo-aguas', 'value')
            ],
            prevent_initial_call=True,
        )
        def btn_generate_image(n_clickes,
                               value_pai,
                               value_mae,
                               value_naturalidade,
                               value_sexo,
                               value_conversao,
                               value_batismo):
            card = Card_format()
            data = {
                'nome_pai':value_pai,
                'nome_mae':value_mae,
                'nacionalidade':value_naturalidade,
                'sexo': value_sexo,
                'conversao':value_conversao,
                'batismo':value_batismo
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
        def btn_generate_pdf(n_clickes):
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
    