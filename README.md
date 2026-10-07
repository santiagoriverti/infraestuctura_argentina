# Índice de Infraestructura Productiva de Argentina

Índice del estado de la infraestructura que usan las empresas para producir, crecer y atraer
inversiones: **energía, transporte y logística, telecomunicaciones, agua y saneamiento, e inversión
en infraestructura**. Proyecto de INECO-UADE; va como sección del documento
*Propuesta de Indicadores Económicos*.

> Para retomar el trabajo (humanos o Claude): leer primero [`ESTADO.md`](ESTADO.md).
> Marco conceptual, metodología propuesta y trampas de las fuentes: [`CONTEXTO.md`](CONTEXTO.md).

**Estado: en construcción (oct-2026).** Las fuentes están relevadas y se descargan solas; la
metodología es una propuesta (v0) a validar. Todavía no hay índice calculado.

---

## Tres módulos

| Módulo | Pregunta | Unidad | Frecuencia |
|---|---|---|---|
| **A. Nacional** | ¿La infraestructura argentina mejora o empeora? | Argentina | trimestral, 2014-hoy |
| **B. Provincial** | ¿Dónde está mejor la infraestructura para invertir? | 24 jurisdicciones | anual / censal |
| **C. Internacional** | ¿Cómo está Argentina frente a sus pares? | 11 países + América Latina y OCDE | anual, 2000-hoy |

Los tres comparten los mismos cinco pilares. Detalle de variables, fuentes y transformaciones:
[`CONTEXTO.md`](CONTEXTO.md) y el catálogo [`data/reference/catalogo_variables.csv`](data/reference/catalogo_variables.csv).

## Datos

Todas las fuentes son públicas y sin clave. `scripts/actualizar_datos.py` baja las series del
catálogo y las guarda en formato largo en `data/raw/`:

| Archivo | Contenido |
|---|---|
| `data/raw/nacional.csv` | `codigo, fecha, valor` — CAMMESA, INDEC (ISSP, ISAC), Hacienda (IMIG), ENACOM, auxiliares (IPC, PIB, EMAE) |
| `data/raw/provincial.csv` | `codigo, provincia, fecha, valor` — ENACOM por provincia (por ahora) |
| `data/raw/internacional.csv` | `codigo, iso3, pais, anio, valor` — Banco Mundial (WDI, LPI, Enterprise Surveys) |
| `data/raw/enacom/` | Archivos de ENACOM tal como se publican |

```bash
python scripts/actualizar_datos.py
```

## Estructura

```
data/reference/catalogo_variables.csv   fuente de verdad: qué variable, de dónde, con qué signo
data/reference/certs/                   certificado intermedio de ENACOM (ver CONTEXTO §5)
data/raw/                               datos descargados (versionados: el repo es autocontenido)
scripts/actualizar_datos.py             descarga todo el catálogo
notebooks/                              (próximo) un notebook por módulo, para Google Colab
docs/informe_indicadores/               (próximo) sección LaTeX para el documento de INECO-UADE
```
