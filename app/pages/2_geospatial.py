import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd
from app.utils import load_clean

dash.register_page(__name__, path="/geospatial", title="Geospatial")

df = load_clean()
df_2024 = df[df["date"].dt.year == 2024].copy()
# TODO: join con bocas/estaciones (lat/lon) para scatter_mapbox
# Placeholder: top stations by passengers
top_st = (df_2024.groupby("station", observed=True)["passengers"]
          .sum(min_count=1).reset_index()
          .sort_values("passengers", ascending=False).head(20))

fig = px.bar(top_st, x="station", y="passengers", title="Top stations — 2024 (placeholder)")

layout = html.Div([
    html.P("Geospatial page (placeholder). Integrate lat/lon to enable Mapbox."),
    dcc.Graph(figure=fig)
])
