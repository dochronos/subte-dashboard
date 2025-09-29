# app/pages/3_kpis.py
import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd
import numpy as np

from app.utils import load_clean, load_formations

dash.register_page(__name__, path="/kpis", title="KPIs")

df = load_clean()
df = df[df["date"].dt.year == 2024].copy()

graphs = []

# ---------- KPI 1: Passengers per dispatched train ----------
form = load_formations()
if form is not None:
    pax_day_line = (
        df.groupby([df["date"].dt.date, "line"], observed=True)["passengers"]
          .sum(min_count=1)
          .reset_index()
          .rename(columns={"date": "date"})
    )
    pax_day_line["date"] = pd.to_datetime(pax_day_line["date"])

    trains = form.dropna(subset=["date", "line"]).copy()
    trains["date"] = pd.to_datetime(trains["date"])

    merged = pd.merge(
        pax_day_line,
        trains[["date", "line", "trains"]],
        on=["date", "line"],
        how="inner"
    )
    merged = merged[merged["trains"] > 0]
    merged["pax_per_train"] = merged["passengers"] / merged["trains"]

    if not merged.empty:
        fig_ppt = px.line(
            merged.sort_values("date"),
            x="date", y="pax_per_train", color="line",
            markers=True, title="Passengers per dispatched train — daily (2024)"
        )
        graphs.append(dcc.Graph(figure=fig_ppt))
    else:
        graphs.append(html.Div([
            html.H5("Passengers per dispatched train"),
            html.P("No data after merging passengers and formations.")
        ], style={"padding":"8px","border":"1px solid #eee","borderRadius":"8px"}))
else:
    graphs.append(html.Div([
        html.H5("Passengers per dispatched train"),
        html.P("Missing formations dataset — showing placeholder."),
        html.P("To enable this KPI, provide a file like data/processed/formaciones_2024.(parquet|csv) "
               "with columns [date, line, trains].")
    ], style={"padding":"8px","border":"1px solid #eee","borderRadius":"8px"}))

# ---------- KPI 2: Peak vs Off-Peak ----------
# If date lacks hour info, show monthly line series
if df["date"].dt.hour.isna().all():
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    monthly = (
        df.groupby(["month", "line"], observed=True)["passengers"]
          .sum(min_count=1)
          .reset_index()
    )
    fig_month = px.line(
        monthly, x="month", y="passengers", color="line", markers=True,
        title="Monthly passengers by line — (no hourly data available)"
    )
    graphs.append(dcc.Graph(figure=fig_month))
else:
    df["hour"] = df["date"].dt.hour
    peak_hours = set(range(7,10)) | set(range(17,20))  # simple heuristic
    df["peak_flag"] = df["hour"].isin(peak_hours)

    kpi_peak = (
        df.groupby(["line", "peak_flag"], observed=True)["passengers"]
          .sum(min_count=1)
          .reset_index()
    )
    kpi_pivot = kpi_peak.pivot(index="line", columns="peak_flag", values="passengers").fillna(0)
    kpi_pivot = kpi_pivot.rename(columns={False: "off_peak", True: "peak"})
    kpi_pivot["peak_off_ratio"] = np.where(kpi_pivot["off_peak"] > 0,
                                           kpi_pivot["peak"] / kpi_pivot["off_peak"],
                                           np.nan)
    kpi_pivot = kpi_pivot.reset_index()

    fig_ratio = px.bar(
        kpi_pivot.sort_values("peak_off_ratio", ascending=False),
        x="line", y="peak_off_ratio",
        title="Peak / Off-Peak ratio by line — 2024"
    )
    graphs.append(dcc.Graph(figure=fig_ratio))

# ---------- KPI 3: Station utilization percentiles ----------
station_tot = (
    df.groupby(["line", "station"], observed=True)["passengers"]
      .sum(min_count=1)
      .reset_index()
)

def pct(x, q): 
    return np.nanpercentile(x, q) if len(x) else np.nan

pcts = []
for ln, g in station_tot.groupby("line", observed=True):
    p50 = pct(g["passengers"], 50)
    p75 = pct(g["passengers"], 75)
    p90 = pct(g["passengers"], 90)
    pcts.append({"line": ln, "p50": p50, "p75": p75, "p90": p90})
pcts = pd.DataFrame(pcts)

fig_pcts = px.bar(
    pcts.melt(id_vars="line", value_vars=["p50","p75","p90"],
              var_name="percentile", value_name="passengers"),
    x="line", y="passengers", color="percentile", barmode="group",
    title="Station utilization percentiles (total 2024)"
)
graphs.append(dcc.Graph(figure=fig_pcts))

layout = html.Div([
    html.P("KPIs: operational and demand metrics. Datasets: molinetes 2024 (+ formations 2024 if available)."),
    *graphs
])
