# CLAUDE.md — instrucciones para sesiones de Claude en este repo

## Al empezar

1. `git pull` antes de cualquier cambio (el usuario trabaja desde más de una PC).
2. Leer **`ESTADO.md`** (estado actual, cifras y dónde se citan, próximos pasos).
3. Si hay que tocar cálculos o fuentes: leer **`CONTEXTO.md`** (marco, metodología, flujo del código,
   trampas), el catálogo `data/reference/catalogo_variables.csv` y `data/README.md`.
4. Si hay que tocar la sección LaTeX: `docs/informe_indicadores/README.md`.
5. Historial de sesiones: `.claude/memory/project.md`.

## Reglas del usuario

- **Commits solo con el usuario (Santiago Riverti). NUNCA agregar `Co-Authored-By: Claude`** ni
  ninguna atribución a Claude en commits o PRs.
- Idioma: español (rioplatense) en respuestas, commits y documentación.
- El usuario corre los notebooks en **Google Colab**; cada notebook termina descargando un ZIP con
  todo (Excel + gráficos). El notebook clona el repo (SETUP con fetch + reset y purga de `src.*`).
  Cuando el usuario pasa un ZIP de Colab: `python scripts/comparar_zip.py RUTA/iip_nacional.zip`
  (antes `python scripts/correr_nacional.py` con el mismo commit).
- El IIP es la **sección 4, "Índice de Infraestructura en Argentina", del documento INECO-UADE
  "Propuesta de Indicadores Económicos"** (Overleaf): `docs/informe_indicadores/seccion_iip.tex`,
  redactada como **propuesta** (pedido del usuario). Usar las claves bibliográficas que ya tiene el
  documento y sus convenciones (trimestres `2026T2`, "RIC", "Índice de Fortaleza Macroeconómica
  Argentina"); probar con `python scripts/probar_seccion_latex.py` antes de entregarla. Cuando el
  usuario pide la sección, entregarle el código listo para copiar y pegar (sección + bibitems nuevos).
- **Decisiones metodológicas del usuario (2026-10-07, CONTEXTO §4):** nombre IIP; telecom como
  distancia a los países de comparación; uso relativo al EMAE; pesos iguales pero configurables;
  pares = BRA CHL URY MEX COL PER AUS CAN ESP USA. No cambiarlas sin acuerdo.
- Comunicar el último dato con su **rango de sensibilidad**; una comparación (entre gestiones, contra
  hace un año) solo es "firme" si se mantiene en todas las variantes de `iip.sensibilidad()`. Los
  promedios por gestión describen condiciones y no evalúan gestiones (la infraestructura es un stock).

## Reglas técnicas que muerden

- Python ≥ 3.10. Windows: correr Python con `PYTHONUTF8=1`.
- **El catálogo es la fuente de verdad de los datos**: para sumar/cambiar una serie se edita
  `catalogo_variables.csv` (api + id_api) y se corre el script de su api. La composición del índice
  (qué variable entra y con qué transformación) está en `VARIABLES` de `src/iip_nacional.py`. En la
  columna `notas` del catálogo: `IIP: ...` si entra al índice, `Fuera del IIP: ...` si no. El CSV no
  usa comillas: en los textos usar `;` en lugar de comas (una coma suelta corre las columnas).
- datos.gob.ar: pedir cada serie sola (juntas, la API las agrega a la menor frecuencia).
- ENACOM: el servidor no manda el certificado intermedio; el descargador lo agrega desde
  `data/reference/certs/`. **Nunca `verify=False`** (además lo bloquea el clasificador de permisos).
- Ookla: ~3,5 min por trimestre; `actualizar_ookla.py` solo baja los trimestres nuevos (cache en
  `data/raw/ookla/`). Correrlo en segundo plano. Licencia CC BY-NC-SA: citarlo siempre.
- Los `.ipynb` se generan con `scripts/gen_notebooks.py`; no editarlos a mano ni con NotebookEdit.
  Verificar con `scripts/correr_nacional.py` y `python -m jupyter nbconvert --to notebook --execute
  notebooks/01_iip_nacional.ipynb --output-dir _local_run` (correrlo desde `notebooks/`).
- Las figuras llevan el prefijo `iip_` (van a la carpeta `figuras/` del Overleaf junto con las de otras
  secciones).
- No escribir scripts con heredocs de bash (rompen `\n` en f-strings).
- No cortar la salida de `correr_nacional.py` con `| head`: el script muere antes de escribir los PNG.
- Trampas de datos (ISSP mal rotulado, peajes, CAMMESA congelado, PIB anualizado, EPH 2016, ITU/OCDE con
  rezago): CONTEXTO §5.

## Cierre de sesión

Actualizar `ESTADO.md` (fecha, cobertura, cifras, próximos pasos) y el historial de
`.claude/memory/project.md`; si cambió la metodología, CONTEXTO §2/§4, la nota del README y la sección
LaTeX (y correr `probar_seccion_latex.py`). Commit + push (si el push pide credenciales, lo hace el
usuario: Claude no ingresa tokens).
