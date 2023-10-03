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


# Creating the Dash application
app = dash.Dash(__name__, suppress_callback_exceptions=True,assets_folder = 'assets')

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
		return '/page-2?country={}'.format(value) # Passing the country value as a parameter to the URL
	else:
		return '#'


# Defining the layout and contents of the second page (Graph page)
page_2_layout = html.Div([
	html.Div([
		dcc.Graph(id ='my-graph'), # Render graph

		dcc.Location(id="user-url")
	])
])


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


	s = 10
	df = pd.DataFrame({"Country": np.random.choice(["USA America", "JPY one two", "MEX", "IND", "AUS"], s),   
				 "employee": np.random.choice(["Bob", "Sam", "John", "Tom", "Harry"], s),
				 "economy_cat": np.random.choice(["developing","develop"], s),
			  "Net": np.random.randint(5, 75, s),
		})

	# Filtering for the selected country
	df = df[(df.Country==value_country)]
	#dataframe for first chart
	df2 = df.pivot_table(index='Country',columns='economy_cat',values='Net',aggfunc='sum')
	df2.reset_index(inplace=True)
	
	df9 = df[(df.Country==value_country) & (df.employee == 'John')]
	#dataframe for second chart
	df3 = df9.query('economy_cat == "develop"')
	df3 = df9.pivot_table(index='employee',values='Net',aggfunc='sum')
	df3.reset_index(inplace=True)
	
	# first chart
	fig = make_subplots(rows=1, cols = 2)
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
	
	# second chart
	if (len(df3) <= 0):
		print('fsafas')
		fig.add_trace(
			go.Figure().add_annotation(x=2, y=2,text="No Data to Display",font=dict(family="sans serif",size=25,color="crimson"),showarrow=False,yshift=10),
			row = 1,
			col = 2,
		)
		fig.update_layout(clickmode='event+select')

	else:
		fig.add_trace(
			go.Bar(
				x = df3['Net'],
				y = df3['employee'], orientation = 'h', marker_color = 'blue',
			),
			row = 1,
			col = 2,
		)
		fig.update_layout(clickmode='event+select')	

	return fig

# Callback to redirect on the next page with the filtered plot for specific user
@app.callback(
	Output('user-url', 'href'),
	[Input('my-graph', 'clickData'), Input('url', 'search')])

def display_click_data(clickData, country):
	country = country[9:].replace('%20', ' ')
	return 'http://127.0.0.1:8050/page-3?user={}&country={}'.format(json.dumps(clickData['points'][0]['label'], indent=2), country)

# Defining the layout for third page (User-specific plots)
page_3_layout = html.Div([
	html.Div([
		dcc.Graph(id ='user-graph') # Render graph
	])
])

# Callback for filtering the plot based on the Country and User
@app.callback(
	Output(component_id = 'user-graph', component_property = 'figure'),
	Input('url','search'))
def page_3_graph(value_country):
	'''
		This function gets the selected country and clicked User, filters the dataframe for the values and displays the plot

		arguments: URL parameter consisting of the selected country
		return: plot for the filtered country and user
	'''

	# The URL parameter is of the format - ?user=ABC&country=ABC
	parameters = value_country.partition('&') #Extract parameters from the URL
	user = parameters[0] #Extract the user parameter
	user = user[9:].replace('%22', '')
	print(user)

	country = parameters[2] #Extract country parameter
	country = country[8:].replace('%20', ' ') # Get only the country part from the parameter and replacing special character with space
	print(country)
	s = 100
	cat_g = ["developing","develop"]
	sample_cat = [cat_g[np.random.randint(0,2)]for i in range(100)]
	s = 100
	df = pd.DataFrame({"Country": np.random.choice(["USA America", "JPY one two", "MEX", "IND", "AUS"], s),   
				 "employee": np.random.choice(["Bob", "Sam", "John", "Tom", "Harry"], s),
				 "economy_cat": np.random.choice(["developing","develop"], s),
			  "Net": np.random.randint(5, 75, s),
		})

	# Filtering for the selected employee and country
	df = df[(df.employee == user) & (df.Country==country)]
	df2 = df.pivot_table(index='Country',columns='economy_cat',values='Net',aggfunc='sum')
	df2.reset_index(inplace=True)
	# Create a bar graph
	fig = px.bar(df2, x="Country",
		  y=['develop','developing'])

	return fig

# Update the main page
@app.callback(dash.dependencies.Output('page-content', 'children'),
			  [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
	if pathname == '/page-2':
		return page_2_layout
	elif pathname == '/page-3':
		return page_3_layout
	else:
		return index_page

# Running the application
if __name__ == '__main__':
		app.run_server(debug=True, dev_tools_ui=False)