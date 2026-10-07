"""
Genera los notebooks de notebooks/ (no editarlos a mano: cambiar este script y volver a correrlo).

Uso:
    python scripts/gen_notebooks.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLAB = "https://colab.research.google.com/github/santiagoriverti/infraestuctura_argentina/blob/main/notebooks/{}"


def md(texto: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": texto.strip("\n").splitlines(keepends=True)}


def code(texto: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": texto.strip("\n").splitlines(keepends=True)}


def guardar(nombre: str, celdas: list) -> None:
    nb = {"cells": celdas, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                        "language_info": {"name": "python"}, "colab": {"provenance": []}},
          "nbformat": 4, "nbformat_minor": 5}
    for i, c in enumerate(nb["cells"]):
        c["id"] = f"c{i:02d}"
    ruta = ROOT / "notebooks" / nombre
    ruta.parent.mkdir(exist_ok=True)
    ruta.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"  {ruta.relative_to(ROOT)}")


SETUP = r'''
# SETUP: en Colab clona (o actualiza) el repo; localmente usa la carpeta del repo
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/santiagoriverti/infraestuctura_argentina.git"
EN_COLAB = "google.colab" in sys.modules
if EN_COLAB:
    BASE = Path("/content/infraestuctura_argentina")
    if (BASE / ".git").exists():
        subprocess.run(["git", "-C", str(BASE), "fetch", "-q", "origin"], check=True)
        subprocess.run(["git", "-C", str(BASE), "reset", "-q", "--hard", "origin/main"], check=True)
    else:
        subprocess.run(["git", "clone", "-q", "--depth", "1", REPO_URL, str(BASE)], check=True)
else:
    BASE = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()

sys.path.insert(0, str(BASE))
for m in [m for m in sys.modules if m == "src" or m.startswith("src.")]:
    del sys.modules[m]  # Colab reutiliza la sesion: forzar la version nueva del codigo

import pandas as pd
from IPython.display import Image, display

import src.graficos as graf
import src.iip_nacional as iip

pd.set_option("display.width", 160)
commit = subprocess.run(["git", "-C", str(BASE), "log", "-1", "--format=%h %cs"], capture_output=True, text=True).stdout.strip()
print("Repo:", BASE, "| commit", commit)
'''


def nb_nacional():
    celdas = [
        md(f"""
# Índice de Infraestructura Productiva (IIP) — módulo nacional

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({COLAB.format("01_iip_nacional.ipynb")})

Índice trimestral del estado de la infraestructura que usan las empresas para producir e invertir, en
cinco pilares: **energía, transporte y logística, telecomunicaciones, agua y saneamiento, e inversión en
infraestructura**. Proyecto INECO-UADE.

- **Lectura:** 0 = lo típico del período; +1 = una desviación (robusta) mejor que lo típico.
- **Telecomunicaciones** se mide como **brecha contra los países de comparación** (si no, la velocidad
  o la fibra suben solas con la tecnología). Las variables de **uso** (carga) se relativizan al EMAE.
- Los **pesos** y la **referencia de los pares** se cambian en la celda de parámetros.

**Uso:** Entorno de ejecución → Ejecutar todas. Al final se descarga `iip_nacional.zip` (Excel + gráficos).
Metodología completa: `CONTEXTO.md` del repo.
"""),
        code(SETUP),
        md("## Parámetros\nPesos iguales por defecto. Para cambiar el peso de un pilar o de una variable, editar acá y volver a correr todo."),
        code('''
PARAMETROS = dict(
    inicio="2016-01-01",                  # primer trimestre de la ventana
    pesos_pilares={"energia": 1, "transporte": 1, "telecom": 1, "agua": 1, "inversion": 1},
    pesos_variables={},                   # ej. {"cemento": 0.5}; las que no figuran pesan 1
    pares=["BRA", "CHL", "URY", "MEX", "COL", "PER", "AUS", "CAN", "ESP", "USA"],
    referencia="mediana",                 # "mediana" de los pares o "mejor" (la frontera del grupo)
    max_arrastre=4,                       # trimestres que se puede arrastrar el último dato
)
'''),
        md("## Cálculo"),
        code('''
res = iip.calcular(BASE, **PARAMETROS)
print(iip.resumen(res))
print()
display(res["por_gobierno"].round(2))
'''),
        md("""
### Sensibilidad
El mismo índice con variantes razonables de la metodología (sin cada pilar, referencia = el mejor de los
pares, otra ventana, otro tope). Una conclusión es firme si se mantiene en todas las variantes.
"""),
        code('''
sens, series_sens = iip.sensibilidad(BASE, **PARAMETROS)
display(sens.round(2))
print(f"IIP {sens.loc[0, 'ultimo']}: {sens.loc[0, 'IIP']:+.2f} (rango {sens['IIP'].min():+.2f} a {sens['IIP'].max():+.2f}); "
      f"cambio en 12 meses {sens.loc[0, 'cambio_12m']:+.2f} (rango {sens['cambio_12m'].min():+.2f} a {sens['cambio_12m'].max():+.2f})")
'''),
        md("### Variables, transformaciones y normalización\n`mediana` y `escala` (IQR / 1,349) se calculan sobre los datos propios de la ventana; `arrastrados` = trimestres con el último dato repetido o con la referencia de los pares arrastrada."),
        code('''
met = res["metodologia"].copy()
for c in ["desde", "hasta"]:
    met[c] = [iip.etiqueta(t) if pd.notna(t) else "" for t in met[c]]
display(met[["pilar", "nombre", "unidad", "transformacion", "fuente", "desde", "hasta", "mediana", "escala", "arrastrados", "peso"]].round(3))
'''),
        md("## Gráficos"),
        code('''
SALIDA = BASE / "output"
pngs = graf.todos(res, SALIDA)
for p in pngs:
    display(Image(filename=str(p)))
'''),
        md("## Exportar\nExcel con el índice, los pilares, las variables (valor y z), los arrastres, Telecom vs pares y la metodología; más los gráficos, en un ZIP."),
        code('''
import zipfile

xlsx = SALIDA / "iip_nacional.xlsx"
iip.exportar_excel(res, xlsx, sens)
zip_path = SALIDA / "iip_nacional.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for p in [xlsx, *pngs]:
        z.write(p, p.name)
print("ZIP:", zip_path, "|", ", ".join(p.name for p in [xlsx, *pngs]))
if EN_COLAB:
    from google.colab import files
    files.download(str(zip_path))
'''),
    ]
    guardar("01_iip_nacional.ipynb", celdas)


if __name__ == "__main__":
    nb_nacional()
