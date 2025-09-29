# app/pages/2_geospatial.py
import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd

from app.utils import load_clean, load_stations_geo

dash.register_page(__name__, path="/geospatial", title="Geospatial")

# Load base
df = load_clean()
df = df[df["date"].dt.year == 2024].copy()

# Try to load geo; if missing, we keep the page alive with a placeholder
GEO_ERROR = None
try:
    geo = load_stations_geo()
except Exception as e:
    geo = None
    GEO_ERROR = str(e)

def norm(s: pd.Series) -> pd.Series:
    return (s.astype("string")
              .str.normalize("NFKD").str.encode("ascii","ignore").str.decode("ascii")
              .str.strip().str.replace(r"\s+"," ", regex=True))

# Aggregate passengers by station-line
agg = (
    df.groupby(["line", "station"], observed=True)["passengers"]
      .sum(min_count=1)
      .reset_index()
)

if geo is not None:
    # Normalize to join
    agg["station_norm"] = norm(agg["station"]).str.title()
    agg["line_norm"] = (
        norm(agg["line"])
        .str.replace(r"\s+", "", regex=True)
        .str.replace("linea", "Linea", case=False)
    )
    geo["station_norm"] = norm(geo["station"]).str.title()
    geo["line_norm"] = (
        norm(geo["line"])
        .str.replace(r"\s+", "", regex=True)
        .str.replace("linea", "Linea", case=False)
    )

    m = agg.merge(
        geo[["line_norm", "station_norm", "lat", "lon"]],
        on=["line_norm", "station_norm"],
        how="left"
    )
else:
    m = agg.copy()
    m["lat"] = pd.NA
    m["lon"] = pd.NA

# Top stations table (bar)
top_st = m.sort_values("passengers", ascending=False).head(30)

graphs = []

# Map (only if we have coords)
if geo is not None and m[["lat", "lon"]].notna().all(axis=1).any():
    fig_map = px.scatter_mapbox(
        m.dropna(subset=["lat", "lon"]),
        lat="lat", lon="lon",
        color="line", size="passengers",
        hover_name="station",
        hover_data={"line": True, "passengers": ":,", "lat": False, "lon": False},
        zoom=10, height=600
    )
    fig_map.update_layout(
        mapbox_style="carto-positron",
        margin=dict(l=10, r=10, t=40, b=10),
        title="Stations — Passengers (2024)"
    )
    graphs.append(dcc.Graph(figure=fig_map))
else:
    msg = GEO_ERROR or "Stations geo file missing. Please create data/processed/stations_geo.csv"
    graphs.append(html.Div([
        html.H5("Geospatial map unavailable"),
        html.Pre(msg)
    ], style={"padding":"8px","border":"1px solid #eee","borderRadius":"8px","background":"#fffdf5"}))

# Top stations bar
fig_bar = px.bar(
    top_st.sort_values("passengers", ascending=True),
    x="passengers", y="station", color="line",
    orientation="h", height=700,
    title="Top stations by passengers — 2024"
)
graphs.append(dcc.Graph(figure=fig_bar))

layout = html.Div([
    html.P("Geospatial: interactive map of stations with 2024 passenger totals."),
    *graphs
])
