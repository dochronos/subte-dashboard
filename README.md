# 🚇 Buenos Aires Subway (Subte) — Business Intelligence Dashboard

**Goal:** Build an interactive BI dashboard that transforms official open data of the Buenos Aires Subway (Subte) into actionable insights for demand, frequency, and station-level patterns.

> This is a professional portfolio project designed to demonstrate data analysis, data modeling, geospatial visualization, and product-thinking. It follows a weekly iteration plan with public updates on LinkedIn.

---

## 🔍 Key Questions
- Which **lines and stations** have the highest passenger demand?
- How does **demand evolve over time** (month/season)?
- How does **service frequency** relate to demand (efficiency proxy)?
- What **geographical patterns** emerge (stations proximity, corridor usage)?

---

## 🧩 Datasets (Official Open Data — GCBA)
- **Passengers by station (turnstiles/molinete)** — demand by station & line  
- **Monthly frequency** — trains dispatched / service frequency  
- **Stations & entrances (geolocation)** — coordinates for mapping  
> Source portal: https://data.buenosaires.gob.ar/dataset/?q=subtes

*(Exact dataset links and data dictionaries will be documented in `/data/README_DATASETS.md` after download.)*

---

## 🛠️ Tech Stack
- **Python 3.11+**, **Pandas**
- **Plotly + Dash** (interactive app) / *(Tableau or Power BI optional for comparison screenshots)*
- **Jupyter Notebooks** (exploration & EDA)

---

## 📂 Repository Structure
subte-dashboard/
│── assets/
│ └── screenshots/
│── data/ # raw/ and processed/ will live here
│ └── README_DATASETS.md # source links, schema, refresh policy
│── notebooks/ # EDA, experiments, drafts
│ └── 01_exploration.ipynb
│── src/
│ ├── app.py # Dash entry point (MVP dashboard)
│ └── utils/ # helpers (loading, cleaning, mapping)
│── requirements.txt
│── README.md

---

## 📸 Screenshots & LinkedIn Updates

- **Week 1**  
  Initial EDA — passengers by line (sample of 3 CSVs).  
  ![Week 1 preview](assets/screenshots/week1_preview.png)  
  👉 [LinkedIn Post](https://www.linkedin.com/posts/hermanschubert_dataanalytics-businessintelligence-python-activity-7365832932294381569-go3H?utm_source=share&utm_medium=member_desktop&rcm=ACoAAAggMogBjBE17nitimWMiApsgdQkRtJey-M)

---

## 📊 Week 2 — Demand & Trends

✅ Cleaned + normalized full 2024 dataset (11.4M rows)  
✅ Aggregations by subway line and by month  
✅ First visualizations exported with Kaleido  

### Key Outputs
- **Total Passengers by Line (2024)**  
  ![bar_passengers_by_line](assets/screenshots/week2_demand_by_line.png)

- **Monthly Demand by Line (2024)**  
  ![line_trend_by_line](assets/screenshots/week2_trend_by_month.png)

---

## 📍 Week 3 — Geospatial Join (Stations + Demand)

✅ Clean join between **station entrances** (bocas) and **2024 turnstile demand**  
✅ 100% station–line match after alias normalization (pair-specific overrides for tricky cases)  
✅ Map + CSV exports generated for dashboard and recruiters  

### Key Outputs
- **BA Subway — Demand by Station (2024)**  
  ![week3_map](assets/screenshots/week3_map.png)

### Files Produced
- `data/processed/stations_with_demand_2024.csv`  
- `data/processed/map_stations_demand_2024.png`  
- `assets/screenshots/week3_map.png` (for README/LinkedIn)  

**Tech notes**  
- Robust CSV loader with multi-encoding fallback (`utf-8-sig`, `utf-8`, `latin1`, `cp1252`)  
- Column normalization + alias strategy (global + pair-wise mapping)  
- Plotly/Mapbox (OpenStreetMap tiles) for reproducible maps  

---

## 📈 Week 4 — Frequency & KPI (Pax / Train)

This week we integrated **service frequency** (trains dispatched) to create a simple efficiency proxy:  
**KPI = Passengers / Dispatched Train** (by line & by month, 2024).

**What we did**
- Normalized monthly frequency from *Formaciones Despachadas 2024*.
- Rebuilt passengers trend (2024) robustly from turnstiles if not cached.
- Created KPI snapshots per line and a monthly trend.
- Exported ready-to-share **CSVs** and **PNGs**.

**Key outputs**
- `data/processed/kpi_pax_per_train_2024_by_line.csv`
- `data/processed/kpi_pax_per_train_2024_trend.csv`

**Visuals**
- KPI by Line (2024)  
  ![Week 4 — KPI by Line](assets/screenshots/week4_kpi_by_line.png)

- Monthly KPI Trend (2024)  
  ![Week 4 — KPI Trend](assets/screenshots/week4_kpi_trend.png)

---

### Week 5 — Data Quality Checks

- Added a robust multi-CSV loader (24 files, 11.44M rows for 2024).
- Sanity checks:
  - **Nulls** in `passengers`
  - **Negative values**
  - **Per-line extreme outliers** (above the 99.9th percentile)
  - **Duplicates** on (`station`, `line`, `date`)
- Exported anomalies to: `data/processed/quality_flags.csv`
- Distribution chart (boxplot, 15-min intervals) saved to:
  `assets/screenshots/week5_quality.png`

**Dataset scope (2024):**
- Date range: 2024-01-01 → 2024-12-31  
- Unique lines: 6  
- Unique stations: 97  
- Rows: 11,440,440  

**Coverage checks (monthly):**
- Low-coverage detection per (`station`, `line`, `month`)
- Reports saved to:  
  - `data/processed/quality_coverage_monthly.csv`  
  - `data/processed/quality_coverage_worst_cases.csv`  
- Heatmap saved to: `assets/screenshots/week5_quality.png`

_Screenshots:_  
![Week 5 — Distribution by Line](assets/screenshots/week5_quality.png)  
![Week 5 — Coverage Heatmap](assets/screenshots/week5_coverage.png)

---

### Week 6 — Dash MVP (Overview, Geospatial & KPIs)

- **Dash app** with three pages: Overview, Geospatial, and KPIs.
- **Overview:** total demand and monthly trends by line (2024).
- **Geospatial:** station map with 2024 passenger totals (via `stations_geo.csv`).
- **KPIs:** *Passengers per dispatched train* using `formaciones_2024`.

**Reproducible scripts (`/scripts`):**
- `generate_stations_geo.py` — build `data/processed/stations_geo.csv` from the raw “bocas/estaciones” file.
- `build_formaciones_from_freq.py` — derive `formaciones_2024.(csv|parquet)` from `freq_from_form_2024.csv`.
- `generate_formations_2024.py` — generic converter for raw formations (kept for future updates).
- `make_week6_screenshots.py` — exports the images used below.

**Screenshots:**
![Week 6 — Overview (Monthly)](assets/screenshots/week6_overview_line.png)  
![Week 6 — Geospatial map](assets/screenshots/week6_map.png)  
![Week 6 — KPI (by line)](assets/screenshots/week6_kpi_bar.png)  
![Week 6 — KPI (trend)](assets/screenshots/week6_kpi_trend.png)

---

## 📊 Dash App — Subte Dashboard

In addition to the weekly notebooks, this repository includes an interactive application built with Dash, featuring multiple pages (Overview, Geospatial, KPIs).

👉 [Instructions to launch the app](app/README.md)

---

## 🚀 Getting Started (Local)
```bash
git clone https://github.com/dochronos/subte-dashboard.git
cd subte-dashboard

# Create and activate venv
python -m venv venv
# Mac/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

# Install deps
pip install -r requirements.txt

# Run Dash app
python src/app.py
# App will run at http://127.0.0.1:8050

🗺️ MVP Dashboard (Week 2 target)

Page 1 — Demand Overview

Top stations by passengers

Demand by line (A, B, C, D, E, H)

Monthly trend chart

Page 2 — Geomap

Stations & entrances (tooltip: station, line, demand)

📅 Iteration Plan (Build-in-Public)

Week 1 — Setup & Data

Download datasets, document sources (/data/README_DATASETS.md)

First EDA notebook

Minimal Dash app skeleton (runs locally)

Week 2 — Demand & Trends

Cleaned demand dataset (station/line/month)

Visuals: top stations, demand by line, trend

Week 3 — Geospatial

Join with station geolocation

Interactive map in Dash (tooltips & filters)

Week 4 — Frequency & KPI

Integrate frequency dataset

KPI: passengers per dispatched train (proxy)

Final polish (layout, filters, README update, screenshots)

🧪 Data Quality & Refresh

Version datasets in /data/raw and /data/processed

Track refresh policy and caveats in README_DATASETS.md

📸 Screenshots (to be added)

/assets/screenshots/ — add key views

🔗 LinkedIn Updates

Weekly posts summarizing progress, insights, visuals, and tech decisions.

📜 License

Open for educational and portfolio purposes. Data © Gobierno de la Ciudad de Buenos Aires (per their open-data license).

## 📌 Notes

This project is part of a professional growth journey, showcasing data-driven skills and technical learning.