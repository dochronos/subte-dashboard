Subte-Dashboard — Dash App

Multipage dashboard (Dash) for the Subte project.

✅ Pages: Overview, Geospatial (placeholder), KPIs (placeholder)

✅ Reads the cleaned dataset from data/processed/

✅ Bootstrap styling via dash-bootstrap-components

1) Requirements

Python 3.10+ (tested on 3.12)

Dependencies listed in the repo root: requirements.txt

Install (from the repo root):

pip install -r requirements.txt

If you prefer a virtual env:

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt

2) Project structure (app)

app/
├─ __init__.py
├─ main.py                 # entrypoint (python -m app.main)
├─ utils.py                # data loaders & paths
└─ pages/                  # multipage layout
   ├─ __init__.py
   ├─ 1_overview.py
   ├─ 2_geospatial.py      # placeholder (hook for Mapbox)
   └─ 3_kpis.py            # placeholder

Data expected under the repo root:

data/
└─ processed/
   ├─ molinetes_2024_clean.parquet   # preferred
   ├─ molinetes_2024_clean.csv       # fallback if parquet not found
   └─ quality_coverage_monthly.csv   # optional (QC badge)

These files are produced by the notebooks (Weeks 2 & 5).
Run the notebooks first if they’re missing.

3) How to run

From the repo root:

python -m app.main

Then open: http://127.0.0.1:8050/

4) Pages

Overview

Total passengers by line (2024)

Monthly trend by line (2024)

Optional QC badge if quality_coverage_monthly.csv is present

Geospatial (placeholder)

Bar chart with top stations (ready to replace with px.scatter_mapbox)

KPIs (placeholder)

Slots for passengers per dispatched train (will join with formations 2024)

5) Configuration & paths

No environment variables needed. Paths are auto-resolved relative to the repo root (the app walks up to find data/ and assets/).

6) Troubleshooting

A) ModuleNotFoundError: No module named 'dash_bootstrap_components'
→ Install deps from the root:

pip install -r requirements.txt

B) ImportError: attempted relative import beyond top-level package
→ Ensure this structure:

app/__init__.py exists

app/pages/__init__.py exists

Imports inside pages are absolute:

from app.utils import load_clean, load_coverage

Run from the repo root:

python -m app.main

C) ObsoleteAttributeException: app.run_server
→ Dash ≥ 2.16 uses:

app.run(debug=True)

(Already handled in main.py.)

D) Still can’t find data

Check the files exist in data/processed/ (parquet or CSV).

Run the cleaning notebooks to generate molinetes_2024_clean.*.

E) Port already in use

python -m app.main --port 8051

(You can customize in main.py if needed.)

7) Extending the app

Add a new page: create app/pages/4_my_page.py with:

import dash
from dash import html

dash.register_page(__name__, path="/my-page", title="My Page")

layout = html.Div(["Hello from my page"])

Geospatial: replace the placeholder with a join to your stations layer (lat/lon) and render:

px.scatter_mapbox(..., mapbox_style="carto-positron", zoom=10)

(No token required for carto-positron.)

8) Dependencies

Maintained in repo root requirements.txt:

dash>=2.16
dash-bootstrap-components>=1.6
plotly>=5.22
pandas>=2.2
pyarrow>=16

9) License / Credits

This app is part of the Subte-Dashboard project. Feel free to fork and adapt with attribution.