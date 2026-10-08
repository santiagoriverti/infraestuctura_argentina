# CONTEXTO — marco conceptual, metodología y fuentes

> Documento de referencia para tocar cálculos. Estado y próximos pasos: [`ESTADO.md`](ESTADO.md).
> La lista completa de variables (con id de API, unidad, signo y estado) está en
> [`data/reference/catalogo_variables.csv`](data/reference/catalogo_variables.csv): **el catálogo
> es la fuente de verdad**; si una variable cambia, se cambia ahí y el descargador la sigue.

## 1. Qué mide

La **infraestructura productiva**: los servicios de red que una empresa necesita para operar y que
pesan en la decisión de invertir — energía disponible y confiable, rutas/trenes/puertos para mover
carga, conectividad, agua y cloacas, y el ritmo de inversión que repone y amplía ese stock. No mide
infraestructura social (escuelas, hospitales, vivienda) salvo como referencia.

Referencias de marco: pilar 2 (Infraestructura) del Global Competitiveness Index del WEF (última
edición 2019), Logistics Performance Index del Banco Mundial, Infrascope (BID/EIU), y los índices
compuestos de la OCDE/JRC (*Handbook on Constructing Composite Indicators*, 2008).

### Pilares y dimensiones

| Pilar | Cobertura | Capacidad | Calidad | Uso | Inversión |
|---|---|---|---|---|---|
| **Energía** | hogares con gas de red | margen de reserva eléctrica, producción de gas | pérdidas de red, cortes | demanda eléctrica | capex energía (IMIG) |
| **Transporte y logística** | rutas pavimentadas | — | estado de rutas, LPI | carga ferroviaria y aérea, contenedores | capex transporte, ISAC asfalto |
| **Telecomunicaciones** | accesos a internet fijo c/100 hogares | — | velocidad, % fibra | — | — |
| **Agua y saneamiento** | hogares con agua de red y cloacas | — | — | — | capex agua (IMIG) |
| **Inversión** | — | stock de capital público | — | — | capex infraestructura % PIB, construcción, cemento |

El pilar **Inversión** agrupa los flujos de inversión: el gasto de capital nacional de los tres
sectores (energía, transporte y agua) va todo ahí, junto con la construcción vial y el cemento. Los
pilares sectoriales miden el estado (cobertura, capacidad, calidad, uso) y el de Inversión, el flujo
que lo va a cambiar.

## 2. Los tres módulos

### A. Nacional (serie trimestral) — v1, implementado

¿La infraestructura argentina mejora o empeora? Código: `src/iip_nacional.py` (cálculo) y
`src/graficos.py`; notebook `notebooks/01_iip_nacional.ipynb` (generado por `scripts/gen_notebooks.py`);
corrida local `scripts/correr_nacional.py` → `output/`.

**Flujo del código** (`src/iip_nacional.py`): `calcular(base, **parametros)` → `cargar()` (lee
`data/raw/`) → `construir_variables()` (las 12 transformaciones de `VARIABLES`; brechas con
`_referencia()` + `_extrapolar()`) → corte en el último trimestre con dato propio en ≥ la mitad de las
variables → `_arrastrar()` → `normalizar()` (z robusto) → `agregar()` (`_encadenado()` o
`_promedio_ponderado()`) → `por_gobierno()`. `sensibilidad()` recalcula con las variantes de
`variantes()`. `exportar_excel(res, ruta, sens)` arma el Excel (9 hojas; 8 si no se le pasa la
sensibilidad); `src/graficos.py` (`todos()`) los 4 PNG
`iip_g0*.png`. Todos los parámetros y sus valores por defecto están en `PARAMETROS`.

**Ventana:** 2016-T1 a hoy (parámetro `inicio`). El último trimestre es el último con dato propio en al
menos la mitad de las variables. Las mensuales se llevan a trimestre con ventanas de 12 meses tomadas en
el último mes del trimestre (sacan la estacionalidad) o con el promedio de los 3 meses (ISAC, ya
desestacionalizado).

| Pilar | Variable | Transformación | Fuente |
|---|---|---|---|
| Energía | margen de reserva eléctrica | potencia instalada / pico de demanda de los últimos **36** meses − 1 (con 12 meses saltaba con el clima de un verano). La instalada es anual (stock a diciembre): va al 4to trimestre y se interpola; después del último año se repite (marcado) | CAMMESA |
| Energía | autoabastecimiento de gas | producción / consumo entregado, 12 meses | SE, ENARGAS |
| Transporte | carga ferroviaria | t-km de 12 meses / EMAE promedio de 12 meses (2016 = 100) | INDEC ISSP |
| Transporte | carga aérea | ídem | INDEC ISSP |
| Telecom | penetración de internet fijo | Argentina (ENACOM, c/100 hab.) / referencia de los pares (ITU, dato anual = stock a diciembre → 4to trimestre, interpolado) − 1 | ENACOM, ITU |
| Telecom | velocidad medida | Argentina / referencia de los pares − 1, desde 2019-T1 | Ookla |
| Telecom | accesos por fibra | % de Argentina / referencia de los pares − 1 (OCDE semestral, interpolado). Cociente y no diferencia: en una curva de adopción en S la diferencia en p.p. se agranda aunque Argentina se acerque (2019: 7% vs 19%; 2025: 47% vs 69%) | ENACOM, OCDE |
| Agua | hogares con agua de red | % hogares, promedio de 4 trimestres (saca ruido muestral) | EPH |
| Agua | hogares con cloaca | ídem | EPH |
| Inversión | gasto de capital nacional en infraestructura | energía + transporte + agua (Nación + transf. a provincias), 12 meses / PIB nominal | IMIG, INDEC |
| Inversión | construcción vial | ISAC insumo asfalto, desest., promedio trimestral | INDEC ISAC |
| Inversión | despachos de cemento | suma de 12 meses | INDEC |

**Telecomunicaciones contra los pares (decisión del usuario, oct-2026).** La velocidad (3,6 → 265 Mbps
contratados en 2014-2026) y la fibra suben solas con la tecnología: contra su propia historia el pilar
crecería mecánicamente. Por eso se mide la **brecha** de Argentina contra la **mediana** de los 10
países de comparación (parámetro `referencia="mejor"` para medir contra la frontera del grupo). La
referencia exige al menos 5 pares con dato. La velocidad es la **medida** de Ookla (ENACOM solo publica
la contratada, y solo de Argentina).

**Uso relativo a la actividad.** La carga transportada sigue al ciclo; dividida por el EMAE mide si la
red absorbe más o menos carga por unidad de actividad.

**Normalización:** la del Índice Macroeconómico de `cuentas_publicas` (v9; en el documento de INECO se
llama "Índice de Fortaleza Macroeconómica Argentina"), para que los dos índices del documento se lean igual: z robusto (mediana e IQR/1,349 sobre los datos propios de la ventana,
con el signo de la variable, tope ±3). Pilar = promedio ponderado de sus variables; IIP = promedio
ponderado de los pilares. **Pesos iguales por defecto, configurables** (`pesos_pilares`,
`pesos_variables` en la celda de parámetros del notebook). 0 = lo típico del período.

**Encadenamiento hacia atrás** (`encadenar=True`): el último trimestre es el promedio de todas las
variables (la cifra titular no cambia); hacia atrás, cada trimestre difiere del siguiente en el promedio
ponderado de las variaciones de las variables presentes en ambos. Sin esto, la entrada de la velocidad
medida (2019-T1, con una brecha chica) hacía saltar Telecom +1,1 y el IIP +0,2 en un trimestre. Se
aplica igual a los pilares dentro del IIP (Agua entra en 2017-T4).

**Rezagos y arrastres:**
- La ITU y la OCDE publican con ~1,5 años de rezago (hoy llegan a 2024-T4). La referencia de los pares
  se **extiende con la tendencia lineal de cada país** (últimos 8 trimestres, fibra acotada a 100%)
  hasta `max_rezago_pares` = 6 trimestres, marcado como arrastre. Repetir el último dato sobreestimaba a
  Argentina (los pares siguen creciendo); dejar caer las variables cambiaba la composición del pilar.
- Para el resto, después del último dato propio se repite el último valor a lo sumo `max_arrastre` = 4
  trimestres; más allá, la variable queda vacía. Todo arrastre queda marcado (hoja Arrastrados).

**Sensibilidad** (`iip.sensibilidad()`, hoja Sensibilidad): 13 variantes — base, referencia = el mejor
de los pares, sin cada pilar (5), Inversión solo con gasto de capital, ventana desde 2017, arrastre 2,
referencia sin extender, sin encadenar, tope ±2. Una conclusión es **firme** si se mantiene en todas.

**Resultado 2026-T2 (oct-2026):** IIP **+0,32** (rango +0,09 a +0,74: por encima de lo típico en todas
las variantes); cambio en 12 meses **+0,18** (rango +0,11 a +0,27: mejora firme). Pilares: Energía
+0,91 · Transporte +0,02 · Telecom +1,17 · Agua +0,87 · Inversión −1,37. Por gestión: Macri −0,19 ·
A. Fernández +0,11 · Milei +0,14. Firme: Macri el más bajo en las 13 (advertencia: es un stock y la
ventana arranca en 2016, así que incluye el punto de partida heredado; sin Energía la diferencia es
mínima). **No firme:** A. Fernández vs Milei.

**Fuera del índice (a propósito):**
- *Hogares que cocinan con gas de red* (EPH): cae de 70% a 65% desde 2022, más por la suba de tarifas
  (cambio a electricidad o garrafa) que por menos red. Mide uso, no conexión.
- *Demanda eléctrica*: uso con signo ambiguo (eficiencia vs electrificación).
- *Peajes*: quiebre de cobertura 2018-2019 (§5).
- *Velocidad contratada de ENACOM*: no comparable con otros países.

### B. Provincial (ranking)

¿Dónde está mejor la infraestructura para invertir? Corte transversal de las 24 jurisdicciones,
anual (o censal para agua/cloacas/gas). Normalización entre provincias del mismo año (min-max 0-100
o z), pilares con pesos iguales, ranking y mapa.

Variables: internet (penetración, velocidad, fibra — **descargadas**, trimestral 2014+), agua, cloacas
y gas de red (Censo 2010/2022; EPH para los aglomerados), demanda eléctrica por habitante (CAMMESA),
usuarios de gas (ENARGAS), rutas pavimentadas por km² (DNV + vialidades provinciales), obra pública
nacional por habitante (Mapa de Inversiones), parques industriales (RENPI).

Para CAMMESA por provincia y ENARGAS, **reutilizar el repo hermano `consumo_energetico_argentina`**
(`src/fuentes.py`): ya baja la Base del Informe Mensual de CAMMESA (demanda por agente, provincia y
tarifa, 2012+) y los datos de ENARGAS por provincia desde el pivot cache de sus Excel. Para Ookla por
provincia ya está `data/raw/ookla_fijo.csv` (`nivel = provincia`) y para la EPH, `eph_servicios.csv`
por aglomerado (falta mapear aglomerado → provincia).

### C. Internacional (benchmark)

¿Cómo está Argentina frente a sus pares? Anual 2000+. Comparación: Brasil, Chile, Uruguay, México,
Colombia, Perú (región); Australia, Canadá, España, EEUU (referencias: países extensos o
exportadores de materias primas); agregados América Latina y el Caribe y OCDE.

Medida propuesta: **distancia a la frontera** dentro del grupo de comparación de cada año,
(x − peor) / (mejor − peor) × 100 (con el signo de la variable), promediada por pilar. Variables
descargadas: Banco Mundial (acceso a electricidad, pérdidas de red, consumo eléctrico por habitante,
banda ancha fija, usuarios de internet, servidores seguros, contenedores (TEU), carga aérea, LPI,
FBKF % PIB, agua y saneamiento básicos, empresas con cortes eléctricos), OCDE (% fibra) y Ookla
(velocidad medida, trimestral). Candidatas: stock de capital público (FMI ICSD), WEF GCI 2019.

## 3. Sección para el informe de INECO-UADE

`docs/informe_indicadores/seccion_iip.tex` es la sección 4, "Índice de Infraestructura en Argentina",
del documento *Propuesta de Indicadores Económicos* (Overleaf; el documento no está en el repo). La
introducción del documento la presenta como un índice "que debería desarrollarse en su totalidad" y que
"evalúe la inversión en obra pública": por eso está redactada como **propuesta** (pedido del usuario,
2026-10-08) — introducción, propuesta metodológica con un cuadro de pilares "versión preliminar / a
incorporar", resultados preliminares (2 figuras + cuadro por gestión) y próximos pasos.

Estructura del documento, preámbulo, bibitems existentes, convenciones (trimestres `2026T2`, "RIC",
"Cuadro"), cómo pegarla y cómo probarla (`scripts/probar_seccion_latex.py`):
[`docs/informe_indicadores/README.md`](docs/informe_indicadores/README.md).

## 4. Decisiones (respondidas por el usuario, 2026-10-07)

1. **Nombre:** Índice de Infraestructura Productiva (IIP).
2. **Variables con tendencia:** se miden como **distancia a los países de comparación** (telecom).
3. **Variables de uso:** relativas al EMAE.
4. **Capex sectorial:** a criterio de Claude → todo en el pilar Inversión (§1).
5. **Pesos:** iguales, pero **configurables** (celda de parámetros del notebook).
6. **Países de comparación:** Brasil, Chile, Uruguay, México, Colombia, Perú, Australia, Canadá,
   España y EEUU.

## 5. Fuentes y trampas conocidas

- **datos.gob.ar (API Series de Tiempo):** pedir **cada serie por separado**. Si se piden juntas
  series de distinta frecuencia, la API las agrega todas a la menor (p. ej. potencia instalada,
  anual, convierte a anual también a las mensuales).
- **ISSP del INDEC (dataset 302):** la API rotula "2004=100" series que en realidad están en
  unidades: carga ferroviaria = **miles de t-km** (~10.000 M t-km/año). La unidad de carga aérea
  está sin confirmar.
- **Peajes (ISSP, uteqs):** ~20 M/mes en 2012-2017, bajan desde 2018 (antes de la pandemia) y no
  se recuperan (2019: 15,5 M; 2025: 13,7 M/mes, −33% vs 2012). Probable cambio de cobertura (rutas que dejaron de cobrar peaje, cambios de
  concesión), no menos tránsito. **No usar sin revisar.**
- **CAMMESA en datos.energia.gob.ar** (demanda por agente y provincia, potencia por central): los
  CSV están **congelados en feb-2020**. Para la apertura provincial ir a la Base del Informe Mensual
  de CAMMESA (ya resuelto en el repo `consumo_energetico_argentina`). La demanda total y la potencia
  nacional sí están al día en datos.gob.ar (dataset 367 del SSPM).
- **ENACOM** (`indicadores.enacom.gob.ar/Files/DatosAbiertos/*.csv`): el servidor no envía el
  certificado intermedio (Sectigo Public Server Authentication CA DV R36) y Python falla con
  `CERTIFICATE_VERIFY_FAILED`. Solución: el intermedio está en `data/reference/certs/` y el
  descargador lo agrega al bundle de certifi (la verificación sigue completa). **No usar
  `verify=False`.** El intermedio vence en 2036.
- **ENACOM, contenido:** la velocidad media es la **contratada**, no la medida; la penetración
  cuenta accesos, no hogares (CABA supera 100).
- **IMIG** (CSV mensual 2016+, dataset 452.3): gasto de capital por finalidad (energía, transporte,
  agua, vivienda, educación, otros), Nación + transferencias a provincias, en millones de $
  nominales. Para antes de 2016 habría que ir al Presupuesto Abierto (a verificar).
- **PIB nominal** (`4.4_OGP_2004_T_17`): viene trimestral **anualizado**: anual = suma / 4.
- **Banco Mundial:** agua y saneamiento de Argentina solo hasta 2016 (JMP); Enterprise Surveys
  de Argentina solo 2006, 2010 y 2017; LPI cada 2-4 años (2007-2018 y 2022); carga ferroviaria
  y km de vías desactualizados (no se usan).
- **Mapa de Inversiones** (`mapainversiones.obraspublicas.gob.ar/opendata/dataset_mop.csv`):
  7.285 obras 2008-2024 con provincia, sector y monto; viene en latin-1. Cubre la cartera de la
  Secretaría de Obras Públicas, no toda la obra pública.
- **Vialidad:** no hay dato abierto actualizado del estado de las rutas por provincia; el dataset
  "Pavimentos" (DNV, 2019) solo trae el material de calzada.
- **Ookla Open Data** (`scripts/actualizar_ookla.py`): un parquet de ~350 MB por trimestre (teselas de
  zoom 16 del mundo, sin país). Los archivos 2019-2022 no traen coordenadas: se ubican por el `quadkey`.
  Se bajan solo las columnas necesarias (~3,5 min por trimestre); cada trimestre queda en
  `data/raw/ookla/` y no se vuelve a bajar. País = polígono de Natural Earth 1:50m, provincia = polígono
  del IGN, ambos simplificados a ~0,005° y versionados en `data/reference/geo/` (el WFS del IGN devuelve
  los nombres con la codificación rota: se identifican por código INDEC). Velocidad = promedio de
  teselas ponderado por tests. **Licencia CC BY-NC-SA 4.0**: uso no comercial y citar "Speedtest® by
  Ookla® Global Fixed and Mobile Network Performance Maps".
- **ITU (DataHub):** la API no es pública (403). La penetración de los pares sale del Banco Mundial
  (`IT.NET.BBND.P2`, que es la ITU); el dato anual es el stock a diciembre y coincide con ENACOM del 4to
  trimestre (2014-2024, diferencias < 0,4).
- **OCDE (SDMX, `DSD_BB_DATABASE@DF_BB_TEL_DATABASE`):** % de suscripciones por fibra (`FIB`,
  `PT_SB_FBB`), Q2 y Q4. Cubre 9 de los 10 pares (falta Uruguay) y no a Argentina.
- **EPH** (`scripts/actualizar_eph.py`): los zips de 2016 no están en el FTP del INDEC con el nombre
  estándar → la serie arranca en 2017-T1. Lee los zips de `../analisis_EPH/data/raw` si existen. Agua y
  cloaca son casi planas (~90% y ~73%) y con ruido muestral de ~0,5 p.p.: van suavizadas.
