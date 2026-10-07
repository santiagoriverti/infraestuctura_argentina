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
  todo (Excel + gráficos). Los notebooks leen los datos de GitHub (`raw.githubusercontent.com/.../main`).
- El índice va como **sección del documento INECO-UADE "Propuesta de Indicadores Económicos"**
  (Overleaf), con el mismo formato que `IPC_jubilados/docs/informe_indicadores/seccion_iijp.tex`.
- La metodología es una **propuesta v0**: no darla por cerrada sin las respuestas del usuario a las
  decisiones abiertas (CONTEXTO §4).

## Reglas técnicas que muerden

- Windows: correr Python con `PYTHONUTF8=1`.
- **El catálogo es la fuente de verdad**: para sumar/cambiar una variable se edita
  `catalogo_variables.csv` (api + id_api) y se corre `scripts/actualizar_datos.py`.
- datos.gob.ar: pedir cada serie sola (juntas, la API las agrega a la menor frecuencia).
- ENACOM: el servidor no manda el certificado intermedio; el descargador lo agrega desde
  `data/reference/certs/`. **Nunca `verify=False`.**
- Los `.ipynb` se generan con scripts de Python (como en los otros repos del usuario); no editarlos
  con NotebookEdit. No escribir scripts con heredocs de bash (rompen `\n` en f-strings).
- Trampas de datos (unidades mal rotuladas del ISSP, peajes, CAMMESA congelado, PIB anualizado):
  CONTEXTO §5.

## Cierre de sesión

Actualizar `ESTADO.md` (fecha, cobertura, próximos pasos) y el historial de
`.claude/memory/project.md`; si cambió la metodología, CONTEXTO §2/§4. Commit + push (si el push pide
credenciales, lo hace el usuario: Claude no ingresa tokens).
