# Índice de Infraestructura Productiva (IIP) de Argentina

Índice del estado de la infraestructura que usan las empresas para producir, crecer y atraer
inversiones: **energía, transporte y logística, telecomunicaciones, agua y saneamiento, e inversión
en infraestructura**. Proyecto de INECO-UADE; va como sección del documento
*Propuesta de Indicadores Económicos* ([`docs/informe_indicadores/seccion_iip.tex`](docs/informe_indicadores/seccion_iip.tex)).

> Para retomar el trabajo (humanos o Claude): leer primero [`ESTADO.md`](ESTADO.md).
> Metodología completa, decisiones y trampas de las fuentes: [`CONTEXTO.md`](CONTEXTO.md).

## Abrir en Google Colab

| Notebook | Descripción | Link |
|---|---|---|
| **01 — IIP nacional** | Índice trimestral 2016-hoy, 5 pilares y 12 indicadores, con sensibilidad (13 variantes) + 4 gráficos + Excel de 9 hojas, en un ZIP | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/santiagoriverti/infraestuctura_argentina/blob/main/notebooks/01_iip_nacional.ipynb) |

Entorno de ejecución → Ejecutar todas. El notebook clona el repo y al final descarga `iip_nacional.zip`.
Los pesos de los pilares y de las variables, los países de comparación y la referencia (mediana o
el mejor de los pares) se cambian en la celda de parámetros.

## Último dato (2026-T2)

| | 2026-T2 | Un año antes |
|---|---|---|
| **IIP** | **+0,32** (rango de sensibilidad +0,09 a +0,74) | +0,14 |
| Energía | +0,91 | +0,62 |
| Transporte y logística | +0,02 | −0,06 |
| Telecomunicaciones | +1,17 | +0,69 |
| Agua y saneamiento | +0,87 | +0,63 |
| Inversión en infraestructura | −1,37 | −1,21 |

**Lectura:** algo mejor que lo típico de 2016-2026 y en mejora (+0,18 en un año, positiva en las 13
variantes), sostenida por el gas (autoabastecimiento 122%) y las telecomunicaciones (Argentina alcanzó
a sus pares en accesos y acorta la brecha de fibra, aunque su velocidad medida es 37% menor). La
inversión pública en infraestructura está en el mínimo de la serie: 0,19% del PIB.

## Nota metodológica (módulo nacional)

- **Indicadores** (12, en 5 pilares): margen de reserva eléctrica y autoabastecimiento de gas; carga
  ferroviaria y aérea por unidad de actividad (÷ EMAE); accesos a internet fijo, velocidad medida (Ookla)
  y % de fibra **frente a la mediana de 10 países de comparación** (BRA, CHL, URY, MEX, COL, PER, AUS,
  CAN, ESP, USA); hogares con agua de red y cloacas (EPH); gasto de capital nacional en energía,
  transporte y agua (% PIB), ISAC asfalto y despachos de cemento.
- **Normalización:** la del Índice Macroeconómico de `cuentas_publicas`: z robusto (mediana e IQR/1,349
  sobre 2016-hoy, tope ±3). Pilar = promedio de sus indicadores; IIP = promedio de los pilares, **pesos
  iguales y configurables**. 0 = lo típico del período.
- **Encadenamiento hacia atrás** para que la entrada de un indicador (agua 2017, velocidad 2019) no
  produzca saltos; la referencia de los pares se extiende con la tendencia de cada país mientras la ITU y
  la OCDE no publican (hasta 6 trimestres, marcado).
- **Sensibilidad:** 13 variantes; una conclusión es firme si se mantiene en todas. La comparación entre
  gestiones no es firme salvo que el promedio de Macri es el más bajo (la infraestructura es un stock:
  incluye el punto de partida de 2016).

## Tres módulos

| Módulo | Pregunta | Estado |
|---|---|---|
| **A. Nacional** | ¿La infraestructura argentina mejora o empeora? | **v1 implementado** (notebook 01) |
| **B. Provincial** | ¿Dónde está mejor la infraestructura para invertir? | datos de internet (ENACOM, Ookla) y EPH listos; faltan Censo, CAMMESA, Vialidad |
| **C. Internacional** | ¿Cómo está Argentina frente a sus pares? | datos del Banco Mundial, OCDE y Ookla listos; falta el cálculo |

## Datos y scripts

Todas las fuentes son públicas. El catálogo [`data/reference/catalogo_variables.csv`](data/reference/catalogo_variables.csv)
es la fuente de verdad; los datos descargados están versionados (el repo es autocontenido).

| Script | Qué hace | Salida |
|---|---|---|
| `scripts/actualizar_datos.py` | datos.gob.ar, IMIG, ENACOM, Banco Mundial, OCDE | `data/raw/{nacional,provincial,internacional}.csv` |
| `scripts/actualizar_ookla.py` | velocidad medida por país y provincia (~3,5 min por trimestre nuevo) | `data/raw/ookla_fijo.csv` |
| `scripts/actualizar_eph.py` | agua, cloaca y gas de red de los hogares urbanos (EPH) | `data/raw/eph_servicios.csv` |
| `scripts/correr_nacional.py` | calcula el IIP como el notebook | `output/` (Excel + PNG) |
| `scripts/gen_notebooks.py` | genera los `.ipynb` | `notebooks/` |

Velocidad medida: *Speedtest® by Ookla® Global Fixed and Mobile Network Performance Maps* (CC BY-NC-SA 4.0,
uso no comercial).
