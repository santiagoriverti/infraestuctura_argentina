"""
Corre el modulo A (IIP nacional) localmente, igual que el notebook, y deja en output/:
iip_nacional.xlsx + graficos PNG. Sirve para verificar antes de subir y para comparar con el ZIP
que descarga Colab.

Uso:
    python scripts/correr_nacional.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import src.graficos as graf  # noqa: E402
import src.iip_nacional as iip  # noqa: E402


def main():
    res = iip.calcular(ROOT)
    print(iip.resumen(res))
    print("\nPor gobierno:\n" + res["por_gobierno"].round(2).to_string(index=False))
    sens, _ = iip.sensibilidad(ROOT)
    print("\nSensibilidad:\n" + sens.round(2).to_string(index=False))
    salida = ROOT / "output"
    salida.mkdir(exist_ok=True)
    iip.exportar_excel(res, salida / "iip_nacional.xlsx", sens)
    for p in graf.todos(res, salida):
        print(f"  {p.relative_to(ROOT)}")
    print(f"  {(salida / 'iip_nacional.xlsx').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
