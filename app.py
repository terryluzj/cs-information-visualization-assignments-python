import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import flask

server = flask.Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])
