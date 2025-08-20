# Datasets — Buenos Aires Subway (Subte)

This folder contains **raw datasets** downloaded from the official Open Data portal of the Government of the City of Buenos Aires (GCBA).  
All files in `data/raw/` are kept **as originally downloaded** (no modifications). Processed outputs are stored under `data/processed/` (excluded from version control).

## Source
- Portal: https://data.buenosaires.gob.ar/dataset/?q=subtes
- Download date: 2025-08-18 (YYYY-MM-DD)

## Files Overview

### 1) Turnstiles / Passenger Demand (Molinete)
- Path: `data/raw/molinetes/2024/`
- Format: CSV (24 files)
- Year: 2024
- Size per file: ~20–49 MB each
- Description: Passenger counts by station (and line, if provided by the dataset).
- Notes: Used to compute demand by line/station and monthly trends.

### 2) Service Frequency (Subway)
- Path: `data/raw/frecuencia/frecuencia_subte.xlsx`
- Format: XLSX
- Size: ~23 KB
- Description: Frequency / service metrics by line and period.

### 3) Dispatched Trains (Formaciones despachadas)
- Path: `data/raw/formaciones/formaciones-despachadas-2024.xlsx`
- Format: XLSX
- Size: ~47 MB
- Description: Trains dispatched by line and period (proxy for operational capacity).

### 4) Stations & Entrances (Geolocation)
- Path: `data/raw/estaciones/bocas-de-subte.csv`
- Format: CSV
- Size: ~84 KB
- Description: Station names, entrances, and coordinates for mapping.

## Conventions & Schema Notes
- Dates use ISO format when applicable: `YYYY-MM-DD`.
- Subway lines: `{A, B, C, D, E, H}`.
- Raw files are **never altered**. Any cleaning/transformations are written to `data/processed/`.
- If GCBA publishes a new version, add it as a **new file** with the date/version in the filename (do not overwrite existing files).

## Data Quality & Refresh
- Keep a clear separation between `raw/` and `processed/`.
- Track any caveats (missing values, outliers, column changes) in the EDA notebooks and/or here.
- Document refresh policy (e.g., monthly/annual updates) if applicable.

## Reproducibility
- EDA and transformations are documented in notebooks under `/notebooks/` and scripts under `/src/`.
- To clone this (potentially heavy) repository faster you can use a partial clone:
  ```bash
  git clone --filter=blob:none https://github.com/dochronos/subte-dashboard.git
