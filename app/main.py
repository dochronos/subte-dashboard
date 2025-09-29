import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from pathlib import Path

PAGES_DIR = Path(__file__).parent / "pages"

app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder=str(PAGES_DIR),
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Subte Dashboard",
)

app.layout = dbc.Container([
    html.H2("Subte-Dashboard"),
    html.Div([
        dcc.Link("Overview", href="/"),
        html.Span(" | "),
        dcc.Link("Geospatial", href="/geospatial"),
        html.Span(" | "),
        dcc.Link("KPIs", href="/kpis"),
    ], className="mb-3"),
    dash.page_container
], fluid=True)

server = app.server

if __name__ == "__main__":
    app.run(debug=True)
