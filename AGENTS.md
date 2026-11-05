# AGENTS.md — objetivo_4 (IFOP Seguimiento CTD)

Evaluación de variabilidad ambiental y exposición de áreas de emplazamiento acuícola a forzantes naturales y cambio climático. Repositorio git con 2 commits; fuentes `.xlsx` de solo lectura, no versionadas.

## Entorno

- Python: `~/miniconda3/envs/r_env/bin/python` (pandas 3.0.2, openpyxl instalado). No usar pip en sistema (PEP 668).
- Entorno opcional `~/miniconda3/envs/gebco_env` (xarray, netCDF4) usado solo para descargar batimetría GEBCO vía OPeNDAP; no es necesario para re-ejecutar el pipeline.
- Ejecutar desde cualquier directorio: las rutas en `procesar_fondo_ctd.py` son absolutas (`BASE = /home/rfvera/.../objetivo_4`).

## Pipeline (único script)

`~/miniconda3/envs/r_env/bin/python procesar_fondo_ctd.py`

Lee:
1. `Compilacion_BD_CTD_SEGUIMIENTO_2019-2025.xlsx` — hoja `Base de Datos CTD2019-2025_IFOP`, encabezado en fila 20 (0-indexed), 31 columnas renombradas por posición.
2. `datos CTD - marea roja.xlsx` — hoja `Datos CTD`, `FECHA` mixta (datetime / `DD-MM-YYYY` / `S/I` → NaT).
3. `estaciones_CTD_con_zona_final.csv` — 259 estaciones con zona (159 `ACS_SUBPESCA`, 100 `ZONA_PROXIMIDAD`).
4. `gebco_profundidades_marea_roja.csv` — profundidad de fondo por estación del archivo B, extraída de GEBCO_2026.

Escribe:
- `fondo_ctd_por_zona.csv` — registro de fondo (una fila por estación×fecha) con zona unida, 2.366 filas.

Reglas clave del script (no modificar sin anotar):
- Por cada (estación, fecha) se selecciona la fila de **profundidad de medición máxima** (`idxmax`, primera fila en caso de empate). Las variables (temperatura, oxígeno, salinidad) se toman de esa fila.
- `profundidad_fondo_m` (profundidad real del fondo):
  - Archivo A: desde `PROF_SECT_m` (profundidad de sector/carta). Si un grupo tiene varios valores, se toma el máximo.
  - Archivo B (marea roja): desde `gebco_profundidades_marea_roja.csv` (batimetría GEBCO_2026 por estación). Los perfiles de marea roja solo llegan a ~50 m y el archivo no trae profundidad de fondo, por lo que **no se asume que la medición más profunda es el fondo**.
- `profundidad_fondo_fuente`: `PROF_SECT_m` (A) o `GEBCO_2026` (B).
- Sin match de zona → zona NaN, reportado (no se inventa).
- Archivo B solo reporta oxígeno en ml/L; `oxigeno_mg_L` = NaN para esas filas.

## Salidas derivadas (versionadas, regenerables)

- `fondo_ctd_por_zona.csv` — salida del script (columnas: archivo, estacion_id, fecha, profundidad_fondo_m, profundidad_fondo_fuente, temperatura_C, oxigeno_ml_L, oxigeno_mg_L, salinidad_psu, zona, zona_tipo, dist_km, fuente).
- `gebco_profundidades_marea_roja.csv` — profundidad de fondo GEBCO para las 227 estaciones de marea roja (extraída vía OPeNDAP).
- `estaciones_CTD_con_zona_final.csv`, `estaciones_CTD_con_zona.gpkg`, `estaciones_CTD_con_ZONA_MACROFAUNA.csv`, `estaciones_sin_ACS.csv`, `estaciones_con_ACS_asignado.csv`, `estaciones_CTD_paso1_ACS.csv`, `estaciones_archivoA/B_UTM18S.csv`, `resumen_estaciones_por_zona.csv` — capas y resúmenes previos.
- `acs_subpesca.gpkg` — polígonos oficiales ACS SUBPESCA (EPSG:4326).

## Reglas de versión

- Nunca sobrescribir `.xlsx` fuentes. Están en `.gitignore` (`*.xlsx`).
- `fondo_ctd_por.zona.csv` y demás derivados son regenerables; revisar diff antes de commitear si hay cambio real (pandas 3.x puede introducir ruido ≤1e-13 en sumas).
- `git status` debe quedar limpio tras re-ejecutar el script (salida byte-idéntica).
- `gebco_profundidades_marea_roja.csv` se genera una vez con `gebco_env` (xarray + netCDF4) consultando GEBCO_2026 vía OPeNDAP; no se regenera en cada corrida del pipeline a menos que cambie.

## Gotchas

- Archivo A: 45.820 filas, estaciones 1–32, fechas 2019–05–09 a 2025–10–27. `PROF_SECT_m` no es único en 19 de 222 grupos (estación×fecha); se toma el máximo.
- Archivo B: 358.360 filas, 227 códigos únicos, fechas 2023–06–23 a 2025–03–26. 16 fechas nulas, 57 profundidades nulas, 73 grupos con empate de profundidad máxima, 51 afectan variables (desempate por primera fila). Profundidad de medición máxima ~50 m (no es fondo).
- Cobertura total: todas las estaciones CTD tienen zona asignada (0 sin zona, 0 CTD sin datos de fondo).
- `oxigeno_mg_L` es NaN en todo el archivo B (no se reporta en esa unidad).
- GEBCO_2026: grid global 15 arc-segundos (~450 m), valor negativo = profundidad, positivo = tierra. 124 estaciones con píxel de agua directo, 103 con búsqueda en vecindario (±50 px ≈ 20 km).