# CLAUDE.md — instrucciones para sesiones de Claude en este repo

## Al empezar

1. `git pull` antes de cualquier cambio (el usuario trabaja desde más de una PC).
2. Leer **`ESTADO.md`** (estado actual y próximos pasos).
3. Si hay que tocar cálculos o fuentes: leer **`CONTEXTO.md`** (marco, metodología, trampas) y el
   catálogo `data/reference/catalogo_variables.csv`.
4. Historial de sesiones: `.claude/memory/project.md`.

## Reglas del usuario

- **Commits solo con el usuario (Santiago Riverti). NUNCA agregar `Co-Authored-By: Claude`** ni
  ninguna atribución a Claude en commits o PRs.
- Idioma: español (rioplatense) en respuestas, commits y documentación.
- El usuario corre los notebooks en **Google Colab**; cada notebook termina descargando un ZIP con
  todo (Excel + gráficos). El notebook clona el repo (SETUP con fetch + reset y purga de `src.*`).
- El índice va como **sección del documento INECO-UADE "Propuesta de Indicadores Económicos"**
  (Overleaf): `docs/informe_indicadores/seccion_iip.tex`, mismo formato que
  `IPC_jubilados/docs/informe_indicadores/seccion_iijp.tex`.
- **Decisiones metodológicas del usuario (2026-10-07, CONTEXTO §4):** nombre IIP; telecom como
  distancia a los países de comparación; uso relativo al EMAE; pesos iguales pero configurables;
  pares = BRA CHL URY MEX COL PER AUS CAN ESP USA. No cambiarlas sin acuerdo.
- Comunicar el último dato con su **rango de sensibilidad**; una comparación (entre gestiones, contra
  hace un año) solo es "firme" si se mantiene en todas las variantes de `iip.sensibilidad()`.

## Reglas técnicas que muerden

- Windows: correr Python con `PYTHONUTF8=1`.
- **El catálogo es la fuente de verdad de los datos**: para sumar/cambiar una serie se edita
  `catalogo_variables.csv` (api + id_api) y se corre el script de su api. La composición del índice
  (qué variable entra y con qué transformación) está en `VARIABLES` de `src/iip_nacional.py`.
- datos.gob.ar: pedir cada serie sola (juntas, la API las agrega a la menor frecuencia).
- ENACOM: el servidor no manda el certificado intermedio; el descargador lo agrega desde
  `data/reference/certs/`. **Nunca `verify=False`.**
- Ookla: ~3,5 min por trimestre; `actualizar_ookla.py` solo baja los trimestres nuevos (cache en
  `data/raw/ookla/`). Correrlo en segundo plano. Licencia CC BY-NC-SA: citarlo siempre.
- Los `.ipynb` se generan con `scripts/gen_notebooks.py`; no editarlos a mano ni con NotebookEdit.
  Verificar con `scripts/correr_nacional.py` y/o `jupyter nbconvert --execute` (salida en `_local_run/`).
- No escribir scripts con heredocs de bash (rompen `\n` en f-strings).
- No cortar la salida de `correr_nacional.py` con `| head`: el script muere antes de escribir los PNG.
- Trampas de datos (ISSP mal rotulado, peajes, CAMMESA congelado, PIB anualizado, EPH 2016, ITU/OCDE con
  rezago): CONTEXTO §5.

## Cierre de sesión

Actualizar `ESTADO.md` (fecha, cobertura, cifras, próximos pasos) y el historial de
`.claude/memory/project.md`; si cambió la metodología, CONTEXTO §2/§4 y la sección LaTeX. Commit + push
(si el push pide credenciales, lo hace el usuario: Claude no ingresa tokens).
