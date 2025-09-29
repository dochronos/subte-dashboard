# scripts/make_week6_screenshots.py
from pathlib import Path
import pandas as pd
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "screenshots"
PROCESSED = ROOT / "data" / "processed"

ASSETS.mkdir(parents=True, exist_ok=True)

# ---- Load datasets ----
clean_pq = PROCESSED / "molinetes_2024_clean.parquet"
clean_csv = PROCESSED / "molinetes_2024_clean.csv"
stations_csv = PROCESSED / "stations_geo.csv"
forms_pq = PROCESSED / "formaciones_2024.parquet"
forms_csv = PROCESSED / "formaciones_2024.csv"

if clean_pq.exists():
    df = pd.read_parquet(clean_pq)
elif clean_csv.exists():
    df = pd.read_csv(clean_csv)
else:
    raise FileNotFoundError("molinetes_2024_clean.(parquet|csv) not found in data/processed/")

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["passengers"] = pd.to_numeric(df["passengers"], errors="coerce")

geo = pd.read_csv(stations_csv) if stations_csv.exists() else None
forms = pd.read_parquet(forms_pq) if forms_pq.exists() else (pd.read_csv(forms_csv) if forms_csv.exists() else None)

# ---- OVERVIEW (bar + monthly line, en una sola figura) ----
agg_line = df.groupby("line", as_index=False)["passengers"].sum().sort_values("passengers", ascending=False)
monthly = (df.assign(year_month=df["date"].dt.to_period("M").dt.to_timestamp())
             .groupby(["year_month", "line"], as_index=False)["passengers"].sum())

fig_overview_bar = px.bar(agg_line, x="line", y="passengers",
                          title="Total passengers by line — 2024",
                          labels={"passengers": "Passengers"})
fig_overview_line = px.line(monthly, x="year_month", y="passengers", color="line",
                            markers=True,
                            title="Monthly passengers by line — 2024",
                            labels={"year_month": "Month", "passengers": "Passengers"})

# Guardar como una sola lámina (stack simple: guardamos la segunda por simplicidad)
# Si querés una colmena, podríamos generar un SVG o un collage; por ahora exportamos ambas y luego elegís.
overview_bar_path = ASSETS / "week6_overview_bar.png"
overview_line_path = ASSETS / "week6_overview_line.png"
fig_overview_bar.write_image(overview_bar_path, scale=2, width=1000, height=600)
fig_overview_line.write_image(overview_line_path, scale=2, width=1100, height=650)

# ---- GEOSPATIAL (mapa de estaciones con totales 2024) ----
map_path = ASSETS / "week6_map.png"
if geo is not None and {"station","line","lat","lon"}.issubset(geo.columns):
    tot_station = df.groupby(["station","line"], as_index=False)["passengers"].sum()
    g = geo.merge(tot_station, on=["station","line"], how="left")
    g["passengers"] = g["passengers"].fillna(0)

    # Usamos scatter_geo (no requiere token). Si tenés Mapbox token, podemos migrar a scatter_mapbox.
    fig_map = px.scatter_geo(
        g, lat="lat", lon="lon", color="line", size="passengers",
        hover_name="station",
        projection="natural earth",
        title="Stations — Passengers (2024)"
    )
    fig_map.write_image(map_path, scale=2, width=1100, height=700)
else:
    # fallback: no hay geo → generamos un placeholder simple
    px.imshow([[0]]).update_layout(title="Geospatial unavailable (stations_geo.csv missing)").write_image(map_path)

# ---- KPIs (Passengers per dispatched train) ----
kpi_bar_path = ASSETS / "week6_kpi_bar.png"
kpi_trend_path = ASSETS / "week6_kpi_trend.png"

if forms is not None and not forms.empty:
    forms["date"] = pd.to_datetime(forms["date"], errors="coerce")
    forms["line"] = forms["line"].astype("string")
    forms["trains"] = pd.to_numeric(forms["trains"], errors="coerce")

    # Por defecto, nos quedamos con A–H (evitar Premetro si existe)
    known_lines = {f"Linea{x}" for x in list("ABCDEFGH")}
    forms_f = forms[forms["line"].isin(known_lines)].copy()

    demand_daily = df.groupby(["date","line"], as_index=False)["passengers"].sum()
    merged = demand_daily.merge(forms_f, on=["date","line"], how="inner")
    merged = merged[merged["trains"] > 0].copy()
    merged["pax_per_train"] = merged["passengers"] / merged["trains"]

    # By line (avg anual)
    by_line = (merged.groupby("line", as_index=False)["pax_per_train"].mean()
                      .sort_values("pax_per_train", ascending=False))
    fig_kpi_bar = px.bar(by_line, x="line", y="pax_per_train",
                         title="Passengers per dispatched train — by line (avg 2024)",
                         labels={"pax_per_train": "Passengers / train"})
    fig_kpi_bar.write_image(kpi_bar_path, scale=2, width=1000, height=600)

    # Trend mensual
    merged["year_month"] = merged["date"].astype("datetime64[M]")
    trend = merged.groupby(["year_month","line"], as_index=False)["pax_per_train"].mean()
    fig_kpi_trend = px.line(trend, x="year_month", y="pax_per_train", color="line",
                            markers=True,
                            title="Passengers per dispatched train — monthly trend (2024)",
                            labels={"year_month": "Month", "pax_per_train":"Passengers / train"})
    fig_kpi_trend.write_image(kpi_trend_path, scale=2, width=1100, height=650)
else:
    # placeholders si faltan formaciones
    px.imshow([[0]]).update_layout(title="KPI unavailable (formaciones_2024 missing)").write_image(kpi_bar_path)
    px.imshow([[0]]).update_layout(title="KPI trend unavailable (formaciones_2024 missing)").write_image(kpi_trend_path)

print("Saved:")
print(" -", overview_bar_path)
print(" -", overview_line_path)
print(" -", map_path)
print(" -", kpi_bar_path)
print(" -", kpi_trend_path)
