# app/utils.py
# -----------------------------------------------------------------------------
# Utilities for Subte-Dashboard
# - Root discovery
# - Robust data loaders with flexible schema mapping
# -----------------------------------------------------------------------------

from __future__ import annotations

from pathlib import Path
import pandas as pd


# -----------------------------------------------------------------------------
# Root & paths
# -----------------------------------------------------------------------------

def find_root(max_up: int = 6) -> Path:
    """
    Walk up to detect the project root by checking common anchors (data/, app/).
    """
    cur = Path.cwd()
    best = cur
    score_best = (-1, -1)  # (has_data_and_app, has_git)
    for i in range(max_up + 1):
        cand = cur if i == 0 else cur.parents[i - 1]
        has_data_app = int((cand / "data").exists() and (cand / "app").exists())
        has_git = int((cand / ".git").exists())
        score = (has_data_app, has_git)
        if score > score_best:
            best, score_best = cand, score
    return best


ROOT: Path = find_root()
DATA_DIR: Path = ROOT / "data"
PROCESSED: Path = DATA_DIR / "processed"
RAW: Path = DATA_DIR / "raw"
ASSETS: Path = ROOT / "assets"
SCREENSHOTS: Path = ASSETS / "screenshots"

# Back-compat alias some scripts might expect:
PROCESSED_DIR = PROCESSED


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _norm_text(s: pd.Series) -> pd.Series:
    """ASCII-fold, strip and collapse spaces."""
    return (
        s.astype("string")
        .str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("ascii")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )


def _norm_line(s: pd.Series) -> pd.Series:
    """
    Normalize line labels to 'LineaX' (e.g., 'D' -> 'LineaD', 'Linea d' -> 'LineaD').
    """
    s2 = _norm_text(s)
    s2 = (
        s2.str.replace("linea", "Linea", case=False)
          .str.replace("Linea ", "Linea")
          .str.replace(" ", "")
    )
    # Single letters → LineaX
    s2 = s2.apply(lambda x: f"Linea{x.upper()}" if isinstance(x, str) and len(x) == 1 and x.isalpha() else x)
    return s2


def _pick(cols: set[str], names: list[str]) -> str | None:
    for n in names:
        if n in cols:
            return n
    return None


# -----------------------------------------------------------------------------
# Loaders
# -----------------------------------------------------------------------------

def load_clean() -> pd.DataFrame:
    """
    Load cleaned demand dataset for 2024.
    Looks in data/processed for:
      - molinetes_2024_clean.parquet
      - molinetes_2024_clean.csv
    Returns DataFrame with columns: date (datetime64[ns]), line (category),
    station (category), passengers (Float64).
    """
    pq = PROCESSED / "molinetes_2024_clean.parquet"
    csv = PROCESSED / "molinetes_2024_clean.csv"

    if pq.exists():
        df = pd.read_parquet(pq)
    elif csv.exists():
        df = pd.read_csv(csv)
    else:
        raise FileNotFoundError(
            "Clean dataset not found.\n"
            f"Tried:\n  - {pq}\n  - {csv}\n"
            "Run Week 5 notebook (blocks 1–2) to build it."
        )

    # Normalize columns
    df.columns = [c.strip().lower() for c in df.columns]
    need = {"date", "line", "station", "passengers"}
    if not need.issubset(df.columns):
        raise ValueError(
            f"Clean dataset missing columns. Found: {sorted(df.columns)}. Need: {sorted(need)}"
        )

    # Dtypes
    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=False)
    df["line"] = _norm_line(df["line"]).astype("category")
    df["station"] = _norm_text(df["station"]).str.title().astype("category")
    df["passengers"] = pd.to_numeric(df["passengers"], errors="coerce").astype("Float64")

    # Keep 2024
    df = df[(df["date"] >= "2024-01-01") & (df["date"] < "2025-01-01")].copy()
    return df


def load_coverage() -> pd.DataFrame | None:
    """
    Load monthly coverage QC (if available).
    Returns None if not present.
    """
    path = PROCESSED / "quality_coverage_monthly.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    return df


def load_stations_geo() -> pd.DataFrame:
    """
    Load stations geo file and normalize schema:
      station (string, Title Case)
      line    (string, 'LineaX')
      lat     (float)
      lon     (float)

    Tries multiple candidates (processed/raw) and validates required columns.
    """
    candidates = [
        PROCESSED / "stations_geo.csv",
        PROCESSED / "bocas_geo.csv",
        PROCESSED / "bocas_de_subte.csv",
        RAW / "bocas_de_subte.csv",
        RAW / "bocas" / "bocas_de_subte.csv",
        RAW / "estaciones" / "bocas_de_subte.csv",
        RAW / "bocas_de_subte.geo.csv",
    ]
    found = next((p for p in candidates if p.exists()), None)
    if not found:
        raise FileNotFoundError(
            "Stations geo file not found. Expected one of:\n" +
            "\n".join(f"  - {p}" for p in candidates)
        )

    df = pd.read_csv(found)
    cols_map = {c.lower().strip(): c for c in df.columns}
    have = set(cols_map.keys())

    # Minimal set: station / lat / lon
    station_col = _pick(have, ["station", "estacion", "nombre", "nombre_estacion"])
    lat_col     = _pick(have, ["lat", "latitude", "y", "latitud"])
    lon_col     = _pick(have, ["lon", "lng", "long", "longitud", "longitud_wgs84", "x"])

    if not all([station_col, lat_col, lon_col]):
        raise ValueError(
            f"Could not map required columns in {found}.\n"
            f"Found: {sorted(df.columns)}\n"
            f"Need at least station/lat/lon"
        )

    # Optional line
    line_col = _pick(have, ["line", "linea", "linea_id", "linea_nombre"])

    out = pd.DataFrame({
        "station": _norm_text(df[cols_map[station_col]]).str.title(),
        "lat": pd.to_numeric(df[cols_map[lat_col]], errors="coerce"),
        "lon": pd.to_numeric(df[cols_map[lon_col]], errors="coerce"),
    })

    if line_col:
        out["line"] = _norm_line(df[cols_map[line_col]])
    else:
        # Placeholder (map works but won't color by line); recommended: add line in source CSV
        out["line"] = "Linea?"

    out = out.dropna(subset=["lat", "lon"])
    # Deduplicate (line, station) pairs
    out = out.drop_duplicates(subset=["line", "station"], keep="first").reset_index(drop=True)

    # Final schema check
    need = {"station", "line", "lat", "lon"}
    if not need.issubset(out.columns):
        raise ValueError(
            f"Geo schema invalid after normalization. Found: {sorted(out.columns)}. Need: {sorted(need)}"
        )
    return out


def load_formations() -> pd.DataFrame | None:
    """
    Load dispatched formations (trains) per day & line.
    Expected columns: date, line, trains
    Looks in data/processed for formaciones_2024.(parquet|csv).
    Returns None if not present.
    """
    pq = PROCESSED / "formaciones_2024.parquet"
    csv = PROCESSED / "formaciones_2024.csv"

    if pq.exists():
        df = pd.read_parquet(pq)
    elif csv.exists():
        df = pd.read_csv(csv)
    else:
        return None

    # Normalize columns
    df.columns = [c.strip().lower() for c in df.columns]
    need_any = {"date", "line", "trains"}
    if not need_any.issubset(df.columns):
        # Try alternative common names
        cols_map = {c: c for c in df.columns}
        date_col = _pick(set(df.columns), ["date", "fecha", "dia"])
        line_col = _pick(set(df.columns), ["line", "linea", "linea_nombre", "linea_id"])
        trains_col = _pick(set(df.columns), ["trains", "formaciones", "trenes", "despachos", "freq"])
        if not all([date_col, line_col, trains_col]):
            raise ValueError(
                f"Formations dataset missing columns. Found: {sorted(df.columns)}. "
                f"Need at least (date,line,trains)."
            )
        df = df.rename(columns={date_col: "date", line_col: "line", trains_col: "trains"})

    # Dtypes
    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=False)
    df["line"] = _norm_line(df["line"])
    df["trains"] = pd.to_numeric(df["trains"], errors="coerce").astype("Float64")

    # Keep 2024 only
    df = df[(df["date"] >= "2024-01-01") & (df["date"] < "2025-01-01")].copy()

    # Clean NaNs
    df = df.dropna(subset=["date", "line", "trains"])
    return df
