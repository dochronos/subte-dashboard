# scripts/make_week7_screenshots.py
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Paths (root-aware) ----------
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
SCREENSHOTS = ROOT/"assets"/"screenshots"
SCREENSHOTS.mkdir(parents=True, exist_ok=True)

print("ROOT:", ROOT)
print("PROCESSED:", PROCESSED)
print("SCREENSHOTS:", SCREENSHOTS)

# ---------- Inputs ----------
molinetes_pq = PROCESSED/"molinetes_2024_clean.parquet"
formaciones_pq = PROCESSED/"formaciones_2024.parquet"

if not molinetes_pq.exists():
    raise FileNotFoundError(f"Missing {molinetes_pq}")
if not formaciones_pq.exists():
    raise FileNotFoundError(f"Missing {formaciones_pq}")

df = pd.read_parquet(molinetes_pq)
ff = pd.read_parquet(formaciones_pq)

# Keep only subway lines (drop Premetro 'LineaP' for now if desired)
DROP_PREMETRO = True
if DROP_PREMETRO:
    ff = ff[ff["line"].str.upper() != "LINEAP"]

# ---------- Prep monthly demand ----------
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
dem_month = (
    df[df["year"] == 2024]
      .groupby(["line", "year", "month"], as_index=False)["passengers"].sum()
)

# ---------- Prep monthly formations ----------
ff["date"] = pd.to_datetime(ff["date"], errors="coerce")
ff["year"] = ff["date"].dt.year
ff["month"] = ff["date"].dt.month
frm_month = (
    ff[ff["year"] == 2024]
      .groupby(["line", "year", "month"], as_index=False)["trains"].sum()
)

# ---------- Merge + KPI ----------
kpi = dem_month.merge(frm_month, on=["line","year","month"], how="inner")
kpi = kpi[kpi["trains"] > 0].copy()
kpi["pax_per_train"] = kpi["passengers"] / kpi["trains"]

# ---------- Chart 1: By line (all 2024) ----------
by_line = (
    kpi.groupby("line", as_index=False)[["passengers","trains","pax_per_train"]]
       .sum(numeric_only=True)
)
# Recompute pax_per_train after sum (to avoid summing ratios)
by_line["pax_per_train"] = by_line["passengers"] / by_line["trains"]
by_line = by_line.sort_values("pax_per_train", ascending=False)

plt.figure(figsize=(10,6))
plt.bar(by_line["line"], by_line["pax_per_train"])
plt.title("Passengers per dispatched train — 2024 (by line)")
plt.xlabel("Line")
plt.ylabel("Passengers / train")
plt.xticks(rotation=0)
plt.tight_layout()
out1 = SCREENSHOTS/"week7_kpi_pax_per_train_by_line.png"
plt.savefig(out1, dpi=120, bbox_inches="tight")
plt.close()
print("Saved →", out1)

# ---------- Chart 2: Monthly trend (sum across lines) ----------
monthly_total = (
    kpi.groupby(["year","month"], as_index=False)[["passengers","trains"]]
       .sum(numeric_only=True)
)
monthly_total["pax_per_train"] = monthly_total["passengers"] / monthly_total["trains"]
monthly_total["ym"] = pd.to_datetime(
    monthly_total["year"].astype(str) + "-" + monthly_total["month"].astype(str) + "-01"
)

plt.figure(figsize=(10,6))
plt.plot(monthly_total["ym"], monthly_total["pax_per_train"], marker="o")
plt.title("Passengers per dispatched train — 2024 (monthly)")
plt.xlabel("Month")
plt.ylabel("Passengers / train")
plt.grid(True, alpha=0.3)
plt.tight_layout()
out2 = SCREENSHOTS/"week7_kpi_pax_per_train_trend.png"
plt.savefig(out2, dpi=120, bbox_inches="tight")
plt.close()
print("Saved →", out2)
