import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd
from app.utils import load_clean, load_coverage

dash.register_page(__name__, path="/", title="Overview")

df = load_clean()
df_2024 = df[df["date"].dt.year == 2024].copy()
df_2024["month"] = df_2024["date"].dt.to_period("M").dt.to_timestamp()

tot_by_line = (
    df_2024.groupby("line", observed=True)["passengers"].sum(min_count=1).reset_index()
)
fig_bar = px.bar(tot_by_line.sort_values("passengers", ascending=False),
                 x="line", y="passengers", title="Total passengers by line — 2024")

monthly_line = (
    df_2024.groupby(["month","line"], observed=True)["passengers"].sum(min_count=1).reset_index()
)
fig_line = px.line(monthly_line, x="month", y="passengers", color="line",
                   markers=True, title="Monthly passengers by line — 2024")

cov = load_coverage()
cov_badge = None
if cov is not None and "flag_low_coverage" in cov.columns:
    share = cov.groupby(["month","line"], observed=True)["flag_low_coverage"].mean().mean()
    cov_badge = f"QC: avg share of low-coverage station-months ~ {share:.2%}"

layout = html.Div([
    html.Div(cov_badge) if cov_badge else html.Div(),
    dcc.Graph(figure=fig_bar),
    dcc.Graph(figure=fig_line),
])
