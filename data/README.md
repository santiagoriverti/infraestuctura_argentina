# Datos — diccionario y procedencia

Todo lo que está acá es público y está versionado: el repo es autocontenido y el notebook de Colab lee
estos archivos. **No editar `raw/` a mano**: se regenera con los scripts de `scripts/`. Los valores son
crudos; las transformaciones del índice están en `VARIABLES` de `src/iip_nacional.py`.

**Convención de fechas:** `fecha` = primer día del período (`AAAA-MM-DD`). Mensual → día 1 del mes;
trimestral → día 1 del trimestre (2026-T2 = `2026-04-01`); anual → `AAAA-01-01`.

## `raw/` — datos descargados

| Archivo | Columnas | Lo genera | Contenido |
|---|---|---|---|
| `nacional.csv` | `codigo, fecha, valor` | `actualizar_datos.py` | 23 códigos de los módulos `nacional` y `auxiliar` del catálogo (datos.gob.ar, IMIG, ENACOM). Mezcla frecuencias. Unidad de cada código: columna `unidad` del catálogo |
| `provincial.csv` | `codigo, provincia, fecha, valor` | `actualizar_datos.py` | ENACOM por provincia (3 códigos, 24 jurisdicciones, 2014-T1+). `provincia` con los nombres de ENACOM ("Santiago Del Estero", "Tierra Del Fuego"; ver `reference/provincias.csv`) |
| `internacional.csv` | `codigo, iso3, pais, fecha, valor` | `actualizar_datos.py` | Banco Mundial (15 indicadores, anual 2000+) y OCDE (`fibra_share`, semestral: fechas `-04-01` = Q2 y `-10-01` = Q4). 11 países + `LCN` (América Latina y el Caribe) y `OED` (OCDE) |
| `enacom/*.csv` | los de ENACOM (`anio, trimestre, [provincia,] ...`) | `actualizar_datos.py` | Los 6 archivos de ENACOM tal como se publican (penetración, velocidad media contratada y accesos por tecnología; total y por provincia) |
| `ookla_fijo.csv` | `nivel, id, nombre, fecha, mbps_bajada, mbps_subida, latencia_ms, tests, dispositivos, teselas` | `actualizar_ookla.py` | Velocidad **medida** de internet fijo, trimestral 2019-T1+. `nivel` = `pais` (`id` = ISO3, 11 países, `nombre` en inglés de Natural Earth) o `provincia` (`id` = código INDEC de 2 dígitos, 24). Promedios ponderados por tests |
| `ookla/fijo_AAAATn.csv` | ídem | `actualizar_ookla.py` | Cache por trimestre: lo que ya está no se vuelve a bajar (~3,5 min por trimestre nuevo) |
| `eph_servicios.csv` | `codigo, nivel, aglomerado, fecha, valor, hogares` | `actualizar_eph.py` | % de hogares (ponderado por `PONDERA`) con agua de red (`IV7=1`), cloaca (`IV11=1`) y gas de red para cocinar (`II8=1`), 2017-T1+. `nivel` = `total` (aglomerado vacío) o `aglomerado` (32 códigos EPH: CABA y partidos del GBA por separado). `hogares` = casos en la muestra |
| `eph_zips/` | — | `actualizar_eph.py` | Zips del INDEC bajados en esta PC. **Ignorada por git** (pesada); si existe `../analisis_EPH/data/raw` se usan los de ahí |

## `reference/` — insumos fijos

| Archivo | Contenido |
|---|---|
| `catalogo_variables.csv` | **Fuente de verdad de los datos**: una fila por serie (59). Ver columnas abajo |
| `provincias.csv` | `codigo_indec, provincia, nombre_enacom`: código INDEC de 2 dígitos, nombre canónico y nombre como lo escribe ENACOM |
| `geo/paises.geojson` | Polígonos de los 11 países (Natural Earth 1:50m, simplificados a ~0,005°). Propiedades `id` (ISO3), `nombre` |
| `geo/provincias.geojson` | Polígonos de las 24 provincias (WFS del IGN, simplificados, sin el sector antártico). Propiedades `id` (código INDEC), `nombre` |
| `certs/sectigo_public_server_auth_ca_dv_r36.pem` | Certificado intermedio que el servidor de ENACOM no envía; el descargador lo suma al bundle de certifi. Vence en 2036 |

### Columnas del catálogo

| Columna | Valores |
|---|---|
| `codigo` | identificador de la serie (se repite entre módulos: p. ej. `velocidad_medida` nacional, provincial e internacional) |
| `modulo` | `nacional`, `provincial`, `internacional`, `auxiliar` (IPC, PIB, EMAE) |
| `pilar` / `dimension` | `energia`, `transporte`, `telecom`, `agua`, `inversion` / `cobertura`, `capacidad`, `calidad`, `uso`, `inversion` |
| `signo` | `1` mejor si sube, `-1` mejor si baja, vacío = insumo de otra variable |
| `frecuencia` | `mensual`, `trimestral`, `semestral`, `anual`, `censal`, `eventual` |
| `api` | `datos_gob`, `imig`, `enacom`, `wdi`, `oecd_bb` (las baja `actualizar_datos.py`); `ookla`, `eph` (sus scripts); `pendiente` (sin descarga automática) |
| `id_api` | según la api: `datos_gob` = id de la serie · `imig` = columnas del CSV de la IMIG sumadas con `+` · `enacom` = `archivo:columna` o `archivo:numerador/denominador` (participación en %) · `wdi` = código del indicador · `oecd_bb` = `MODO.UNIDAD` · `ookla` = `nivel:id:columna` · `eph` = `VARIABLE=valor` |
| `estado` | `descargada` (48), `verificada` (fuente probada sin descarga automática, 1), `candidata` (10) |
| `notas` | empieza con `IIP:` si entra al índice nacional (y cómo), con `Fuera del IIP:` si se descarga pero se excluyó a propósito |

Para sumar una serie: agregar la fila al catálogo, correr el script de su api y, si va al índice, agregar
la variable en `VARIABLES` de `src/iip_nacional.py` (ver `CONTEXTO.md` §2).
