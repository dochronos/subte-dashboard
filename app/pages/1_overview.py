# app/pages/1_overview.py
import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd

from app.utils import load_clean, load_coverage

dash.register_page(__name__, path="/", title="Overview")

# Load data
df = load_clean()
df = df[df["date"].dt.year == 2024].copy()

# Total passengers by line
by_line = (
    df.groupby("line", observed=True)["passengers"]
      .sum(min_count=1)
      .reset_index()
      .sort_values("passengers", ascending=False)
)

fig_total = px.bar(
    by_line,
    x="line", y="passengers", color="line",
    title="Total passengers by line — 2024"
)

# Monthly passengers by line
df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
monthly = (
    df.groupby(["month", "line"], observed=True)["passengers"]
      .sum(min_count=1)
      .reset_index()
)

fig_month = px.line(
    monthly.sort_values("month"),
    x="month", y="passengers", color="line", markers=True,
    title="Monthly passengers by line — 2024"
)

# Optional coverage info (if exists)
cov = load_coverage()
cov_msg = None
if isinstance(cov, pd.DataFrame):
    cov_msg = f"Coverage QC loaded: {cov.shape[0]} rows"

layout = html.Div([
    html.P("Overview of 2024 demand (molinetes)."),
    dcc.Graph(figure=fig_total),
    dcc.Graph(figure=fig_month),
    html.Small(cov_msg) if cov_msg else html.Small("Coverage QC not available."),
])
