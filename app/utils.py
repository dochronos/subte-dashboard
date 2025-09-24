from pathlib import Path
import pandas as pd

def find_root(max_up=6):
    cur = Path.cwd()
    best = cur
    score_best = (-1, -1)
    for i in range(max_up+1):
        up = cur if i == 0 else cur.parents[i-1]
        has_assets = (up/"assets").exists()
        has_data = (up/"data").exists()
        has_git = (up/".git").exists()
        score = (int(has_assets and has_data), int(has_git))
        if score > score_best:
            best, score_best = up, score
    return best

ROOT = find_root()
PROCESSED = ROOT/"data"/"processed"

def load_clean():
    pq = PROCESSED/"molinetes_2024_clean.parquet"
    csv = PROCESSED/"molinetes_2024_clean.csv"
    if pq.exists():
        df = pd.read_parquet(pq)
    elif csv.exists():
        df = pd.read_csv(csv)
    else:
        raise FileNotFoundError("Clean dataset not found in data/processed/")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["passengers"] = pd.to_numeric(df["passengers"], errors="coerce")
    return df

def load_coverage():
    path = PROCESSED/"quality_coverage_monthly.csv"
    if path.exists():
        df = pd.read_csv(path)
        return df
    return None
