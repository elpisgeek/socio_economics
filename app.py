import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output
import plotly as py
import plotly.graph_objs as go
from flask_caching import Cache



external = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,
                external_stylesheets=external)

server = app.server

app.title = 'Socio-Economic Dashboard'

cache = Cache(server,config={'CACHE_TYPE':'simple'})

app.config.suppress_callback_exceptions = True


def scatter_data(x_indicator,y_indicator,df,year):
    data1 = df[df['Indicator Name']==x_indicator][['Country Name',
                                                  year]]
    data2 = df[df['Indicator Name']==y_indicator][['Country Name',
                                                  year]]
    dff = pd.merge(data1,data2,left_on='Country Name',right_on='Country Name')
    dff.columns = ['Country',x_indicator,y_indicator]
    return dff


def country_data(country,indicator,df):
    dff = df[(df['Country Name']==country)&(df['Indicator Name']==indicator)]
    dff = dff.iloc[:,3:].T.reset_index()
    dff.columns = ['Year','Value']
    return dff

def get_values(index,dff):
    values = dff.Value.values
    years = dff.Year.values
    current_val = np.round(values[index],2)
    pct_change = np.round(((values[index]-np.abs(values[index-1]))/np.abs(values[index-1])),2)
    return current_val,pct_change


def markdown_text(country,indicator,df):
    data = country_data(country,indicator,df)
    average = np.round(data.iloc[40:,1].mean(),2)
    avg_text = '* The average {} of {} since the year 2000 is {}'.format(indicator,
                                                                       country,average)
    value1,pct1 = get_values(-2,data)
    if pct1 < 0:
        text1 = '* The {} for 2018 is {} a {}% decline from 2017'.format(indicator,value1,
                                                                      np.abs(pct1))
    else:
        text1 = '* The {} for 2018 is {} a {}% increase from 2017'.format(indicator,
                                                                        value1,pct1)
    value2,pct2 = get_values(-3,data)
    if pct2 < 0:
        text2 = '* The {} for 2017 is {} a {}% decline from 2016'.format(indicator,value2,
                                                                      np.abs(pct2))
    else:
        text2 = '* The {} for 2017 is {} a {}% increase from 2016'.format(indicator,
                                                                        value2,pct2)
    value3,pct3 = get_values(-4,data)
    if pct3 < 0:
        text3 = '* The {} for 2016 is {} a {}% decline from 2015'.format(indicator,value3,
                                                                      np.abs(pct3))
    else:
        text3 = '* The {} for 2016 is {} a {}% increase from 2015'.format(indicator,
                                                                        value3,pct3)
    return avg_text,text1,text2,text3

def time_series(data,title,color):
    x_data = data.Year
    y_data = data.Value
    chart = [
        go.Scatter(x=x_data,
                  y=y_data,
                  mode='lines+markers',
                  marker={'size':5,
                         'line':{
                             'width':.2
                         },
                         'color':color},
                  opacity=.6)
    ]
    layout = go.Layout(height=225,
                      xaxis={'title':'Years',
                            'titlefont':{
                                'family':'Raleway',
                                'size':13,
                                'color':'#111111'
                            },
                            'showgrid':False,
                            'tickfont':{
                                'family':'Raleway',
                                'size':12,
                                'color':'#111111'
                            }},
                      yaxis={'tickfont':{
                          'family':'Raleway',
                          'size':12,
                          'color':'#111111'
                      }},
                      annotations=[{
                          'x':0,'y':0.85,'xanchor':'left',
                          'yanchor':'bottom','xref':'paper',
                          'yref':'paper','text':title,
                          'showarrow':False,'align':'left'
                      }],
                      margin={'l':30,'b':30,'r':10,'t':10})
    return {'data':chart,'layout':layout}

def indicator_info(indicator_name,metadata):
    data = metadata[metadata['INDICATOR_NAME']==indicator_name]
    return data['SOURCE_NOTE'].values[0]


health_file1 = 'https://raw.githubusercontent.com/prince381/socio_economics/master/data/Health_1.csv'
health_file2 = 'https://raw.githubusercontent.com/prince381/socio_economics/master/data/Health_2.csv'
health_file3 = 'https://raw.githubusercontent.com/prince381/socio_economics/master/data/Health_metadata.csv'
health_data1 = pd.read_csv(health_file1)
health_data2 = pd.read_csv(health_file2)
health_data = pd.concat([health_data1,health_data2],axis=0)
health_metadata = pd.read_csv(health_file3)
health_indicator_names = health_data['Indicator Name'].unique()

edu_file1 = 'https://raw.githubusercontent.com/prince381/socio_economics/master/data/Education.csv'
edu_file2 = 'https://raw.githubusercontent.com/prince381/socio_economics/master/data/Education_metadata.csv'
edu_data = pd.read_csv(edu_file1)
edu_metadata = pd.read_csv(edu_file2)
edu_indicator_names = edu_data['Indicator Name'].unique()

econ_file1 = 'https://raw.githubusercontent.com/prince381/socio_economics/master/data/Economy_1.csv'
econ_file2 = 'https://raw.githubusercontent.com/prince381/socio_economics/master/data/Economy_2.csv'
econ_file3 = 'https://raw.githubusercontent.com/prince381/socio_economics/master/data/Economy_metadata.csv'
econ_data1 = pd.read_csv(econ_file1)
econ_data2 = pd.read_csv(econ_file2)
econ_data = pd.concat([econ_data1,econ_data2],axis=0)
econ_metadata = pd.read_csv(econ_file3)
econ_indicator_names = econ_data['Indicator Name'].unique()

country_names = health_data['Country Name'].unique()
years = health_data.columns[3:]

health_layout = [html.Div([
    
    html.Div([
        
        dcc.RadioItems(id='health_page_no',
                      options=[
                          {'label':i,'value':i} for i in ['Global','Country-Specific']
                      ],
                      value='Global',
                      labelStyle={'display':'inline-block'})
        
    ],className='row',
    style={'margin':'20px'}),
    
    html.Div(id='health_page_output',className='row',
    style={'margin':'20px'})
    
],style={'backgroundColor':'whitesmoke',
        'border-right':'3px solid lightgrey',
        'border-bottom':'3px solid lightgrey'})
]

education_layout = [
    html.Div([
    
    html.Div([
        
        dcc.RadioItems(id='edu_page_no',
                      options=[
                          {'label':i,'value':i} for i in ['Global','Country-Specific']
                      ],
                      value='Global',
                      labelStyle={'display':'inline-block'})
        
    ],className='row',
    style={'margin':'20px'}),
    
    html.Div(id='edu_page_output',className='row',
    style={'margin':'20px'})
    
],style={'backgroundColor':'whitesmoke',
        'border-right':'3px solid lightgrey',
        'border-bottom':'3px solid lightgrey'})
]

economy_layout = [
    html.Div([
    
    html.Div([
        
        dcc.RadioItems(id='page_no',
                      options=[
                          {'label':i,'value':i} for i in ['Global','Country-Specific']
                      ],
                      value='Global',
                      labelStyle={'display':'inline-block'})
        
    ],className='row',
    style={'margin':'20px'}),
    
    html.Div(id='page_output',className='row',
    style={'margin':'20px'})
    
],style={'backgroundColor':'whitesmoke',
        'border-right':'3px solid lightgrey',
        'border-bottom':'3px solid lightgrey'})
]

app.layout = html.Div([
    
    html.Div([
        
        html.Div([
            
                html.Div([

                dcc.Location(id='url',refresh=True),

                dcc.Link('Health Indicators',href='/health',
                        style={'margin':10}),

                dcc.Link('Education Indicators',href='/education',
                        style={'margin':10}),

                dcc.Link('Economic Growth Indicators',href='/economy',
                        style={'margin':10})
                
            ],className='row'),
            
            html.Div([
                
                html.Div([
                    
                    html.Label('Created by : Prince Owusu',
                              style={'fontWeight':'bold',
                                    'fontFamily':'Raleway'})
                    
                ],className='three columns'),
                
                html.Div([
                    
                    html.Div([
                        
                        html.Img(src='https://pmcvariety.files.wordpress.com/2018/04/twitter-logo.jpg?w=1000',
                                width=40,height=30)
                        
                    ],className='two columns'),
                    
                    html.Div([
                        
                        html.A('@iam_kwekhu',href='https://twitter.com/iam_kwekhu')
                        
                    ],className='two columns')
                    
                ],className='three columns')
                
            ],className='row',
            style={'margin-left':'10px',
                  'margin-top':'7px'})
            
        ],className='ten columns'),
        
        html.Span([
            
            html.Div([
           
                html.Img(src='https://repository-images.githubusercontent.com/33702544/b4400c80-718b-11e9-9f3a-306c07a5f3de',
                        width=100,
                        height=50)
                
            ],style={'margin-top':'7px'})
            
        ],className='two columns')
        
    ],className='row',
    style={'border-right':'3px solid lightgrey',
          'border-bottom':'3px solid lightgrey',
          'backgroundColor':'whitesmoke'}),
        
    html.Div(id='page_out'),
    
    html.Div([
        
        dcc.Markdown('source of data : [World Bank](https://data.worldbank.org) || application source code : [Github.com](https://github.com/prince381/socio_economics)')
        
    ],className='row')
        
    
],className='row',
style={'margin':'10px'})

@app.callback(Output('page_out','children'),
             [Input('url','pathname')])
def main_page(pathname):
    if pathname == '/health':
        return health_layout
    elif pathname == '/education':
        return education_layout
    else:
        return economy_layout
    

@app.callback(Output('health_page_output','children'),
             [Input('health_page_no','value')])
def render_healthpage(value):
    if value == 'Global':
        return [
            html.Div([
                
                html.Div([
                    
                    html.Label('Select indicator',
                              className='label',
                              style={'fontWeight':'bold'}),
                    dcc.Dropdown(id='health_xaxis_indi',
                                options=[
                                    {'label':i,'value':i} for i in health_indicator_names
                                ],
                                value='Population, total',
                                clearable=False),
                    html.Div([
                        html.Div([
                            html.Label('X-axis type'),
                            dcc.RadioItems(id='health_xaxis_type',
                                          options=[
                                              {'label':i,'value':i} for i in ['log','linear']
                                          ],
                                          value='log',
                                          labelStyle={'display':'inline-block'})
                        ],className='six columns'),
                        html.Div([
                            html.Label('Y-axis type'),
                            dcc.RadioItems(id='health_yaxis_type',
                                          options=[
                                              {'label':i,'value':i} for i in ['log','linear']
                                          ],
                                          value='log',
                                          labelStyle={'display':'inline-block'})
                        ],className='six columns')
                    ],className='row')
                ],className='six columns'),
                
                html.Div([
                    
                    html.Label('Select indicator',
                              className='label',
                              style={'fontWeight':'bold'}),
                    dcc.Dropdown(id='health_yaxis_indi',
                                options=[
                                    {'label':i,'value':i} for i in health_indicator_names
                                ],
                                value='Newborns protected against tetanus (%)',
                                clearable=False)
                    
                ],className='six columns')
                
            ],className='row',
            style={'margin':'20px'}),
            
            html.Div([
                
                html.Div([
                    
                    dcc.Graph(id='health_scatter',
                              hoverData={'points':[{'customdata':'Malaysia'}]})
                    
                ],className='six columns',
                    style={'border-radius':7,
                          'border-bottom':'4px solid lightgrey',
                          'border-right':'4px solid lightgrey'}),
                
                html.Div([
                    
                    html.Div([
                        
                        dcc.Graph(id='health_series1'),
                        dcc.Graph(id='health_series2')
                        
                    ],className='row',
                    style={'border-radius':7,
                          'border-bottom':'4px solid lightgrey',
                          'border-right':'4px solid lightgrey'})
                    
                ],className='six columns',
                style={'display':'inline-block'})
                
            ],className='row',
            style={'margin':'20px'}),
            
            html.Div([
                
                dcc.Slider(id='health_years',
                           min=int(years[30:-1][0]),
                           max=int(years[30:-1][-1]),
                          marks={int(i):i for i in years[30:-1]},
                          value=int(years[30:-1][-1]))
                
            ],className='row',
            style={'margin':'20px'})
        ]
    else:
        return html.Div([
            
            html.Div([
                
                html.H5('Visualized Historical Data for Health Indicators')
                
            ],className='row',
            style={'margin':'20px',
                  'fontFamily':'Raleway',
                   'fontWeight':'bold',
                  'textAlign':'left'}),
            
            html.Div([
                
                html.Div([
                    
                    html.Label('Select Country',
                              style={'fontWeight':'bold'}),
                    dcc.Dropdown(id='health_country',
                                options=[
                                    {'label':i,'value':i} for i in country_names
                                ],
                                value='Malaysia',
                                clearable=False)
                    
                ],className='six columns'),
                
                html.Div([
                    
                    html.Label('Select Indicator',
                              style={'fontWeight':'bold'}),
                    dcc.Dropdown(id='health_indicator',
                                options=[
                                    {'label':i,'value':i} for i in health_indicator_names
                                ],
                                value='Newborns protected against tetanus (%)',
                                clearable=False)
                    
                ],className='six columns')
                
            ],className='row',
            style={'margin':'20px'}),
            
            html.Div([
                
                html.Div([
                    
                    html.Div(id='health_indicator_info',className='row'),
                    
                    html.Br(),
                    
                    html.Div(id='health_indicator_stat',className='row',
                            style={'color':'purple'})
                    
                ],className='six columns'),
                
                html.Div([
                    
                    dcc.Graph(id='health_country_specific')
                    
                ],className='six columns',
                style={'border-radius':7,
                      'border-bottom':'4px solid lightgrey',
                      'border-right':'4px solid lightgrey'})
                
            ],className='row',
            style={'margin':'20px'})
            
        ])


@app.callback(Output('health_scatter','figure'),
             [Input('health_xaxis_indi','value'),
             Input('health_yaxis_indi','value'),
             Input('health_xaxis_type','value'),
             Input('health_yaxis_type','value'), 
             Input('health_years','value')])
def make_health_scatter(xaxis_indi,yaxis_indi,xaxis_type,yaxis_type,year):
    data = scatter_data(xaxis_indi,yaxis_indi,health_data,str(year))
    xdata = data[xaxis_indi].values
    ydata = data[yaxis_indi].values
    text = data['Country']
    customdata = data['Country'].values
    
    chart = [
        go.Scatter(x=xdata,
                  y=ydata,
                  mode='markers',
                  marker={
                      'size':10
                  },
                  opacity=.5,
                  text=text,
                  customdata=customdata)
    ]
    layout = go.Layout(xaxis={'title':xaxis_indi,
                             'titlefont':{
                                 'family':'Raleway',
                                 'size':15,
                                 'color':'#111111'
                             },
                             'tickfont':{
                                 'family':'Raleway',
                                 'size':13,
                                 'color':'#111111'
                             },'type':'log' if xaxis_type=='log' else 'linear'},
                      yaxis={'title':yaxis_indi,
                             'titlefont':{
                                 'family':'Raleway',
                                 'size':15,
                                 'color':'#111111'
                             },
                             'tickfont':{
                                 'family':'Raleway',
                                 'size':13,
                                 'color':'#111111'
                             },'type':'log' if yaxis_type=='log' else 'linear'},
                      hovermode='closest')
    return {'data':chart,'layout':layout}

@app.callback(Output('health_series1','figure'),
             [Input('health_scatter','hoverData'),
             Input('health_xaxis_indi','value')])
def health_series1(hoverData,indicator):
    country = hoverData['points'][0]['customdata']
    title = '<b>{}</b><br>{}'.format(country,indicator)
    data = country_data(country,indicator,health_data)
    return time_series(data,title,'darkorange')

@app.callback(Output('health_series2','figure'),
             [Input('health_scatter','hoverData'),
             Input('health_yaxis_indi','value')])
def health_series1(hoverData,indicator):
    country = hoverData['points'][0]['customdata']
    title = indicator
    data = country_data(country,indicator,health_data)
    return time_series(data,title,'green')

@app.callback(Output('health_country_specific','figure'),
             [Input('health_country','value'),
             Input('health_indicator','value')])
def health_specific(country,indicator):
    data = country_data(country,indicator,health_data)
    x_data = data.Year
    y_data = data.Value
    title = '<b>{}</b><br>{}'.format(country,indicator)
    chart = [
        go.Scatter(x=x_data,
                  y=y_data,
                  mode='lines+markers',
                  marker={'size':5,
                         'line':{
                             'width':.2
                         },
                         'color':'purple'},
                  opacity=.6)
    ]
    layout = go.Layout(xaxis={'title':'Years',
                            'titlefont':{
                                'family':'Raleway',
                                'size':13,
                                'color':'#111111'
                            },
                            'showgrid':False,
                            'tickfont':{
                                'family':'Raleway',
                                'size':12,
                                'color':'#111111'
                            }},
                      yaxis={'tickfont':{
                          'family':'Raleway',
                          'size':12,
                          'color':'#111111'
                      }},
                      annotations=[{
                          'x':0,'y':0.85,'xanchor':'left',
                          'yanchor':'bottom','xref':'paper',
                          'yref':'paper','text':title,
                          'showarrow':False,'align':'left'
                      }],
                      margin={'l':30,'b':30,'r':10,'t':10},
                      height=430)
    return {'data':chart,'layout':layout}


@app.callback(Output('health_indicator_info','children'),
             [Input('health_indicator','value')])
def health_text1(indicator):
    text = indicator_info(indicator,health_metadata)
    return [
        html.P(text,style={
            'fontFamily':'Raleway',
            'fontWeight':'bold'
        })
    ]


@app.callback(Output('health_indicator_stat','children'),
             [Input('health_country','value'),
             Input('health_indicator','value')])
def health_text2(country,indicator):
    avg,text1,text2,text3 = markdown_text(country,indicator,health_data)
    return [
        dcc.Markdown(avg),
        dcc.Markdown(text1),
        dcc.Markdown(text2),
        dcc.Markdown(text3)
    ]

@app.callback(Output('edu_page_output','children'),
             [Input('edu_page_no','value')])
def render_edupage(value):
    if value == 'Global':
        return [
            html.Div([
                
                html.Div([
                    
                    html.Label('Select indicator',
                              className='label',
                              style={'fontWeight':'bold'}),
                    dcc.Dropdown(id='edu_xaxis_indi',
                                options=[
                                    {'label':i,'value':i} for i in edu_indicator_names
                                ],
                                value='School enrollment, tertiary (% gross)',
                                clearable=False),
                    html.Div([
                        html.Div([
                            html.Label('X-axis type'),
                            dcc.RadioItems(id='edu_xaxis_type',
                                          options=[
                                              {'label':i,'value':i} for i in ['log','linear']
                                          ],
                                          value='log',
                                          labelStyle={'display':'inline-block'})
                        ],className='six columns'),
                        html.Div([
                            html.Label('Y-axis type'),
                            dcc.RadioItems(id='edu_yaxis_type',
                                          options=[
                                              {'label':i,'value':i} for i in ['log','linear']
                                          ],
                                          value='log',
                                          labelStyle={'display':'inline-block'})
                        ],className='six columns')
                    ],className='row')
                ],className='six columns'),
                
                html.Div([
                    
                    html.Label('Select indicator',
                              className='label',
                              style={'fontWeight':'bold'}),
                    dcc.Dropdown(id='edu_yaxis_indi',
                                options=[
                                    {'label':i,'value':i} for i in edu_indicator_names
                                ],
                                value='Population ages 15-64 (% of total population)',
                                clearable=False)
                    
                ],className='six columns')
                
            ],className='row',
            style={'margin':'20px'}),
            
            html.Div([
                
                html.Div([
                    
                    dcc.Graph(id='edu_scatter',
                              hoverData={'points':[{'customdata':'United Kingdom'}]})
                    
                ],className='six columns',
                    style={'border-radius':7,
                          'border-bottom':'4px solid lightgrey',
                          'border-right':'4px solid lightgrey'}),
                
                html.Div([
                    
                    html.Div([
                        
                        dcc.Graph(id='edu_series1'),
                        dcc.Graph(id='edu_series2')
                        
                    ],className='row',
                    style={'border-radius':7,
                          'border-bottom':'4px solid lightgrey',
                          'border-right':'4px solid lightgrey'})
                    
                ],className='six columns',
                style={'display':'inline-block'})
                
            ],className='row',
            style={'margin':'20px'}),
            
            html.Div([
                
                dcc.Slider(id='edu_years',
                           min=int(years[30:-1][0]),
                           max=int(years[30:-1][-1]),
                          marks={int(i):i for i in years[30:-1]},
                          value=int(years[30:-1][-1]))
                
            ],className='row',
            style={'margin':'20px'})
        ]
    else:
        return html.Div([
            
            html.Div([
                
                html.H5('Visualized Historical Data for Educational Indicators')
                
            ],className='row',
            style={'margin':'20px',
                  'fontFamily':'Raleway',
                   'fontWeight':'bold',
                  'textAlign':'left'}),
            
            html.Div([
                
                html.Div([
                    
                    html.Label('Select Country',
                              style={'fontWeight':'bold'}),
                    dcc.Dropdown(id='edu_country',
                                options=[
                                    {'label':i,'value':i} for i in country_names
                                ],
                                value='United Kingdom',
                                clearable=False)
                    
                ],className='six columns'),
                
                html.Div([
                    
                    html.Label('Select Indicator',
                              style={'fontWeight':'bold'}),
                    dcc.Dropdown(id='edu_indicator',
                                options=[
                                    {'label':i,'value':i} for i in edu_indicator_names
                                ],
                                value='School enrollment, tertiary (% gross)',
                                clearable=False)
                    
                ],className='six columns')
                
            ],className='row',
            style={'margin':'20px'}),
            
            html.Div([
                
                html.Div([
                    
                    html.Div(id='edu_indicator_info',className='row'),
                    
                    html.Br(),
                    
                    html.Div(id='edu_indicator_stat',className='row',
                            style={'color':'purple'})
                    
                ],className='six columns'),
                
                html.Div([
                    
                    dcc.Graph(id='edu_country_specific')
                    
                ],className='six columns',
                style={'border-radius':7,
                      'border-bottom':'4px solid lightgrey',
                      'border-right':'4px solid lightgrey'})
                
            ],className='row',
            style={'margin':'20px'})
            
        ])


@app.callback(Output('edu_scatter','figure'),
             [Input('edu_xaxis_indi','value'),
             Input('edu_yaxis_indi','value'),
             Input('edu_xaxis_type','value'),
             Input('edu_yaxis_type','value'), 
             Input('edu_years','value')])
def make_edu_scatter(xaxis_indi,yaxis_indi,xaxis_type,yaxis_type,year):
    data = scatter_data(xaxis_indi,yaxis_indi,edu_data,str(year))
    xdata = data[xaxis_indi].values
    ydata = data[yaxis_indi].values
    text = data['Country']
    customdata = data['Country'].values
    
    chart = [
        go.Scatter(x=xdata,
                  y=ydata,
                  mode='markers',
                  marker={
                      'size':10
                  },
                  opacity=.5,
                  text=text,
                  customdata=customdata)
    ]
    layout = go.Layout(xaxis={'title':xaxis_indi,
                             'titlefont':{
                                 'family':'Raleway',
                                 'size':15,
                                 'color':'#111111'
                             },
                             'tickfont':{
                                 'family':'Raleway',
                                 'size':13,
                                 'color':'#111111'
                             },'type':'log' if xaxis_type=='log' else 'linear'},
                      yaxis={'title':yaxis_indi,
                             'titlefont':{
                                 'family':'Raleway',
                                 'size':15,
                                 'color':'#111111'
                             },
                             'tickfont':{
                                 'family':'Raleway',
                                 'size':13,
                                 'color':'#111111'
                             },'type':'log' if yaxis_type=='log' else 'linear'},
                      hovermode='closest')
    return {'data':chart,'layout':layout}

@app.callback(Output('edu_series1','figure'),
             [Input('edu_scatter','hoverData'),
             Input('edu_xaxis_indi','value')])
def edu_series1(hoverData,indicator):
    country = hoverData['points'][0]['customdata']
    title = '<b>{}</b><br>{}'.format(country,indicator)
    data = country_data(country,indicator,edu_data)
    return time_series(data,title,'darkorange')

@app.callback(Output('edu_series2','figure'),
             [Input('edu_scatter','hoverData'),
             Input('edu_yaxis_indi','value')])
def edu_series1(hoverData,indicator):
    country = hoverData['points'][0]['customdata']
    title = indicator
    data = country_data(country,indicator,edu_data)
    return time_series(data,title,'green')

@app.callback(Output('edu_country_specific','figure'),
             [Input('edu_country','value'),
             Input('edu_indicator','value')])
def edu_specific(country,indicator):
    data = country_data(country,indicator,edu_data)
    x_data = data.Year
    y_data = data.Value
    title = '<b>{}</b><br>{}'.format(country,indicator)
    chart = [
        go.Scatter(x=x_data,
                  y=y_data,
                  mode='lines+markers',
                  marker={'size':5,
                         'line':{
                             'width':.2
                         },
                         'color':'purple'},
                  opacity=.6)
    ]
    layout = go.Layout(xaxis={'title':'Years',
                            'titlefont':{
                                'family':'Raleway',
                                'size':13,
                                'color':'#111111'
                            },
                            'showgrid':False,
                            'tickfont':{
                                'family':'Raleway',
                                'size':12,
                                'color':'#111111'
                            }},
                      yaxis={'tickfont':{
                          'family':'Raleway',
                          'size':12,
                          'color':'#111111'
                      }},
                      annotations=[{
                          'x':0,'y':0.85,'xanchor':'left',
                          'yanchor':'bottom','xref':'paper',
                          'yref':'paper','text':title,
                          'showarrow':False,'align':'left'
                      }],
                      margin={'l':30,'b':30,'r':10,'t':10},
                      height=430)
    return {'data':chart,'layout':layout}


@app.callback(Output('edu_indicator_info','children'),
             [Input('edu_indicator','value')])
def edu_text1(indicator):
    text = indicator_info(indicator,edu_metadata)
    return [
        html.P(text,style={
            'fontFamily':'Raleway',
            'fontWeight':'bold'
        })
    ]


@app.callback(Output('edu_indicator_stat','children'),
             [Input('edu_country','value'),
             Input('edu_indicator','value')])
def edu_text2(country,indicator):
    avg,text1,text2,text3 = markdown_text(country,indicator,edu_data)
    return [
        dcc.Markdown(avg),
        dcc.Markdown(text1),
        dcc.Markdown(text2),
        dcc.Markdown(text3)
    ]

@app.callback(Output('page_output','children'),
             [Input('page_no','value')])
def render_econpage(value):
    if value == 'Global':
        return [
            html.Div([
                
                html.Div([
                    
                    html.Label('Select indicator',
                              className='label',
                              style={'fontWeight':'bold'}),
                    dcc.Dropdown(id='econ_xaxis_indi',
                                options=[
                                    {'label':i,'value':i} for i in econ_indicator_names
                                ],
                                value='GDP (constant 2010 US$)',
                                clearable=False),
                    html.Div([
                        html.Div([
                            html.Label('X-axis type'),
                            dcc.RadioItems(id='econ_xaxis_type',
                                          options=[
                                              {'label':i,'value':i} for i in ['log','linear']
                                          ],
                                          value='log',
                                          labelStyle={'display':'inline-block'})
                        ],className='six columns'),
                        html.Div([
                            html.Label('Y-axis type'),
                            dcc.RadioItems(id='econ_yaxis_type',
                                          options=[
                                              {'label':i,'value':i} for i in ['log','linear']
                                          ],
                                          value='log',
                                          labelStyle={'display':'inline-block'})
                        ],className='six columns')
                    ],className='row')
                ],className='six columns'),
                
                html.Div([
                    
                    html.Label('Select indicator',
                              className='label',
                              style={'fontWeight':'bold'}),
                    dcc.Dropdown(id='econ_yaxis_indi',
                                options=[
                                    {'label':i,'value':i} for i in econ_indicator_names
                                ],
                                value='GDP per capita (current US$)',
                                clearable=False)
                    
                ],className='six columns')
                
            ],className='row',
            style={'margin':'20px'}),
            
            html.Div([
                
                html.Div([
                    
                    dcc.Graph(id='econ_scatter',
                              hoverData={'points':[{'customdata':'France'}]})
                    
                ],className='six columns',
                    style={'border-radius':7,
                          'border-bottom':'4px solid lightgrey',
                          'border-right':'4px solid lightgrey'}),
                
                html.Div([
                    
                    html.Div([
                        
                        dcc.Graph(id='econ_series1'),
                        dcc.Graph(id='econ_series2')
                        
                    ],className='row',
                    style={'border-radius':7,
                          'border-bottom':'4px solid lightgrey',
                          'border-right':'4px solid lightgrey'})
                    
                ],className='six columns',
                style={'display':'inline-block'})
                
            ],className='row',
            style={'margin':'20px'}),
            
            html.Div([
                
                dcc.Slider(id='econ_years',
                           min=int(years[30:-1][0]),
                           max=int(years[30:-1][-1]),
                          marks={int(i):i for i in years[30:-1]},
                          value=int(years[30:-1][-1]))
                
            ],className='row',
            style={'margin':'20px'})
        ]
    else:
        return html.Div([
            
            html.Div([
                
                html.H5('Visualized Historical Data for Economic Growth Indicators')
                
            ],className='row',
            style={'margin':'20px',
                  'fontFamily':'Raleway',
                   'fontWeight':'bold',
                  'textAlign':'left'}),
            
            html.Div([
                
                html.Div([
                    
                    html.Label('Select Country',
                              style={'fontWeight':'bold'}),
                    dcc.Dropdown(id='econ_country',
                                options=[
                                    {'label':i,'value':i} for i in country_names
                                ],
                                value='France',
                                clearable=False)
                    
                ],className='six columns'),
                
                html.Div([
                    
                    html.Label('Select Indicator',
                              style={'fontWeight':'bold'}),
                    dcc.Dropdown(id='econ_indicator',
                                options=[
                                    {'label':i,'value':i} for i in econ_indicator_names
                                ],
                                value='GDP per capita (current US$)',
                                clearable=False)
                    
                ],className='six columns')
                
            ],className='row',
            style={'margin':'20px'}),
            
            html.Div([
                
                html.Div([
                    
                    html.Div(id='econ_indicator_info',className='row'),
                    
                    html.Br(),
                    
                    html.Div(id='econ_indicator_stat',className='row',
                            style={'color':'purple'})
                    
                ],className='six columns'),
                
                html.Div([
                    
                    dcc.Graph(id='econ_country_specific')
                    
                ],className='six columns',
                style={'border-radius':7,
                      'border-bottom':'4px solid lightgrey',
                      'border-right':'4px solid lightgrey'})
                
            ],className='row',
            style={'margin':'20px'})
            
        ])


@app.callback(Output('econ_scatter','figure'),
             [Input('econ_xaxis_indi','value'),
             Input('econ_yaxis_indi','value'),
             Input('econ_xaxis_type','value'),
             Input('econ_yaxis_type','value'), 
             Input('econ_years','value')])
def make_econ_scatter(xaxis_indi,yaxis_indi,xaxis_type,yaxis_type,year):
    data = scatter_data(xaxis_indi,yaxis_indi,econ_data,str(year))
    xdata = data[xaxis_indi].values
    ydata = data[yaxis_indi].values
    text = data['Country']
    customdata = data['Country'].values
    
    chart = [
        go.Scatter(x=xdata,
                  y=ydata,
                  mode='markers',
                  marker={
                      'size':10
                  },
                  opacity=.5,
                  text=text,
                  customdata=customdata)
    ]
    layout = go.Layout(xaxis={'title':xaxis_indi,
                             'titlefont':{
                                 'family':'Raleway',
                                 'size':15,
                                 'color':'#111111'
                             },
                             'tickfont':{
                                 'family':'Raleway',
                                 'size':13,
                                 'color':'#111111'
                             },'type':'log' if xaxis_type=='log' else 'linear'},
                      yaxis={'title':yaxis_indi,
                             'titlefont':{
                                 'family':'Raleway',
                                 'size':15,
                                 'color':'#111111'
                             },
                             'tickfont':{
                                 'family':'Raleway',
                                 'size':13,
                                 'color':'#111111'
                             },'type':'log' if yaxis_type=='log' else 'linear'},
                      hovermode='closest')
    return {'data':chart,'layout':layout}

@app.callback(Output('econ_series1','figure'),
             [Input('econ_scatter','hoverData'),
             Input('econ_xaxis_indi','value')])
def econ_series1(hoverData,indicator):
    country = hoverData['points'][0]['customdata']
    title = '<b>{}</b><br>{}'.format(country,indicator)
    data = country_data(country,indicator,econ_data)
    return time_series(data,title,'darkorange')

@app.callback(Output('econ_series2','figure'),
             [Input('econ_scatter','hoverData'),
             Input('econ_yaxis_indi','value')])
def econ_series1(hoverData,indicator):
    country = hoverData['points'][0]['customdata']
    title = indicator
    data = country_data(country,indicator,econ_data)
    return time_series(data,title,'green')

@app.callback(Output('econ_country_specific','figure'),
             [Input('econ_country','value'),
             Input('econ_indicator','value')])
def econ_specific(country,indicator):
    data = country_data(country,indicator,econ_data)
    x_data = data.Year
    y_data = data.Value
    title = '<b>{}</b><br>{}'.format(country,indicator)
    chart = [
        go.Scatter(x=x_data,
                  y=y_data,
                  mode='lines+markers',
                  marker={'size':5,
                         'line':{
                             'width':.2
                         },
                         'color':'purple'},
                  opacity=.6)
    ]
    layout = go.Layout(xaxis={'title':'Years',
                            'titlefont':{
                                'family':'Raleway',
                                'size':13,
                                'color':'#111111'
                            },
                            'showgrid':False,
                            'tickfont':{
                                'family':'Raleway',
                                'size':12,
                                'color':'#111111'
                            }},
                      yaxis={'tickfont':{
                          'family':'Raleway',
                          'size':12,
                          'color':'#111111'
                      }},
                      annotations=[{
                          'x':0,'y':0.85,'xanchor':'left',
                          'yanchor':'bottom','xref':'paper',
                          'yref':'paper','text':title,
                          'showarrow':False,'align':'left'
                      }],
                      margin={'l':30,'b':30,'r':10,'t':10},
                      height=430)
    return {'data':chart,'layout':layout}


@app.callback(Output('econ_indicator_info','children'),
             [Input('econ_indicator','value')])
def econ_text1(indicator):
    text = indicator_info(indicator,econ_metadata)
    return [
        html.P(text,style={
            'fontFamily':'Raleway',
            'fontWeight':'bold'
        })
    ]


@app.callback(Output('econ_indicator_stat','children'),
             [Input('econ_country','value'),
             Input('econ_indicator','value')])
def econ_text2(country,indicator):
    avg,text1,text2,text3 = markdown_text(country,indicator,econ_data)
    return [
        dcc.Markdown(avg),
        dcc.Markdown(text1),
        dcc.Markdown(text2),
        dcc.Markdown(text3)
    ]
    


if __name__ == '__main__':
    app.run_server(debug=False)
