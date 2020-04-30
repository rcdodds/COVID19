# Libraries
import datetime
import pandas as pd
import numpy as np
# Plotly for making visuals
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# Dash for generating HTML
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Create app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# State abbreviations
us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}
state_dd = [{'label': 'Select a state', 'value': 'unused', 'disabled': True}]
for abbrev in us_state_abbrev:
    state_dd.append({'label': abbrev, 'value': abbrev})

# Pull Overview Statistics -- Important Columns include Province_State, ST, Confirmed, Deaths, People_Tested, People_Hospitalized
OverviewFileRoot = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/'
OverviewFileName = OverviewFileRoot + datetime.datetime.today().strftime('%m-%d-%Y') + '.csv'
try:        # Try to use today's data
    Overview = pd.read_csv(OverviewFileName)
except:     # If today's report hasn't been uploaded yet, use yesterday's report
    OverviewFileName = OverviewFileRoot + datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(1), '%m-%d-%Y') + '.csv'
    Overview = pd.read_csv(OverviewFileName)
# Rename a few columns
Overview = Overview.rename(columns={'People_Tested': 'Tested', 'People_Hospitalized': 'Hospitalizations'})
# Add state abbreviations
Overview.insert(1, 'ST', Overview['Province_State'].map(us_state_abbrev))
# Remove anything that isn't a state/district/territory (e.g. cruise ships, prisons, etc)
Overview = Overview[Overview['Province_State'].isin(us_state_abbrev.keys())]
Overview.to_csv("Overview.csv")

# Pull cases & deaths by county
CasesFileName = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
DeathsFileName = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv'
CtyCases = pd.read_csv(CasesFileName)
CtyDeaths = pd.read_csv(DeathsFileName)

# Remove anything that isn't a state/district/territory (e.g. cruise ships, prisons, etc)
CtyCases = CtyCases[CtyCases['Province_State'].isin(us_state_abbrev.keys())]
CtyDeaths = CtyDeaths[CtyDeaths['Province_State'].isin(us_state_abbrev.keys())]

# Sum totals by state & organize as time series (Columns = state names, Rows = dates)
drop_cols = ['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'Lat', 'Long_', 'Combined_Key']
group_cols = ['Province_State']
CtyCases = CtyCases.drop(columns=drop_cols)
drop_cols.append('Population')
CtyDeaths = CtyDeaths.drop(columns=drop_cols)

# TotalCases = CtyCases.groupby(group_cols).sum().transpose().diff()
# TotalDeaths = CtyDeaths.groupby(group_cols).sum().transpose().diff()
#
# # Calculate increases by day
# NewCases = TotalCases.diff()
# NewDeaths = TotalDeaths.diff()
#
# DailyData = pd.concat([NewCases, NewDeaths], keys=['New Confirmed Cases', 'Deaths'])
#
# # For viewing
CtyCases.to_csv("CtyCases.csv")
CtyDeaths.to_csv("CtyDeaths.csv")
# TotalCases.to_csv("TotalCases.csv")
# TotalDeaths.to_csv("TotalDeaths.csv")
# NewCases.to_csv("NewCases.csv")
# NewDeaths.to_csv("NewDeaths.csv")

# US map showing data from chosen radio button
usmap = go.Figure()
usmap.layout.template = 'plotly_dark'
usmap.add_trace(
        go.Choropleth(
            locations=Overview['ST'],  # State abbreviations
            z=Overview['Confirmed'].astype(float),  # Data to be color-coded
            locationmode='USA-states',  # set of locations match entries in `locations`
            colorscale='Reds',
            colorbar=dict(
                title='Confirmed Cases',
                thickness=15,
                len=1.75,
                xanchor='left',
                x=0
            )
        )
)
usmap.update_layout(
    geo=dict(
        scope='usa',
        projection=go.layout.geo.Projection(type='albers usa'),
        showlakes=False
    )
)


# Build the actual web page
app.layout = \
    html.Div(
        children=[
            # Title section
            html.Div(
                children=[
                    # Title
                    html.H1(children='United States vs COVID-19', style={'textAlign': 'center'}),
                    # Sub-title
                    html.H2(children='How is the United States progressing towards a phased re-opening?',
                            style={'textAlign': 'center'})
                ]
            ),

            # Top row -- country map & line graph
            dbc.Row(
                [
                    # USA choropleth map with radio buttons
                    dbc.Col(
                        [
                            # USA choropleth map
                            dcc.Graph(figure=usmap, id='usmap'),
                            # Radio buttons
                            dbc.RadioItems(
                                id='variable-picker',
                                options=[
                                    {'label': 'People Tested', 'value': 'People Tested'},
                                    {'label': 'Confirmed Cases', 'value': 'Confirmed Cases'},
                                    {'label': 'Hospitalizations', 'value': 'Hospitalizations'},
                                    {'label': 'Deaths', 'value': 'Deaths'}
                                ],
                                value='Confirmed Cases',
                                inline=True
                            )
                        ]
                    ),
                    # Line graph of recent data for subset of country
                    dbc.Col(
                        [
                            # Line graph
                            dcc.Graph(id='line_graph'),
                            # Multiple inputs to change graph view
                            dbc.Row(
                                [
                                    # Aggregate level drop-down selection
                                    dbc.Col(dbc.Button(id='country_toggle', color='secondary')),
                                    # State drop-down selection
                                    dbc.Col(dbc.Select(id='state_dd', options=state_dd, value='unused')),
                                    # County drop-down selection
                                    dbc.Col(dbc.Select(id='county_dd', options=[{'label': 'Select a county', 'value': 'unused', 'disabled': True}], value='unused')),
                                    # Moving average period
                                    dbc.Col(
                                        dbc.Row(
                                            [
                                                dbc.Col(dbc.Input(id='moving_avg', value="3", bs_size="sm", type='number', inputMode='numeric', min=2, step=1, max=14), width=5),
                                                dbc.Col(html.Div("-day moving average", style={'fontSize': 11}), width=7)
                                            ]
                                        )
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )


# Chained Callback for Interactive Inputs (1 of 2)
# When a state is selected, enable the "country" button and fill the county dropdown menu
@app.callback(
    [Output(component_id='country_toggle', component_property='children'),
     Output(component_id='country_toggle', component_property='outline'),
     Output(component_id='country_toggle', component_property='disabled'),
     Output(component_id='county_dd', component_property='options'),
     Output(component_id='county_dd', component_property='value')],
    [Input(component_id='state_dd', component_property='value')]
)
def interactive_inputs(st):
    # If the user has not picked a state, the graph is showing the entire country
    if st not in list(us_state_abbrev.keys()):
        return 'Showing Entire Country', False, True, [{'label': 'Select a county', 'value': 'unused', 'disabled': True}], 'unused'
    # Once the user picks a state, enable the country button & fill in the county dropdown
    else:
        # Find appropriate list of counties based on chosen state
        cty_dd_list = [{'label': 'Select a county', 'value': 'unused', 'disabled': True}]
        for result in CtyCases[CtyCases['Province_State'] == st]['Admin2']:
            cty_dd_list.append({'label': result, 'value': result})
        return 'Show Entire Country', True, False, cty_dd_list, 'unused'


# Chained Callback for Interactive Inputs (2 of 2)
# When  the "country" button is clicked, reset the state and county selections
@app.callback(
     Output(component_id='state_dd', component_property='value'),
    [Input(component_id='country_toggle', component_property='n_clicks')]
)
def reset_inputs(st):
    return 'unused'


# Update US map based off radio button (tests / cases / hospitalizations / deaths)
@app.callback(
    Output(component_id='usmap', component_property='figure'),
    [Input(component_id='variable-picker', component_property='value')]
)
def update_map_variable(radio_selection):
    # Determine variable to be color-coded
    if radio_selection == 'People Tested':
        variable = 'Tested'
    elif radio_selection == 'Confirmed Cases':
        variable = 'Confirmed'
    else:
        variable = radio_selection

    # Update map with new data variable
    usmap.update_traces(
        z=Overview[variable].astype(float),
        colorbar=dict(title=radio_selection,),
        selector=dict(type="choropleth"))

    return usmap


# Update scatter plot based off of multiple input fields
@app.callback(
    Output(component_id='line_graph', component_property='figure'),
    [
        Input(component_id='state_dd', component_property='value'),
        Input(component_id='county_dd', component_property='value'),
        Input(component_id='moving_avg', component_property='value')
    ]
)
def update_scatter_plot(state, county, mavgpd):
    # Bring in data
    CountyCases = CtyCases
    CountyDeaths = CtyDeaths

    # Aggregate data at the correct level
    if state == 'unused':
        # Aggregate by country
        group_columns = ['Country_Region']
        # Variable to graph will be "US"
        region = 'US'
    elif county == 'unused':
        # Aggregate by state
        group_columns = ['Province_State']
        # Variable to graph will be the selected state
        region = state
    else:
        # Filter by state
        CountyCases = CountyCases[CountyCases['Province_State'] == state]
        CountyDeaths = CountyDeaths[CountyDeaths['Province_State'] == state]
        # Aggregate by county
        group_columns = ['Admin2']
        # Variable to graph will be the selected county
        region = county

    # Aggregate at necessary level, creating time series data for graph
    DailyNewCases = CountyCases.groupby(group_columns).sum().transpose().diff()
    DailyNewDeaths = CountyDeaths.groupby(group_columns).sum().transpose().diff()

    CountyCases.to_csv("CountyCases for graph.csv")
    CountyDeaths.to_csv("CountyDeaths for graph.csv")
    DailyNewCases.to_csv("DailyNewCases for graph.csv")
    DailyNewDeaths.to_csv("DailyNewDeaths for graph.csv")

    # Some general graph variables
    cases_color = 'yellow'
    deaths_color = 'red'

    # Set up figure
    help(go.Scatter)
    scatter = go.Figure()
    scatter.layout.template = 'plotly_dark'
    scatter.update_xaxes(rangeslider_visible=True)

    # Add newly confirmed cases to graph
    scatter.add_trace(
        go.Scatter(
            x=list(DailyNewCases.index.values),
            y=DailyNewCases[region],
            name='Newly Confirmed Cases',
            line=dict(color=cases_color)
        )
    )

    # Add moving average of newly confirmed cases to graph
    scatter.add_trace(
        go.Scatter(
            x=list(DailyNewCases.index.values),
            y=DailyNewCases[region].rolling(int(mavgpd)).mean(),
            name='Moving Avg - Newly Confirmed Cases',
            line=dict(color=cases_color, dash='dash')
        )
    )

    # Add deaths to graph
    scatter.add_trace(
        go.Scatter(
            x=list(DailyNewDeaths.index.values),
            y=DailyNewDeaths[region],
            name='Deaths',
            line=dict(color=deaths_color)
        )
    )

    # Add moving average of deaths to graph
    scatter.add_trace(
        go.Scatter(
            x=list(DailyNewDeaths.index.values),
            y=DailyNewDeaths[region].rolling(int(mavgpd)).mean(),
            name='Moving Avg - Deaths',
            line=dict(color=deaths_color, dash='dash')
        )
    )

    return scatter


# Gotta make it run
if __name__ == '__main__':
    app.run_server(debug=False)