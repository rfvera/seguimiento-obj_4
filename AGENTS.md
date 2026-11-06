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
- `estado_referencia_por_zona.csv` — 20 zonas, estadísticas por zona y variable.
- `trayectorias_cambio_por_zona.csv` — 20 zonas, pendientes OLS por variable.
- `resumen_regional.csv` — métricas regionales.
- `README.md` — documentación.

### Resultados (2019–2025, 2.363 registros fondo, 20 zonas, 258 estaciones)

- Temperatura regional: media 9,73 °C, mediana 9,87 °C, desvío 1,50 °C (n=2.310).
- Oxígeno regional: media 7,83 mg/L, mediana 7,52 mg/L, desvío 2,81 mg/L (n=2.189). Medido en ml/L por el sensor SBE43; convertido a mg/L con factor 1,429 mg/ml. Saturación calculada con Weiss (1970) en `oxigeno_sat_pct`.
- Salinidad regional: media 32,16 PSU, mediana 32,56 PSU, desvío 1,54 PSU (n=2.247).
- Tendencias significativas (p<0,05, registro de fondo): **6**, no 3.
  - Quellón: temperatura +0,88 °C/año (p=0,0235, R2=1,00, n=3 años).
  - Puyuhuapi: oxígeno +0,26 ml/L/año (p=0,0222, R2=0,77, n=6 años).
  - Reloncaví: oxígeno +0,45 ml/L/año (p=0,0261, R2=0,66, n=7 años).
  - Aysén: salinidad +0,41 psu/año (p=0,0496, R2=0,66, n=6 años).
  - Butachauques: salinidad -0,05 psu/año (p=0,0305, R2=0,73, n=6 años).
  - Desertores: salinidad -0,08 psu/año (p=0,0291, R2=0,65, n=7 años).
- El OLS de `analisis_estado_referencia.py` se ajusta contra el **año calendario**, no contra la posición 0,1,2 de la serie. Con años faltantes (Puyuhuapi y Aysén no tienen 2020), la versión anterior sobreestimaba la pendiente y omitía Butachauques. No volver a `v.index` posicional.
- 9 zonas con solo 2024–2025 (sin tendencia): Ancud, Calbuco, Chacao, Chiloé central, Guaitecas, Hornopirén, Natales, Pta. Arenas, Tenaun.
- Pta. Arenas es zona propia desde la corrección de zonificación: 393 registros y 41 estaciones que antes se contabilizaban en Natales. El análisis por zona debe regenerarse si se toca `estaciones_CTD_con_ZONA_MACROFAUNA.csv`, o queda con 19 zonas y cifras sesgadas.

### Resultados de perfiles por profundidad y series de tiempo (140.787 registros, 349 profundidades, 20 zonas)

- 179 tendencias significativas (p<0,05) de **anomalías** en zona×profundidad×variable (41 temperatura, 48 oxígeno, 90 salinidad).
- 178 tendencias significativas (p<0,05) de **series anuales OLS**, concentradas en 8 zonas y 106 profundidades (41 temperatura, 46 oxígeno, 91 salinidad). Son dos estimadores distintos: no sumar 179 y 178.
- Temperatura: 41 tendencias sig., calentamiento en Quellón +1,07 °C/año (R²=0,996, 3–23 m).
- Oxígeno: 46 tendencias sig., aumentos en Butachauques +0,68 ml/L/año (R²=0,966).
- Salinidad: 91 tendencias sig., desalinización en Reloncaví −0,92 psu/año (R²=0,999), salinización en Aysén +0,60 psu/año (R²=0,73).
- Aysén muestra contraste vertical: salinización sobre 56 m y desalinización en 239–251 m (−0,14 psu/año, R²=0,78–0,82).
- Butachauques (285–304 m): salinidad −0,04 psu/año, pero con 3 años no consecutivos (2019, 2021, 2025) y un solo registro válido por año. El R²>0,99 no implica robustez.

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

## Pipeline 6: Polígonos de zona (Voronoi, recortados por área marina sin tierra)

`~/miniconda3/envs/r_env/bin/python zonas_poligonos.py`

Usa `estaciones_CTD_con_ZONA_MACROFAUNA.csv` y `salidas/figuras/ne_10m_admin_0_countries.shp` (países, Natural Earth 10m).

Metodología:
- Tesselación de Voronoi por estación con `shapely.voronoi_polygons` (no `geovoronoi`): las regiones se generan sobre el bbox y luego se recortan. Así no falla con estaciones en fiordos que Natural Earth clasifica como tierra.
- Área marina = bounding box grande alrededor de todas las estaciones MINUS la unión de TODOS los países que intersectan ese bbox (Chile, Argentina y cualquier otro). Restar solo Chile dejaba tierra argentina dentro de los polígonos.
- Cada región de Voronoi se asigna a la zona de su punto generador contenido (`region.contains`/`covers`) y se recorta al área marina.
- Los polígonos se disuelven (unen) por zona_mf y se recortan de nuevo contra tierra; `set_precision(1e-9)` elimina astillas de borde.
- Cada zona se recorta a la unión de buffers **geodésicos** de 100 km alrededor de sus propias estaciones, generados con `pyproj.Geod` (72 vértices). No se usa EPSG:6933: a estas latitudes un "buffer de 100 km" en 6933 resulta una elipse de ~148 km N-S por ~66 km E-O. Esto elimina extrapolaciones oceánicas sin respaldo: la auditoría SIG detectó que Puyuhuapi tenía 11.009,99 km² (94,4% de su área) en el Atlántico, a 649,9 km de su estación más cercana.
- Después del recorte se conservan solo las partes conectadas por mar a una parte ancla (la que contiene una estación, o la más cercana si todas caen en tierra). Una parte al otro lado de una barrera terrestre está en otra componente conexa de la máscara marina y se descarta; una parte sin estación pero en la misma componente (agua adyacente) se conserva. No se descarta toda parte sin estación: eso abría huecos de cobertura innecesarios.
- Resultado: 20 polígonos de zona, sin solapimientos significativos, sin tierra firme y sin partes al otro lado de una barrera terrestre sin respaldo.

Verificación del script:
- Área total: 178.279,27 km² (antes 325.139,94 km²).
- Puyuhuapi: 657,94 km²; 2 partes (32,18 + 625,76 km²); bbox (-73,354, -44,965) – (-72,591, -44,341); 8 estaciones dentro, 5 fuera; fragmento atlántico ausente.
- Partes sin estación conservadas: 17; en componentes sin ancla: **0** (todas conectadas por mar a una estación).
- Partes menores a 1 km²: 3 (Chacao 0,224; Moraleda 0,007; Pta. Arenas 0,676).
- Solapamiento entre zonas: 0,074 km² (73.607 m²; precisión de borde).
- Tierra residual: 0,00000000 km² con `set_precision(1e-9)`; sin esa rejilla, 0,123 km² de astillas de borde.
- Distancia máxima estación -> su polígono: 8,54 km (60 estaciones en fiordos quedan fuera por la costa NE 10m; se requiere GSHHG full/high o cartografía SHOA para corregirlo).
- Distancia máxima parte -> estación más cercana de su zona: 97,76 km (dentro del buffer geodésico de 100 km).

Salida:
- `salidas/figuras/zonas_macrofauna.gpkg` — 20 polígonos de zona (EPSG:4326), sin tierra y con extensión acotada a 100 km de sus estaciones.
- `salidas/figuras/ne_10m_admin_0_countries.*` — países Natural Earth 10m (necesario para reproducir).

## Pipeline 7: Verificación de cifras del informe

`~/miniconda3/envs/r_env/bin/python salidas/verificacion/cifras_informe.py`

Lee las salidas de los pipelines 1–4 y escribe en `salidas/verificacion/`:
- `cifras_informe.csv` — 152 cifras clave/valor/fuente. Es la única fuente admisible para el .typ.
- `tendencias_fondo_significativas.csv`, `tendencias_profundidad_seleccion.csv`,
  `top_tendencias_por_variable.csv`, `cuadro_resumen_por_profundidad.csv` — las tablas del informe.

Regla: ninguna cifra del informe se transcribe a mano. Si cambia un CSV del pipeline, se
re-ejecuta este script y se compara `cifras_informe.csv` antes de recompilar el PDF.

## Pipeline 7b: Conversión de oxígeno (ml/L → mg/L)

`~/miniconda3/envs/r_env/bin/python salidas/oxigeno_conversion.py`

Añade a `fondo_ctd_por_zona.csv` y `perfiles_procesados.csv`:
- `oxigeno_mg_L` = `oxigeno_ml_L` × 1,42903 (densidad del O2 a STP).
- `oxigeno_sat_pct` = saturación con la ecuación de Weiss (1970).

Añade `oxigeno_mg_L_media` / `oxigeno_mg_L_desvio` a `promedio_anual_por_profundidad.csv`.

Regla: el sensor reporta en ml/L; el informe publica en mg/L. La conversión es un factor constante; la saturación es Weiss.

## Pipeline 8: Figuras de series de tiempo

`~/miniconda3/envs/r_env/bin/python salidas/figuras/series_tiempo_fig.py`

Lee `fondo_ctd_por_zona.csv` y `salidas/perfiles_procesados/promedio_anual_por_profundidad.csv`.
Escribe `informe/figuras/series_tendencias_fondo.png`: 6 paneles (una zona por tendencia
significativa), cada uno con la serie anual de fondo y la de 10 m, y la recta OLS sobre el
año real. El tamaño de la figura está pensado para insertarse a 90% del ancho de página:
si se cambia el `figsize`, revisar que el texto interno siga siendo legible en el PDF.

## Pipeline 9: Cobertura temporal del muestreo

`~/miniconda3/envs/r_env/bin/python salidas/figuras/cobertura_temporal.py`

Lee `fondo_ctd_por_zona.csv`. Escribe:
- `salidas/verificacion/cobertura_temporal.csv` — 20 zonas con estaciones, primer/ultimo año, años con dato, casts y casts por año.
- `informe/figuras/cobertura_temporal.png` — matriz zona×año (escala sqrt).

## Informe Typst (en `informe/`)

- `informe/informe_ambiental.typ` — documento Typst completo.
- `informe/informe_ambiental.pdf` — PDF compilado.

Compilar: `/home/rfvera/.typst/bin/typst compile informe/informe_ambiental.typ`

## Pipeline 10: Estaciones por zona

`~/miniconda3/envs/r_env/bin/python salidas/verificacion/zonas_estaciones.py`

Lee `estaciones_CTD_con_ZONA_MACROFAUNA.csv`. Escribe `salidas/verificacion/zonas_estaciones.csv`:
zona, n de estaciones, lista de códigos, orden norte-sur.

## Reglas de versión

- Nunca sobrescribir `.xlsx` fuentes. Están en `.gitignore` (`*.xlsx`).
- Salidas derivadas en `salidas/` y `informe/` son regenerables; revisar diff antes de commitear.
- `git status` debe quedar limpio tras re-ejecutar los scripts.
- **Orden norte-sur en figuras y tablas.** Toda tabla o figura que liste zonas de macrofauna se ordena de norte a sur por latitud media de sus estaciones (Estuario → Reloncaví → … → Pta. Arenas). No usar orden alfabético. Los scripts calculan el orden desde `estaciones_CTD_con_ZONA_MACROFAUNA.csv` (columna `lat`); no hardcodear la lista.
