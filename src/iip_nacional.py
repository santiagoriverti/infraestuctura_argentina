"""
Indice de Infraestructura Productiva (IIP) - modulo A: Argentina, trimestral.

    import src.iip_nacional as iip
    res = iip.calcular(Path("."))                       # parametros por defecto
    res = iip.calcular(Path("."), pesos_pilares={...})  # cualquier parametro de PARAMETROS

Metodo (detalle en CONTEXTO.md):
1. Cada variable se lleva a trimestre con su transformacion (VARIABLES). Las que crecen solas por
   el avance tecnologico (telecomunicaciones) se miden como BRECHA contra los paises de comparacion
   (mediana de los pares, o el mejor de ellos con referencia="mejor"). Las de uso se relativizan al
   EMAE. Los montos van en % del PIB.
2. z robusto sobre los datos propios de la ventana [inicio, ultimo]: (x - mediana) / (IQR / 1,349),
   con el signo de la variable y tope +-tope_z. 0 = lo tipico del periodo.
3. Pilar = promedio ponderado de sus variables disponibles; IIP = promedio ponderado de los pilares
   disponibles. Pesos por defecto iguales; se cambian con pesos_variables / pesos_pilares.
4. Un dato que falta al final se arrastra hasta max_arrastre trimestres (queda marcado).
"""

from pathlib import Path

import numpy as np
import pandas as pd

PILARES = {
    "energia": "Energía",
    "transporte": "Transporte y logística",
    "telecom": "Telecomunicaciones",
    "agua": "Agua y saneamiento",
    "inversion": "Inversión en infraestructura",
}

PARES = ["BRA", "CHL", "URY", "MEX", "COL", "PER", "AUS", "CAN", "ESP", "USA"]

PARAMETROS = {
    "inicio": "2016-01-01",
    "pesos_pilares": {p: 1.0 for p in PILARES},
    "pesos_variables": {},      # codigo -> peso (las que no figuran pesan 1)
    "pares": PARES,
    "referencia": "mediana",    # "mediana" de los pares o "mejor" (la frontera del grupo)
    "min_pares": 5,             # pares con dato necesarios para calcular la referencia
    "max_arrastre": 4,          # trimestres que se puede arrastrar el ultimo dato propio
    "max_rezago_pares": 6,      # trimestres que se extiende la referencia de los pares (ITU y OCDE
                                # publican con ~1,5 anios de rezago) con la tendencia de cada pais
    "tope_z": 3.0,
    "encadenar": True,          # pilares e IIP encadenados hacia atras (sin saltos por composicion)
}

GOBIERNOS = [
    ("Macri", "2016-01-01", "2019-12-31"),
    ("A. Fernández", "2020-01-01", "2023-12-31"),
    ("Milei", "2024-01-01", "2099-12-31"),
]

VARIABLES = [
    # codigo, pilar, signo, nombre, unidad, transformacion, fuente
    ("margen_reserva", "energia", 1, "Margen de reserva eléctrica", "%",
     "potencia instalada / pico de demanda de los últimos 36 meses - 1", "CAMMESA (SSPM)"),
    ("autoabastecimiento_gas", "energia", 1, "Autoabastecimiento de gas", "%",
     "producción / consumo entregado, 12 meses", "Secretaría de Energía, ENARGAS (SSPM)"),
    ("carga_ferroviaria_rel", "transporte", 1, "Carga ferroviaria relativa a la actividad", "2016=100",
     "t-km de 12 meses / EMAE promedio de 12 meses", "INDEC (ISSP, EMAE)"),
    ("carga_aerea_rel", "transporte", 1, "Carga aérea relativa a la actividad", "2016=100",
     "carga de 12 meses / EMAE promedio de 12 meses", "INDEC (ISSP, EMAE)"),
    ("brecha_penetracion", "telecom", 1, "Penetración de internet fijo vs pares", "% vs pares",
     "accesos c/100 hab. de Argentina / referencia de los pares - 1", "ENACOM; ITU (Banco Mundial)"),
    ("brecha_velocidad", "telecom", 1, "Velocidad medida de internet fijo vs pares", "% vs pares",
     "Mbps de Argentina / referencia de los pares - 1", "Ookla Open Data"),
    ("brecha_fibra", "telecom", 1, "Accesos por fibra óptica vs pares", "% vs pares",
     "% de accesos por fibra de Argentina / referencia de los pares - 1", "ENACOM; OCDE"),
    ("agua_red", "agua", 1, "Hogares con agua de red", "% hogares",
     "promedio de 4 trimestres (31 aglomerados urbanos)", "INDEC (EPH)"),
    ("cloaca", "agua", 1, "Hogares con cloaca", "% hogares",
     "promedio de 4 trimestres (31 aglomerados urbanos)", "INDEC (EPH)"),
    ("capex_infra_pib", "inversion", 1, "Gasto de capital nacional en infraestructura", "% PIB",
     "energía + transporte + agua (Nación + transf. a provincias), 12 meses / PIB", "Hacienda (IMIG); INDEC"),
    ("isac_asfalto", "inversion", 1, "Construcción vial (ISAC asfalto)", "2004=100",
     "promedio trimestral, desestacionalizado", "INDEC (ISAC)"),
    ("cemento", "inversion", 1, "Despachos de cemento", "Mt (12 meses)",
     "suma de 12 meses", "INDEC (SSPM)"),
]
META = pd.DataFrame(VARIABLES, columns=["codigo", "pilar", "signo", "nombre", "unidad", "transformacion", "fuente"]).set_index("codigo")


# ---------------------------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------------------------

def cargar(base: Path) -> dict:
    raw = Path(base) / "data" / "raw"
    leer = lambda f, **kw: pd.read_csv(raw / f, dtype={"fecha": str, "id": str}, **kw)  # noqa: E731
    return {
        "nacional": leer("nacional.csv"),
        "internacional": leer("internacional.csv"),
        "ookla": leer("ookla_fijo.csv"),
        "eph": leer("eph_servicios.csv"),
    }


def _serie(df: pd.DataFrame, codigo: str) -> pd.Series:
    s = df[df["codigo"] == codigo].set_index("fecha")["valor"].astype(float)
    s.index = pd.to_datetime(s.index)
    return s.sort_index()


def _trimestre(idx) -> pd.DatetimeIndex:
    return pd.DatetimeIndex(idx).to_period("Q").to_timestamp()


def _movil_12m(s: pd.Series, como: str, meses: int = 12) -> pd.Series:
    """Mensual -> ventana de `meses` meses tomada en el ultimo mes de cada trimestre."""
    s = s.asfreq("MS")
    r = getattr(s.rolling(meses, min_periods=meses), como)()
    r = r[r.index.month % 3 == 0].dropna()
    r.index = _trimestre(r.index)
    return r


def _promedio_trimestral(s: pd.Series) -> pd.Series:
    q = s.resample("QS").agg(["mean", "count"])
    return q["mean"].where(q["count"] == 3).dropna()


def _panel_pares(df: pd.DataFrame, codigo: str, desplazar_meses: int = 0) -> pd.DataFrame:
    """Largo (iso3, fecha, valor) -> trimestral por pais, interpolando entre datos propios."""
    p = df[df["codigo"] == codigo].pivot(index="fecha", columns="iso3", values="valor")
    p.index = pd.to_datetime(p.index) + pd.DateOffset(months=desplazar_meses)
    grilla = pd.date_range(p.index.min(), p.index.max(), freq="QS")
    return p.reindex(grilla).interpolate(limit_area="inside")


def _extrapolar(panel: pd.DataFrame, grilla, n_max: int, tope: float | None, ventana: int = 8) -> pd.DataFrame:
    """Extiende cada pais con su tendencia lineal de los ultimos `ventana` trimestres, hasta n_max."""
    out = panel.reindex(panel.index.union(grilla))
    for c in panel.columns:
        s = panel[c].dropna()
        if len(s) < 2:
            continue
        base = s.iloc[-ventana:]
        pendiente = np.polyfit(np.arange(len(base)), base.values, 1)[0]
        futuros = out.index[out.index > s.index[-1]][:n_max]
        out.loc[futuros, c] = (s.iloc[-1] + pendiente * np.arange(1, len(futuros) + 1)).clip(0, tope)
    return out.reindex(grilla)


def _referencia(panel: pd.DataFrame, grilla, prm, tope: float | None = None) -> tuple[pd.Series, pd.Series]:
    """Referencia de los pares (mediana o mejor). Las fuentes internacionales publican con rezago: al
    final, cada pais se extiende con su tendencia (hasta max_rezago_pares trimestres) y esos trimestres
    quedan marcados como arrastre."""
    sub = panel.reindex(columns=prm["pares"])

    def ref(x):
        r = x.median(axis=1) if prm["referencia"] == "mediana" else x.max(axis=1)
        return r.where(x.notna().sum(axis=1) >= prm["min_pares"])

    propio = ref(sub.reindex(grilla))
    extendido = propio.fillna(ref(_extrapolar(sub, grilla, prm["max_rezago_pares"], tope)))
    return extendido, propio.isna() & extendido.notna()


# ---------------------------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------------------------

def construir_variables(d: dict, prm: dict, grilla: pd.DatetimeIndex) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """-> X (valores), A (True = dato arrastrado o con referencia arrastrada), detalle de pares."""
    nac, inter = d["nacional"], d["internacional"]
    X, A, pares = {}, {}, {}

    # Energia
    # Pico de 36 meses (el record reciente): con 12 meses el margen salta con el clima de un verano.
    # La potencia instalada es anual (stock a diciembre): va al 4to trimestre y se interpola entre
    # anios (asignarla entera al anio producia escalones cada 1er trimestre). Despues del ultimo
    # dato se repite (marcado como arrastre).
    instalada = _serie(nac, "pot_instalada_mw")
    instalada.index = instalada.index + pd.DateOffset(months=9)
    pico = _movil_12m(_serie(nac, "pot_maxima_mw"), "max", meses=36)
    q = pd.date_range(instalada.index.min(), pico.index.max(), freq="QS")
    inst = instalada.reindex(q).interpolate(limit_area="inside")
    inst_q = inst.ffill().reindex(pico.index)
    X["margen_reserva"] = 100 * (inst_q / pico - 1)
    A["margen_reserva"] = pd.Series(pico.index > instalada.index.max(), index=pico.index)
    X["autoabastecimiento_gas"] = 100 * (_movil_12m(_serie(nac, "produccion_gas_mm3"), "sum")
                                         / _movil_12m(_serie(nac, "consumo_gas_mm3"), "sum"))

    # Transporte: uso relativo a la actividad
    emae = _movil_12m(_serie(nac, "emae_desest"), "mean")
    for cod, fuente in [("carga_ferroviaria_rel", "carga_ferroviaria"), ("carga_aerea_rel", "carga_aerea")]:
        r = _movil_12m(_serie(nac, fuente), "sum") / emae
        X[cod] = 100 * r / r[r.index.year == 2016].mean()

    # Telecomunicaciones: brecha contra los pares
    # Penetracion: la ITU publica el stock a diciembre -> el dato anual va al 4to trimestre
    arg = _serie(nac, "internet_penetracion_hab")
    ref, arr = _referencia(_panel_pares(inter, "banda_ancha_fija", desplazar_meses=9), grilla, prm)
    X["brecha_penetracion"] = 100 * (arg.reindex(grilla) / ref - 1)
    A["brecha_penetracion"] = arr
    pares["penetracion"] = pd.DataFrame({"Argentina": arg.reindex(grilla), "Referencia pares": ref,
                                         "Referencia arrastrada": arr})

    ook = d["ookla"][d["ookla"]["nivel"] == "pais"].rename(columns={"id": "iso3", "mbps_bajada": "valor"})
    ook = ook.assign(codigo="velocidad")
    panel = _panel_pares(ook, "velocidad")
    ref, arr = _referencia(panel, grilla, prm)
    X["brecha_velocidad"] = 100 * (panel["ARG"].reindex(grilla) / ref - 1)
    A["brecha_velocidad"] = arr
    pares["velocidad"] = pd.DataFrame({"Argentina": panel["ARG"].reindex(grilla), "Referencia pares": ref,
                                       "Referencia arrastrada": arr})

    arg = _serie(nac, "internet_share_fibra")
    ref, arr = _referencia(_panel_pares(inter, "fibra_share"), grilla, prm, tope=100.0)
    # Cociente y no diferencia: en una curva de adopcion en S la diferencia en p.p. se agranda aunque
    # Argentina se acerque (2019: 7% vs 19%; 2025: 47% vs 69%).
    X["brecha_fibra"] = 100 * (arg.reindex(grilla) / ref - 1)
    A["brecha_fibra"] = arr
    pares["fibra"] = pd.DataFrame({"Argentina": arg.reindex(grilla), "Referencia pares": ref,
                                   "Referencia arrastrada": arr})

    # Agua y saneamiento (EPH; promedio de 4 trimestres para sacar ruido de muestreo)
    eph = d["eph"][d["eph"]["nivel"] == "total"]
    for cod, fuente in [("agua_red", "hogares_agua_red"), ("cloaca", "hogares_cloaca")]:
        s = _serie(eph, fuente).asfreq("QS")
        X[cod] = s.rolling(4, min_periods=4).mean()

    # Inversion
    capex = sum(_serie(nac, c) for c in ["capex_energia", "capex_transporte", "capex_agua"])
    pib = _serie(nac, "pib_nominal_anualizado").asfreq("QS") / 4   # trimestre anualizado -> trimestral
    X["capex_infra_pib"] = 100 * _movil_12m(capex, "sum") / pib.rolling(4, min_periods=4).sum()
    X["isac_asfalto"] = _promedio_trimestral(_serie(nac, "isac_asfalto"))
    X["cemento"] = _movil_12m(_serie(nac, "cemento_despachos"), "sum") / 1000

    X = pd.DataFrame({k: v.reindex(grilla) for k, v in X.items()})[META.index]
    A = pd.DataFrame({k: A[k].astype(bool).reindex(grilla, fill_value=False) if k in A
                      else pd.Series(False, index=grilla) for k in X.columns})
    return X, A, pares


def _arrastrar(X: pd.DataFrame, A: pd.DataFrame, limite: int, limite_pares: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Despues del ultimo dato PROPIO de cada variable se admiten a lo sumo `limite` trimestres
    (`limite_pares` para las brechas contra los pares): con la referencia extendida (ya marcados en A)
    o, si falta el dato, con el ultimo valor. Mas alla del limite la variable queda vacia. Solo actua
    al final (no rellena huecos intermedios)."""
    Xf, A = X.copy(), A.copy()
    for c in X.columns:
        up = X[c].where(~A[c]).last_valid_index()
        if up is None:
            continue
        cola = Xf.index > up
        n = limite_pares if c.startswith("brecha_") else limite
        tope = up + pd.DateOffset(months=3 * n)
        relleno = X[c].ffill().where(Xf.index <= tope)
        Xf.loc[cola, c] = relleno.loc[cola]
        A.loc[cola, c] = Xf.loc[cola, c].notna()
    return Xf, A


# ---------------------------------------------------------------------------------------------
# Indice
# ---------------------------------------------------------------------------------------------

def normalizar(X: pd.DataFrame, A: pd.DataFrame, tope: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    propio = X.where(~A)
    med = propio.median()
    esc = (propio.quantile(0.75) - propio.quantile(0.25)) / 1.349
    Z = ((X - med) / esc * META["signo"]).clip(-tope, tope)
    stats = pd.DataFrame({"mediana": med, "escala": esc, "n_propios": propio.notna().sum(),
                          "desde": propio.apply(lambda c: c.first_valid_index()),
                          "hasta": propio.apply(lambda c: c.last_valid_index()),
                          "arrastrados": (A & X.notna()).sum(),
                          "pct_en_tope": 100 * (Z.abs() >= tope).sum() / Z.notna().sum()})
    return Z, stats


def _promedio_ponderado(df: pd.DataFrame, pesos: pd.Series) -> pd.Series:
    w = df.notna() * pesos.reindex(df.columns).values
    return (df.fillna(0) * w).sum(axis=1) / w.sum(axis=1).replace(0, np.nan)


def _encadenado(df: pd.DataFrame, pesos: pd.Series) -> pd.Series:
    """Promedio ponderado encadenado hacia atras: el ultimo trimestre es el promedio de todas las
    variables disponibles; hacia atras, cada trimestre difiere del siguiente en el promedio de las
    variaciones de las variables presentes en ambos. Asi la entrada o salida de una variable no
    produce saltos (la velocidad medida entra en 2019, agua en 2017)."""
    pesos = pesos.reindex(df.columns)
    df = df.loc[:, pesos > 0]
    pesos = pesos[df.columns]
    simple = _promedio_ponderado(df, pesos)
    fechas = simple.dropna().index
    out = pd.Series(np.nan, index=df.index)
    if len(fechas) == 0:
        return out
    out[fechas[-1]] = simple[fechas[-1]]
    for t_ant, t in zip(fechas[-2::-1], fechas[:0:-1]):
        comunes = df.loc[t].notna() & df.loc[t_ant].notna()
        if comunes.any():
            w = pesos[comunes]
            delta = ((df.loc[t, comunes] - df.loc[t_ant, comunes]) * w).sum() / w.sum()
            out[t_ant] = out[t] - delta
        else:
            out[t_ant] = simple[t_ant]  # sin variables en comun: se reinicia con el promedio simple
    return out


def agregar(Z: pd.DataFrame, prm: dict) -> pd.DataFrame:
    combinar = _encadenado if prm["encadenar"] else _promedio_ponderado
    pv = pd.Series({c: float(prm["pesos_variables"].get(c, 1.0)) for c in Z.columns})
    pil = pd.DataFrame({p: combinar(Z[META.index[META["pilar"] == p]], pv) for p in PILARES})
    pp = pd.Series({p: float(prm["pesos_pilares"].get(p, 1.0)) for p in PILARES})
    out = pil.copy()
    out.insert(0, "IIP", combinar(pil, pp))
    out["n_pilares"] = pil.notna().sum(axis=1)
    out["n_variables"] = Z.notna().sum(axis=1)
    return out


def por_gobierno(indice: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for nombre, desde, hasta in GOBIERNOS:
        sub = indice.loc[desde:hasta, ["IIP", *PILARES]]
        if len(sub):
            filas.append({"gobierno": nombre, "desde": etiqueta(sub.index[0]), "hasta": etiqueta(sub.index[-1]),
                          "trimestres": len(sub), **sub.mean().round(3).to_dict()})
    return pd.DataFrame(filas)


def etiqueta(t) -> str:
    return f"{t.year}-T{(t.month - 1) // 3 + 1}"


def variantes(prm: dict) -> dict:
    """Variantes razonables de la metodologia para medir que conclusiones son firmes."""
    v = {"base": {}, "referencia: el mejor de los pares": {"referencia": "mejor"}}
    for p, nombre in PILARES.items():
        v[f"sin {nombre}"] = {"pesos_pilares": {**prm["pesos_pilares"], p: 0.0}}
    v["Inversión solo con gasto de capital"] = {"pesos_variables": {**prm["pesos_variables"], "isac_asfalto": 0.0, "cemento": 0.0}}
    v["ventana desde 2017-T1"] = {"inicio": "2017-01-01"}
    v["arrastre máximo 2 trimestres"] = {"max_arrastre": 2}
    v["referencia de los pares sin extender"] = {"max_rezago_pares": 0}
    v["sin encadenar (promedio simple)"] = {"encadenar": False}
    v["tope z ±2"] = {"tope_z": 2.0}
    return v


def sensibilidad(base: Path, **parametros) -> tuple[pd.DataFrame, pd.DataFrame]:
    """-> (una fila por variante: ultimo dato, cambio en 12 meses, promedio por gobierno;
           IIP trimestral de cada variante)."""
    prm = {**PARAMETROS, **parametros}
    filas, series = [], {}
    for nombre, cambio in variantes(prm).items():
        r = calcular(base, **{**prm, **cambio})
        s, u = r["indice"]["IIP"], r["ultimo"]
        fila = {"variante": nombre, "ultimo": etiqueta(u), "IIP": s.loc[u],
                "cambio_12m": s.loc[u] - s.loc[u - pd.DateOffset(years=1)]}
        fila.update({f"prom. {g}": v for g, v in r["por_gobierno"].set_index("gobierno")["IIP"].items()})
        filas.append(fila)
        series[nombre] = s
    tabla = pd.DataFrame(filas)
    S = pd.DataFrame(series)
    tabla["corr_con_base"] = [S["base"].corr(S[c]) for c in S.columns]
    return tabla, S


def calcular(base: Path, **parametros) -> dict:
    prm = {**PARAMETROS, **parametros}
    d = cargar(base)
    grilla = pd.date_range(prm["inicio"], pd.Timestamp.today(), freq="QS")
    X, A, pares = construir_variables(d, prm, grilla)
    # Ultimo trimestre: el ultimo con dato propio en al menos la mitad de las variables
    con_dato = X.where(~A).notna().sum(axis=1)
    ultimo = con_dato[con_dato >= len(X.columns) / 2].index.max()
    X, A = X.loc[:ultimo], A.loc[:ultimo]
    X, A = _arrastrar(X, A, prm["max_arrastre"], prm["max_rezago_pares"])
    Z, stats = normalizar(X, A, prm["tope_z"])
    indice = agregar(Z, prm)
    metodologia = META.join(stats)
    metodologia["peso"] = [float(prm["pesos_variables"].get(c, 1.0)) for c in metodologia.index]
    return {"parametros": prm, "ultimo": ultimo, "valores": X, "arrastre": A, "z": Z, "indice": indice,
            "metodologia": metodologia, "por_gobierno": por_gobierno(indice),
            "pares": {k: v.loc[:ultimo] for k, v in pares.items()}}


# ---------------------------------------------------------------------------------------------
# Salidas
# ---------------------------------------------------------------------------------------------

def resumen(res: dict) -> str:
    ind, u = res["indice"], res["ultimo"]
    hace = u - pd.DateOffset(years=1)
    f = lambda v: "s/d" if pd.isna(v) else f"{v:+.2f}"  # noqa: E731
    lineas = [f"IIP {etiqueta(u)}: {f(ind.loc[u, 'IIP'])}  (hace un año: {f(ind.loc[hace, 'IIP'])})"]
    for p, nombre in PILARES.items():
        lineas.append(f"  {nombre:<30} {f(ind.loc[u, p]):>5}  (hace un año: {f(ind.loc[hace, p])})")
    arr = res["arrastre"].loc[u]
    if arr.any():
        lineas.append(f"  Arrastrados en {etiqueta(u)}: {', '.join(arr[arr].index)}")
    return "\n".join(lineas)


def _con_etiquetas(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.insert(0, "trimestre", [etiqueta(t) for t in out.index])
    return out.reset_index(drop=True)


def exportar_excel(res: dict, ruta: Path, sens: pd.DataFrame | None = None) -> None:
    prm, u = res["parametros"], res["ultimo"]
    leeme = pd.DataFrame({"Campo": [
        "Índice", "Último trimestre", "Ventana", "Lectura", "Pares", "Referencia de los pares",
        "Pesos de los pilares", "Pesos de las variables", "Arrastre máximo", "Tope z", "Metodología",
        "Licencia Ookla"],
        "Valor": [
        "Índice de Infraestructura Productiva (IIP), módulo nacional trimestral (INECO-UADE)",
        etiqueta(u), f"{etiqueta(pd.Timestamp(prm['inicio']))} a {etiqueta(u)}",
        "0 = lo típico del período; +1 = una desviación (robusta) mejor que lo típico",
        ", ".join(prm["pares"]), prm["referencia"],
        ", ".join(f"{k} {v:g}" for k, v in prm["pesos_pilares"].items()),
        ", ".join(f"{k} {v:g}" for k, v in prm["pesos_variables"].items()) or "todas 1",
        f"{prm['max_arrastre']} trimestres", f"±{prm['tope_z']:g}",
        "Ver CONTEXTO.md del repo santiagoriverti/infraestuctura_argentina",
        "Velocidad medida: Speedtest® by Ookla® Global Fixed and Mobile Network Performance Maps "
        "(CC BY-NC-SA 4.0, uso no comercial)"]})
    detalle = []
    for nombre, df in res["pares"].items():
        detalle.append(df.add_prefix(f"{nombre}: "))
    with pd.ExcelWriter(ruta, engine="openpyxl") as xw:
        leeme.to_excel(xw, sheet_name="Leeme", index=False)
        _con_etiquetas(res["indice"].round(3)).to_excel(xw, sheet_name="IIP", index=False)
        res["por_gobierno"].to_excel(xw, sheet_name="Por_gobierno", index=False)
        if sens is not None:
            sens.round(3).to_excel(xw, sheet_name="Sensibilidad", index=False)
        _con_etiquetas(res["z"].round(3)).to_excel(xw, sheet_name="Variables_z", index=False)
        _con_etiquetas(res["valores"].round(3)).to_excel(xw, sheet_name="Variables_valor", index=False)
        _con_etiquetas(res["arrastre"]).to_excel(xw, sheet_name="Arrastrados", index=False)
        _con_etiquetas(pd.concat(detalle, axis=1).round(2)).to_excel(xw, sheet_name="Telecom_vs_pares", index=False)
        met = res["metodologia"].copy()
        for c in ["desde", "hasta"]:
            met[c] = [etiqueta(t) if pd.notna(t) else "" for t in met[c]]
        met.round(4).reset_index().to_excel(xw, sheet_name="Metodologia", index=False)
