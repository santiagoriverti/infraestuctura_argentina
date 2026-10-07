"""Graficos del IIP (PNG estaticos, para Colab y para el documento LaTeX de INECO)."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from src.iip_nacional import GOBIERNOS, PILARES, etiqueta  # noqa: E402

# Paleta (skill dataviz, instancia de referencia, modo claro)
TINTA, TINTA_2, TINTA_3 = "#0b0b0b", "#52514e", "#8a8984"
GRILLA, FONDO, BANDA = "#e4e3de", "#ffffff", "#f4f3f0"
AZUL, NARANJA = "#2a78d6", "#eb6834"

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": TINTA_3, "axes.labelcolor": TINTA_2, "axes.titlecolor": TINTA,
    "xtick.color": TINTA_2, "ytick.color": TINTA_2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRILLA, "grid.linewidth": 0.8,
    "figure.facecolor": FONDO, "axes.facecolor": FONDO, "legend.frameon": False, "savefig.dpi": 200,
    "savefig.bbox": "tight",
})


def _gobiernos(ax, desde, hasta, rotulos=True):
    for k, (nombre, ini, fin) in enumerate(GOBIERNOS):
        a, b = max(pd.Timestamp(ini), desde), min(pd.Timestamp(fin), hasta)
        if a >= b:
            continue
        if k % 2 == 1:
            ax.axvspan(a, b, color=BANDA, zorder=0, lw=0)
        if rotulos:
            ax.text(a + (b - a) / 2, 1.0, nombre, transform=ax.get_xaxis_transform(), ha="center", va="bottom",
                    color=TINTA_2, fontsize=8)


def _eje_cero(ax):
    ax.axhline(0, color=TINTA_3, lw=0.9, zorder=1)


def g01_iip(res: dict, ruta: Path) -> Path:
    s = res["indice"]["IIP"].dropna()
    fig, ax = plt.subplots(figsize=(8, 3.6))
    _gobiernos(ax, s.index[0], s.index[-1] + pd.DateOffset(months=3))
    _eje_cero(ax)
    ax.plot(s.index, s.values, color=AZUL, lw=2, zorder=3)
    ax.plot(s.index[-1], s.iloc[-1], "o", color=AZUL, ms=6, mec=FONDO, mew=2, zorder=4)
    ax.annotate(f"{etiqueta(s.index[-1])}: {s.iloc[-1]:+.2f}", (s.index[-1], s.iloc[-1]), xytext=(-6, 10),
                textcoords="offset points", ha="right", color=TINTA, fontsize=9)
    ax.set_ylabel("desvíos respecto de lo típico (z)")
    ax.set_title("Índice de Infraestructura Productiva (IIP)", loc="left", pad=16, fontsize=11)
    fig.savefig(ruta)
    plt.close(fig)
    return ruta


def g02_pilares(res: dict, ruta: Path) -> Path:
    ind = res["indice"]
    paneles = [("IIP", "IIP (promedio de los pilares)")] + list(PILARES.items())
    fig, axes = plt.subplots(2, 3, figsize=(9, 5), sharex=True, sharey=True)
    for ax, (col, titulo) in zip(axes.flat, paneles):
        s = ind[col].dropna()
        _gobiernos(ax, ind.index[0], ind.index[-1] + pd.DateOffset(months=3), rotulos=False)
        _eje_cero(ax)
        ax.plot(s.index, s.values, color=AZUL, lw=2 if col == "IIP" else 1.6, zorder=3)
        ax.set_title(titulo, loc="left", fontsize=9)
        if len(s):
            ax.annotate(f"{s.iloc[-1]:+.2f}", (s.index[-1], s.iloc[-1]), xytext=(4, 0), textcoords="offset points",
                        va="center", color=TINTA, fontsize=8)
    for ax in axes[:, 0]:
        ax.set_ylabel("z")
    fig.suptitle("IIP por pilar (bandas: gestiones de gobierno)", x=0.01, ha="left", fontsize=11, color=TINTA)
    fig.tight_layout()
    fig.savefig(ruta)
    plt.close(fig)
    return ruta


def g03_ultimo(res: dict, ruta: Path) -> Path:
    ind, u = res["indice"], res["ultimo"]
    hace = u - pd.DateOffset(years=1)
    filas = ["IIP", *PILARES]
    nombres = ["IIP", *PILARES.values()][::-1]
    actual, previo = ind.loc[u, filas].values[::-1], ind.loc[hace, filas].values[::-1]
    y = range(len(filas))
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.grid(axis="x", color=GRILLA)
    ax.grid(axis="y", visible=False)
    ax.axvline(0, color=TINTA_3, lw=0.9)
    alto = 0.36
    ax.barh([i + alto / 2 + 0.02 for i in y], actual, height=alto, color=AZUL, label=etiqueta(u))
    ax.barh([i - alto / 2 - 0.02 for i in y], previo, height=alto, color=NARANJA, label=etiqueta(hace))
    for i, v in zip(y, actual):
        if pd.isna(v):
            ax.text(0.04, i + alto / 2 + 0.02, "s/d", va="center", ha="left", color=TINTA_2, fontsize=8)
            continue
        ax.text(v + (0.04 if v >= 0 else -0.04), i + alto / 2 + 0.02, f"{v:+.2f}", va="center",
                ha="left" if v >= 0 else "right", color=TINTA, fontsize=8)
    ax.set_yticks(list(y), nombres)
    ax.set_xlabel("desvíos respecto de lo típico (z)")
    ax.legend(loc="lower right", fontsize=8)
    lim = pd.Series([*actual, *previo]).abs().max() + 0.4
    ax.set_xlim(-lim, lim)
    ax.set_title(f"Último trimestre vs un año antes", loc="left", fontsize=11)
    fig.savefig(ruta)
    plt.close(fig)
    return ruta


def g04_telecom(res: dict, ruta: Path) -> Path:
    paneles = [("penetracion", "Accesos a internet fijo c/100 hab."),
               ("velocidad", "Velocidad medida de bajada (Mbps, Ookla)"),
               ("fibra", "Accesos por fibra óptica (%)")]
    ref = "mediana" if res["parametros"]["referencia"] == "mediana" else "mejor"
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.2), sharex=True)
    for ax, (clave, titulo) in zip(axes, paneles):
        df = res["pares"][clave]
        arr = df["Referencia arrastrada"].astype(bool)
        propio = df["Referencia pares"].where(~arr)
        # el tramo arrastrado arranca en el ultimo dato propio para que la linea no se corte
        arrastre = df["Referencia pares"].where(arr | arr.shift(-1, fill_value=False))
        ax.plot(df.index, df["Argentina"], color=AZUL, lw=2, label="Argentina")
        ax.plot(df.index, propio, color=NARANJA, lw=2, label=f"Pares ({ref})")
        ax.plot(df.index, arrastre, color=NARANJA, lw=1.4, ls=(0, (2, 2)), label="Pares: tendencia extendida (fuente con rezago)")
        ax.set_title(titulo, loc="left", fontsize=9)
        ax.set_ylim(bottom=0)
    fig.suptitle("Telecomunicaciones: Argentina frente a los países de comparación", x=0.01, ha="left",
                 fontsize=11, color=TINTA)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=3, fontsize=8)
    fig.savefig(ruta)
    plt.close(fig)
    return ruta


def todos(res: dict, carpeta: Path) -> list[Path]:
    # prefijo iip_: las figuras van a la carpeta figuras/ del Overleaf junto con las de otras secciones
    carpeta.mkdir(parents=True, exist_ok=True)
    return [g01_iip(res, carpeta / "iip_g01_indice.png"), g02_pilares(res, carpeta / "iip_g02_pilares.png"),
            g03_ultimo(res, carpeta / "iip_g03_ultimo_trimestre.png"),
            g04_telecom(res, carpeta / "iip_g04_telecom_pares.png")]
