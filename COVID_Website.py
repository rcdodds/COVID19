# Libraries
import datetime
# Pandas for data manipulation
import pandas as pd
# Plotly for making visuals
import plotly.graph_objs as go
# Dash for generating HTML
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
# Dash dependencies for interactivity
from dash.dependencies import Input, Output, State

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
    'Northern Mariana Islands': 'MP',
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

# Pull cases & deaths by county
CasesFileName = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
DeathsFileName = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv'
CtyCases = pd.read_csv(CasesFileName)
CtyDeaths = pd.read_csv(DeathsFileName)

# Remove anything that isn't a state/district/territory (e.g. cruise ships, prisons, etc)
CtyCases = CtyCases[CtyCases['Province_State'].isin(us_state_abbrev.keys())]
CtyDeaths = CtyDeaths[CtyDeaths['Province_State'].isin(us_state_abbrev.keys())]

# Extract population
CtyPops = CtyDeaths[['Admin2', 'Province_State', 'Country_Region', 'Population']]

# Trim unnecessary columns
drop_cols = ['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'Lat', 'Long_', 'Combined_Key', '1/22/20', '1/23/20', '1/24/20', '1/25/20', '1/26/20', '1/27/20', '1/28/20', '1/29/20', '1/30/20', '1/31/20', '2/1/20', '2/2/20', '2/3/20', '2/4/20', '2/5/20', '2/6/20', '2/7/20', '2/8/20', '2/9/20', '2/10/20', '2/11/20', '2/12/20', '2/13/20', '2/14/20', '2/15/20', '2/16/20', '2/17/20', '2/18/20', '2/19/20', '2/20/20', '2/21/20', '2/22/20', '2/23/20', '2/24/20', '2/25/20', '2/26/20', '2/27/20', '2/28/20']
CtyCases = CtyCases.drop(columns=drop_cols)
drop_cols.append('Population')
CtyDeaths = CtyDeaths.drop(columns=drop_cols)

# Apply index -- Index = Country, State, County -- Columns = dates
CtyCases.set_index(['Country_Region', 'Province_State', 'Admin2'], inplace=True)
CtyDeaths.set_index(['Country_Region', 'Province_State', 'Admin2'], inplace=True)
CtyPops.set_index(['Country_Region', 'Province_State', 'Admin2'], inplace=True)
CtyCases = CtyCases.rename_axis(index=['Country', 'State', 'County'])
CtyDeaths = CtyDeaths.rename_axis(index=['Country', 'State', 'County'])
CtyPops = CtyPops.rename_axis(index=['Country', 'State', 'County'])

# Get populations by state and reformat
StPops = CtyPops.groupby(level='State').sum().transpose()

# Get dictionary of dates in dataset for date slider
DateList = list(CtyCases.columns.values)
DateMarks = dict(list(enumerate(CtyCases.columns.values)))
num_dates = len(DateMarks)
for i in range(num_dates):
    if i % 7 != 0:
        del DateMarks[num_dates - 1 - i]                                    # Only keep marks on a weekly basis
    else:
        DateMarks[num_dates - 1 - i] = DateMarks[num_dates - 1 - i][:-3]    # Remove year to save space

# US map frame
usmap = go.Figure()
usmap.layout.template = 'plotly_dark'
usmap.add_trace(go.Choropleth())
usmap.update_layout(
    geo=dict(
        scope='usa',
        projection=go.layout.geo.Projection(type='albers usa'),
        showlakes=False
    )
)

# Map & graph
app.layout = \
    html.Div(
        [
            # Title section
            dbc.NavbarSimple(children=[dbc.Button('Show Tutorial', id='show_tutorial')
                                       ], brand='United States vs COVID-19', color='dark', dark=True, id='navbar'),
            # Everything
            dbc.Row(
                [
                    # USA choropleth map with radio buttons
                    dbc.Col(
                        [
                            # USA choropleth map
                            dcc.Graph(figure=usmap, id='usmap'),
                            # Choose date and variable
                            dbc.Card(
                                [
                                    # Slider to choose date
                                    dbc.CardHeader('Date Selection'),
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col([dbc.Button('Play', id='play_button', disabled=False)], width={'size': 1}),
                                                    dbc.Col(
                                                        [
                                                            dcc.Slider(
                                                                id='date_slider',
                                                                min=1,
                                                                max=num_dates - 1,
                                                                value=num_dates - 1,
                                                                marks=DateMarks
                                                            )
                                                        ], width={'size': 10}
                                                    ),
                                                    dcc.Interval(
                                                        id='interval',
                                                        interval=0.5*1000,     # sec * 1000 = milliseconds
                                                        n_intervals=0,
                                                        max_intervals=0        # Disabled until enabled by play button
                                                    )
                                                ]
                                            )
                                        ]
                                    ),
                                    # Radio buttons to select variable & switches to apply variable modifiers
                                    dbc.CardHeader("Variable Selection"),
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        # Radio buttons to choose variable
                                                        dbc.RadioItems(
                                                            id='variable-picker',
                                                            options=[
                                                                {'label': 'Cases', 'value': 'Cases'},
                                                                {'label': 'Deaths', 'value': 'Deaths'}
                                                            ],
                                                            value='Cases',
                                                            inline=True
                                                        )
                                                    ),
                                                    dbc.Col(
                                                        # Switches to toggle variable modifiers
                                                        dbc.Checklist(
                                                            options=[
                                                                {'label': 'Per Capita', 'value': 'percap'},
                                                                {'label': 'Totals', 'value': 'totals'},
                                                            ],
                                                            value=['', ''],
                                                            id='modifiers',
                                                            inline=True,
                                                            switch=True,
                                                        )
                                                    )
                                                ], form=True
                                            )
                                        ]
                                    )
                                ], id='map_vars'
                            )
                        ], width={'size': 5}  # Map graph gets 5/12 of website
                    ),
                    # Line graph of recent data for subset of country
                    dbc.Col(
                        [
                            # Line graph
                            dcc.Graph(id='line_graph'),
                            # Multiple inputs to change region being considered
                            dbc.Card(
                                [
                                    dbc.CardHeader('Region Selection'),
                                    # Select region
                                    dbc.Row(
                                        [
                                            # Aggregate level drop-down selection
                                            dbc.Col(dbc.Button(id='country_toggle', color='info', block=True)),
                                            # State drop-down selection
                                            dbc.Col(dbc.Select(id='state_dd', options=[
                                                {'label': 'Select a state', 'value': 'unused'}], value='unused')),
                                            # County drop-down selection
                                            dbc.Col(dbc.Select(id='county_dd', options=[
                                                {'label': 'Select a county', 'value': 'unused'}], value='unused')),
                                        ], form=True
                                    ),
                                    # Determine how drop down menus are sorted
                                    dbc.Row(
                                        [
                                            dbc.Col(dbc.RadioItems(
                                                id='dd-sort',
                                                options=[
                                                    {'label': 'Sort state & county drop-downs alphabetically', 'value': 'abc'},
                                                    {'label': 'Sort state & county drop-downs by number of cases', 'value': 'cases'}
                                                ], value='abc'), width={'offset': 4}
                                            ),
                                        ], form=True
                                    ),
                                    # Box for adjusting the moving average period
                                    dbc.CardHeader('Moving Average Period Selection'),
                                    dbc.Row(
                                        dbc.Col(
                                            dbc.Input(id='moving_avg', value='7', bs_size='lg', type='number',
                                                      inputMode='numeric', min=2, step=1, max=14),
                                            width={'size': 2, 'offset': 1}
                                        )
                                    )
                                ], id='region_sel'
                            )
                        ], width={'size': 7}  # Line graph gets 7/12 of website
                    )
                ], no_gutters=False  # Squish the map & graph together
            ),
            # Tutorial elements as popovers - can be toggled by button in navbar
            dbc.Popover(
                [
                    dbc.PopoverHeader("Change the Graph Region"),
                    dbc.PopoverBody("Use the drop down menus to specify a region."),
                    dbc.PopoverBody("Clicking the button on the left will graph the whole country."),
                    dbc.PopoverBody("The radio buttons can change how the drop down menus are sorted"),
                ],
                id='region_sel_popover', target='region_sel', placement='top', is_open=False
            ),
            dbc.Popover(
                [
                    dbc.PopoverHeader("Change the Moving Average Lines (Dashed Lines)"),
                    dbc.PopoverBody("This controls how many recent days are used to calculate the moving average lines (dashed lines)."),
                    dbc.PopoverBody("For instance, the 7-day moving average on 5/1 shows the average of all days from 4/25 to 5/1."),
                ],
                id='moving_avg_popover', target='moving_avg', placement='right', is_open=False
            ),
            dbc.Popover(
                [
                    dbc.PopoverHeader("Change the Map Date"),
                    dbc.PopoverBody("When the 'Totals' switch is on, the graph shows all data up to the chosen date."),
                    dbc.PopoverBody("When the 'Totals' switch is off, the graph shows the data from this specific date."),
                ],
                id='date_slider_popover', target='map_vars', placement='top', is_open=False
            ),
            dbc.Popover(
                [
                    dbc.PopoverHeader("Change the Map Variable"),
                    dbc.PopoverBody("The radio buttons control whether the map is showing the number of cases or deaths."),
                    dbc.PopoverBody("The 'Per Capita' switch can be used to more accurately compare states of different populations."),
                    dbc.PopoverBody("The 'Totals' switch can be used to show either the total amount of cases/deaths up to the chosen date."),
                ],
                id='modifiers_popover', target='modifiers', placement='left', is_open=False
            )
        ]
    )


# Update US map based off chosen variables & modifiers
@app.callback(
    [Output(component_id='usmap', component_property='figure'),
     Output(component_id='date_slider', component_property='included')],
    [Input(component_id='date_slider', component_property='value'),
     Input(component_id='variable-picker', component_property='value'),
     Input(component_id='modifiers', component_property='value')]
)
def update_map(date, radio_selection, modifiers):
    # Change slider number to the date
    date = DateList[date]

    # Summarize data at state level
    MapCases = CtyCases.groupby(level='State').sum().transpose()
    MapDeaths = CtyDeaths.groupby(level='State').sum().transpose()

    # Determine variable to be color-coded
    if radio_selection == 'Cases':
        MapData = MapCases
    else:
        MapData = MapDeaths

    # Determine if map should show New Daily data or Total data
    if 'totals' in modifiers:
        title_prefix = 'Total '
        title_suffix = ' by ' + str(date)
        included = True
    else:
        title_prefix = 'New '
        title_suffix = ' on ' + str(date)
        included = False
        # Transform data from totals to new
        MapData = MapData.diff()

    # Determine if map is showing data per capita or not
    if 'percap' in modifiers:
        title_suffix = ' per 100,000 Capita' + title_suffix
        MapData = MapData.div(StPops.loc['Population']).mul(100000)

    # Add qualifiers to map title
    map_title = title_prefix + radio_selection + title_suffix

    # Update map with new data variable
    usmap.update_traces(
        locations=list(map(lambda x: us_state_abbrev[x], list(MapData.columns.values))),
        locationmode='USA-states',  # set of locations match entries in `locations`
        z=MapData.loc[date],
        zmin=0,
        zmax=max(MapData.loc[date]),
        colorscale=[[0, 'white'], [1, 'red']],
        colorbar=dict(
            thickness=15,
            len=1.5,
            xanchor='left',
            x=-0.1,
            ticks='inside'),
        selector=dict(type='choropleth')
    )
    usmap.update_layout(
        title={
            'text': map_title,
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
        }
    )

    return usmap, included


# Update scatter plot based off of chosen region & moving average period
@app.callback(
    Output(component_id='line_graph', component_property='figure'),
    [
        Input(component_id='state_dd', component_property='value'),
        Input(component_id='county_dd', component_property='value'),
        Input(component_id='moving_avg', component_property='value')
    ],
    # State(component_id='line_graph', component_property='layout')
)
def update_scatter_plot(state, county, mavgpd):
    # Aggregate data at the correct level
    if state == 'unused':
        # Set title
        graph_title = 'United States'
        # Set region (for filtering later)
        region = 'US'
        # Generate time series of cases & deaths for the United States of America
        TotalCases = CtyCases.groupby(level='Country').sum()
        TotalDeaths = CtyDeaths.groupby(level='Country').sum()
    elif county == 'unused':
        # Set title
        graph_title = state
        # Set region (for filtering later)
        region = state
        # Generate time series of cases & deaths for the selected state
        TotalCases = CtyCases.groupby(level='State').sum().sort_values(str(list(CtyCases.columns.values)[-1]), ascending=False)
        TotalDeaths = CtyDeaths.groupby(level='State').sum().sort_values(str(list(CtyCases.columns.values)[-1]), ascending=False)
    else:
        # Set title
        graph_title = county + ' County, ' + state
        # Set region (for filtering later)
        region = county
        # Generate time series of cases & deaths for the selected state and county
        TotalCases = CtyCases.xs(state, level='State').groupby(level='County').sum().sort_values(str(list(CtyCases.columns.values)[-1]), ascending=False)
        TotalDeaths = CtyDeaths.xs(state, level='State').groupby(level='County').sum().sort_values(str(list(CtyCases.columns.values)[-1]), ascending=False)

    # Turn total data into daily new data
    NewCases = TotalCases.transpose().diff()
    NewDeaths = TotalDeaths.transpose().diff()

    # Graph configuration
    cases_color = 'yellow'
    deaths_color = 'red'

    # Set up figure
    scatter = go.Figure()
    scatter.layout.template = 'plotly_dark'
    scatter.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=14,
                         label="14 Days",
                         step="day",
                         stepmode="backward"),
                    dict(count=1,
                         label="1 Month",
                         step="month",
                         stepmode="backward"),
                    dict(label="All",
                         step="all")
                ]),
                x=0.5,
                xanchor='center',
                bgcolor='#121212',  # Background when not clicked - dark black
                activecolor='#272623',  # Background when clicked - gray
                bordercolor='#ffffff',  # Border color - white
                font=dict(color='#ffffff')  # Font color - white
            ),
            rangeslider=dict(
                visible=True
            ),
            type='date'
        ),
        title={
            'text': graph_title,
            'x': 0.5,
            'xanchor': 'center'
        },
        legend=dict(
            orientation='h',
            x=0.5,
            xanchor='center',
            y=-0.6,
            yanchor='top')
    )

    # Add newly confirmed cases to graph
    scatter.add_trace(
        go.Scatter(
            x=[datetime.datetime.strptime(x, '%m/%d/%y') for x in CtyCases.columns.values],
            y=NewCases[region],
            name='Newly Confirmed Cases',
            line=dict(color=cases_color)
        )
    )

    # Add moving average of newly confirmed cases to graph
    scatter.add_trace(
        go.Scatter(
            x=[datetime.datetime.strptime(x, '%m/%d/%y') for x in CtyCases.columns.values],
            y=NewCases[region].rolling(int(mavgpd)).mean(),
            name='Moving Avg of Confirmed Cases',
            line=dict(color=cases_color, dash='dash')
        )
    )

    # Add deaths to graph
    scatter.add_trace(
        go.Scatter(
            x=[datetime.datetime.strptime(x, '%m/%d/%y') for x in CtyDeaths.columns.values],
            y=NewDeaths[region],
            name='Deaths',
            line=dict(color=deaths_color)
        )
    )

    # Add moving average of deaths to graph
    scatter.add_trace(
        go.Scatter(
            x=[datetime.datetime.strptime(x, '%m/%d/%y') for x in CtyDeaths.columns.values],
            y=NewDeaths[region].rolling(int(mavgpd)).mean(),
            name='Moving Avg of Deaths',
            line=dict(color=deaths_color, dash='dash')
        )
    )

    return scatter


# Chained Callback for Animated Date Slider (1 of 2)
# When  the 'play' button is clicked, enable the interval
@app.callback(
    [Output(component_id='interval', component_property='n_intervals'),
     Output(component_id='interval', component_property='max_intervals')],
    [Input(component_id='play_button', component_property='n_clicks')]
)
def play_button(play_clicks):
    if play_clicks:                         # Ensure nothing happens when page loads (when play_clicks==0)
        # if play_clicks % 2 == 1:            # Use mod 2 to toggle between play/stop
        return 0, num_dates-1           # Set max_ints to allow interval to run
    return 0, 0                         # Don't do anything when this callback fires on page load (when play_clicks==0)


# Chained Callback for Animated Date Slider (2 of 2)
# Once the interval has been enabled, use the interval to adjust the date slider
@app.callback(
    [Output(component_id='date_slider', component_property='value'),
     Output(component_id='play_button', component_property='children')],
    [Input(component_id='interval', component_property='n_intervals')])
def animate_map(n_intervals):
    if n_intervals == 0:             # Interval has not started
        return num_dates-1, 'Play'
    elif n_intervals == num_dates-1:    # Interval has ended
        return num_dates-1, 'Play'
    else:                               # Interval is running
        return (n_intervals % (num_dates-1)) + 1, 'Stop'


# Chained Callback for Interactive Region Inputs (1 of 2)
# When a state is selected, enable the 'country' button and fill the county dropdown menu
@app.callback(
    [Output(component_id='country_toggle', component_property='children'),
     Output(component_id='country_toggle', component_property='outline'),
     Output(component_id='country_toggle', component_property='disabled'),
     Output(component_id='state_dd', component_property='options'),
     Output(component_id='county_dd', component_property='options'),
     Output(component_id='county_dd', component_property='value')],
    [Input(component_id='state_dd', component_property='value'),
     Input(component_id='dd-sort', component_property='value')]
)
def interactive_inputs(st, sort):
    # Populate the state drop down menu
    if sort == 'cases':
        # Pull lists of states by decreasing amount of total COVID cases
        StateList = list(CtyCases.groupby(level='State').sum().sort_values(
            str(list(CtyCases.columns.values)[-1]), ascending=False).index.values)
    else:
        # Pull lists of states by decreasing amount of total COVID cases
        StateList = list(CtyCases.groupby(level='State').sum().index.values)

    # Build state drop down menu
    state_dd_list = [{'label': 'Select a state', 'value': 'unused'}]
    for state_name in StateList:
        state_dd_list.append({'label': state_name, 'value': state_name})

    # If the user has picked a state, enable the country button & fill in the county selection options
    if st in list(us_state_abbrev.keys()):
        cty_dd_list = [{'label': 'Select a county', 'value': 'unused'}]
        if sort == 'cases':
            # Add counties by decreasing amount of total COVID cases
            for cty in list(CtyCases.xs(st, level='State').groupby(level='County').sum().sort_values(
                    str(list(CtyCases.columns.values)[-1]), ascending=False).index.values):
                cty_dd_list.append({'label': cty, 'value': cty})
        else:
            # Add counties alphabetically
            for cty in list(CtyCases.xs(st, level='State').groupby(level='County').sum().index.values):
                cty_dd_list.append({'label': cty, 'value': cty})
        return 'Show United States of America', True, False, state_dd_list, cty_dd_list, 'unused'

    # If the state was reset to unused, the graph is showing the United States of America
    else:
        return 'Showing United States of America', False, True, state_dd_list, [
            {'label': 'Select a county', 'value': 'unused'}], 'unused'


# Chained Callback for Interactive Region Inputs (2 of 2)
# When  the 'country' button is clicked, return state selection to none. This triggers the chained callback below
@app.callback(
    Output(component_id='state_dd', component_property='value'),
    [Input(component_id='country_toggle', component_property='n_clicks')]
)
def reset_state(st):
    return 'unused'


# When "Show Tutorial" button is clicked, toggle the instruction popovers
@app.callback(
    [Output(component_id='date_slider_popover', component_property='is_open'),
     Output(component_id='modifiers_popover', component_property='is_open'),
     Output(component_id='region_sel_popover', component_property='is_open'),
     Output(component_id='moving_avg_popover', component_property='is_open')
     ],
    [Input(component_id='show_tutorial', component_property='n_clicks')],
    [State(component_id='region_sel_popover', component_property='is_open')]
)
def toggle_popover(n, is_open):
    if n:
        return [not is_open] * 4
    return [is_open] * 4


# Gotta make it run
if __name__ == '__main__':
    app.run_server(debug=False)