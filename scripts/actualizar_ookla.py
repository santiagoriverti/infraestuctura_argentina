"""
Velocidad MEDIDA de internet fijo (Ookla Open Data) por pais y por provincia argentina, trimestral
desde 2019-T1. Sirve para medir la brecha de Argentina contra los paises de comparacion (modulo A y
C) y la velocidad por provincia (modulo B). ENACOM solo publica la velocidad CONTRATADA y solo de
Argentina.

Uso:
    python scripts/actualizar_ookla.py            # procesa los trimestres que falten
    python scripts/actualizar_ookla.py --forzar   # reprocesa todo

Fuente: Ookla Speedtest Open Data (s3://ookla-open-data, acceso anonimo), teselas de zoom 16
(~600 m) con promedio de velocidad, cantidad de tests y de dispositivos. Licencia CC BY-NC-SA 4.0
(uso no comercial, citar "Speedtest by Ookla Global Fixed and Mobile Network Performance Maps").

Metodo: cada tesela se ubica por el centroide de su quadkey; pais por poligono de Natural Earth
1:50m y provincia por poligono del IGN (simplificados a ~0,005 grados y guardados en
data/reference/geo/). Velocidad del pais/provincia = promedio de las teselas ponderado por tests
(criterio de los tutoriales de Ookla).

Cada trimestre se baja una sola vez (~150 MB de columnas) y queda en data/raw/ookla/; al final se
arma data/raw/ookla_fijo.csv:
    nivel (pais|provincia), id (iso3 | codigo INDEC), nombre, fecha, mbps_bajada, mbps_subida,
    latencia_ms, tests, dispositivos, teselas
"""

import io
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.fs as pafs
import pyarrow.parquet as pq
import requests
from matplotlib.path import Path as MplPath

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "data" / "reference" / "geo"
CACHE = ROOT / "data" / "raw" / "ookla"
SALIDA = ROOT / "data" / "raw" / "ookla_fijo.csv"
PROVINCIAS = ROOT / "data" / "reference" / "provincias.csv"

NE_PAISES = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson"
IGN_PROVINCIAS = ("https://wms.ign.gob.ar/geoserver/ign/ows?service=WFS&version=1.1.0&request=GetFeature"
                  "&typeName=ign:provincia&outputFormat=application/json")
OOKLA = "ookla-open-data/parquet/performance/type=fixed/year={a}/quarter={q}/{a}-{m:02d}-01_performance_fixed_tiles.parquet"
PRIMER_TRIMESTRE = (2019, 1)
PAISES = ["ARG", "BRA", "CHL", "URY", "MEX", "COL", "PER", "AUS", "CAN", "ESP", "USA"]
COLUMNAS = ["quadkey", "avg_d_kbps", "avg_u_kbps", "avg_lat_ms", "tests", "devices"]
GRILLA = 0.005  # grados: simplificacion de los poligonos (la tesela mide ~0,0055 grados)


# ---------------------------------------------------------------------------------------------
# Poligonos (se arman una vez y quedan versionados)
# ---------------------------------------------------------------------------------------------

def _simplificar_anillo(anillo):
    pts = np.round(np.asarray(anillo, dtype=float) / GRILLA) * GRILLA
    keep = np.ones(len(pts), dtype=bool)
    keep[1:] = np.any(np.diff(pts, axis=0) != 0, axis=1)
    pts = pts[keep]
    return pts.round(4).tolist() if len(pts) >= 4 else None


def _simplificar(geom, lat_min=-60.0):
    """MultiPolygon/Polygon -> lista de poligonos [exterior, *agujeros] simplificados.
    Descarta lo que queda al sur de lat_min (sector antartico de Tierra del Fuego)."""
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    salida = []
    for poly in polys:
        if max(p[1] for p in poly[0]) < lat_min:
            continue
        anillos = [_simplificar_anillo(a) for a in poly]
        if anillos[0] is not None:
            salida.append([a for a in anillos if a is not None])
    return {"type": "MultiPolygon", "coordinates": salida}


def preparar_geo():
    GEO.mkdir(parents=True, exist_ok=True)
    destino = GEO / "paises.geojson"
    if not destino.exists():
        js = requests.get(NE_PAISES, timeout=180).json()
        feats = [{"type": "Feature", "properties": {"id": f["properties"]["ADM0_A3"], "nombre": f["properties"]["NAME"]},
                  "geometry": _simplificar(f["geometry"])}
                 for f in js["features"] if f["properties"]["ADM0_A3"] in PAISES]
        destino.write_text(json.dumps({"type": "FeatureCollection", "features": feats}), encoding="utf-8")
        print(f"  geo: {destino.relative_to(ROOT)} ({len(feats)} paises)")
    destino = GEO / "provincias.geojson"
    if not destino.exists():
        nombres = pd.read_csv(PROVINCIAS, dtype=str).set_index("codigo_indec")["provincia"]
        js = requests.get(IGN_PROVINCIAS, timeout=600).json()
        feats = [{"type": "Feature", "properties": {"id": f["properties"]["in1"], "nombre": nombres[f["properties"]["in1"]]},
                  "geometry": _simplificar(f["geometry"])}
                 for f in js["features"]]
        destino.write_text(json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False), encoding="utf-8")
        print(f"  geo: {destino.relative_to(ROOT)} ({len(feats)} provincias)")


def cargar_geo(nombre: str):
    """-> lista de (id, nombre, [(path_exterior, [paths_agujeros]), ...], bbox)"""
    js = json.loads((GEO / nombre).read_text(encoding="utf-8"))
    out = []
    for f in js["features"]:
        polys = [(MplPath(p[0]), [MplPath(h) for h in p[1:]]) for p in f["geometry"]["coordinates"]]
        todos = np.vstack([np.asarray(p[0]) for p in f["geometry"]["coordinates"]])
        bbox = (*todos.min(axis=0), *todos.max(axis=0))
        out.append((f["properties"]["id"], f["properties"]["nombre"], polys, bbox))
    return out


def asignar(lon, lat, regiones):
    """Para cada punto devuelve el indice de la region que lo contiene (-1 si ninguna)."""
    idx = np.full(len(lon), -1, dtype=int)
    for k, (_, _, polys, (x0, y0, x1, y1)) in enumerate(regiones):
        cand = np.flatnonzero((idx < 0) & (lon >= x0) & (lon <= x1) & (lat >= y0) & (lat <= y1))
        if len(cand) == 0:
            continue
        pts = np.column_stack([lon[cand], lat[cand]])
        dentro = np.zeros(len(cand), dtype=bool)
        for ext, agujeros in polys:
            m = ext.contains_points(pts)
            for h in agujeros:
                m &= ~h.contains_points(pts)
            dentro |= m
        idx[cand[dentro]] = k
    return idx


# ---------------------------------------------------------------------------------------------
# Ookla
# ---------------------------------------------------------------------------------------------

def centroides(quadkeys: np.ndarray):
    """quadkey (zoom 16) -> lon, lat del centro de la tesela."""
    d = np.frombuffer(quadkeys.astype("S16").tobytes(), dtype=np.uint8).reshape(-1, 16).astype(np.int64) - 48
    pesos = 1 << np.arange(15, -1, -1)
    x = ((d & 1) * pesos).sum(axis=1)
    y = (((d >> 1) & 1) * pesos).sum(axis=1)
    n = 2 ** 16
    lon = (x + 0.5) / n * 360.0 - 180.0
    lat = np.degrees(np.arctan(np.sinh(math.pi * (1 - 2 * (y + 0.5) / n))))
    return lon, lat


def agregar(df: pd.DataFrame, idx: np.ndarray, regiones, nivel: str, fecha: str) -> pd.DataFrame:
    df = df.assign(k=idx)
    df = df[df["k"] >= 0]
    filas = []
    for k, g in df.groupby("k"):
        w = g["tests"]
        filas.append({
            "nivel": nivel, "id": regiones[k][0], "nombre": regiones[k][1], "fecha": fecha,
            "mbps_bajada": (g["avg_d_kbps"] * w).sum() / w.sum() / 1000,
            "mbps_subida": (g["avg_u_kbps"] * w).sum() / w.sum() / 1000,
            "latencia_ms": (g["avg_lat_ms"] * w).sum() / w.sum(),
            "tests": int(w.sum()), "dispositivos": int(g["devices"].sum()), "teselas": len(g),
        })
    return pd.DataFrame(filas)


def procesar_trimestre(s3, anio: int, trim: int, paises, provincias) -> pd.DataFrame:
    ruta = OOKLA.format(a=anio, q=trim, m=3 * (trim - 1) + 1)
    tabla = pq.read_table(ruta, columns=COLUMNAS, filesystem=s3)
    df = tabla.to_pandas()
    lon, lat = centroides(df["quadkey"].to_numpy())
    df = df.drop(columns="quadkey")
    fecha = f"{anio}-{3 * (trim - 1) + 1:02d}-01"
    idx_pais = asignar(lon, lat, paises)
    res = [agregar(df, idx_pais, paises, "pais", fecha)]
    k_arg = [p[0] for p in paises].index("ARG")
    en_arg = idx_pais == k_arg
    idx_prov = np.full(len(df), -1, dtype=int)
    idx_prov[en_arg] = asignar(lon[en_arg], lat[en_arg], provincias)
    res.append(agregar(df, idx_prov, provincias, "provincia", fecha))
    return pd.concat(res, ignore_index=True)


def trimestres_disponibles(s3):
    out = []
    a, q = PRIMER_TRIMESTRE
    while True:
        ruta = OOKLA.format(a=a, q=q, m=3 * (q - 1) + 1)
        if s3.get_file_info(ruta).type == pafs.FileType.NotFound:
            break
        out.append((a, q))
        a, q = (a, q + 1) if q < 4 else (a + 1, 1)
    return out


def main():
    forzar = "--forzar" in sys.argv
    preparar_geo()
    paises, provincias = cargar_geo("paises.geojson"), cargar_geo("provincias.geojson")
    s3 = pafs.S3FileSystem(anonymous=True, region="us-west-2")
    CACHE.mkdir(parents=True, exist_ok=True)
    disponibles = trimestres_disponibles(s3)
    print(f"Ookla: {len(disponibles)} trimestres publicados ({disponibles[0]} a {disponibles[-1]})")
    for anio, trim in disponibles:
        archivo = CACHE / f"fijo_{anio}T{trim}.csv"
        if archivo.exists() and not forzar:
            continue
        res = procesar_trimestre(s3, anio, trim, paises, provincias)
        res.to_csv(archivo, index=False, float_format="%.4f")
        arg = res[(res["nivel"] == "pais") & (res["id"] == "ARG")]
        print(f"  {anio}T{trim}: {len(res)} filas | ARG {arg['mbps_bajada'].iloc[0]:.1f} Mbps, "
              f"{res[res['nivel'] == 'provincia']['id'].nunique()} provincias", flush=True)
    todo = pd.concat([pd.read_csv(f, dtype={"id": str}) for f in sorted(CACHE.glob("fijo_*.csv"))], ignore_index=True)
    todo.sort_values(["nivel", "id", "fecha"]).to_csv(SALIDA, index=False, float_format="%.4f")
    print(f"\n{SALIDA.relative_to(ROOT)}: {len(todo)} filas, {todo['fecha'].min()} a {todo['fecha'].max()}")


if __name__ == "__main__":
    main()
