"""
generate_stations_geo.py
-------------------------
Genera data/processed/stations_geo.csv con columnas:
station, line, lat, lon
"""

from pathlib import Path
import pandas as pd

def find_root(max_up=6):
    cur = Path.cwd()
    for i in range(max_up + 1):
        cand = cur if i == 0 else cur.parents[i - 1]
        if (cand / "data").exists() and (cand / "app").exists():
            return cand
    return Path.cwd()

ROOT = find_root()
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

# Candidatos de archivo base (incluye tu carpeta 'estaciones/')
candidates = [
    RAW / "bocas_de_subte.csv",
    RAW / "bocas" / "bocas_de_subte.csv",
    RAW / "bocas_de_subte.geo.csv",
    RAW / "estaciones" / "bocas_de_subte.csv",
]

source_file = next((c for c in candidates if c.exists()), None)
if source_file is None:
    raise FileNotFoundError(
        "No se encontró archivo base. Colocar 'bocas_de_subte.csv' en:\n"
        + "\n".join(str(c) for c in candidates)
    )

print(f"Usando archivo base: {source_file}")

# Carga flexible
try:
    df = pd.read_csv(source_file)
except Exception:
    df = pd.read_csv(source_file, sep=";")
df.columns = [c.strip().lower() for c in df.columns]

# Helpers de mapeo
def pick(cols, names):
    for n in names:
        if n in cols:
            return n
    return None

cols = set(df.columns)
c_station = pick(cols, ["station", "estacion", "nombre", "nombre_estacion"])
c_line    = pick(cols, ["line", "linea", "linea_id", "linea_nombre"])
c_lat     = pick(cols, ["lat", "latitude", "y", "latitud"])
c_lon     = pick(cols, ["lon", "lng", "long", "longitud", "longitud_wgs84", "x"])

if not all([c_station, c_lat, c_lon]):
    raise ValueError(f"No se detectaron columnas mínimas. Vistas: {sorted(df.columns)}")

# Normalizadores
def norm_text(s: pd.Series) -> pd.Series:
    return (s.astype("string")
             .str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("ascii")
             .str.strip().str.replace(r"\s+", " ", regex=True))

def norm_line(s: pd.Series) -> pd.Series:
    s2 = norm_text(s)
    # uniformar: sin espacios y con 'Linea' capitalizado
    s2 = (s2.str.replace(r"\s+", "", regex=True)
              .str.replace("linea", "Linea", case=False))
    return s2

# Construcción con/fallback de 'line'
out = pd.DataFrame({
    "station": norm_text(df[c_station]).str.title(),
    "lat": pd.to_numeric(df[c_lat], errors="coerce"),
    "lon": pd.to_numeric(df[c_lon], errors="coerce"),
})

if c_line:
    out["line"] = norm_line(df[c_line])
else:
    # ⚠️ Fallback: si no hay columna de línea en el CSV de bocas,
    # intentamos inferirla a partir del nombre de estación (muy débil).
    # Recomendado: aportar una columna de línea en el CSV base.
    print("⚠️ No se encontró columna de línea. Intento de inferencia básica (puede ser inexacta).")
    # Regla tonta: si el nombre contiene patrones (raro). Dejar vacío si no se puede inferir.
    out["line"] = "Linea?"

# Limpieza y dedupe
out = out.dropna(subset=["lat", "lon"])
out = out[["station", "line", "lat", "lon"]].copy()
out = out.drop_duplicates(subset=["line", "station"], keep="first")

# Guardar
dst = PROCESSED / "stations_geo.csv"
out.to_csv(dst, index=False)
print(f"Archivo generado → {dst.resolve()}")
print(f"Total filas: {len(out)}")
print(out.head(10))
