# ESTADO DEL PROYECTO — infraestuctura_argentina

> Punto de entrada para retomar el trabajo en otra sesión o en otra PC.
> Última actualización: **2026-10-07** (sesión 1: arranque).
> Siguiente tarea: **validar la propuesta v0** (decisiones abiertas, CONTEXTO §4) y construir el módulo A.

## 1. Dónde estamos

| Ítem | Estado |
|---|---|
| Diseño | Definido con el usuario: módulo **A nacional** (serie) + **B provincial** (ranking) + **C internacional** (benchmark); los **5 pilares**; va como **sección del documento INECO-UADE** "Propuesta de Indicadores Económicos" |
| Metodología | **Propuesta v0** en CONTEXTO §2, con 6 decisiones abiertas (§4). No hay índice calculado |
| Catálogo | `data/reference/catalogo_variables.csv`: 53 variables (39 con descarga automática, 14 candidatas sin descarga automática todavía) |
| Datos | `scripts/actualizar_datos.py` baja las 39 sin errores (2026-10-07) |
| Notebooks | Ninguno todavía |

### Cobertura de lo descargado (2026-10-07)

| Módulo | Series | Rango |
|---|---|---|
| Nacional | 18 + 3 auxiliares (IPC, PIB, EMAE) | CAMMESA/gas 2001+ · ISSP/ISAC 2012+ · ENACOM 2014-T1 · IMIG 2016+ → hasta jun/ago-2026 (ENACOM 2026-T2) |
| Provincial | 3 (internet: penetración, velocidad, % fibra) | 24 jurisdicciones, 2014-T1 a 2026-T2 |
| Internacional | 15 del Banco Mundial | 2000-2024/25; 11 países + América Latina y OCDE |

### Primeros números (chequeo de sanidad, no son resultados del índice)

- Margen de reserva eléctrica (instalada / máxima − 1): 34% (2014) → 63% (2020) → 46% (2025).
- Capex del SPN en energía + transporte + agua: 1,06% del PIB (2016) → 0,80% (2023) → **0,20% (2025)**.
- Internet fijo 2026-T2: 85,4 accesos c/100 hogares, 265 Mbps contratados, 50% por fibra (2014: 4 Mbps).
- Carga ferroviaria ~10.000 M t-km/año, estable 2012-2025 (pico 12.084 en 2022).

## 2. Próximos pasos

1. **Usuario:** revisar la propuesta v0 y responder las decisiones abiertas (CONTEXTO §4): nombre,
   variables con tendencia, variables de uso, capex por pilar o junto, pesos, países.
2. **Módulo A (nacional):** `src/` con la normalización (z robusto, reutilizar el criterio del NB03 de
   `cuentas_publicas`) + notebook `01_indice_nacional.ipynb` (Colab, termina descargando un ZIP con
   Excel + gráficos). Generar el .ipynb con un script, no a mano.
3. **Pilar Agua:** sumar agua de red y cloacas desde la EPH (reutilizar el pipeline de `analisis_EPH`).
4. **Módulo C (internacional):** notebook con distancia a la frontera; evaluar FMI ICSD y Ookla.
5. **Módulo B (provincial):** Censo 2022 (agua, cloacas, gas), CAMMESA directo (demanda por
   provincia), Mapa de Inversiones, DNV, ENARGAS.
6. **Sección LaTeX** para el Overleaf de INECO (formato de `seccion_iijp.tex`).
7. Revisar la caída de los peajes (CONTEXTO §5) antes de usarlos.

## 3. Rutina de actualización

```bash
git pull
python scripts/actualizar_datos.py     # revisar que no haya FALLA y la cobertura del final
git add data/raw && git commit -m "Actualizacion de datos <mes>"
```

## 4. PC nueva

```bash
git clone https://github.com/santiagoriverti/infraestuctura_argentina.git
pip install -r requirements.txt
python scripts/actualizar_datos.py
```

En Windows correr Python con `PYTHONUTF8=1`.
