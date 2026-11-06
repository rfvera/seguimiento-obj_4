# Auditoría de citas bibliográficas — objetivo_4

Auditor: VERITAS (subagente). Fecha de auditoría: 6 de noviembre de 2026.
Alcance: `informe/informe_ambiental.typ` (Referencias, 3 citas), `contexto_metodologico_ctd.md` (Referencias verificadas, 3 citas), `AGENTS.md` (mención sin cita formal).
Método: resolución de URL/DOI (curl), extracción de texto de PDFs con `pdftotext -layout` + `grep`, verificación de autor/año/título/pasaje.

## Tabla de auditoría

| # | Afirmación / Elemento | Archivo | Agente de origen | Estado | Evidencia / Motivo |
|---|---|---|---|---|---|
| A | Kelley, D. y Richards, C. (2026). *Analysis of CTD data*. Vignette del paquete oce. URL CRAN | `informe/informe_ambiental.typ` (ref. 1) | redacción/informe | OK | URL resuelve (HTTP 200). Página recuperada: autores Dan Kelley (ORCID) y Clark Richards; fecha del documento 2026-06-30; título "2. Analysis of CTD data". Pasaje verificado: `ctdTrim()` (7 ocurrencias) y `ctd.decimate()` (1 ocurrencia) en el vignette. |
| B | Williams, C. A. J. (2014). *DY026 CTD processing report*. National Oceanography Centre, Liverpool. URL BODC PDF | `informe/informe_ambiental.typ` (ref. 2) | redacción/informe | OK | PDF descargado y extraído con pdftotext. Encabezado: "DY026 CTD processing report / March 2014 / C. A. J. Williams / National Oceanography Centre, Liverpool". Pasajes verificados: "bin averaging, despiking and calibrations"; smoothing "10m (5m for oxygen and chlorophyll)" (líneas 319-321); despiking de datos 24 Hz downcast; calibraciones a salinidad/oxígeno/clorofila. |
| C | Rohan, S. K., Charriere, N. E., Riggle, B., O'Leary, C. A. y Raring, N. W. (2023). NOAA. *A flexible approach for processing data collected using trawl-mounted CTDs during Alaska bottom-trawl surveys*. NOAA Technical Memorandum NMFS-AFSC 475. DOI 10.25923/8ape-q461 | `informe/informe_ambiental.typ` (ref. 3) | redacción/informe | OK | DOI resuelve (HTTP 302 → repository.library.noaa.gov/view/noaa/55614). Página NOAA recuperada: autores exactos, año 2023, título exacto (capitalización menor), serie "NOAA technical memorandum NMFS-AFSC 475". PDF recuperado: pasaje verificado "Averages for all variables are calculated for 1-m depth bins" (línea 612) y discusión de despiking/spikes. |
| D | Kelley, D. & Richards, C. (2022). *oce: Analysis of Oceanographic Data*. Vignette "Analysis of CTD data". Funciones ctdTrim(), ctd.decimate(). URL CRAN | `contexto_metodologico_ctd.md` (ref. 1) | contexto_metodológico | CORREGIR | Misma URL que (A) pero año 2022. La fuente recuperada en esta sesión reporta la vignette fechada 2026-06-30. Inconsistente con (A) y con la fuente. Debe ser 2026. (El claim `ctdTrim()` con `method="downcast"` se verifica: la documentación rdrr.io indica que si no se proporciona `method`, se asume "downcast"; especificarlo explícitamente es válido.) |
| E | Williams, C.A.J. (2015). *DY026 CTD processing report*. BODC / NOC Liverpool. Bin averaging, despiking, calibraciones, smoothing. URL BODC PDF | `contexto_metodologico_ctd.md` (ref. 2) | contexto_metodológico | CORREGIR | Misma URL/PDF que (B), cuyo encabezado dice "March 2014". Inconsistente con (B) y con la fuente. Debe ser 2014. |
| F | NOAA AFSC. *gapctd* R package for CTD processing (trawl-mounted CTDs, SBE 19plus V2). Bin average 1 m, despiking. URL repository.library.noaa.gov/view/noaa/55614 | `contexto_metodologico_ctd.md` (ref. 3) | contexto_metodológico | CORREGIR | La URL resuelve, pero corresponde al Technical Memorandum de Rohan et al. (2023), no a un paquete R independiente. El paquete `gapctd` es el software descrito en ese memorandum (repo GitHub afsc-gap-products/gapctd). La cita debe atribuirse a Rohan et al., 2023 (mismo que C) y no a "NOAA AFSC. gapctd". Además, el claim "promedio en bins de 1 m de profundidad, con interpolación lineal a valores de presión uniformemente espaciados" (línea 41) es impreciso: `oce::ctdDecimate()` por defecto usa método "boxcar" (promedio local); la interpolación lineal corresponde a `method="approx"`. |
| G | RBR CTD Guidelines DFO 2017 (sin cita formal) | `AGENTS.md` (línea 7) | AGENTS.md | CORREGIR (sin cita formal) | Referencia real verificada: Halverson, M., Jackson, J., Richards, C., Melling, H., Brunsting, R., Dempsey, M., Gatien, G., Hamilton, A., Hunt, B., Jacob, W., y Zimmerman, S. (2017). *Guidelines for processing RBR CTD profiles*. Can. Tech. Rep. Hydrogr. Ocean Sci. 314: iv + 38 p. (DFO, Institute of Ocean Sciences). PDF disponible en https://waves-vagues.dfo-mpo.gc.ca/Library/40578112.pdf. Debe añadirse la cita formal. |

## Inconsistencias entre archivos

1. **Williams: 2014 vs 2015.** `informe_ambiental.typ` cita 2014 (correcto, según PDF); `contexto_metodologico_ctd.md` cita 2015 (incorrecto). Misma fuente.
2. **Kelley: 2026 vs 2022.** `informe_ambiental.typ` cita 2026 (correcto, según vignette CRAN fechada 2026-06-30); `contexto_metodologico_ctd.md` cita 2022 (incorrecto). Misma URL.
3. **Rohan vs gapctd.** `contexto_metodologico_ctd.md` ref. 3 presenta como fuente independiente un "paquete gapctd" con una URL que en realidad es el Technical Memorandum de Rohan et al. (2023) ya citado en el informe. Duplicación/mala atribución.
4. **AGENTS.md** menciona "RBR CTD Guidelines DFO 2017" sin cita formal; la referencia existe y se pudo verificar (Halverson et al., 2017).

## Correcciones propuestas (texto exacto → valor correcto)

- `contexto_metodologico_ctd.md`, línea 29: `(Kelley & Richards, 2022)` → `(Kelley & Richards, 2026)`.
- `contexto_metodologico_ctd.md`, línea 88: `Kelley, D. & Richards, C. (2022).` → `Kelley, D. & Richards, C. (2026).`
- `contexto_metodologico_ctd.md`, línea 35/89: `Williams, C.A.J. (2015).` → `Williams, C.A.J. (2014).`
- `contexto_metodologico_ctd.md`, línea 41: claim "interpolación lineal a valores de presión uniformemente espaciados" → "interpolación a valores de presión uniformemente espaciados (por defecto método 'boxcar' = promedio local; interpolación lineal solo con `method='approx'`)".
- `contexto_metodologico_ctd.md`, línea 90: reemplazar `3. NOAA AFSC. *gapctd* R package for CTD processing (trawl-mounted CTDs, SBE 19plus V2). Bin average 1 m, despiking. [NOAA Repository](...)` por `3. Rohan, S. K., Charriere, N. E., Riggle, B., O'Leary, C. A. y Raring, N. W. (2023). *A flexible approach for processing data collected using trawl-mounted CTDs during Alaska bottom-trawl surveys*. NOAA Technical Memorandum NMFS-AFSC 475. Bin average 1 m, despiking. [DOI](https://doi.org/10.25923/8ape-q461)` (o eliminar por redundancia con el informe).
- `informe/informe_ambiental.typ`, línea 491: `Rohan, S. K., ... (2023), NOAA (National Oceanic and Atmospheric Administration).` → mover "NOAA" al campo de serie/editorial: `Rohan, S. K., Charriere, N. E., Riggle, B., O'Leary, C. A. y Raring, N. W. (2023). *A flexible approach ...*. NOAA Technical Memorandum NMFS-AFSC 475.` (menor; opcional).
- `AGENTS.md`, línea 7: añadir cita formal: `Halverson, M., Jackson, J., Richards, C., Melling, H., Brunsting, R., Dempsey, M., Gatien, G., Hamilton, A., Hunt, B., Jacob, W., y Zimmerman, S. (2017). Guidelines for processing RBR CTD profiles. Can. Tech. Rep. Hydrogr. Ocean Sci. 314: iv + 38 p. https://waves-vagues.dfo-mpo.gc.ca/Library/40578112.pdf`

## Veredicto global

**APROBADO CON CORRECCIONES.**

No se detectaron citas inventadas ni DOI inexistentes: las tres referencias del informe (A, B, C) resuelven y sus pasajes citados existen en las fuentes. Las correcciones se limitan a inconsistencias de año (D, E), atribución/etiqueta de fuente (F) e imprecisión técnica (F), y a la falta de cita formal en AGENTS.md (G). Ninguna cifra del informe se vio afectada.

## Acciones para SMITH

1. Aplicar las correcciones de año en `contexto_metodologico_ctd.md` (2022→2026, 2015→2014).
2. Reetiquetar o eliminar la referencia "gapctd" en `contexto_metodologico_ctd.md`, reemplazándola por Rohan et al., 2023 (o marcándola como la misma fuente que el informe).
3. Corregir la afirmación sobre "interpolación lineal" de `ctd.decimate()` a la descripción verificada (boxcar por defecto).
4. Añadir la cita formal de Halverson et al. (2017) en `AGENTS.md`.
5. (Opcional) Ajustar la posición de "NOAA" en la referencia Rohan del informe.
6. No modificar datos ni cifras del informe; solo metadatos bibliográficos.
