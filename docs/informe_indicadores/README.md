# Sección del IIP para el documento INECO-UADE

[`seccion_iip.tex`](seccion_iip.tex) es la sección **"Índice de Infraestructura en Argentina"** del
documento *Propuesta de Indicadores Económicos* (INECO-UADE, octubre de 2026). El documento completo vive
en **Overleaf** y no está en este repo. La sección está redactada como **propuesta**: versión preliminar
del módulo nacional con resultados, un cuadro de indicadores "versión preliminar / a incorporar" y una
subsección de próximos pasos.

## El documento (estado al 2026-10-08)

| N.º | Sección | Origen |
|---|---|---|
| — | Introducción (sin número) | — |
| 1 | Termómetro de la Economía de los Hogares Argentinos | repo `analisis_EPH` |
| 2 | Índice de Fortaleza Macroeconómica Argentina | repo `cuentas_publicas` (notebook 03, "índice macro") |
| 3 | Índice de Precios de Jubilados Argentinos | repo `IPC_jubilados` |
| **4** | **Índice de Infraestructura en Argentina** | **este repo** |
| 5 | Índice Inmobiliario en Argentina | repo `indice_inmobiliario_argentina` |
| 6 | Índice de Precios de Supermercados Argentinos | repo `precios_minoristas_supermercados` |
| 7 | Consumo de energía en Pinamar | repo `consumo_energetico_argentina` |

- **Preámbulo:** `article` 11pt A4, `inputenc` utf8, `fontenc` T1, `babel` spanish, `lmodern`,
  `geometry` (márgenes de 2,5 cm), `amsmath`, `graphicx`, `booktabs`, `xcolor`, `titlesec`, `hyperref`.
  Con babel en español los cuadros salen como "Cuadro" (las tablas se citan como `Cuadro~\ref{...}`).
- **Bibitems que ya tiene el documento:** `indec_eph`, `indec_ipc`, `oecd2008`, `utdt`, `sepa`,
  `indec_engho`, `haber_minimo`, `mecon_imig`. La sección del IIP usa `indec_eph`, `oecd2008` y
  `mecon_imig` y agrega 9 nuevos (están comentados al final de `seccion_iip.tex`).
- **Convenciones del documento:** trimestres como `2026T2` (las define la sección del Termómetro);
  decimales con coma (`$+0{,}32$`); "RIC" para el rango intercuartil; el índice macro se llama "Índice
  de Fortaleza Macroeconómica Argentina"; figuras en la carpeta `figuras/`.

## Cómo pegarla

1. En el Overleaf, reemplazar `\section{Índice de Infraestructura en Argentina}` y su `% Escribir aquí`
   por el contenido de `seccion_iip.tex` (sin los comentarios del encabezado y del final).
2. Subir a `figuras/` los PNG `iip_g02_pilares.png` e `iip_g04_telecom_pares.png`: vienen en el ZIP del
   notebook 01 o en `output/` después de `python scripts/correr_nacional.py`. El prefijo `iip_` evita
   choques con las figuras de otras secciones.
3. Pegar los 9 `\bibitem` nuevos (descomentados) antes de `\end{thebibliography}`.

## Cómo probarla antes de pegar

```bash
python scripts/correr_nacional.py
python scripts/probar_seccion_latex.py
```

Arma `_local_run/latex/documento.tex` con el mismo preámbulo y la misma bibliografía del documento,
verifica que toda cita tenga su bibitem (y que no se repitan claves del documento) y compila dos veces
con `pdflatex` (MiKTeX o TeX Live). Tiene que terminar en `RESULTADO: OK` (0 errores, 0 referencias
indefinidas, 0 cajas desbordadas). Si el preámbulo o la bibliografía del documento cambian en el Overleaf,
actualizar `PREAMBULO` y `CLAVES_DEL_DOCUMENTO` en ese script.

## Cuando se actualizan los datos

Las cifras del texto, del Cuadro de gestiones y de las figuras salen de `scripts/correr_nacional.py`
(= notebook 01). La lista de cada cifra citada está en `ESTADO.md` §2: actualizarlas todas, regenerar
las figuras, correr `probar_seccion_latex.py` y volver a subir la sección y los PNG al Overleaf.

Cuando se desarrollen los módulos provincial e internacional, o se incorpore algún indicador
pendiente, actualizar el Cuadro de pilares (columna "A incorporar") y la subsección "Próximos pasos".

Pendiente opcional: las dos figuras traen un título dentro de la imagen que repite el `\caption`; se
pueden regenerar sin título si el usuario lo pide (`src/graficos.py`).
