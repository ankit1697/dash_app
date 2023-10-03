# Importing required libraries
import json
import pandas as pd # to create dataframe
import plotly.express as px
import dash # core dash library
import dash_core_components as dcc # to render various HTML components like dropdowns, etc.
import dash_html_components as html # to render HTML components like headings, divs, etc.
from dash.dependencies import Output, Input, State # for interacting with dropdowns
import numpy as np
import plotly.io as pio # plotting library
from dash.exceptions import PreventUpdate
pio.renderers.default='browser'
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import re
import dash_bootstrap_components as dbc


# Creating the Dash application
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Creating the dataframe
s = 100
df = pd.DataFrame({"Country": np.random.choice(["USA America", "JPY one two", "MEX", "IND", "AUS"], s),   
				 "employee": np.random.choice(["Bob", "Sam", "John", "Tom", "Harry"], s),
				 "economy_cat": np.random.choice(["developing","develop"], s),
			  "Net": np.random.randint(5, 75, s),
		})


# Creating the application layout, with the URLs for different pages
app.layout = html.Div([
	dcc.Location(id='url', refresh=False),
	html.Div(id='page-content')
])

# Defining the layout and contents of the first page (Dropdown page)
index_page = html.Div([
	html.H1('Customer Margin Analysis', style={'textAlign': 'center', 'marginTop':'10%'}), # heading for the page 
	dcc.Dropdown(id='Country_select', 
		placeholder='Select country..',
		options=[{'label': x, 'value': x}
		for x in np.sort(df.Country.unique())]
	), # dropdown with Country values from the dataframe
	html.Br(), # HTML break tag for line break
	dcc.Link(html.Button('Search', id='btn'), id="link", href='#', target=""), # Link button to redirect to next page
]),

# This part checks if the input is empty. If it is empty, it does not redirect to the next page
@app.callback(dash.dependencies.Output('link', 'target'),
			  [dash.dependencies.Input('Country_select', 'value')])
def page_1_dropdown(value):
	if len(value)>0: # Check if input not empty
		return '_blank'
	else:
		return ''

# This part updates the target URL of the link with the selected country value
@app.callback(dash.dependencies.Output('link', 'href'),
			  [dash.dependencies.Input('Country_select', 'value')])
def page_1_dropdown(value):
	if len(value)>0:
		return '/summary?country={}'.format(value) # Passing the country value as a parameter to the URL
	else:
		return '#'


# Defining the layout and contents of the second page (Graph page)
summary_layout = html.Div([
	html.Nav(className = "nav nav-pills", children=[
		html.A('Summary', className="nav-item nav-link btn", href='#', style={"color":"white"}),
		html.A('IRS', className="nav-item nav-link active btn", id='irs_nav', href='#', style={"color":"white", "marginLeft":"2%", "textDecoration":"none"}),
		# dcc.Dropdown(id='select_country', placeholder='Select country..',options=[{'label': x, 'value': x}for x in np.sort(df.Country.unique())], style={"width":"50%", "float":"right"}),
], style={"backgroundColor":"black", "padding":"0.9%", "marginBottom":"2%"}),
	html.Div([
		dcc.Graph(id ='my-graph'), # Render graph

		# dcc.Location(id="summary-location")
	])
])

@app.callback(
	Output('irs_nav', 'href'),
	Input('url', 'search'))
def update_irs_href(value):
	value = value[9:].replace('%20', ' ')
	return '/irs?country={}'.format(value)


# @app.callback(
# 	Output('user-url', 'search'),
# 	Input('select_country','value'))
# def change_country(value):
# 	if value is None:
# 		PreventUpdate
# 	else:
# 		return '?country={}'.format(value)

# Callback for filtering based on the URL parameter passed from the First page
@app.callback(
	Output(component_id = 'my-graph', component_property = 'figure'),
	Input('url','search'))
def interactive_graphing(value_country):
	'''
		This function gets the selected country, filters the dataframe for the selected country and displays the plot

		arguments: URL parameter consisting of the selected country
		return: plot for the filtered country
	'''

	# The URL parameter is of the format - ?country=ABC
	value_country = value_country[9:].replace('%20', ' ') # Get only the country part from the parameter and replacing special character with space

	s = 100
	df_1 = pd.DataFrame({"Country": np.random.choice(["USA America", "JPY one two", "MEX", "IND", "AUS"], s),   
				 "employee": np.random.choice(["Bob", "Sam", "John", "Tom", "Harry"], s),
				 "economy_cat": np.random.choice(["developing","develop"], s),
			  "Net": np.random.randint(5, 75, s),
		})

	# Filtering for the selected country
	df8 = df_1[(df.Country==value_country)]
	#dataframe for first chart
	df2 = df8.pivot_table(index='Country',columns='economy_cat',values='Net',aggfunc='sum')
	df2.reset_index(inplace=True)
	
	df9 = df_1[(df.Country==value_country)]
	#dataframe for second chart
	df3 = df9.query('economy_cat == "develop"')
	df3 = df9.pivot_table(index='employee',values='Net',aggfunc='sum')
	df3.reset_index(inplace=True)
	# first chart

	fig = make_subplots(rows=2, cols = 3)
	fig.add_trace(
		go.Bar(
			x = df2['Country'],
			y = df2['develop'], marker_color = 'blue',
		),
		row = 1,
		col = 1,
	)
	fig.add_trace(
		go.Bar(
			x = df2['Country'],
			y = df2['developing'], marker_color = 'red',
		),
		row = 1,
		col = 1,
	)
	fig.add_trace(
		go.Bar(
			x = df3['Net'],
			y = df3['employee'], orientation = 'h', marker_color = 'blue',
		),
		row = 1,
		col = 2,
	)
	# second chart
	if(len(df3) > 0):
		fig.add_trace(
			go.Bar(
				x = df3['Net'],
				y = df3['employee'], orientation = 'h', marker_color = 'blue',
			),
			row = 1,
			col = 3,
		)
	fig.update_layout(clickmode='select')

	return fig


irs_layout = html.Div([
	html.Nav(className = "nav nav-pills", children=[
		html.A('Summary', id='summary_nav', className="nav-item nav-link btn", href='#', style={"color":"white", "textDecoration":"none"}),
		html.A('IRS', className="nav-item nav-link active btn", href='#', style={"color":"white", "marginLeft":"2%"}),
		# dcc.Dropdown(id='select_country', placeholder='Select country..',options=[{'label': x, 'value': x}for x in np.sort(df.Country.unique())], style={"width":"50%", "float":"right"}),
], style={"backgroundColor":"black", "padding":"0.9%", "marginBottom":"2%"}),
	html.Div([
		dcc.Graph(id ='irs-graph'), # Render graph
		
		dcc.Location(id="irs-location")
	])
])

@app.callback(
	Output('irs-location', 'search'),
	Input('irs-graph', 'clickData'))
def display_click_data(clickData):
	if clickData is None:
		PreventUpdate
	else:
		return 'country={}'.format(json.dumps(clickData['points'][0]['label']))

@app.callback(
	Output(component_id = 'irs-graph', component_property = 'figure'),
	Input('url','search'))
def graphing(value_country):
	'''
		This function gets the selected country, filters the dataframe for the selected country and displays the plot

		arguments: URL parameter consisting of the selected country
		return: plot for the filtered country
	'''

	# The URL parameter is of the format - ?country=ABC
	value_country = value_country[9:].replace('%20', ' ') # Get only the country part from the parameter and replacing special character with space

	s = 30
	df = pd.DataFrame({"Country": np.random.choice(["USA America", "JPY one two", "MEX", "IND", "AUS"], s),   
				 "employee": np.random.choice(["Bob", "Sam", "John", "Tom", "Harry"], s),
				 "economy_cat": np.random.choice(["developing","develop"], s),
			  "Net": np.random.randint(5, 75, s),
		})

	# Filtering for the selected country
	df8 = df[(df.Country==value_country)]
	#dataframe for first chart
	df2 = df8.pivot_table(index='Country',columns='economy_cat',values='Net',aggfunc='sum')
	df2.reset_index(inplace=True)
	
	df9 = df[(df.Country==value_country)]
	#dataframe for second chart
	df3 = df9.query('economy_cat == "develop"')
	df3 = df9.pivot_table(index='employee',values='Net',aggfunc='sum')
	df3.reset_index(inplace=True)
	# first chart

	irs_fig = make_subplots(rows=2, cols = 3)
	irs_fig.add_trace(
		go.Bar(
			x = df2['Country'],
			y = df2['develop'], marker_color = 'blue',
		),
		row = 1,
		col = 1,
	)
	irs_fig.add_trace(
		go.Bar(
			x = df2['Country'],
			y = df2['developing'], marker_color = 'red',
		),
		row = 1,
		col = 1,
	)
	irs_fig.add_trace(
		go.Bar(
			x = df3['Net'],
			y = df3['employee'], orientation = 'h', marker_color = 'blue',
		),
		row = 1,
		col = 2,
	)
	# second chart
	if(len(df3) > 0):
		irs_fig.add_trace(
			go.Bar(
				x = df3['Net'],
				y = df3['employee'], orientation = 'h', marker_color = 'blue',
			),
			row = 1,
			col = 3,
		)

	irs_fig.update_layout(clickmode='event+select')

	return irs_fig

@app.callback(
	Output('summary_nav', 'href'),
	Input('url', 'search'))
def update_summary_href(value):
	value = value[9:].replace('%20', ' ')
	return '/summary?country={}'.format(value)


# Update the main page
@app.callback(dash.dependencies.Output('page-content', 'children'),
			  [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
	if pathname == '/summary':
		return summary_layout
	elif pathname == '/irs':
		return irs_layout
	else:
		return index_page

# Running the application
if __name__ == '__main__':
		app.run_server(debug=True, dev_tools_ui=False)