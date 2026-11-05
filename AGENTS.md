# AGENTS.md — objetivo_4 (IFOP Seguimiento CTD)

Evaluación de variabilidad ambiental y exposición de áreas de emplazamiento acuícola a forzantes naturales y cambio climático. Repositorio git; fuentes `.xlsx` de solo lectura, no versionadas.

## Contexto metodológico

Los datos son perfiles CTD (conductividad, temperatura, profundidad, oxígeno, densidad) tomados en estaciones repetidas a través del tiempo (etapas/fechas/años). Cada estación×fecha es un cast independiente. El procesamiento sigue el estándar oceánico (RBR CTD Guidelines DFO 2017, BODC series documents, paquete R `oce`):

1. **Trimming**: remover datos de superficie/calibración (FLAG_BOOL==0 en A, profundidad <0,5 m en B).
2. **Despiking**: eliminar valores atípicos por grupo (regla IQR 3×).
3. **Bin averaging**: promedio en bins de 1 metro de profundidad, centrados en valores enteros.
4. **Perfiles procesados**: conservar cada nivel de profundidad bineado (estación×fecha×profundidad).
5. **Registro de fondo**: tomar la medición a la profundidad máxima por estación×fecha.
6. **Profundidad de fondo**: Archivo A desde `PROF_SECT_m`; Archivo B desde GEBCO_2026.
7. **Series de tiempo por profundidad**: promedio anual por zona×profundidad, ciclo estacional (seno/coseno), anomalías y tendencia lineal de anomalías (OLS).

Ver `contexto_metodologico_ctd.md` para detalles y referencias verificadas.

## Entorno

- Python: `~/miniconda3/envs/r_env/bin/python` (pandas 3.0.2, openpyxl, scipy instalados). No usar pip en sistema (PEP 668).
- Entorno opcional `~/miniconda3/envs/gebco_env` (xarray, netCDF4) usado solo para descargar batimetría GEBCO vía OPeNDAP.
- Rutas en scripts son absolutas (`BASE = /home/rfvera/.../objetivo_4`).

## Pipeline 1: Reconstrucción desde archivos originales

`~/miniconda3/envs/r_env/bin/python reconstruir_ctd.py`

Lee:
1. `Compilacion_BD_CTD_SEGUIMIENTO_2019-2025.xlsx` — hoja `Base de Datos CTD2019-2025_IFOP`, encabezado fila 20, 31 columnas. 45.820 filas, estaciones 1–32, fechas 2019–2025. Sensor CTD SeaBird SBE19plus.
2. `datos CTD - marea roja.xlsx` — hoja `Datos CTD`, FECHA mixta. 358.360 filas, 227 códigos, fechas 2023–2025. Profundidades 0.8–100,6 m.
3. `estaciones_CTD_con_ZONA_MACROFAUNA.csv` — 259 estaciones con zona_mf.
4. `gebco_profundidades_marea_roja.csv` — profundidad GEBCO_2026 para 227 estaciones de marea roja.

Escribe:
- `fondo_ctd_por_zona.csv` — 2.363 registros de fondo (220 archivo A + 2.143 archivo B).

Reglas clave:
- Archivo A: FLAG_BOOL==0 se descarta (220 filas de superficie/calibración). Profundidades son enteros (1m, 2m...). Nutrientes/clorofila de botella Niskin se dejan como están (no se promedian).
- Archivo B: profundidad <0,5 m se descarta. Datos de alta frecuencia, bin averaging por 1m.
- `profundidad_fondo_m`: Archivo A desde `PROF_SECT_m`; Archivo B desde `GEBCO_2026`.
- `profundidad_fondo_fuente`: `PROF_SECT_m` (A) o `GEBCO_2026` (B).
- Todas las estaciones tienen zona_mf asignada (0 nulas).

## Pipeline 2: Perfiles procesados y series de tiempo por profundidad

`~/miniconda3/envs/r_env/bin/python perfiles_procesados.py`

Usa los mismos archivos originales + `gebco_profundidades_marea_roja.csv`.

Escribe (en `salidas/perfiles_procesados/`):
- `perfiles_procesados.csv` — 140.787 filas (estación×fecha×profundidad, 1–349 m).
- `promedio_anual_por_profundidad.csv` — 16.559 filas (zona×profundidad×año).
- `ciclo_estacional_por_profundidad.csv` — 7.615 filas (zona×profundidad×variable, ajuste seno/coseno).
- `tendencias_anomalias_por_profundidad.csv` — 7.615 filas (zona×profundidad×variable, tendencia de anomalías).
- `resumen_regional_por_profundidad.csv` — 349 filas (una por profundidad).

Metodología de series de tiempo integrada:
- Ciclo estacional: A = A_avg + A_amp·sin(2π·t/12) + A_pha·cos(2π·t/12).
- Anomalías: observado menos ciclo estacional esperado.
- Tendencia: OLS de anomalías vs año (mínimo 3 años).

## Pipeline 3: Análisis ambiental (registro de fondo)

`~/miniconda3/envs/r_env/bin/python salidas/analisis_ambiental/analisis_estado_referencia.py`

Usa `fondo_ctd_por_zona.csv` (ya tiene zona_mf, no necesita merge).

Salidas (en `salidas/analisis_ambiental/`):
- `estado_referencia_por_zona.csv` — 19 zonas, estadísticas por zona y variable.
- `trayectorias_cambio_por_zona.csv` — 19 zonas, pendientes OLS por variable.
- `resumen_regional.csv` — métricas regionales.
- `README.md` — documentación.

### Resultados (2019–2025, 2.363 registros fondo, 20 zonas, 258 estaciones)

- Temperatura regional: media 9,73 °C, mediana 9,87 °C, desvío 1,50 °C (n=2.310).
- Oxígeno regional: media 5,48 ml/L, mediana 5,26 ml/L, desvío 1,97 ml/L (n=2.189).
- Salinidad regional: media 32,16 psu, mediana 32,56 psu, desvío 1,54 psu (n=2.247).
- Tendencias significativas (p<0,05, registro de fondo):
  - Quellón: temperatura +0,88 °C/año (p=0,023, R2=0,999, n=3 años).
  - Aysén: salinidad +0,50 psu/año (p=0,030, R2=0,76, n=6 años).
  - Desertores: salinidad -0,08 psu/año (p=0,029, R2=0,65, n=7 años).
- 8 zonas con solo 2024–2025 (sin tendencia): Ancud, Calbuco, Chacao, Chiloé central, Guaitecas, Hornopirén, Natales, Tenaun.

### Resultados de perfiles por profundidad y series de tiempo (140.787 registros, 349 profundidades, 20 zonas)

- 178 tendencias significativas (p<0,05) en zona×profundidad×variable.
- Temperatura: 41 tendencias sig., calentamiento en Quellón +1,07 °C/año (R²=0,996).
- Oxígeno: 46 tendencias sig., aumentos en Butachauques +0,68 ml/L/año (R²=0,966).
- Salinidad: 91 tendencias sig., desalinización en Reloncaví −0,92 psu/año (R²=0,999), salinización en Aysén +0,60 psu/año (R²=0,73).
- Aysén (238–250 m): salinidad −0,14 psu/año (R²=0,78–0,82).
- Butachauques (284–290 m): salinidad −0,04 psu/año (R²>0,99).
- Quellón (superficie): temperatura +0,88 °C/año (R²=1,00).

## Pipeline 4: Análisis de series de tiempo por variable

`~/miniconda3/envs/r_env/bin/python analisis_serie_tiempo.py`

Usa `salidas/perfiles_procesados/promedio_anual_por_profundidad.csv`.

Salidas (en `salidas/analisis_serie_tiempo/`):
- `serie_tiempo_por_variable.csv` — 19.940 filas (zona×profundidad×variable con estadísticas y tendencia).
- `series_tiempo_detalladas.csv` — 50.277 filas (zona×profundidad×variable×año con valor anual).
- `resumen_tendencias_significativas.csv` — 178 filas (solo tendencias con p<0.05).

## Pipeline 5: Mapa de estaciones y zonas ACS

`~/miniconda3/envs/r_env/bin/python mapa_estaciones_acs.py`

Usa `estaciones_CTD_con_ZONA_MACROFAUNA.csv`, `acs_subpesca.gpkg` y `salidas/figuras/zonas_macrofauna.gpkg`.

Salida:
- `salidas/figuras/mapa_estaciones_acs.png` — mapa con 259 estaciones de muestreo, polígonos de zona (Voronoi recortado por área marina) y 106 polígonos ACS SUBPESCA, estaciones coloreadas por zona_mf (20 zonas).
- `salidas/figuras/zonas_macrofauna.gpkg` — capa GPKG con 19 polígonos de zona (EPSG:4326), sin solapamientos entre sí.

## Pipeline 6: Polígonos de zona (Voronoi, recortados por área marina)

`~/miniconda3/envs/r_env/bin/python zonas_poligonos.py`

Usa `estaciones_CTD_con_ZONA_MACROFAUNA.csv` y `salidas/figuras/ne_10m_admin_0_countries.shp` (países, Natural Earth).

Metodología:
- Tesselación de Voronoi por estación.
- Cada polígono de Voronoi se recorta por un polígono de "área marina" = bounding box grande alrededor de todas las estaciones MINUS polígono del país Chile (Natural Earth 10m).
- Los polígonos se disuelven (unen) por zona_mf.
- Resultado: polígonos de zona que NO se solapan entre sí y están limitados al área marina (no incluyen tierra firme).

Salida:
- `salidas/figuras/zonas_macrofauna.gpkg` — 19 polígonos de zona (EPSG:4326), sin solapamientos entre sí.
- `salidas/figuras/ne_10m_admin_0_countries.*` — países Natural Earth 10m (necesario para reproducir).

## Informe Typst (en `informe/`)

- `informe/informe_ambiental.typ` — documento Typst completo.
- `informe/informe_ambiental.pdf` — PDF compilado.

Compilar: `/home/rfvera/.typst/bin/typst compile informe/informe_ambiental.typ`

## Reglas de versión

- Nunca sobrescribir `.xlsx` fuentes. Están en `.gitignore` (`*.xlsx`).
- Salidas derivadas en `salidas/` y `informe/` son regenerables; revisar diff antes de commitear.
- `git status` debe quedar limpio tras re-ejecutar los scripts.
