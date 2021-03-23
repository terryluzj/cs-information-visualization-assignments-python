import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import datetime
import flask
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output


def parse_date(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d")


def cast_date_type(df):
    df["date"] = df["date"].apply(lambda x: parse_date(x))
    return df


def convert_year_month(df):
    df["date"] = df["Year"].astype(str).str.cat(df["Month"].astype(str), sep="-")
    df["date"] = df["date"].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m"))
    return df


server = flask.Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])

"""
Questions
"""


def plot_questions_chart(df):
    fig = go.Figure([
        go.Bar(x=df["date"], y=df["Number_of_Questions"], name="Total Number of Questions"),
        go.Bar(x=df["date"], y=df["Number_of_Questions_Answered"],
               name="Number of Questions Answered")
    ])
    fig.update_layout(title_text="Questions Trend")
    fig.update_layout(barmode="overlay")
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))
    return fig


questions_df = pd.read_csv("data/questions.csv")
questions_df = convert_year_month(questions_df)
questions_df["Number_of_Questions_Answered"] = questions_df["Number_of_Questions"] * (
    questions_df["Percent_Questions_with_Answers"] / 100)
fig1 = plot_questions_chart(questions_df)

"""
Answers
"""


def plot_answers_chart(df):
    fig = go.Figure([
        go.Bar(x=df["date"], y=df["Number_of_Answers"], name="Total Number of Answers"),
        go.Bar(x=df["date"], y=df["Number_of_Answers_with_Scores"],
               name="Number of Answers with Scores")
    ])
    fig.update_layout(title_text="Answers Trend")
    fig.update_layout(barmode="overlay")
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))
    return fig


answers_df = pd.read_csv("data/answers.csv")
answers_df = convert_year_month(answers_df)
answers_df["Number_of_Answers_with_Scores"] = answers_df["Number_of_Answers"] * (
    answers_df["Percent_Answers_with_Scores"] / 100)
fig2 = plot_answers_chart(answers_df)

"""
Tags
"""


def plot_tags_chart(df):
    df = df.sort_values("Tag_Count", ascending=False).head(50)
    fig = go.Figure(
        go.Bar(
            y=df["Tag_Used"],
            x=df["Tag_Count"],
            orientation="h",
        )
    )
    fig.update_layout(title_text="Tag Count")
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return fig


tags_df = pd.read_csv("data/tags_cumulative.csv")
tags_df = convert_year_month(tags_df)
tags_df_max_date = tags_df[tags_df["date"] == tags_df["date"].max()]
fig3 = plot_tags_chart(tags_df_max_date)

"""
Interactive components
"""
min_date = tags_df["date"].min()
max_date = tags_df["date"].max()
min_date_ts = min_date.timestamp()
max_data_ts = max_date.timestamp()
slider = dcc.RangeSlider(
    id="date-slider",
    min=min_date_ts,
    max=max_data_ts,
    value=[min_date_ts, max_data_ts],
    allowCross=False,
    marks={int(datetime.datetime(year, 1, 1).timestamp()): str(year) for year in
           range(min_date.year, max_date.year + 1)},
)


@app.callback(
    [Output("time-series-chart-1", "figure"), Output("time-series-chart-2", "figure"), Output("chart-1", "figure")],
    Input("date-slider", "value"))
def update_output(value):
    min_ts, max_ts = value
    filtered_questions_df = questions_df[(questions_df.date >= datetime.datetime.fromtimestamp(min_ts)) & (
        questions_df.date <= datetime.datetime.fromtimestamp(max_ts))]
    filtered_answers_df = answers_df[(answers_df.date >= datetime.datetime.fromtimestamp(min_ts)) & (
        answers_df.date <= datetime.datetime.fromtimestamp(max_ts))]
    filtered_tags_df = tags_df[(tags_df.date >= datetime.datetime.fromtimestamp(min_ts)) & (
        tags_df.date <= datetime.datetime.fromtimestamp(max_ts))]
    filtered_tags_df = filtered_tags_df[filtered_tags_df["date"] == filtered_tags_df["date"].max()]
    fig_new_1 = plot_questions_chart(filtered_questions_df)
    fig_new_1.update_layout(transition_duration=500)
    fig_new_2 = plot_answers_chart(filtered_answers_df)
    fig_new_2.update_layout(transition_duration=500)
    fig_new_3 = plot_tags_chart(filtered_tags_df)
    return [fig_new_1, fig_new_2, fig_new_3]


stack_overflow_visualization = dbc.Container([
    html.H1("Stack Overflow Trend Visualization"),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="time-series-chart-1", figure=fig1),
            dcc.Graph(id="time-series-chart-2", figure=fig2)
        ], width=8),
        dbc.Col([
            dcc.Graph(id="chart-1", figure=fig3, style={"height": "100%"})
        ]),
    ]),
    slider
],
    fluid=True
)


@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/stack-overflow':
        return stack_overflow_visualization


if __name__ == "__main__":
    app.run_server(threaded=True)
