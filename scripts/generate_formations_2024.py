"""
generate_formations_2024.py
---------------------------
Builds data/processed/formaciones_2024.(csv|parquet) with columns:
  - date (YYYY-MM-DD)
  - line (LineaA/B/C/...)
  - trains (number of dispatched formations per day & line)
"""

from pathlib import Path
import pandas as pd

# ---------- paths ----------
ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

# where to look (add/adjust if your files are elsewhere)
CANDIDATE_DIRS = [
    RAW,
    RAW / "formaciones",
    PROCESSED,  # in case you already exported something earlier
]

def find_files():
    exts = ("*.csv", "*.parquet")
    files = []
    for base in CANDIDATE_DIRS:
        if not base.exists():
            continue
        for pat in exts:
            files += list(base.glob(pat))
    # filter by name hints
    files = [f for f in files if any(k in f.name.lower() for k in [
        "form", "despach", "train", "freq", "formation"
    ])]
    return sorted(files)

def norm_line(s: pd.Series) -> pd.Series:
    x = s.astype("string").str.strip()
    # 'd' → 'LineaD'
    x = x.apply(lambda v: f"Linea{v.upper()}" if isinstance(v, str) and len(v) == 1 and v.isalpha() else v)
    x = (x.str.replace("linea", "Linea", case=False)
           .str.replace("Linea ", "Linea")
           .str.replace(" ", ""))
    return x

def pick(cols, names):
    for n in names:
        if n in cols:
            return n
    return None

def load_one(path: Path) -> pd.DataFrame | None:
    # read
    try:
        df = pd.read_csv(path)
    except Exception:
        try:
            df = pd.read_csv(path, sep=";")
        except Exception:
            if path.suffix.lower() == ".parquet":
                df = pd.read_parquet(path)
            else:
                raise
    df.columns = [c.lower().strip() for c in df.columns]
    cols = set(df.columns)

    # map
    c_date = pick(cols, ["date", "fecha", "dia"])
    c_line = pick(cols, ["line", "linea", "linea_nombre", "linea_id"])
    c_trns = pick(cols, ["trains", "formaciones", "trenes", "despachos", "freq", "salidas"])

    if not all([c_date, c_line, c_trns]):
        # skip silently if it's not a formations-like file
        return None

    out = df[[c_date, c_line, c_trns]].copy()
    out = out.rename(columns={c_date: "date", c_line: "line", c_trns: "trains"})

    # dtypes
    out["date"] = pd.to_datetime(out["date"], errors="coerce", utc=False).dt.date
    out["line"] = norm_line(out["line"])
    out["trains"] = pd.to_numeric(out["trains"], errors="coerce")

    # drop NA and keep 2024
    out = out.dropna(subset=["date", "line", "trains"])
    out = out[(out["date"] >= pd.to_datetime("2024-01-01").date()) &
              (out["date"] <  pd.to_datetime("2025-01-01").date())]
    if out.empty:
        return None

    # aggregate (por si viene hora a hora o con duplicados)
    out = (
        out.groupby(["date", "line"], as_index=False)["trains"]
           .sum()
    )
    return out

def main():
    files = find_files()
    if not files:
        raise FileNotFoundError(
            "No raw formations files found.\n"
            "Place CSV/Parquet in data/raw/ or data/raw/formaciones/ "
            "with columns like (fecha|date|dia), (linea|line), (formaciones|trenes|despachos|freq)."
        )
    print("Found candidates:")
    for f in files:
        print(" -", f)

    parts = []
    for f in files:
        try:
            df = load_one(f)
        except Exception as e:
            print(f" !! Error loading {f.name}: {type(e).__name__}: {e}")
            continue
        if df is not None and not df.empty:
            parts.append(df)

    if not parts:
        raise RuntimeError("Could not load any formations-like file with valid schema for 2024.")

    full = pd.concat(parts, ignore_index=True)
    # aggregate again in case multiple sources overlap
    full = full.groupby(["date", "line"], as_index=False)["trains"].sum()

    # save
    csv_path = PROCESSED / "formaciones_2024.csv"
    pq_path  = PROCESSED / "formaciones_2024.parquet"
    full.to_csv(csv_path, index=False)
    try:
        full.to_parquet(pq_path, index=False)
    except Exception:
        pass

    print("\nSaved:")
    print(" -", csv_path)
    if pq_path.exists():
        print(" -", pq_path)
    print("\nSample:")
    print(full.head())

if __name__ == "__main__":
    main()
