# ESTADO DEL PROYECTO — infraestuctura_argentina

> Punto de entrada para retomar el trabajo en otra sesión o en otra PC.
> Última actualización: **2026-10-07** (sesión 1).
> Siguiente tarea: **el usuario corre el notebook 01 en Colab y pega la sección LaTeX en el Overleaf**;
> después, módulo C (internacional) o B (provincial).

## 1. Dónde estamos

| Ítem | Estado |
|---|---|
| Diseño | Módulos **A nacional** + **B provincial** + **C internacional**; 5 pilares; sección del documento INECO-UADE |
| Decisiones del usuario | Respondidas (CONTEXTO §4): nombre IIP, telecom contra los pares, uso ÷ EMAE, pesos iguales configurables, 10 pares |
| **Módulo A** | **v1 implementado**: `src/iip_nacional.py`, notebook `01_iip_nacional.ipynb` (verificado con nbconvert: 0 errores, ZIP = Excel 9 hojas + 4 PNG). **Falta correrlo en Colab** |
| Sección LaTeX | `docs/informe_indicadores/seccion_iip.tex` — compila con pdflatex (sin citas ni referencias indefinidas) |
| Módulo B | Datos listos: ENACOM y Ookla por provincia, EPH por aglomerado. Falta: Censo 2022, CAMMESA por provincia, Vialidad, ENARGAS, Mapa de Inversiones; el cálculo |
| Módulo C | Datos listos: Banco Mundial (15 indicadores), OCDE (fibra), Ookla (11 países). Falta el cálculo (distancia a la frontera) |

### Cobertura de los datos (2026-10-07)

| Fuente | Rango |
|---|---|
| datos.gob.ar (CAMMESA, gas, ISSP, ISAC, cemento, IPC, PIB, EMAE) | hasta jun/ago-2026 (PIB 2026-T2) |
| IMIG (gasto de capital) | 2016-01 a 2026-08 |
| ENACOM (nacional y 24 provincias) | 2014-T1 a 2026-T2 |
| Ookla (11 países y 24 provincias) | 2019-T1 a 2026-T2 (30 trimestres en `data/raw/ookla/`) |
| EPH (agua, cloaca, gas de red) | 2017-T1 a 2026-T1 |
| Banco Mundial / ITU | hasta 2024 (algunos 2025) |
| OCDE fibra | hasta 2024-T4 (9 pares, sin URY) |

## 2. Cifras del IIP (2026-T2) — donde se citan

Las cifras salen de `python scripts/correr_nacional.py` (= notebook 01). Se citan en
**`seccion_iip.tex`**, **README** (tabla "Último dato") y **CONTEXTO §2** (Resultado 2026-T2).

| | Valor |
|---|---|
| IIP 2026-T2 | **+0,32** (rango +0,09 a +0,74 en 13 variantes) |
| Un año antes / cambio | +0,14 / **+0,18** (rango +0,11 a +0,27) |
| Pilares | Energía +0,91 · Transporte +0,02 · Telecom +1,17 · Agua +0,87 · Inversión −1,37 |
| Por gestión (IIP) | Macri −0,19 · A. Fernández +0,11 · Milei +0,14 (firme solo: Macri el más bajo) |
| Datos citados en el texto | gas 122% del consumo (99% en 2016) · margen de reserva 46% (máx. 62% en 2021; 33% en 2016) · internet 29,6 vs 29,7 c/100 hab. (−25% en 2016) · fibra 50%, −34% vs pares (−73% en 2016) · velocidad 180 vs 286 Mbps (−37%; ~−20% en 2019) · agua 91,0% / cloaca 73,0% · capex 0,19% PIB (0,80% 2023; 1,06% 2016) · velocidad contratada 3,6 → 265 Mbps (2014-2026) |

## 3. Próximos pasos

1. **Usuario:** correr el notebook 01 en Colab (debería dar lo mismo que local) y pegar
   `seccion_iip.tex` en el Overleaf (subir `output/iip_g02_pilares.png` y `output/iip_g04_telecom_pares.png`
   a `figuras/`; bibitems al final del archivo).
2. **Módulo C (internacional):** distancia a la frontera por pilar con Banco Mundial + OCDE + Ookla.
   Evaluar FMI ICSD (stock de capital público). Notebook 02.
3. **Módulo B (provincial):** Censo 2022 (agua, cloacas, gas de red por provincia), CAMMESA por
   provincia (base del informe mensual; datos.energia está congelado en 2020), Mapa de Inversiones,
   Vialidad, ENARGAS. Notebook 03 con ranking y mapa. **Reutilizar el repo hermano
   `consumo_energetico_argentina`**, que ya resolvió CAMMESA por provincia (por tarifa) y ENARGAS.
4. Posibles mejoras del módulo A: estado de rutas (no hay dato abierto), contenedores mensuales (AGP /
   SSPVNyMM), calidad del servicio eléctrico (SAIDI/SAIFI del ENRE, solo AMBA).

## 4. Rutina de actualización (trimestral)

```bash
git pull
python scripts/actualizar_datos.py     # revisar que no haya FALLA y la cobertura del final
python scripts/actualizar_eph.py       # cuando el INDEC publica un trimestre de la EPH
python scripts/actualizar_ookla.py     # en segundo plano: ~3,5 min por trimestre nuevo
python scripts/correr_nacional.py      # revisar resumen y sensibilidad; actualizar cifras (sección 2)
git add -A && git commit -m "Actualizacion <trimestre>" && git push
```

Después: correr el notebook 01 en Colab y actualizar las cifras donde se citan (sección 2).

## 5. PC nueva

```bash
git clone https://github.com/santiagoriverti/infraestuctura_argentina.git
pip install -r requirements.txt
python scripts/correr_nacional.py
```

En Windows correr Python con `PYTHONUTF8=1`. Para la EPH, los zips se leen de `../analisis_EPH/data/raw`
si existe; si no, se bajan del INDEC a `data/raw/eph_zips/` (ignorada por git).
