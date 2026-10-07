# infraestuctura_argentina — historial de sesiones

## Sesión 1 — 2026-10-07: arranque

**Pedido del usuario:** índice de infraestructura argentina que refleje el estado de la
infraestructura que permite a las empresas desarrollarse y atraer inversiones.

**Decisiones del usuario (AskUserQuestion):**
- Unidad: serie **nacional** en el tiempo + **ranking provincial** + **benchmark internacional**
  (Argentina vs otros países).
- Pilares: **todos** (energía; transporte y logística; telecomunicaciones; agua, saneamiento e inversión).
- Destino: **sección del documento INECO-UADE "Propuesta de Indicadores Económicos"** (como el IIJP).

**Hecho:**
- Relevamiento de fuentes verificado contra las APIs (datos.gob.ar series + CKAN, ENACOM, Banco
  Mundial, datos.energia, Mapa de Inversiones). Ver CONTEXTO §5.
- `data/reference/catalogo_variables.csv` (53 variables; 39 con descarga automática).
- `scripts/actualizar_datos.py`: baja las 39 a `data/raw/{nacional,provincial,internacional}.csv`
  (formato largo) + `data/raw/enacom/`. Corrida OK.
- ENACOM: certificado intermedio Sectigo DV R36 faltante → se agrega al bundle de certifi
  (`data/reference/certs/`). `verify=False` fue rechazado por el clasificador de permisos y es la
  regla del repo no usarlo.
- Propuesta metodológica v0 (CONTEXTO §2) con 6 decisiones abiertas (§4).

**Hallazgos de datos:** ISSP con unidades mal rotuladas (carga ferroviaria = miles de t-km); peajes
con quiebre 2018-2019 (−33% vs 2012, probable cambio de cobertura); CAMMESA en datos.energia
congelado en feb-2020; capex de infraestructura del SPN 1,06% PIB (2016) → 0,20% (2025).

**Pendiente:** respuestas del usuario a las decisiones abiertas → módulo A (notebook nacional).
