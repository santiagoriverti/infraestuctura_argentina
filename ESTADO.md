# ESTADO DEL PROYECTO — infraestuctura_argentina

> Punto de entrada para retomar el trabajo en otra sesión o en otra PC.
> Última actualización: **2026-10-08** (cierre de la sesión 1).
> Siguiente tarea: **el usuario pega la sección LaTeX en el Overleaf**; después, módulo C
> (internacional) o B (provincial), a elección del usuario.

## 1. Dónde estamos

| Ítem | Estado |
|---|---|
| Diseño | Módulos **A nacional** + **B provincial** + **C internacional**; 5 pilares; sección 4 del documento INECO-UADE |
| Decisiones del usuario | Respondidas (CONTEXTO §4): nombre IIP, telecom contra los pares, uso ÷ EMAE, pesos iguales configurables, 10 pares |
| **Módulo A** | **v1 implementado**: `src/iip_nacional.py` + `src/graficos.py`, notebook `01_iip_nacional.ipynb`. **Verificado en Colab (2026-10-08, código del commit d99d860): idéntico a local en las 9 hojas** (`comparar_zip.py`: IDENTICO). Los commits posteriores no cambian el cálculo |
| Sección LaTeX | `docs/informe_indicadores/seccion_iip.tex`, redactada como **propuesta** para la sección 4 del documento. `probar_seccion_latex.py`: OK (0 errores, 0 indefinidas, 0 desbordes). **Falta que el usuario la pegue en el Overleaf** (instrucciones en `docs/informe_indicadores/README.md`) |
| Módulo B (provincial) | Datos listos: ENACOM (3 series) y Ookla por provincia, EPH por aglomerado. Falta: Censo 2022, CAMMESA por provincia (reutilizar `consumo_energetico_argentina`), Mapa de Inversiones, Vialidad, ENARGAS; mapeo aglomerado → provincia; el cálculo y el notebook |
| Módulo C (internacional) | Datos listos: Banco Mundial (15 indicadores), OCDE (fibra), Ookla (11 países). Falta el cálculo (distancia a la frontera por pilar) y el notebook |
| Catálogo | 59 series: 48 descargadas (42 con `actualizar_datos.py`, 3 EPH, 3 Ookla), 1 verificada sin descarga automática (Mapa de Inversiones), 10 candidatas |

### Cobertura de los datos (descarga del 2026-10-07)

| Fuente | Rango |
|---|---|
| datos.gob.ar (CAMMESA, gas, ISSP, ISAC, cemento, IPC, PIB, EMAE) | hasta jun/ago/sep-2026 según la serie (PIB 2026-T2) |
| IMIG (gasto de capital) | 2016-01 a 2026-08 |
| ENACOM (nacional y 24 provincias) | 2014-T1 a 2026-T2 |
| Ookla (11 países y 24 provincias) | 2019-T1 a 2026-T2 (30 trimestres en `data/raw/ookla/`) |
| EPH (agua, cloaca, gas de red) | 2017-T1 a 2026-T1 |
| Banco Mundial / ITU | hasta 2024 (algunos 2025) |
| OCDE fibra | hasta 2024-T4 (9 pares, sin URY) |

## 2. Cifras del IIP (2026-T2) — dónde se citan

Las cifras salen de `python scripts/correr_nacional.py` (= notebook 01). Se citan en
**`seccion_iip.tex`** (texto y Cuadro de gestiones), **README** (tabla "Último dato" y "Lectura"),
**CONTEXTO §2** ("Resultado 2026-T2") y la memoria global de Claude. Si los datos cambian, actualizar
todas.

| | Valor |
|---|---|
| IIP 2026-T2 | **+0,32** (rango +0,09 a +0,74 en 13 variantes) |
| Un año antes / cambio | +0,14 / **+0,18** (rango +0,11 a +0,27) |
| Pilares 2026-T2 | Energía +0,91 · Transporte +0,02 · Telecom +1,17 · Agua +0,87 · Inversión −1,37 |
| Pilares un año antes | Energía +0,62 · Transporte −0,06 · Telecom +0,69 · Agua +0,63 · Inversión −1,21 |
| Por gestión (IIP) | Macri −0,19 · A. Fernández +0,11 · Milei +0,14 (firme solo: Macri el más bajo) |
| Por gestión (pilares E/T/Tel/A/I) | Macri −0,89/+0,06/+0,02/−0,55/+0,72 · A. Fernández +0,56/−0,08/+0,28/−0,28/+0,06 · Milei +0,58/−0,12/+0,74/+0,70/−1,18 |
| Datos citados en el texto | gas 122% del consumo (99% en 2016) · margen de reserva 46% (máx. 62% en 2021; 33% en 2016) · internet 29,6 vs 29,7 c/100 hab. (−25% en 2016) · fibra 50%, −34% vs pares (−73% en 2016) · velocidad 180 vs 286 Mbps (−37%; ~−20% en 2019) · agua 91,0% / cloaca 73,0% · capex 0,19% PIB (0,80% 2023; 1,06% 2016) · velocidad contratada 3,6 → 265 Mbps (2014-2026) |

## 3. Próximos pasos

1. **Usuario:** pegar `seccion_iip.tex` en el Overleaf (ver `docs/informe_indicadores/README.md`:
   reemplazar la sección 4, subir `iip_g02_pilares.png` e `iip_g04_telecom_pares.png` a `figuras/`,
   pegar los 9 bibitems nuevos).
2. Opcional (si el usuario lo pide): figuras sin título interno para el documento (el `\caption` ya
   lo dice).
3. **Módulo C (internacional):** distancia a la frontera por pilar, (x − peor)/(mejor − peor), con
   Banco Mundial + OCDE + Ookla; evaluar FMI ICSD (stock de capital público). Notebook 02.
4. **Módulo B (provincial):** Censo 2022 (agua, cloacas, gas de red por provincia), CAMMESA por
   provincia (reutilizar `consumo_energetico_argentina/src/fuentes.py`), Mapa de Inversiones, Vialidad,
   ENARGAS, Ookla y ENACOM ya descargados. Notebook 03 con ranking y mapa.
5. Mejoras del módulo A (indicadores "a incorporar" de la sección): calidad del servicio eléctrico
   (SAIDI/SAIFI del ENRE, solo AMBA), estado de la red vial (sin dato abierto), contenedores mensuales
   (AGP / SSPVNyMM), cobertura móvil 4G/5G.

## 4. Rutina de actualización (cuando hay datos nuevos; idealmente trimestral)

```bash
git pull
python scripts/actualizar_datos.py     # revisar que no haya FALLA y la cobertura del final
python scripts/actualizar_eph.py       # cuando el INDEC publica un trimestre de la EPH
python scripts/actualizar_ookla.py     # en segundo plano: ~3,5 min por trimestre nuevo
python scripts/correr_nacional.py      # revisar resumen y sensibilidad
git add -A && git commit -m "Actualizacion <trimestre>" && git push
```

Después: correr el notebook 01 en Colab, `python scripts/comparar_zip.py RUTA/iip_nacional.zip`
(tiene que dar IDENTICO), actualizar las cifras donde se citan (sección 2), `python
scripts/probar_seccion_latex.py` y volver a subir sección y figuras al Overleaf.

## 5. PC nueva

```bash
git clone https://github.com/santiagoriverti/infraestuctura_argentina.git
cd infraestuctura_argentina
pip install -r requirements.txt
python scripts/correr_nacional.py
```

- Python ≥ 3.10. En Windows, `PYTHONUTF8=1` (PowerShell: `$env:PYTHONUTF8 = "1"`; Git Bash:
  `export PYTHONUTF8=1`).
- Los datos están versionados: `correr_nacional.py` reproduce el índice sin descargar nada y tiene que
  imprimir `IIP 2026-T2: +0.32` (con los datos actuales).
- Commits con el usuario: `git config user.name "Santiago Riverti"` y su email. Si el push pide
  credenciales, las ingresa el usuario (Git Credential Manager).
- EPH: los zips se leen de `../analisis_EPH/data/raw` si existe; si no, `actualizar_eph.py` los baja del
  INDEC a `data/raw/eph_zips/` (ignorada por git).
- Para `probar_seccion_latex.py`: `pdflatex` (MiKTeX o TeX Live). Sin él, el script solo revisa las citas.
- Para ejecutar el notebook localmente: `nbconvert` e `ipykernel` (en `requirements.txt`).

## 6. Verificaciones hechas al cierre (2026-10-08)

- `scripts/correr_nacional.py`: IIP 2026-T2 +0,32, igual que el notebook.
- `scripts/comparar_zip.py` con el ZIP de Colab del usuario: IDENTICO (9 hojas, 4 gráficos).
- Notebook 01 con `nbconvert --execute`: 0 errores.
- `scripts/probar_seccion_latex.py`: OK (12 claves citadas: 3 del documento y 9 nuevas).
