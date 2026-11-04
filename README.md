# Objetivo 4 — Seguimiento CTD (IFOP)

Evaluación de la variabilidad ambiental y exposición de áreas de emplazamiento
acuícola a forzantes naturales y asociados al cambio climático.

## Contenido

- `Compilacion_BD_CTD_SEGUIMIENTO_2019-2025.xlsx` — CTD seguimiento 2019-2025 (fuente, solo lectura)
- `datos CTD - marea roja.xlsx` — CTD marea roja 2023-2025 (fuente, solo lectura)
- `estaciones_*_UTM18S.csv` — Estaciones convertidas a UTM WGS84 18S (EPSG:32718)
- `estaciones_CTD_con_zona_final.csv` — 259 estaciones con zona asignada (ACS_SUBPESCA o ZONA_PROXIMIDAD)
- `estaciones_CTD_con_zona.gpkg` — Capa SIG de estaciones con zona (EPSG:4326)
- `acs_subpesca.gpkg` — Polígonos oficiales de ACS de SUBPESCA (capa ACStats, EPSG:4326)
- `fondo_ctd_por_zona.csv` — Registro de fondo (profundidad máxima) por estación×fecha con zona
- `resumen_estaciones_por_zona.csv` — Conteo de estaciones por zona
- `procesar_fondo_ctd.py` — Script de procesamiento

## Zonas asignadas

- **ACS_SUBPESCA** (159 estaciones): dentro de polígonos oficiales de ACS de SUBPESCA
- **ZONA_PROXIMIDAD** (100 estaciones): estación de referencia MACROFAUNA más cercana (ver `dist_km`)

## Reglas

- Los `.xlsx` fuentes son de solo lectura y no se versionan (ver `.gitignore`).
- Las salidas derivadas (`.csv`, `.gpkg`) son regenerables.
