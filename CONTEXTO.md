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

El pilar **Inversión** agrupa los flujos que no son de un sector solo (construcción, cemento,
capex total en % del PIB). El capex sectorial puede ir en su pilar o en Inversión: es una de las
decisiones abiertas (§4).

## 2. Los tres módulos

### A. Nacional (serie trimestral)

¿La infraestructura argentina mejora o empeora? Serie trimestral desde 2014-T1 (inicio de ENACOM);
algunas variables arrancan en 2012 (ISSP, ISAC) o 2016 (IMIG). Las mensuales se llevan a
trimestre (promedio o suma según la variable) y las anuales (potencia instalada) se repiten en los
cuatro trimestres del año.

Variables de la **propuesta v0** (todas descargadas):

| Pilar | Variable | Transformación | Signo |
|---|---|---|---|
| Energía | margen de reserva eléctrica | potencia instalada / potencia máxima de los últimos 12 meses − 1 | + |
| Energía | producción de gas natural | MMm³/día, promedio móvil 4 trimestres | + |
| Transporte | carga ferroviaria | t-km relativas al EMAE (uso independiente del ciclo) | + |
| Transporte | carga aérea | relativa al EMAE | + |
| Telecom | penetración de internet fijo | accesos c/100 hogares | + |
| Telecom | velocidad media de bajada | logaritmo de Mbps | + |
| Telecom | accesos por fibra óptica | % de accesos | + |
| Agua | hogares con agua de red / cloacas | % hogares (EPH, 31 aglomerados) — **pendiente** | + |
| Inversión | capex en infraestructura del SPN | energía + transporte + agua, % del PIB, 4 trimestres móviles | + |
| Inversión | construcción vial | ISAC insumo asfalto, desest. | + |
| Inversión | construcción total | despachos de cemento, desest./promedio móvil | + |

**Normalización propuesta:** la misma del Índice Macroeconómico de `cuentas_publicas` (v9), para que
los dos índices del documento de INECO se lean igual: z robusto (mediana e IQR/1,349 sobre los datos
propios de cada variable, tope ±3), pilar = promedio simple de sus variables, índice = promedio simple
de los pilares disponibles. 0 = lo típico del período.

### B. Provincial (ranking)

¿Dónde está mejor la infraestructura para invertir? Corte transversal de las 24 jurisdicciones,
anual (o censal para agua/cloacas/gas). Normalización entre provincias del mismo año (min-max 0-100
o z), pilares con pesos iguales, ranking y mapa.

Variables: internet (penetración, velocidad, fibra — **descargadas**, trimestral 2014+), agua, cloacas
y gas de red (Censo 2010/2022; EPH para los aglomerados), demanda eléctrica por habitante (CAMMESA),
usuarios de gas (ENARGAS), rutas pavimentadas por km² (DNV + vialidades provinciales), obra pública
nacional por habitante (Mapa de Inversiones), parques industriales (RENPI).

### C. Internacional (benchmark)

¿Cómo está Argentina frente a sus pares? Anual 2000+. Comparación: Brasil, Chile, Uruguay, México,
Colombia, Perú (región); Australia, Canadá, España, EEUU (referencias: países extensos o
exportadores de materias primas); agregados América Latina y el Caribe y OCDE.

Medida propuesta: **distancia a la frontera** dentro del grupo de comparación de cada año,
(x − peor) / (mejor − peor) × 100 (con el signo de la variable), promediada por pilar. Variables
descargadas del Banco Mundial: acceso a electricidad, pérdidas de red, consumo eléctrico por
habitante, banda ancha fija, usuarios de internet, servidores seguros, contenedores (TEU), carga
aérea, LPI (infraestructura y general), FBKF % PIB, agua y saneamiento básicos, empresas con cortes
eléctricos. Candidatas: stock de capital público (FMI ICSD), velocidad medida (Ookla), WEF GCI 2019.

## 3. Sección para el informe de INECO-UADE

Mismo formato que la sección del IIJP (`IPC_jubilados/docs/informe_indicadores/seccion_iijp.tex`):
texto + metodología + 1-2 figuras + bibitems, lista para pegar en el Overleaf. Se escribe cuando el
módulo A tenga cifras. Irá en `docs/informe_indicadores/seccion_infraestructura.tex`.

## 4. Decisiones abiertas (a validar con el usuario)

1. **Nombre.** Trabajo con "Índice de Infraestructura Productiva (IIP)".
2. **Variables con tendencia.** Internet (velocidad 4 → 265 Mbps en 2014-2026) sube siempre: con z
   contra su propia historia el pilar Telecom crece mecánicamente y arrastra el índice. Opciones:
   (a) dejarlo (es mejora real), (b) medir la brecha contra la frontera internacional (usa el
   módulo C), (c) usar variaciones en lugar de niveles.
3. **Variables de uso.** La carga transportada o la demanda eléctrica siguen al ciclo económico más
   que a la infraestructura. Propuesta: relativizarlas al EMAE; alternativa: dejarlas fuera.
4. **Capex sectorial**: en cada pilar o todo junto en el pilar Inversión.
5. **Pesos**: iguales por pilar (como el índice macro). PCA solo como control.
6. **Países de comparación** del módulo C.

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
  CSV están **congelados en feb-2020**. Para la apertura provincial ir a la base del informe
  mensual de CAMMESA. La demanda total y la potencia nacional sí están al día en datos.gob.ar
  (dataset 367 del SSPM).
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
