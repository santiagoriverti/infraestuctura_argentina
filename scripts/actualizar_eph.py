"""
Cobertura de servicios de red de los hogares urbanos (EPH, INDEC), trimestral desde 2017-T1:
agua de red, desague a cloaca y gas de red para cocinar. Total de los 31 aglomerados y por
aglomerado (para el modulo provincial).

Uso:
    python scripts/actualizar_eph.py [--zips CARPETA]

Busca los zips del INDEC (EPH_usu_<T>_Trim_<AAAA>_txt.zip) en data/raw/eph_zips/ (ignorada por
git) y en --zips (por defecto ../analisis_EPH/data/raw, el repo hermano que ya los baja). Los que
falten se bajan del INDEC a data/raw/eph_zips/.

Base de hogares, ponderada por PONDERA:
- hogares_agua_red: IV7 = 1 (el agua es de red publica / agua corriente)
- hogares_cloaca:   IV11 = 1 (desague del bano a red publica / cloaca; sin bano = no)
- hogares_gas_red:  II8 = 1 (combustible para cocinar: gas de red)

Salida: data/raw/eph_servicios.csv  codigo, nivel (total|aglomerado), aglomerado, fecha, valor (%), hogares
"""

import argparse
import re
import zipfile
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "raw" / "eph_zips"
SALIDA = ROOT / "data" / "raw" / "eph_servicios.csv"
ZIPS_HERMANO = ROOT.parent / "analisis_EPH" / "data" / "raw"
URL = "https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/"
PRIMER_ANIO = 2017

INDICADORES = {  # codigo -> (variable, valor que cuenta)
    "hogares_agua_red": ("IV7", 1),
    "hogares_cloaca": ("IV11", 1),
    "hogares_gas_red": ("II8", 1),
}


def nombre_zip(anio: int, trim: int) -> str:
    return f"EPH_usu_{trim}_Trim_{anio}_txt.zip"


def nombre_indec(anio: int, trim: int) -> str:
    # el INDEC publico T1-2017 con otro nombre
    return "EPH_usu_1er_Trim_2017_txt.zip" if (anio, trim) == (2017, 1) else nombre_zip(anio, trim)


def buscar_o_bajar(anio: int, trim: int, carpetas) -> Path | None:
    for c in carpetas:
        p = c / nombre_zip(anio, trim)
        if p.exists():
            return p
    r = requests.get(URL + nombre_indec(anio, trim), timeout=180)
    if not (r.ok and "zip" in r.headers.get("Content-Type", "")):
        return None  # el sitio responde una pagina HTML cuando el trimestre no existe
    CACHE.mkdir(parents=True, exist_ok=True)
    destino = CACHE / nombre_zip(anio, trim)
    destino.write_bytes(r.content)
    print(f"  bajado {destino.name} ({len(r.content) / 1e6:.1f} MB)")
    return destino


def leer_hogares(ruta: Path) -> pd.DataFrame:
    with zipfile.ZipFile(ruta) as z:
        miembro = next(n for n in z.namelist() if re.search(r"hogar", n, re.IGNORECASE) and n.lower().endswith(".txt"))
        with z.open(miembro) as f:
            h = pd.read_csv(f, sep=";", low_memory=False, encoding="latin-1")
    h.columns = [c.strip().upper() for c in h.columns]
    return h


def indicadores(h: pd.DataFrame) -> pd.DataFrame:
    """% de hogares (ponderado) por indicador, total y por aglomerado."""
    w = pd.to_numeric(h["PONDERA"], errors="coerce").fillna(0)
    filas = []
    grupos = [("total", None, h.index)] + [("aglomerado", a, g.index) for a, g in h.groupby("AGLOMERADO")]
    for codigo, (var, val) in INDICADORES.items():
        x = (pd.to_numeric(h[var], errors="coerce") == val).astype(float)
        for nivel, aglo, idx in grupos:
            filas.append({"codigo": codigo, "nivel": nivel, "aglomerado": aglo,
                          "valor": 100 * (x[idx] * w[idx]).sum() / w[idx].sum(), "hogares": len(idx)})
    return pd.DataFrame(filas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zips", type=Path, default=ZIPS_HERMANO)
    args = ap.parse_args()
    carpetas = [CACHE] + ([args.zips] if args.zips.exists() else [])
    print(f"Zips de la EPH en: {', '.join(str(c) for c in carpetas)}")

    partes, anio, faltantes_seguidos = [], PRIMER_ANIO, 0
    while faltantes_seguidos < 4:  # 4 trimestres seguidos sin publicar = fin de la serie
        for trim in range(1, 5):
            ruta = buscar_o_bajar(anio, trim, carpetas)
            if ruta is None:
                faltantes_seguidos += 1
                continue
            faltantes_seguidos = 0
            df = indicadores(leer_hogares(ruta))
            df["fecha"] = f"{anio}-{3 * (trim - 1) + 1:02d}-01"
            partes.append(df)
            tot = df[df["nivel"] == "total"].set_index("codigo")["valor"]
            print(f"  {anio}T{trim}: agua {tot['hogares_agua_red']:.1f}% | cloaca {tot['hogares_cloaca']:.1f}% | "
                  f"gas {tot['hogares_gas_red']:.1f}%")
        anio += 1

    out = pd.concat(partes, ignore_index=True)
    out["aglomerado"] = out["aglomerado"].astype("Int64")
    out = out[["codigo", "nivel", "aglomerado", "fecha", "valor", "hogares"]]
    out.sort_values(["codigo", "nivel", "aglomerado", "fecha"]).to_csv(SALIDA, index=False, float_format="%.4f")
    print(f"\n{SALIDA.relative_to(ROOT)}: {len(out)} filas, {out['fecha'].min()} a {out['fecha'].max()}")


if __name__ == "__main__":
    main()
