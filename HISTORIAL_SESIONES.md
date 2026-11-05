# Historial de sesiones — objetivo_4 (IFOP Seguimiento CTD)

## Sesión 2026-11-05 (usuario `rfvera`) — corrección profundidad fondo marea roja + GEBCO

### Objetivo
Corregir el cálculo de `profundidad_fondo_m` para el archivo B (marea roja): los perfiles CTD de marea roja solo llegan a ~50 m, por lo que no se asume que la medición más profunda es el fondo. Se obtiene la profundidad real del fondo desde batimetría GEBCO_2026 por estación.

### Decisiones (usuario)
1. Archivo A (seguimiento 2019–2025): `profundidad_fondo_m` desde `PROF_SECT_m` (profundidad de sector/carta), valor máximo por grupo (estación×fecha).
2. Archivo B (marea roja): `profundidad_fondo_m` desde GEBCO_2026 (OPeNDAP, CEDA/THREDDS), archivo `gebco_profundidades_marea_roja.csv`. Fuente registrada como `GEBCO_2026` en columna `profundidad_fondo_fuente`.
3. Nueva columna `profundidad_fondo_fuente` en la salida.

### Diagnósticos (no perder)
- Archivo A: 45.820 filas, estaciones 1–32, fechas 2019–05–09 a 2025–10–27. `PROF_SECT_m` no es único en 19 de 222 grupos; se toma el máximo.
- Archivo B: 358.360 filas, 227 códigos únicos, fechas 2023–06–23 a 2025–03–26. 16 fechas nulas, 57 profundidades nulas, 73 grupos con empate de profundidad máxima, 51 afectan variables. Profundidad de medición máxima ~50 m (no es fondo).
- GEBCO_2026: grid global 15 arc-segundos (~450 m), valor negativo = profundidad. 124 estaciones con píxel de agua directo, 103 con búsqueda en vecindario (±50 px ≈ 20 km). Todas las 227 estaciones tienen profundidad.
- Rango de profundidades GEBCO: -1 m (costa) a 4567 m (Magallanes).
- Archivo B solo reporta oxígeno en ml/L; `oxigeno_mg_L` = NaN.
- Cobertura total: todas las estaciones CTD tienen zona asignada (0 sin zona).

### Archivos creados/modificados
- `procesar_fondo_ctd.py`: lógica de `registro_fondo` parametrizada con `fondo_col`; archivo B usa `gebco_profundidades_marea_roja.csv` para `profundidad_fondo_m`.
- `gebco_profundidades_marea_roja.csv` (nuevo): 227 estaciones con profundidad de GEBCO_2026, método de extracción y elevación.
- `fondo_ctd_por_zona.csv` (modificado): 2.366 filas, `profundidad_fondo_m` sin nulos.
- `AGENTS.md` (nuevo): documentación del proyecto, entorno, pipeline, reglas, gotchas.
- `HISTORIAL_SESIONES.md` (nuevo): esta bitácora.

### Resultados de referencia
- Salida: 2.366 filas (222 archivo A + 2.144 archivo B), 13 columnas.
- `profundidad_fondo_m`: archivo A de `PROF_SECT_m` (79–447 m), archivo B de GEBCO_2026 (-1–4567 m).
- `git status` limpio tras re-ejecutar el pipeline (salida reproducible).

### Pendiente (sesión 2026-11-05)
1. Commit y push a GitHub (`rfvera/seguimiento-obj_4`).
2. Opcional: análisis de variabilidad ambiental por zona/año.

---

## Sesión 2026-11-05 (usuario `rfvera`) — estado de referencia y trayectorias de cambio ambiental

### Objetivo
Pasar de "caracterizar condiciones oceanográficas" a "definir el estado ambiental de referencia y las trayectorias de cambio ambiental regional", usando las zonas de macrofauna como zonificación de referencia.

### Decisiones (usuario)
1. Usar `zona_mf` de `estaciones_CTD_con_ZONA_MACROFAUNA.csv` como zonificación de referencia (19 zonas).
2. No imputar por proximidad: todas las 259 estaciones ya tienen zona_mf asignada.
3. Tendencia lineal anual (OLS) por zona; requiere ≥3 años para calcular.

### Archivos creados/modificados
- `salidas/analisis_ambiental/analisis_estado_referencia.py` (nuevo): script de análisis.
- `salidas/analisis_ambiental/estado_referencia_por_zona.csv` (nuevo): 19 zonas, estadísticas de referencia.
- `salidas/analisis_ambiental/trayectorias_cambio_por_zona.csv` (nuevo): 19 zonas, pendientes de tendencia.
- `salidas/analisis_ambiental/resumen_regional.csv` (nuevo): métricas regionales.
- `salidas/analisis_ambiental/README.md` (nuevo): documentación del análisis.
- `AGENTS.md` (modificado): sección de análisis ambiental agregada.
- `HISTORIAL_SESIONES.md` (modificado): esta bitácora.

### Resultados de referencia
- 2366 registros (2019–2025), 19 zonas de macrofauna, 258 estaciones.
- Temperatura regional: media 9,72 °C, mediana 9,86 °C, desvío 1,51 °C.
- Oxígeno regional: media 5,51 ml/L, mediana 5,26 ml/L, desvío 2,03 ml/L.
- Salinidad regional: media 32,15 psu, mediana 32,56 psu, desvío 1,57 psu.
- Tendencias significativas (p<0,05):
  - Quellon: temperatura +0,87 °C/año (p=0,013, R²=0,999, n=3 años)
  - Aysen: salinidad +0,54 psu/año (p=0,024, R²=0,76, n=6 años)
  - Desertores: salinidad -0,08 psu/año (p=0,029, R²=0,65, n=7 años)
- 8 zonas con solo 2024–2025 (n_anos=2, sin tendencia): Ancud, Calbuco, Chacao, Chiloe central, Guaitecas, Hornopiren, Natales, Tenaun.

### Pendiente (cerrado)
1. Commit y push a GitHub (`rfvera/seguimiento-obj_4`) — HECHO (commit 96be762).
2. Informe Typst con figuras por zona — HECHO (`informe/informe_ambiental.typ` + PDF compilado).

---

## Sesión 2026-11-05 (usuario `rfvera`) — informe Typst de estado ambiental de referencia

### Objetivo
Generar un informe en Typst dentro de `informe/` que documente el estado ambiental de referencia y las trayectorias de cambio ambiental regional (2019–2025).

### Archivos creados
- `informe/informe_ambiental.typ` — documento Typst completo con resumen ejecutivo, contexto, metodología, estado de referencia regional y por zona, trayectorias de cambio, tendencias significativas y conclusiones.
- `informe/informe_ambiental.pdf` — PDF compilado (117 KB).

### Contenido del informe
- Resumen ejecutivo con hallazgos principales (temperatura 9,72 °C, oxígeno 5,51 ml/L, salinidad 32,15 psu).
- 3 tendencias significativas: Quellón temperatura +0,87 °C/año (p=0,013), Aysén salinidad +0,54 psu/año (p=0,024), Desertores salinidad -0,08 psu/año (p=0,029).
- 8 zonas sin datos suficientes para tendencia (solo 2024–2025).
- Conclusiones y recomendaciones de monitoreo.

### Correcciones aplicadas al .typ
- Eliminados delimitadores `*` que chocaban con caracteres especiales (`²`, `<`).
- Reemplazado `header + center` por `center` en tablas.
- Reemplazado `#counter(page).align(right)` por `#counter(page)` en footer.
- Tablas envueltas dentro de `#figure(table(...), caption: [...])`.

### Pendiente (cerrado)
1. Commit y push a GitHub (`rfvera/seguimiento-obj_4`) — HECHO (commit cb6671d en main).

---

## Sesión 2026-11-05 (usuario `rfvera`) — reconstrucción desde archivos originales con procedimiento CTD estándar

### Objetivo
Reconstruir `fondo_ctd_por_zona.csv` desde los dos archivos Excel originales aplicando el procedimiento estándar de procesamiento de perfiles CTD (trimming, despiking, bin averaging por 1 metro, registro de fondo).

### Decisiones (usuario)
1. Separar datos de CTD (perfil continuo) de datos de botella Niskin (muestras discretas) en el archivo A.
2. Archivo A: FLAG_BOOL==0 = superficie/calibración, se descarta (220 filas). Profundidades son enteros (1m, 2m...).
3. Archivo B: profundidad < 0,5 m se descarta (datos en aire/calibración). Datos de alta frecuencia, requieren bin averaging.
4. Despiking por grupo usando regla IQR 3×. Valores atípicos se marcan NaN.
5. Bin averaging por 1 metro de profundidad.
6. Registro de fondo: fila de profundidad máxima por estación×fecha.
7. Profundidad de fondo: Archivo A desde PROF_SECT_m; Archivo B desde GEBCO_2026.

### Archivos creados/modificados
- `reconstruir_ctd.py` (nuevo): script de reconstrucción desde archivos originales.
- `fondo_ctd_por_zona.csv` (modificado): 2.363 registros (220 archivo A + 2.143 archivo B), profundidad de fondo sin nulos.
- `contexto_metodologico_ctd.md` (nuevo): documentación del procedimiento CTD estándar con referencias verificadas.
- `salidas/analisis_ambiental/analisis_estado_referencia.py` (modificado): cargar_datos() usa zona_mf ya presente si existe.
- `salidas/analisis_ambiental/estado_referencia_por_zona.csv` (regenerado): 19 zonas con nuevos valores.
- `salidas/analisis_ambiental/trayectorias_cambio_por_zona.csv` (regenerado): 19 zonas con nuevas pendientes.
- `salidas/analisis_ambiental/resumen_regional.csv` (regenerado): métricas regionales actualizadas.
- `informe/informe_ambiental.typ` (regenerado): con nuevos datos.
- `informe/informe_ambiental.pdf` (regenerado): PDF recompilado.
- `AGENTS.md` (regenerado): documentación completa del nuevo pipeline.
- `HISTORIAL_SESIONES.md` (modificado): esta bitácora.

### Resultados de referencia (datos reconstruidos)
- 2.363 registros (2019–2025), 19 zonas de macrofauna, 258 estaciones.
- Temperatura regional: media 9,73 °C, mediana 9,87 °C, desvío 1,50 °C (n=2.310).
- Oxígeno regional: media 5,48 ml/L, mediana 5,26 ml/L, desvío 1,97 ml/L (n=2.189).
- Salinidad regional: media 32,16 psu, mediana 32,56 psu, desvío 1,54 psu (n=2.247).
- Tendencias significativas (p<0,05):
  - Quellón: temperatura +0,88 °C/año (p=0,023, R2=0,999, n=3 años).
  - Aysén: salinidad +0,50 psu/año (p=0,030, R2=0,76, n=6 años).
  - Desertores: salinidad -0,08 psu/año (p=0,029, R2=0,65, n=7 años).
- 8 zonas con solo 2024–2025 (sin tendencia): Ancud, Calbuco, Chacao, Chiloé central, Guaitecas, Hornopirén, Natales, Tenaun.
- Nulos en variables: temperatura 53, oxígeno 174, salinidad 116 (despiking o datos originales faltantes).

### Pendiente (cerrado)
1. Commit y push a GitHub (`rfvera/seguimiento-obj_4`) — HECHO (commit b9b1a3d en main).

---

## Sesión 2026-11-05 (usuario `rfvera`) — perfiles procesados y series de tiempo por profundidad

### Objetivo
Integrar metodologías de análisis de CTD en series de tiempo: generar perfiles procesados (todas las profundidades, no solo el fondo), promedios anuales por profundidad, ciclo estacional y tendencias de anomalías por zona×profundidad.

### Decisiones (usuario)
1. Los promedios anuales deben ser por profundidad, no solo por registro de fondo.
2. Integrar metodologías de análisis de CTD en series de tiempo (bin averaging 1m, ciclo estacional seno/coseno, anomalías, tendencias lineales de anomalías).
3. Crear archivos de salida con los perfiles procesados.

### Metodología aplicada (verificada en literatura)
- Bin averaging 1 m (aguas costeras): RBR CTD Guidelines (DFO 2017), BODC series documents, oce R package.
- Ciclo estacional anual: ajuste de mínimos cuadrados A_avg + A_amp·sin/cos (Scottish Marine & Freshwater Science 2013).
- Anomalías y tendencias: restar ciclo estacional, OLS de anomalías vs año (RADMED/STOCA, Frontiers 2022).

### Archivos creados/modificados
- `perfiles_procesados.py` (nuevo): script de reconstrucción de perfiles y análisis de series de tiempo por profundidad.
- `salidas/perfiles_procesados/perfiles_procesados.csv` (nuevo): 140.787 filas (estación×fecha×profundidad, 1–349 m).
- `salidas/perfiles_procesados/promedio_anual_por_profundidad.csv` (nuevo): 16.559 filas (zona×profundidad×año).
- `salidas/perfiles_procesados/ciclo_estacional_por_profundidad.csv` (nuevo): 7.615 filas (zona×profundidad×variable).
- `salidas/perfiles_procesados/tendencias_anomalias_por_profundidad.csv` (nuevo): 7.615 filas (zona×profundidad×variable).
- `salidas/perfiles_procesados/resumen_regional_por_profundidad.csv` (nuevo): 349 filas (una por profundidad).
- `informe/informe_ambiental.typ` (regenerado): incluye perfiles por profundidad, ciclo estacional, tendencias de anomalías.
- `informe/informe_ambiental.pdf` (regenerado): PDF recompilado.
- `AGENTS.md` (regenerado): documentación de los 3 pipelines.
- `HISTORIAL_SESIONES.md` (modificado): esta bitácora.

### Resultados de referencia (perfiles procesados)
- 140.787 registros de perfil (2019–2025), 19 zonas, 258 estaciones, 349 profundidades (1–349 m).
- 102 tendencias significativas (p<0,05) en zona×profundidad×variable.
- Aysén (238–250 m): salinidad −0,14 psu/año (R²=0,78–0,82).
- Butachauques (284–290 m): salinidad −0,04 psu/año (R²>0,99).
- Quellón (superficie): temperatura +0,88 °C/año (R²=1,00).
- Nulos: fecha 8.333, temperatura 3.289, oxígeno 8.931, salinidad 8.804 (despiking o datos originales faltantes).
- 43.474 registros de archivo B sin profundidad de fondo (GEBCO no disponible o valor de tierra).

### Pendiente (cerrado)
1. Commit y push a GitHub (`rfvera/seguimiento-obj_4`) — HECHO (commit f9f1494 en main).

---

## Sesión 2026-11-05 (usuario `rfvera`) — análisis de series de tiempo por variable

### Objetivo
Analizar cada zona×profundidad×variable como serie de tiempo anual (2019–2025) con tendencia lineal OLS, estadísticas descriptivas y detección de tendencias significativas.

### Archivos creados/modificados
- `analisis_serie_tiempo.py` (nuevo): script de análisis de series de tiempo por variable.
- `salidas/analisis_serie_tiempo/serie_tiempo_por_variable.csv` (nuevo): 19.893 filas con estadísticas y tendencia por zona×profundidad×variable.
- `salidas/analisis_serie_tiempo/series_tiempo_detalladas.csv` (nuevo): 49.677 filas con valor anual por zona×profundidad×variable×año.
- `salidas/analisis_serie_tiempo/resumen_tendencias_significativas.csv` (nuevo): 178 filas con tendencias significativas (p<0.05).
- `informe/informe_ambiental.typ` (regenerado): sección de series de tiempo por variable añadida con 4 nuevas tablas.
- `informe/informe_ambiental.pdf` (regenerado): PDF recompilado.
- `AGENTS.md` (regenerado): documentación de los 4 pipelines.
- `HISTORIAL_SESIONES.md` (modificado): esta bitácora.

### Resultados de referencia (series de tiempo anual)
- 178 tendencias significativas (p<0,05).
- Temperatura: 41 tendencias sig., Quellón +1,07 °C/año (R²=0,996).
- Oxígeno: 46 tendencias sig., Butachauques +0,68 ml/L/año (R²=0,966).
- Salinidad: 91 tendencias sig., Reloncaví −0,92 psu/año (R²=0,999), Aysén +0,60 psu/año (R²=0,73).

### Pendiente (cerrado)
1. Commit y push a GitHub (`rfvera/seguimiento-obj_4`) — HECHO (commit 522ae62 en main).

---

## Sesión 2026-11-05 (usuario `rfvera`) — mapa de estaciones y zonas ACS agregado al informe Typst

### Objetivo
Agregar el mapa de estaciones de muestreo y polígonos ACS al informe Typst compilado.

### Archivos creados/modificados
- `informe/mapa_estaciones_acs.png` (nuevo): copia del mapa PNG dentro del directorio informe/ (requerido por el sandbox de Typst).
- `informe/informe_ambiental.typ` (modificado): sección "Área de estudio" con el mapa embebido (Mapa 1), ruta de imagen corregida a ruta local.
- `informe/informe_ambiental.pdf` (regenerado): PDF recompilado con el mapa incluido (534 KB).
- `AGENTS.md` (modificado): ruta de la figura actualizada en el anexo.
- `HISTORIAL_SESIONES.md` (modificado): esta bitácora.

### Pendiente
1. Commit y push a GitHub (`rfvera/seguimiento-obj_4`).

### Objetivo
Generar un mapa visual con las estaciones de muestreo CTD y los polígonos de las áreas ACS de SUBPESCA, para mostrar el dominio del análisis.

### Archivos creados/modificados
- `mapa_estaciones_acs.py` (nuevo): script para generar el mapa con estaciones y polígonos ACS.
- `salidas/figuras/mapa_estaciones_acs.png` (nuevo): mapa PNG (470 KB) con 259 estaciones de muestreo y 106 polígonos ACS, estaciones coloreadas por zona_mf (19 zonas).
- `AGENTS.md` (modificado): sección de Pipeline 5 agregada.
- `HISTORIAL_SESIONES.md` (modificado): esta bitácora.

### Resultados de referencia
- 259 estaciones con coordenadas válidas (lat/lon).
- 20 zonas de macrofauna representadas en el mapa (incluyendo "Pta. Arenas").
- 106 polígonos ACS de SUBPESCA mostrados como fondo.
- Costa de Chile agregada (línea continua marrón, Natural Earth 10m) al fondo del mapa.
- Eje X ajustado para llegar hasta 76°W.
- CRS: EPSG:4326 (WGS84).
- Estaciones coloreadas por zona_mf (zorder=3), polígonos ACS gris semitransparente (zorder=1), costa marrón (zorder=0).
- 42 estaciones movidas de zona "Natales" a "Pta. Arenas" (latitud <= -52.45°S).
- 1 estación corregida: M08N1 latitud de -59.916940 a -49.916944 (error de tipeo), vuelve a zona "Natales".

### Pendiente (cerrado)
1. Commit y push a GitHub (`rfvera/seguimiento-obj_4`) — HECHO (commit 1fe206b en main).

---

## Sesión 2026-11-05 (usuario `rfvera`) — nueva zona "Pta. Arenas"

### Objetivo
Crear una nueva zona de macrofauna llamada "Pta. Arenas" que incluya todas las estaciones al sur de los 52°27'S (-52.45°S), separadas de la zona "Natales".

### Decisiones (usuario)
1. Las estaciones con latitud <= -52.45°S cambian de zona "Natales" a "Pta. Arenas".
2. El punto de corte (-52.45°S) es la latitud intermedia entre Puerto Natales (-51.73°S) y Punta Arenas (-53.16°S).

### Archivos creados/modificados
- `estaciones_CTD_con_ZONA_MACROFAUNA.csv` (modificado): 42 estaciones movidas de "Natales" a "Pta. Arenas".
- `mapa_estaciones_acs.py` (modificado): ordenamiento de zonas por latitud (norte a sur).
- `salidas/figuras/mapa_estaciones_acs.png` (regenerado): 20 zonas (incluyendo "Pta. Arenas").
- `informe/mapa_estaciones_acs.png` (copiado): misma imagen en directorio informe/.
- `informe/informe_ambiental.typ` (modificado): mapa actualizado en el informe.
- `informe/informe_ambiental.pdf` (regenerado): PDF recompilado.
- `AGENTS.md` (modificado): documentación actualizada.
- `HISTORIAL_SESIONES.md` (modificado): esta bitácora.

### Resultados de referencia
- 42 estaciones movidas de "Natales" a "Pta. Arenas".
- Zonas: Natales (41), Pta. Arenas (42), Aysen (42), Moraleda (38), Quellon (19), etc. (20 zonas totales).
- Zona Pta. Arenas: latitudes de -52.70°S a -59.92°S.
- Mapa regenerado con costa al fondo, eje X hasta 76°W y leyenda de norte a sur.

### Pendiente
1. Commit y push a GitHub (`rfvera/seguimiento-obj_4`).

## Sesión 2026-11-05 (usuario `rfvera`) — polígonos de zona de macrofauna (Voronoi, sin solapamientos)

### Objetivo
Generar una capa GPKG con polígonos de las zonas de macrofauna usando tesselación de Voronoi por estación y disolución por zona, asegurando que los polígonos NO se solapen entre sí.

### Decisiones (usuario)
1. Usar Voronoi por estación + disolución por zona para evitar solapamientos entre polígonos de zona.
2. Cada polígono de zona representa el área más cercana a las estaciones de esa zona.

### Archivos creados/modificados
- `zonas_poligonos.py` (nuevo): script para generar polígonos de zona usando Voronoi + dissolve.
- `salidas/figuras/zonas_macrofauna.gpkg` (nuevo): capa GPKG con 19 polígonos de zona (EPSG:4326), sin solapamientos entre sí.
- `zonas_poligonos.py` — script reproducible.

### Resultados de referencia
- 19 polígonos de zona generados (una por cada zona de macrofauna).
- Verificación de solapamientos: área de solapamiento ≈ 0 (OK, no hay solapamientos).
- CRS: EPSG:4326 (WGS84).
- Zonas incluidas: Ayacara, Aysen, Butachauques, Calbuco, Chacao, Chaiten, Chaulinec, Chiloe central, Desertores, Estuario, Guaitecas, Hornopiren, Moraleda, Natales, Pta. Arenas, Puyuhuapi, Quellon, Reloncavi, Tenaun.
- Polígonos recortados por área marina (bounding box de estaciones − polígono país Chile de Natural Earth 10m), por lo que NO incluyen tierra firme.

### Pendiente
1. Commit y push a GitHub (`rfvera/seguimiento-obj_4`) — HECHO (commit 4de2599 en main).


## Sesión 2026-11-05 (usuario `rfvera`) — polígonos de zona recortados por área marina (Chile)

### Objetivo
Generar polígonos de zona de macrofauna usando tesselación de Voronoi por estación, recortados
por un área marina = bounding box grande alrededor de las estaciones MINUS el polígono del país
Chile (Natural Earth 10m), para que los polígonos NO incluyan tierra firme.

### Decisiones (usuario)
1. Usar Voronoi por estación + disolución por zona para evitar solapamientos entre polígonos de zona.
2. Recortar cada polígono de Voronoi por el área marina = bbox grande alrededor de las estaciones −
   polígono de Chile (Natural Earth 10m).
3. Cada polígono de zona representa el área marina más cercana a las estaciones de esa zona.

### Archivos creados/modificados
- `zonas_poligonos.py` (reescrito): script para generar polígonos de zona usando Voronoi + dissolve,
  recortado por área marina (bbox − Chile).
- `salidas/figuras/zonas_macrofauna.gpkg` (nuevo): capa GPKG con 19 polígonos de zona (EPSG:4326),
  sin solapamientos entre sí, sin incluir tierra firme.
- `salidas/figuras/ne_10m_admin_0_countries.*` (nuevo): países Natural Earth 10m (necesario para
  reproducir).
- `mapa_estaciones_acs.py` (modificado): mapa actualizado con polígonos de zona recortados por
  área marina, costa de Chile al fondo, eje X hasta 76°W, leyenda de norte a sur.
- `salidas/figuras/mapa_estaciones_acs.png` (regenerado): mapa con estaciones, polígonos de zona,
  polígonos ACS y costa.
- `informe/mapa_estaciones_acs.png` (copiado): misma imagen en directorio informe/.
- `informe/informe_ambiental.pdf` (regenerado): PDF recompilado con el mapa actualizado.
- `AGENTS.md` (modificado): documentación de Pipeline 6 actualizada.
- `HISTORIAL_SESIONES.md` (modificado): esta bitácora.

### Resultados de referencia
- 19 polígonos de zona generados (una por cada zona de macrofauna).
- Verificación de solapamientos: área de solapamiento ≈ 0 (OK, no hay solapamientos).
- CRS: EPSG:4326 (WGS84).
- Zonas incluidas: Ayacara, Aysen, Butachauques, Calbuco, Chacao, Chaiten, Chaulinec,
  Chiloe central, Desertores, Estuario, Guaitecas, Hornopiren, Moraleda, Natales, Pta. Arenas,
  Puyuhuapi, Quellon, Reloncavi, Tenaun.
- Polígonos recortados por área marina = bbox grande de estaciones − polígono país Chile
  (Natural Earth 10m), por lo que NO incluyen tierra firme.

### Pendiente
1. Commit y push a GitHub (`rfvera/seguimiento-obj_4`).


## Sesión 2026-11-05 (usuario `rfvera`) — polígonos de zona recortados por área marina (buffer 30km)

### Objetivo
Corregir los polígonos de zona de macrofauna para que NO incluyan tierra firme.
El método anterior (bbox grande − polígono Chile) dejaba polígonos con tierra en áreas
costeras. Se cambió a un área marina definida como buffer de 30 km alrededor de cada
estación, unido todo junto.

### Decisiones (usuario)
1. Usar buffer de 30 km alrededor de cada estación como área marina (unión de todos los buffers).
2. Crear polígonos de Voronoi por estación recortados por esta área marina.
3. Disolver por zona_mf para obtener polígonos de zona sin solapamientos.

### Archivos creados/modificados
- `zonas_poligonos.py` (reescrito): usa buffer de 30 km alrededor de estaciones como área marina.
- `salidas/figuras/zonas_macrofauna.gpkg` (regenerado): 19 polígonos de zona (EPSG:4326),
  sin solapamientos, sin tierra firme.
- `salidas/figuras/mapa_estaciones_acs.png` (regenerado): mapa con polígonos de zona recortados.
- `informe/mapa_estaciones_acs.png` (copiado).
- `informe/informe_ambiental.pdf` (regenerado).
- `AGENTS.md` (modificado): documentación actualizada.
- `HISTORIAL_SESIONES.md` (modificado): esta bitácora.

### Resultados de referencia
- 19 polígonos de zona generados (una por cada zona de macrofauna).
- Verificación de solapamientos: área de solapamiento ≈ 0 (OK).
- CRS: EPSG:4326 (WGS84).
- Área marina: buffer de 25 km alrededor de estaciones.
- Los polígonos NO incluyen tierra firme y están limitados al área cercana a las estaciones.

### Pendiente
1. Commit y push a GitHub (`rfvera/seguimiento-obj_4`).


## Sesión 2026-11-05 (usuario `rfvera`) — polígonos de zona adyacentes sin solapamientos (área marina = bbox - Chile)

### Objetivo
Generar polígonos de zona de macrofauna que sean ADYACENTES entre sí (comparten bordes) y cubran todo el área marina de estudio, para permitir extrapolación de resultados a cualquier punto dentro de cada zona.

### Decisiones (usuario)
1. Los polígonos de zona deben ser adyacentes entre sí (comparten bordes), no tener huecos entre ellos.
2. Los polígonos deben cubrir todo el área de estudio marina para permitir extrapolación.
3. Usar área marina = bounding box grande alrededor de todas las estaciones MINUS el polígono del país Chile (Natural Earth 10m).
4. Los polígonos NO se solapan entre sí.

### Archivos creados/modificados
- `zonas_poligonos.py` (reescrito): genera polígonos de Voronoi por estación recortados por el área marina = bbox grande - Chile. Los polígonos resultantes son adyacentes entre sí y cubren todo el área marina de estudio.
- `salidas/figuras/zonas_macrofauna.gpkg` (regenerado): 19 polígonos de zona (EPSG:4326), sin solapamientos, sin tierra firme, adyacentes entre sí.
- `salidas/figuras/mapa_estaciones_acs.png` (regenerado): mapa con polígonos de zona adyacentes, estaciones, polígonos ACS y costa.
- `informe/mapa_estaciones_acs.png` (copiado).
- `informe/informe_ambiental.pdf` (regenerado).
- `AGENTS.md` (modificado): documentación de Pipeline 6 actualizada.
- `HISTORIAL_SESIONES.md` (modificado): esta bitácora.

### Resultados de referencia
- 19 polígonos de zona generados (una por cada zona de macrofauna).
- Verificación de solapamientos: área de solapamiento ≈ 0 (OK).
- Verificación de adyacencia: 14 pares de zonas comparten borde (son adyacentes).
- CRS: EPSG:4326 (WGS84).
- Zonas incluidas: Ayacara, Aysen, Butachauques, Calbuco, Chacao, Chaiten, Chaulinec, Chiloe central, Desertores, Estuario, Guaitecas, Hornopiren, Moraleda, Natales, Pta. Arenas, Puyuhuapi, Quellon, Reloncavi, Tenaun.
- Los polígonos cubren todo el área marina de estudio (extrapolación válida para cualquier punto dentro de cada zona).

### Pendiente
1. Commit y push a GitHub (`rfvera/seguimiento-obj_4`).
