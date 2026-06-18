import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
# Note: If your file name varies slightly, adjust this string path locally
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create dynamic options for dropdown from the dataset
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
for site in spacex_df['Launch Site'].unique():
    dropdown_options.append({'label': site, 'value': site})

# Define the user interface application layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart container
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0, 
        max=10000, 
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 2500)},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Add a scatter chart container to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# ==============================================================================
# CALLBACK FUNCTIONS
# ==============================================================================

# TASK 2 Callback: Renders Pie Chart based on site-dropdown selection
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # If ALL sites selected, show total success count grouped by launch site
        fig = px.pie(
            spacex_df, 
            values='class', 
            names='Launch Site', 
            title='Total Success Launches By All Sites'
        )
        return fig
    else:
        # Filter for the selected launch site specifically
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count occurrences of class 1 (Success) vs class 0 (Failure)
        df_counts = filtered_df['class'].value_counts().reset_index()
        df_counts.columns = ['class', 'count']
        # Map values to readable string labels for names rendering
        df_counts['Outcome'] = df_counts['class'].map({1: 'Success', 0: 'Failure'})
        
        fig = px.pie(
            df_counts, 
            values='count', 
            names='Outcome', 
            title=f'Total Success vs. Failure Launches for site: {entered_site}',
            color='Outcome',
            color_discrete_map={'Success': '#2ca02c', 'Failure': '#d62728'} # Green/Red accents
        )
        return fig


# TASK 4 Callback: Renders Scatter Plot based on site-dropdown AND payload-slider inputs
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    # First, mask out records falling outside the range slider boundary values
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
    
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df, 
            x='Payload Mass (kg)', 
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites',
            labels={'class': 'Launch Outcome (0=Failure, 1=Success)'}
        )
        return fig
    else:
        # Filter specifically down to rows matching the active dropdown string name
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_filtered_df, 
            x='Payload Mass (kg)', 
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for site {entered_site}',
            labels={'class': 'Launch Outcome (0=Failure, 1=Success)'}
        )
        return fig


# Run the application
if __name__ == '__main__':
    app.run(debug=True)