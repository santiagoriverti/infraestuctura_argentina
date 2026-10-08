"""
Compara el ZIP que descarga Colab (notebook 01) con la corrida local, hoja por hoja.

Uso:
    python scripts/correr_nacional.py                 # corrida local con el mismo commit que Colab
    python scripts/comparar_zip.py RUTA/iip_nacional.zip

Compara cada hoja de iip_nacional.xlsx (forma, columnas, textos y numeros; los vacios tienen que
coincidir) y que el ZIP traiga los mismos graficos que output/. Sale con codigo 1 si algo difiere.
"""

import io
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SALIDA = ROOT / "output"
EXCEL = "iip_nacional.xlsx"
TOLERANCIA = 1e-9


def comparar_hoja(a: pd.DataFrame, b: pd.DataFrame) -> str:
    if a.shape != b.shape or list(a.columns) != list(b.columns):
        return f"DIFIERE: forma {a.shape} vs {b.shape} o columnas distintas"
    num = [c for c in a.columns
           if pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c])]
    x, y = a[num].astype(float), b[num].astype(float)
    vacios = int((x.isna() != y.isna()).sum().sum())
    d = (x - y).abs().to_numpy()
    dif = float(np.nanmax(d)) if np.isfinite(d).any() else 0.0
    otras = [c for c in a.columns if c not in num]
    textos = int((a[otras].astype(str) != b[otras].astype(str)).sum().sum())
    detalle = f"dif. numerica max {dif:.1e} | vacios distintos {vacios} | textos distintos {textos}"
    return ("OK      " if dif <= TOLERANCIA and vacios == 0 and textos == 0 else "DIFIERE ") + detalle


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    ruta_zip = Path(sys.argv[1])
    local_xlsx = SALIDA / EXCEL
    if not local_xlsx.exists():
        sys.exit(f"Falta {local_xlsx.relative_to(ROOT)}: correr antes python scripts/correr_nacional.py")

    with zipfile.ZipFile(ruta_zip) as z:
        en_zip = set(z.namelist())
        colab = pd.read_excel(io.BytesIO(z.read(EXCEL)), sheet_name=None)
    local = pd.read_excel(local_xlsx, sheet_name=None)

    ok = True
    print(f"Colab: {ruta_zip}\nLocal: {local_xlsx.relative_to(ROOT)}\n")
    for hoja in list(local) + [h for h in colab if h not in local]:
        if hoja not in colab or hoja not in local:
            print(f"  {hoja:<18} FALTA en {'Colab' if hoja not in colab else 'local'}")
            ok = False
            continue
        res = comparar_hoja(colab[hoja], local[hoja])
        ok &= res.startswith("OK")
        print(f"  {hoja:<18} {res}")

    pngs_local = {p.name for p in SALIDA.glob("iip_g*.png")}
    pngs_zip = {n for n in en_zip if n.endswith(".png")}
    if pngs_local != pngs_zip:
        ok = False
        print(f"\n  Graficos distintos: solo en Colab {sorted(pngs_zip - pngs_local)}, "
              f"solo en local {sorted(pngs_local - pngs_zip)}")
    else:
        print(f"\n  Graficos: los mismos {len(pngs_zip)} en ambos")

    print("\nRESULTADO:", "IDENTICO" if ok else "HAY DIFERENCIAS")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
