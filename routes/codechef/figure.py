import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from config import DATA_DIR

"""
Questions
"""


def plot_questions_tag_chart(df):
    fig = go.Figure([
        go.Bar(x=df["SubmissionCount"], y=df["Tags"], orientation="h"),
    ])
    fig.update_layout(yaxis=dict(autorange="reversed"))
    fig.update_layout(xaxis=dict(title="Total Number of Submissions by Tags"))
    return fig


questions_df = pd.read_csv(DATA_DIR / "codechef/questions.csv", index_col=[0])

questions_df_with_count = questions_df.dropna(subset=["SubmissionCount"]).copy()
questions_df_with_count["Tags"] = questions_df_with_count["Tags"].apply(lambda tags: eval(tags))
tag_count_top_10 = questions_df_with_count \
                       .explode("Tags") \
                       .groupby("Tags")["SubmissionCount"] \
                       .sum().sort_values(ascending=False)[:10]
fig1 = plot_questions_tag_chart(pd.DataFrame(tag_count_top_10).reset_index())

"""
Solutions
"""


def plot_submissions_tag_chart(df):
    fig = go.Figure([
        go.Bar(x=df["UserID"], y=df["Language"], orientation="h"),
    ])
    fig.update_layout(yaxis=dict(autorange="reversed"))
    fig.update_layout(xaxis=dict(title="Total Number of Submissions by Languages"))
    return fig


solutions_df = pd.read_csv(DATA_DIR / "codechef/solutions.csv", index_col=[1])
language_count = solutions_df \
                     .reset_index()[["UserID", "Language"]] \
                     .drop_duplicates() \
                     .groupby("Language")["UserID"] \
                     .count() \
                     .sort_values(ascending=False)[:10]
fig2 = plot_submissions_tag_chart(pd.DataFrame(language_count).reset_index())


def plot_language_invalid_state_chart(df):
    status = df["Status"].unique()
    sum_df = df.groupby("Language").agg({"SolutionID": "sum"})
    sorted_index = sum_df.sort_values("SolutionID", ascending=False).index
    percentage_df = df.groupby(["Language", "Status"]).agg({"SolutionID": "sum"}). \
        div(sum_df, level="Language"). \
        reset_index(). \
        set_index("Language").loc[sorted_index]. \
        reset_index()
    fig = go.Figure([
        go.Bar(
            name=state,
            x=percentage_df[percentage_df["Status"] == state]["Language"],
            y=percentage_df[percentage_df["Status"] == state]["SolutionID"],
        )
        for state in status])
    fig.update_layout(dict(barmode="stack"))
    fig.update_layout(xaxis=dict(title="Types of Unsuccessful Submissions by Languages"))
    return fig


valid_state = ["accepted", "wrong answer", "internal error", "running..", "compiling..", "running judge.."]
solutions_df_valid_state = solutions_df.dropna(subset=["Status"]).reset_index()
invalid_state_count = solutions_df_valid_state[~solutions_df_valid_state["Status"].isin(valid_state)] \
    .groupby(["Status", "Language"])["SolutionID"] \
    .count() \
    .reset_index()
top_languages_with_invalid_sum = pd.DataFrame(invalid_state_count
                                              .groupby("Language")["SolutionID"]
                                              .sum()
                                              .sort_values(ascending=False)[:10]).reset_index()
state_df = invalid_state_count[invalid_state_count["Language"].isin(top_languages_with_invalid_sum["Language"])]
fig3 = plot_language_invalid_state_chart(state_df)


def plot_pie_chart(df, level_range):
    charts = []
    for level in level_range:
        fig = go.Figure(
            data=[go.Pie(
                labels=df.loc[level, "SolutionStatus"],
                values=df.loc[level, "SolutionID"],
                hole=.3,
                textinfo="label+percent",
                marker=dict(colors=["red", "royalblue"]))
            ],
            layout=dict(annotations=[
                {
                    "font": {
                        "size": 16,
                        "color": '#5A5A5A'
                    },
                    "showarrow": False,
                    "text": level,
                    "x": 0.5,
                    "y": 0.5
                }
            ])
        )
        fig.update(dict(layout_showlegend=False))
        charts.append(fig)
    return charts


levels = ["beginner", "easy", "medium", "hard", "challenge"]
solutions_df_levels = solutions_df.join(questions_df["level"], on="QCode")
solutions_df_levels.loc[solutions_df_levels["Status"] == "accepted", "SolutionStatus"] = "Passed"
solutions_df_levels.loc[solutions_df_levels["Status"] != "accepted", "SolutionStatus"] = "Failed"
solutions_df_levels = solutions_df_levels.groupby(["level", "SolutionStatus"])["SolutionID"].count().reset_index()
figures = plot_pie_chart(solutions_df_levels.set_index("level"), levels)

codechef_visualization = dbc.Container([
    html.H1("Codechef Competitive Programming Analytics"),
    html.Hr(),
    dbc.Col([
        html.H3("Overview of Passing/Failing Submissions by Levels"),
        dbc.Row(list(map(lambda figure: dcc.Graph(figure=figure, style=dict(width=f"33%")), figures[:3])),
                justify="center"),
        dbc.Row(list(map(lambda figure: dcc.Graph(figure=figure, style=dict(width=f"33%")), figures[3:])),
                justify="center"),
        html.H3("Detailed Submission Breakdown"),
        dbc.Row([
            dcc.Graph(id="status-chart", figure=fig3, style=dict(width="100%")),
        ]),
        dbc.Row([
            dcc.Graph(id="tag-chart", figure=fig1),
            dcc.Graph(id="language-chart", figure=fig2)
        ], justify="center")
    ], align="start"),
],
    fluid=True
)
