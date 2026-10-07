"""
Descarga las series del catalogo (data/reference/catalogo_variables.csv) y las guarda en formato
largo en data/raw/ (una fila por dato, valores crudos sin transformar):

- nacional.csv       codigo, fecha, valor            (modulos nacional y auxiliar; mezcla frecuencias)
- provincial.csv     codigo, provincia, fecha, valor
- internacional.csv  codigo, iso3, pais, fecha, valor   (anual: fecha = 1 de enero del anio)
- enacom/*.csv       archivos de ENACOM tal como se publican (respaldo de la fuente)

Uso:
    python scripts/actualizar_datos.py

Solo se bajan las filas del catalogo con api = datos_gob, imig, enacom, wdi u oecd_bb. Las de
api = ookla y eph tienen su propio script (actualizar_ookla.py, actualizar_eph.py) y las de
api = pendiente son variables candidatas que todavia no tienen descarga automatica.

Fuentes (todas publicas, sin clave):
- datos.gob.ar (API Series de Tiempo): demanda y potencia electrica (CAMMESA via SSPM), produccion
  de gas, Estadisticas de Servicios Publicos del INDEC (carga ferroviaria y aerea, peajes, telefonia
  movil), ISAC, cemento, IPC, PIB nominal y EMAE. Cada serie se pide sola: si se piden juntas
  series de distinta frecuencia, la API las agrega a la menor (p. ej. todo a anual).
- datos.gob.ar (CSV IMIG mensual 2016+, dataset 452.3): gasto de capital del Sector Publico
  Nacional por finalidad (Nacion + transferencias de capital a provincias), en millones de $.
- ENACOM (indicadores.enacom.gob.ar/Files/DatosAbiertos): internet fijo trimestral 2014+,
  total pais y por provincia (penetracion, velocidad media de bajada, accesos por tecnologia).
- Banco Mundial (API WDI v2): indicadores anuales 2000+ de Argentina, pares de la region,
  referencias (Australia, Canada, Espana, EEUU) y agregados (America Latina y el Caribe, OCDE).
- OCDE (SDMX, Broadband and telecom database): suscripciones de banda ancha fija por tecnologia,
  semestral (Q2 y Q4). Cubre a los pares miembros o adherentes (no a Argentina ni Uruguay).

Si una fuente falla se conservan los datos que ya estaban para esos codigos (aviso por pantalla),
asi una caida puntual de una API no borra datos.
"""

import io
import tempfile
from functools import lru_cache
from pathlib import Path

import certifi
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CATALOGO = ROOT / "data" / "reference" / "catalogo_variables.csv"
RAW = ROOT / "data" / "raw"
OUT = {
    "nacional": RAW / "nacional.csv",
    "provincial": RAW / "provincial.csv",
    "internacional": RAW / "internacional.csv",
}
CLAVES = {  # columnas que identifican una fila (sin el valor)
    "nacional": ["codigo", "fecha"],
    "provincial": ["codigo", "provincia", "fecha"],
    "internacional": ["codigo", "iso3", "fecha"],
}

DATOS_GOB = "https://apis.datos.gob.ar/series/api/series/"
IMIG_CSV = "https://infra.datos.gob.ar/catalog/sspm/dataset/452/distribution/452.3/download/imig-mensual.csv"
ENACOM = "https://indicadores.enacom.gob.ar/Files/DatosAbiertos/{}.csv"
# El servidor de ENACOM no envia el certificado intermedio de Sectigo: se agrega al bundle de
# certifi (la verificacion sigue completa; la raiz Sectigo R46 ya esta en certifi).
ENACOM_INTERMEDIO = ROOT / "data" / "reference" / "certs" / "sectigo_public_server_auth_ca_dv_r36.pem"
WDI = "https://api.worldbank.org/v2/country/{paises}/indicator/{indicador}"
WDI_DESDE = 2000
OECD_BB = ("https://sdmx.oecd.org/public/rest/data/OECD.STI.DEP,DSD_BB_DATABASE@DF_BB_TEL_DATABASE,/"
           "{paises}.Q.FBB.SUB.{modo}._Z.{unidad}")

# Pares de la region, referencias (paises extensos y exportadores de materias primas) y agregados
PAISES = {
    "ARG": "Argentina", "BRA": "Brasil", "CHL": "Chile", "URY": "Uruguay", "MEX": "Mexico",
    "COL": "Colombia", "PER": "Peru",
    "AUS": "Australia", "CAN": "Canada", "ESP": "Espana", "USA": "Estados Unidos",
    "LCN": "America Latina y el Caribe", "OED": "Miembros OCDE",
}


# ---------------------------------------------------------------------------------------------
# Fuentes
# ---------------------------------------------------------------------------------------------

def datos_gob(sid: str) -> pd.Series:
    r = requests.get(DATOS_GOB, params={"ids": sid, "format": "csv", "limit": 5000}, timeout=90)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    s = df.set_index("indice_tiempo").iloc[:, 0].dropna()
    s.index = pd.to_datetime(s.index).strftime("%Y-%m-%d")
    return s


@lru_cache(maxsize=None)
def imig() -> pd.DataFrame:
    r = requests.get(IMIG_CSV, timeout=120)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df["indice_tiempo"] = pd.to_datetime(df["indice_tiempo"]).dt.strftime("%Y-%m-%d")
    return df.set_index("indice_tiempo")


@lru_cache(maxsize=None)
def bundle_enacom() -> str:
    """certifi + intermedio de Sectigo, en un archivo temporal."""
    pem = Path(certifi.where()).read_text(encoding="ascii") + "\n" + ENACOM_INTERMEDIO.read_text(encoding="ascii")
    f = tempfile.NamedTemporaryFile("w", suffix=".pem", delete=False, encoding="ascii")
    f.write(pem)
    f.close()
    return f.name


@lru_cache(maxsize=None)
def enacom(archivo: str) -> pd.DataFrame:
    r = requests.get(ENACOM.format(archivo), timeout=120, verify=bundle_enacom())
    r.raise_for_status()
    destino = RAW / "enacom" / f"{archivo}.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(r.content)
    df = pd.read_csv(io.BytesIO(r.content))
    # trimestre -> primer dia del trimestre (misma convencion que datos.gob.ar)
    df["fecha"] = pd.to_datetime(dict(year=df["anio"], month=3 * (df["trimestre"] - 1) + 1, day=1)).dt.strftime("%Y-%m-%d")
    return df


def enacom_valor(df: pd.DataFrame, expr: str) -> pd.Series:
    """'col' -> la columna; 'num/den' -> 100 * num / den (participacion en %)."""
    if "/" in expr:
        num, den = expr.split("/")
        return 100 * df[num] / df[den]
    return df[expr]


def wdi(indicador: str) -> pd.DataFrame:
    url = WDI.format(paises=";".join(PAISES), indicador=indicador)
    r = requests.get(url, params={"format": "json", "per_page": 20000, "date": f"{WDI_DESDE}:2030"}, timeout=120)
    r.raise_for_status()
    js = r.json()
    if len(js) < 2 or not js[1]:
        raise ValueError(f"sin datos para {indicador}: {js[0]}")
    filas = [{"iso3": x["countryiso3code"] or x["country"]["id"], "fecha": f"{x['date']}-01-01", "valor": x["value"]}
             for x in js[1] if x["value"] is not None]
    df = pd.DataFrame(filas)
    df["pais"] = df["iso3"].map(PAISES)
    return df


def oecd_bb(id_api: str) -> pd.DataFrame:
    """'MODO.UNIDAD' (p. ej. 'FIB.PT_SB_FBB') -> datos semestrales; '2024-Q4' -> fecha 2024-10-01."""
    modo, unidad = id_api.split(".")
    paises = "+".join(p for p in PAISES if p not in ("LCN", "OED"))
    r = requests.get(OECD_BB.format(paises=paises, modo=modo, unidad=unidad),
                     params={"startPeriod": WDI_DESDE, "dimensionAtObservation": "AllDimensions"},
                     headers={"Accept": "application/vnd.sdmx.data+csv; charset=utf-8"}, timeout=180)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text)).dropna(subset=["OBS_VALUE"])
    anio, trim = df["TIME_PERIOD"].str.split("-Q", expand=True).T.values
    df = pd.DataFrame({"iso3": df["REF_AREA"].values, "valor": df["OBS_VALUE"].values,
                       "fecha": [f"{a}-{3 * (int(q) - 1) + 1:02d}-01" for a, q in zip(anio, trim)]})
    df["pais"] = df["iso3"].map(PAISES)
    return df


# ---------------------------------------------------------------------------------------------
# Descarga por fila del catalogo
# ---------------------------------------------------------------------------------------------

def descargar(fila) -> pd.DataFrame:
    api, id_api, codigo = fila.api, fila.id_api, fila.codigo
    if api == "datos_gob":
        s = datos_gob(id_api)
        df = pd.DataFrame({"fecha": s.index, "valor": s.values})
    elif api == "imig":
        base = imig()
        s = sum(base[c] for c in id_api.split("+")).dropna()
        df = pd.DataFrame({"fecha": s.index, "valor": s.values})
    elif api == "enacom":
        archivo, expr = id_api.split(":")
        base = enacom(archivo)
        df = base.assign(valor=enacom_valor(base, expr))
        df = df[["provincia", "fecha", "valor"] if "provincia" in base.columns else ["fecha", "valor"]]
    elif api == "wdi":
        df = wdi(id_api)[["iso3", "pais", "fecha", "valor"]]
    elif api == "oecd_bb":
        df = oecd_bb(id_api)[["iso3", "pais", "fecha", "valor"]]
    else:
        raise ValueError(f"api desconocida: {api}")
    df.insert(0, "codigo", codigo)
    return df


def destino(modulo: str) -> str:
    return "nacional" if modulo in ("nacional", "auxiliar") else modulo


def main():
    cat = pd.read_csv(CATALOGO, dtype=str).fillna("")
    cat = cat[cat["api"].isin(["datos_gob", "imig", "enacom", "wdi", "oecd_bb"])]
    print(f"Catalogo: {len(cat)} series con descarga automatica\n")

    partes = {k: [] for k in OUT}
    fallidas = {k: [] for k in OUT}
    for fila in cat.itertuples(index=False):
        mod = destino(fila.modulo)
        try:
            df = descargar(fila)
            partes[mod].append(df)
            print(f"  OK    {fila.modulo:<13} {fila.codigo:<26} {len(df):>6} filas")
        except Exception as e:  # noqa: BLE001 - se informa y se conserva lo anterior
            fallidas[mod].append(fila.codigo)
            print(f"  FALLA {fila.modulo:<13} {fila.codigo:<26} {type(e).__name__}: {str(e)[:90]}")

    RAW.mkdir(parents=True, exist_ok=True)
    for mod, ruta in OUT.items():
        nuevo = pd.concat(partes[mod], ignore_index=True) if partes[mod] else pd.DataFrame()
        if fallidas[mod] and ruta.exists():
            viejo = pd.read_csv(ruta, dtype={"fecha": str})
            conservar = viejo[viejo["codigo"].isin(fallidas[mod])]
            print(f"\n  ! {mod}: se conservan {len(conservar)} filas previas de {fallidas[mod]}")
            nuevo = pd.concat([nuevo, conservar], ignore_index=True)
        if nuevo.empty:
            continue
        nuevo = nuevo.sort_values(CLAVES[mod]).reset_index(drop=True)
        nuevo.to_csv(ruta, index=False, float_format="%.10g")

    resumen()


def resumen():
    print("\n=== Cobertura ===")
    for mod in ("nacional", "provincial"):
        ruta = OUT[mod]
        if not ruta.exists():
            continue
        df = pd.read_csv(ruta, dtype={"fecha": str})
        print(f"\n{mod} ({ruta.relative_to(ROOT)})")
        for codigo, g in df.groupby("codigo", sort=False):
            extra = f" | {g['provincia'].nunique()} jurisdicciones" if "provincia" in g else ""
            print(f"  {codigo:<26} {g['fecha'].min()[:7]} -> {g['fecha'].max()[:7]}  ({len(g)} datos{extra})")
    ruta = OUT["internacional"]
    if ruta.exists():
        df = pd.read_csv(ruta, dtype={"fecha": str})
        print(f"\ninternacional ({ruta.relative_to(ROOT)})")
        for codigo, g in df.groupby("codigo", sort=False):
            arg = g[g["iso3"] == "ARG"]["fecha"]
            rango = f"{arg.min()[:7]} a {arg.max()[:7]} ({len(arg)} datos)" if len(arg) else "SIN DATOS"
            print(f"  {codigo:<26} ARG {rango:<28} | {g['iso3'].nunique()} paises/agregados, ultimo {g['fecha'].max()[:7]}")


if __name__ == "__main__":
    main()
