import dash
from app import app
from routes.stack_overflow.figure import stack_overflow_visualization
from routes.codechef.figure import codechef_visualization


@app.callback(dash.dependencies.Output("page-content", "children"),
              [dash.dependencies.Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/stack-overflow":
        return stack_overflow_visualization
    elif pathname == "/codechef":
        return codechef_visualization


if __name__ == "__main__":
    app.run_server(threaded=True)
