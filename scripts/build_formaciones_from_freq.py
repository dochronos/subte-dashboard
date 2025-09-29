# build_formaciones_from_freq.py
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
PROCESSED = ROOT / "data" / "processed"

src = PROCESSED / "freq_from_form_2024.csv"
dst_csv = PROCESSED / "formaciones_2024.csv"
dst_pq  = PROCESSED / "formaciones_2024.parquet"

if not src.exists():
    raise FileNotFoundError(f"No encontrado: {src}")

df = pd.read_csv(src)
df.columns = [c.strip().lower() for c in df.columns]
cols = set(df.columns)

# Detectar el esquema year_month + line + dispatched_trains
if {"year_month", "line", "dispatched_trains"}.issubset(cols):
    out = df[["year_month", "line", "dispatched_trains"]].copy()
    # date = primer día del mes
    out["date"] = pd.to_datetime(out["year_month"] + "-01", format="%Y-%m-%d", errors="coerce").dt.date
    out = out.drop(columns=["year_month"])
    out = out.rename(columns={"dispatched_trains": "trains"})
else:
    # Intento genérico por si cambian los nombres
    def pick(names):
        for n in names:
            if n in cols:
                return n
        return None
    ym = pick(["year_month","ym","period","month"])
    ln = pick(["line","linea","linea_nombre","linea_id"])
    tr = pick(["dispatched_trains","trains","formaciones","trenes","despachos","services","freq","frequency"])
    if not all([ym, ln, tr]):
        raise ValueError(
            f"No pude mapear columnas en {src}.\n"
            f"Veo: {sorted(df.columns)}\n"
            f"Necesito algo tipo: year_month + line + dispatched_trains (o equivalentes)."
        )
    out = df[[ym, ln, tr]].copy()
    out["date"] = pd.to_datetime(out[ym].astype(str) + "-01", errors="coerce").dt.date
    out = out.drop(columns=[ym])
    out = out.rename(columns={tr:"trains", ln:"line"})

# Normalizar line → "LineaX"
out["line"] = (
    out["line"].astype("string").str.strip()
      .apply(lambda v: f"Linea{v.upper()}" if isinstance(v,str) and len(v)==1 and v.isalpha() else v)
      .str.replace("linea","Linea", case=False).str.replace("Linea ","Linea").str.replace(" ","")
)

# Tipos y filtro 2024
out["trains"] = pd.to_numeric(out["trains"], errors="coerce")
out = out.dropna(subset=["date","line","trains"])
out = out[(out["date"] >= pd.to_datetime("2024-01-01").date()) &
          (out["date"] <  pd.to_datetime("2025-01-01").date())]

# Agregar por día-línea (en nuestro caso día=primer día del mes → agrupa mensual)
out = out.groupby(["date","line"], as_index=False)["trains"].sum()

if out.empty:
    raise RuntimeError("El derivado quedó vacío para 2024. Revisar columnas/fechas del fuente.")

# Guardar
dst_csv.parent.mkdir(parents=True, exist_ok=True)
out.to_csv(dst_csv, index=False)
try:
    out.to_parquet(dst_pq, index=False)
except Exception:
    pass

print("Guardado:")
print(" -", dst_csv)
if dst_pq.exists():
    print(" -", dst_pq)
print("\nSample:")
print(out.head(12))
