"""
Compila docs/informe_indicadores/seccion_iip.tex dentro de un documento de prueba con el MISMO
preambulo y la misma bibliografia que el documento INECO-UADE "Propuesta de Indicadores Economicos"
(Overleaf), para detectar errores, citas o referencias indefinidas y cajas desbordadas antes de
pegar la seccion.

Uso:
    python scripts/correr_nacional.py         # genera las figuras en output/
    python scripts/probar_seccion_latex.py    # necesita pdflatex (MiKTeX o TeX Live)

Salida: _local_run/latex/documento.pdf (ignorada por git). Sale con codigo 1 si hay errores, citas
sin bibitem o referencias indefinidas.

Si cambia el preambulo o la bibliografia del documento en el Overleaf, actualizar PREAMBULO y
CLAVES_DEL_DOCUMENTO (estado al 2026-10-08).
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECCION = ROOT / "docs" / "informe_indicadores" / "seccion_iip.tex"
DESTINO = ROOT / "_local_run" / "latex"

PREAMBULO = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish]{babel}
\usepackage{lmodern}
\usepackage[margin=2.5cm]{geometry}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage[hidelinks]{hyperref}
\definecolor{titulos}{RGB}{20,60,20}
\titleformat{\section}{\Large\bfseries\color{titulos}}{\thesection.}{0.6em}{}
\titleformat{\subsection}{\large\bfseries\color{titulos}}{\thesubsection.}{0.6em}{}
"""

# Bibitems que ya estan en el documento (de las otras secciones): no se repiten en la del IIP
CLAVES_DEL_DOCUMENTO = ["indec_eph", "indec_ipc", "oecd2008", "utdt", "sepa", "indec_engho",
                        "haber_minimo", "mecon_imig"]


def main():
    sec = SECCION.read_text(encoding="utf-8")
    cuerpo = "\n".join(l for l in sec.splitlines() if not l.startswith("%"))
    nuevos = [l[2:] for l in sec.splitlines() if l.startswith("% \\bibitem{")]
    claves_nuevas = [re.match(r"\\bibitem\{([^}]+)\}", b).group(1) for b in nuevos]
    citadas = {k.strip() for grupo in re.findall(r"\\cite\{([^}]+)\}", cuerpo) for k in grupo.split(",")}

    problemas = []
    repetidas = set(claves_nuevas) & set(CLAVES_DEL_DOCUMENTO)
    if repetidas:
        problemas.append(f"bibitems nuevos que ya estan en el documento: {sorted(repetidas)}")
    sin_bibitem = citadas - set(claves_nuevas) - set(CLAVES_DEL_DOCUMENTO)
    if sin_bibitem:
        problemas.append(f"citas sin bibitem: {sorted(sin_bibitem)}")
    sin_citar = set(claves_nuevas) - citadas
    if sin_citar:
        problemas.append(f"bibitems nuevos que no se citan: {sorted(sin_citar)}")
    print(f"Citas: {len(citadas)} claves ({len(citadas & set(CLAVES_DEL_DOCUMENTO))} del documento, "
          f"{len(citadas & set(claves_nuevas))} nuevas)")

    figuras = re.findall(r"figuras/(\S+?\.png)", cuerpo)
    DESTINO.mkdir(parents=True, exist_ok=True)
    (DESTINO / "figuras").mkdir(exist_ok=True)
    for f in figuras:
        origen = ROOT / "output" / f
        if not origen.exists():
            sys.exit(f"Falta output/{f}: correr antes python scripts/correr_nacional.py")
        shutil.copy(origen, DESTINO / "figuras" / f)
    print(f"Figuras: {', '.join(figuras)}")

    bib = [f"\\bibitem{{{k}}} (ya en el documento)." for k in CLAVES_DEL_DOCUMENTO] + nuevos
    doc = (PREAMBULO + "\\begin{document}\n" + sec + "\n\\clearpage\n\\begin{thebibliography}{99}\n"
           + "\n\n".join(bib) + "\n\\end{thebibliography}\n\\end{document}\n")
    (DESTINO / "documento.tex").write_text(doc, encoding="utf-8")

    pdflatex = shutil.which("pdflatex")
    if pdflatex is None:
        problemas.append("no hay pdflatex instalado (MiKTeX o TeX Live): solo se revisaron las citas")
    else:
        version = subprocess.run([pdflatex, "--version"], capture_output=True, text=True).stdout
        cmd = [pdflatex, "-interaction=nonstopmode", "-halt-on-error"]
        if "MiKTeX" in version:
            cmd.append("-disable-installer")  # no instalar paquetes en silencio
        for _ in range(2):  # dos pasadas para resolver referencias
            subprocess.run(cmd + ["documento.tex"], cwd=DESTINO, capture_output=True)
        log = (DESTINO / "documento.log").read_text(encoding="latin-1")
        errores = [l for l in log.splitlines() if l.startswith("!")]
        indefinidas = [l for l in log.splitlines() if "undefined" in l and "Warning" in l]
        desbordes = [l for l in log.splitlines() if l.startswith("Overfull")]
        print(f"pdflatex: {len(errores)} errores, {len(indefinidas)} citas/referencias indefinidas, "
              f"{len(desbordes)} cajas desbordadas")
        for l in errores + indefinidas + desbordes:
            print("   ", l)
        if errores or indefinidas:
            problemas.append("la compilacion tiene errores o referencias indefinidas")
        if (DESTINO / "documento.pdf").exists() and not errores:
            print(f"PDF: {(DESTINO / 'documento.pdf').relative_to(ROOT)}")

    print("\nRESULTADO:", "OK" if not problemas else "PROBLEMAS")
    for p in problemas:
        print("  -", p)
    sys.exit(1 if problemas else 0)


if __name__ == "__main__":
    main()
