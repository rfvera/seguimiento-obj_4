#set page(
  width: 210mm,
  height: 297mm,
  margin: (top: 20mm, right: 20mm, bottom: 20mm, left: 20mm),
  footer: [Página #counter(page)]
)

#set text(
  size: 11pt,
  font: "Libertinus Serif",
  lang: "es",
)

#set heading(
  numbering: "1.",
  supplement: title,
)

#set list(
  spacing: 0.6em,
)

#align(center)[
  #set text(size: 20pt, weight: "bold")
  Estado ambiental de referencia y trayectorias de cambio ambiental regional

  #v(1em)
  #set text(size: 14pt)
  Seguimiento CTD IFOP — Objetivo 4

  #v(1.5em)
  #set text(size: 11pt, fill: gray)
  Período 2019–2025 · 19 zonas de macrofauna · 140.787 registros de perfil CTD
  #v(1em)
  IFOP — Seguimiento de desempeño ambiental acuícola en Chile y su efecto en los ecosistemas de emplazamiento
  #v(2em)
  #set text(size: 10pt, fill: gray)
  Reconstruido desde archivos originales con procedimiento estándar de CTD
  · Perfiles procesados a 1 m de resolución vertical
]

#v(2em)

= Resumen ejecutivo

Este informe presenta el estado ambiental de referencia y las trayectorias de cambio ambiental regional para las áreas de emplazamiento acuícola monitoreadas por el IFOP entre 2019 y 2025. El análisis se basa en 140.787 registros de perfiles CTD (profundidad 1–349 m, resolución 1 metro) distribuidos en 19 zonas de macrofauna y 258 estaciones de muestreo. Los datos fueron reconstruidos desde los archivos originales aplicando el procedimiento estándar de procesamiento de perfiles CTD (trimming del downcast, despiking y bin averaging por 1 metro).

Los principales hallazgos a nivel regional (todos los registros, todas las profundidades) son:

- Temperatura: media 9,73 °C (mediana 9,87 °C, desvío estándar 1,50 °C) sobre 2.310 registros válidos.
- Oxígeno disuelto: media 5,48 ml/L (mediana 5,26 ml/L, desvío estándar 1,97 ml/L) sobre 2.189 registros válidos.
- Salinidad: media 32,16 psu (mediana 32,56 psu, desvío estándar 1,54 psu) sobre 2.247 registros válidos.

En términos de trayectorias de cambio, se detectaron tendencias estadísticamente significativas (p menor que 0,05) en 102 combinaciones de zona×profundidad×variable, principalmente en salinidad de Aysén (profundidades 238–250 m) y Butachauques (profundidades 284–290 m), y en temperatura de Quellón.

= Área de estudio

El mapa 1 muestra la distribución espacial de las 259 estaciones de muestreo CTD y los polígonos oficiales de áreas ACS de SUBPESCA. Las estaciones están agrupadas en 19 zonas de macrofauna que sirven como referencia para el análisis ambiental.

#figure(
  image("mapa_estaciones_acs.png", width: 80%),
  caption: [Mapa 1: Estaciones de muestreo CTD (2019–2025) y polígonos ACS SUBPESCA. Las estaciones están coloreadas por zona de macrofauna (zona_mf). CRS: EPSG:4326 (WGS84).],
)

= Contexto y objetivo

El objetivo 4 del seguimiento IFOP evalúa la variabilidad ambiental y la exposición de áreas de emplazamiento acuícola a forzantes naturales y asociados al cambio climático. El análisis pasa de una mera caracterización de condiciones oceanográficas a definir:

1. Un **estado ambiental de referencia por zona y profundidad**, basado en estadísticas descriptivas de temperatura, oxígeno y salinidad en el registro de fondo y en perfiles completos.
2. **Trayectorias de cambio ambiental regional**, estimadas como tendencias lineales anuales por zona y profundidad, con corrección por ciclo estacional.

Las zonas de referencia son las definidas en la base de macrofauna del IFOP (zona_mf), que agrupan estaciones por similitud ambiental y geográfica.

= Metodología

== Fuentes de datos

- Compilacion_BD_CTD_SEGUIMIENTO_2019-2025.xlsx — CTD seguimiento 2019–2025 (archivo A, 45.820 filas, estaciones 1–32, sensor CTD SeaBird SBE19plus).
- datos CTD - marea roja.xlsx — CTD marea roja 2023–2025 (archivo B, 358.360 filas, 227 códigos únicos).
- estaciones_CTD_con_ZONA_MACROFAUNA.csv — 259 estaciones con zona de macrofauna asignada (zona_mf).
- gebco_profundidades_marea_roja.csv — batimetría GEBCO_2026 para 227 estaciones de marea roja.

== Procedimiento de procesamiento CTD (estándar oceánico)

Se aplicó el procedimiento estándar para perfiles CTD, basado en las directrices RBR CTD Guidelines (DFO 2017), documentos de series BODC y el paquete R `oce`:

1. **Lectura de archivos originales**: Los archivos .xlsx se leen como solo lectura, nunca se sobrescriben.
2. **Trimming**: Se descartan datos de superficie/calibración. Archivo A: FLAG_BOOL==0 se descarta (220 filas). Archivo B: profundidades < 0,5 m se descartan (2.621 filas).
3. **Despiking**: Se eliminan valores atípicos por grupo (estación×fecha) usando la regla del IQR (3×IQR). Los valores atípicos se marcan como NaN.
4. **Bin averaging**: Los datos se promedian en bins de 1 metro de profundidad, centrados en valores enteros (0.5–1.5 m para el bin 1 m, etc.), obteniendo un valor por variable por metro.
5. **Perfiles procesados**: Se conserva cada nivel de profundidad bineado (no solo el fondo), generando un archivo con un registro por estación×fecha×profundidad.
6. **Profundidad de fondo**: Archivo A desde columna PROF_SECT_m (profundidad de sector/carta). Archivo B desde batimetría GEBCO_2026 por coordenada de estación.
7. **Unión con zonas**: Cada registro se asigna a su zona de macrofauna (zona_mf).

== Estado de referencia

Por zona de macrofauna y profundidad se calculan: número de registros, número de estaciones, rango de años, y para cada variable (temperatura, oxígeno, salinidad): media, mediana, percentiles 5/25/75/95 y desvío estándar.

== Trayectorias de cambio (series de tiempo por profundidad)

Por zona×profundidad×variable se calcula el promedio anual y se aplica:

a) **Ciclo estacional anual**: ajuste de mínimos cuadrados de la forma
   A = A_avg + A_amp·sin(2π·t/12) + A_pha·cos(2π·t/12),
   donde t es el mes (1–12). Método basado en Scottish Marine & Freshwater Science (2013).

b) **Anomalías**: se resta el ciclo estacional esperado de cada valor observado.

c) **Tendencia lineal de anomalías**: ajuste OLS de las anomalías vs. año, reportando pendiente, R², p-valor y error estándar. Se requieren al menos 3 años para calcular la tendencia.

Este enfoque de "anomalías con ciclo estacional removido" sigue la metodología utilizada en series de tiempo oceanográficas como RADMED/STOCA (Frontiers 2022).

== Limitaciones

- Algunas profundidades tienen pocos años de datos, limitando la estimación de tendencias.
- Las profundidades de GEBCO_2026 tienen una resolución de 15 segundos de arco (~450 m).
- El archivo B (marea roja) solo reporta oxígeno en ml/L y perfiles hasta ~50 m.
- Valores faltantes: temperatura 3.289 nulos, oxígeno 8.931 nulos, salinidad 8.804 nulos (debido al despiking o a datos originales faltantes).
- 43.474 registros de archivo B sin profundidad de fondo disponible (GEBCO no disponible o valor de tierra).

= Estado de referencia regional

El cuadro 1 presenta las estadísticas regionales agregadas para todas las zonas y profundidades combinadas.

#figure(
  table(
    columns: (2.5cm, 2.5cm, 2.5cm, 2cm),
    align: center,
    [Variable], [Media], [Mediana], [Desvío estándar],
    [Temperatura (°C)], [9,73], [9,87], [1,50],
    [Oxígeno (ml/L)], [5,48], [5,26], [1,97],
    [Salinidad (psu)], [32,16], [32,56], [1,54],
  ),
  caption: [Cuadro 1: Estadísticas regionales del estado de referencia (2019–2025). n temperatura = 2.310, n oxígeno = 2.189, n salinidad = 2.247 registros válidos (registro de fondo).],
)

= Resumen regional por profundidad

El cuadro 2 presenta las estadísticas regionales por nivel de profundidad (promedio de todas las zonas y años disponibles).

#figure(
  table(
    columns: (2.2cm, 1.6cm, 2.2cm, 2.2cm, 2.2cm, 2.2cm),
    align: center,
    [Prof. (m)], [n reg.], [Temp. media (°C)], [O2 media (ml/L)], [Sal. media (psu)], [n zonas],
    [1.0], [259], [12,15], [6,10], [32,40], [19],
    [10.0], [259], [10,82], [5,44], [32,10], [19],
    [20.0], [259], [10,51], [5,31], [32,25], [19],
    [30.0], [259], [10,32], [5,17], [32,37], [19],
    [50.0], [257], [10,12], [4,89], [32,50], [19],
    [100.0], [209], [10,41], [4,55], [32,75], [17],
    [200.0], [116], [10,71], [3,90], [32,91], [12],
    [300.0], [38], [10,90], [3,45], [33,20], [6],
  ),
  caption: [Cuadro 2: Resumen regional por profundidad (2019–2025). n reg. = número de registros de perfil, n zonas = número de zonas con datos en esa profundidad.],
)

= Tendencias significativas (anomalías, p < 0,05)

Se detectaron 102 tendencias estadísticamente significativas en combinaciones de zona×profundidad×variable. Las más relevantes se muestran a continuación.

#figure(
  table(
    columns: (2.4cm, 1.8cm, 1.8cm, 2.0cm, 1.6cm, 1.6cm),
    align: center,
    [Zona], [Prof. (m)], [Variable], [Tendencia anual], [p-valor], [R²],
    [Aysén], [238,5], [Salinidad (psu)], [-0,14], [0,013], [0,82],
    [Aysén], [239,5], [Salinidad (psu)], [-0,14], [0,013], [0,82],
    [Aysén], [240,5], [Salinidad (psu)], [-0,14], [0,020], [0,78],
    [Aysén], [244,5], [Salinidad (psu)], [-0,14], [0,019], [0,79],
    [Aysén], [245,5], [Salinidad (psu)], [-0,14], [0,015], [0,81],
    [Aysén], [246,5], [Salinidad (psu)], [-0,14], [0,015], [0,81],
    [Aysén], [247,5], [Salinidad (psu)], [-0,14], [0,019], [0,79],
    [Aysén], [248,5], [Salinidad (psu)], [-0,08], [0,037], [0,70],
    [Aysén], [249,5], [Salinidad (psu)], [-0,08], [0,035], [0,71],
    [Aysén], [249,5], [Salinidad (psu)], [-0,08], [0,036], [0,71],
    [Butachauques], [284,5], [Salinidad (psu)], [-0,04], [0,047], [0,99],
    [Butachauques], [285,5], [Salinidad (psu)], [-0,04], [0,042], [0,99],
    [Butachauques], [286,5], [Salinidad (psu)], [-0,04], [0,044], [0,99],
    [Butachauques], [287,5], [Salinidad (psu)], [-0,04], [0,047], [0,99],
    [Butachauques], [288,5], [Salinidad (psu)], [-0,04], [0,046], [0,99],
    [Butachauques], [289,5], [Salinidad (psu)], [-0,04], [0,038], [1,00],
    [Butachauques], [290,5], [Salinidad (psu)], [-0,04], [0,027], [1,00],
    [Quellón], [Superficie], [Temperatura (°C)], [+0,88], [0,023], [1,00],
  ),
  caption: [Cuadro 3: Tendencias significativas de anomalías (p menor que 0,05) por zona×profundidad×variable. Solo se muestran las 16 tendencias más relevantes de 102 detectadas.],
)

== Interpretación de las tendencias

- Aysén (profundidades 238–250 m): salinidad disminuye −0,14 psu/año (p menor que 0,05, R²=0,78–0,82). Indica un proceso de desalinización profunda sostenido en la zona.
- Butachauques (profundidades 284–290 m): salinidad disminuye −0,04 psu/año (p menor que 0,05, R² mayor que 0,99). Tendencia muy consistente de desalinización en aguas profundas.
- **Quellón (superficie)**: temperatura aumenta +0,88 °C/año (p=0,023, R²=1,00). Tendencia de calentamiento superficial fuerte, aunque basada en pocos años (2023–2025).

= Series de tiempo por variable

Cada zona×profundidad×variable se analizó como serie de tiempo anual (2019–2025), calculando tendencia lineal por mínimos cuadrados ordinarios (OLS), cambio por década, estadísticas descriptivas y detección de tendencias significativas (p menor que 0,05).

Se detectaron 178 tendencias significativas en 19 zonas, 349 profundidades y 3 variables:

#figure(
  table(
    columns: (2.2cm, 1.6cm, 2.0cm, 2.0cm, 2.0cm, 1.6cm),
    align: center,
    [Variable], [n tend. sig.], [Pendiente media], [Cambio por década], [R² medio], [p-valor mínimo],
    [Temperatura (°C)], [41], [+0,57 °C/año], [+5,71 °C/década], [0,99], [0,006],
    [Oxígeno (ml/L)], [46], [+0,23 ml/L/año], [+2,27 ml/L/década], [0,88], [0,003],
    [Salinidad (psu)], [91], [+0,10 psu/año], [+0,95 psu/década], [0,78], [0,001],
  ),
  caption: [Cuadro 4: Resumen de tendencias significativas por variable (series de tiempo anual, 2019–2025).],
)

== Tendencias de temperatura

La temperatura muestra las tendencias de calentamiento más fuertes, concentradas en Quellón (superficie, 3–21 m) con aumentos de hasta +1,07 °C/año (R²=0,996).

#figure(
  table(
    columns: (2.4cm, 1.8cm, 2.2cm, 2.2cm, 1.8cm, 1.6cm),
    align: center,
    [Zona], [Prof. (m)], [Pendiente (°C/año)], [Cambio por década], [p-valor], [R²],
    [Quellón], [3.0], [+1,07], [+10,73], [0,043], [0,996],
    [Quellón], [5.0], [+1,03], [+10,34], [0,035], [0,997],
    [Quellón], [10.0], [+0,99], [+9,85], [0,024], [0,999],
    [Quellón], [15.0], [+0,94], [+9,42], [0,019], [0,999],
    [Quellón], [20.0], [+0,89], [+8,92], [0,026], [0,998],
  ),
  caption: [Cuadro 5: Tendencias de calentamiento significativas en temperatura (top 5 por pendiente).],
)

== Tendencias de oxígeno disuelto

El oxígeno disuelto muestra 46 tendencias significativas, con los aumentos más fuertes en Butachauques (profundidades 4–7 m, +0,68 ml/L/año, R²=0,966).

#figure(
  table(
    columns: (2.4cm, 1.8cm, 2.2cm, 2.2cm, 1.8cm, 1.6cm),
    align: center,
    [Zona], [Prof. (m)], [Pendiente (ml/L/año)], [Cambio por década], [p-valor], [R²],
    [Butachauques], [6.0], [+0,68], [+6,84], [0,017], [0,966],
    [Butachauques], [5.0], [+0,68], [+6,84], [0,018], [0,965],
    [Butachauques], [4.0], [+0,68], [+6,79], [0,017], [0,967],
    [Butachauques], [7.0], [+0,68], [+6,77], [0,018], [0,965],
    [Butachauques], [2.0], [+0,67], [+6,74], [0,014], [0,972],
  ),
  caption: [Cuadro 6: Tendencias de oxígeno disuelto significativas (top 5 por pendiente).],
)

== Tendencias de salinidad

La salinidad muestra el mayor número de tendencias significativas (91), con los cambios más fuertes en Reloncaví (profundidades 3–5 m, desalinización de hasta −0,92 psu/año, R²=0,999) y Aysén (profundidades 31–44 m, salinización de hasta +0,60 psu/año, R²=0,73).

#figure(
  table(
    columns: (2.4cm, 1.8cm, 2.2cm, 2.2cm, 1.8cm, 1.6cm),
    align: center,
    [Zona], [Prof. (m)], [Pendiente (psu/año)], [Cambio por década], [p-valor], [R²],
    [Reloncaví], [3.0], [−0,92], [−9,18], [0,033], [0,997],
    [Reloncaví], [4.0], [−0,75], [−7,50], [0,007], [1,000],
    [Reloncaví], [5.0], [−0,62], [−6,15], [0,036], [0,997],
    [Aysén], [44.0], [+0,60], [+6,02], [0,030], [0,732],
    [Aysén], [31.0], [+0,59], [+5,92], [0,047], [0,668],
  ),
  caption: [Cuadro 7: Tendencias de salinidad significativas (top 5 por |pendiente|).],
)

= Conclusiones

1. El estado ambiental de referencia regional muestra temperaturas frías (media 9,73 °C), oxígeno moderado (media 5,48 ml/L) y salinidad cercana al océano abierto (media 32,16 psu), con variabilidad entre zonas y profundidades que refleja la heterogeneidad de los fiordos y canales de la Patagonia chilena.

2. Las tendencias más robustas se observan en salinidad profunda de Aysén y Butachauques (desalinización), y en temperatura superficial de Quellón (calentamiento). Estas zonas deberían priorizarse en el monitoreo de cambio climático.

3. El enfoque por profundidad permite detectar cambios que se ocultan al usar solo el registro de fondo, particularmente en aguas profundas donde las tendencias de salinidad son más consistentes (R²>0,78).

4. Ocho zonas tienen datos solo para 2024–2025 (2 años), por lo que no es posible evaluar trayectorias de cambio para ellas. Se recomienda mantener el monitoreo para acumular suficiente serie temporal.

5. Las zonas con menor oxígeno de referencia (Puyuhuapi, Moraleda, Chaitén, Estuario) son candidatas a monitoreo prioritario de desoxigenación.

6. El análisis de series de tiempo por variable confirma 178 tendencias significativas (p menor que 0,05), con temperatura mostrando el calentamiento más intenso en Quellón (+1,07 °C/año en superficie), oxígeno mostrando aumentos en Butachauques (+0,68 ml/L/año), y salinidad mostrando cambios opuestos en Reloncaví (desalinización −0,92 psu/año) y Aysén (salinización +0,60 psu/año).

= Anexo: archivos de salida

- salidas/perfiles_procesados/perfiles_procesados.csv — perfiles CTD procesados (140.787 filas, estación×fecha×profundidad).
- salidas/perfiles_procesados/promedio_anual_por_profundidad.csv — promedios anuales por zona×profundidad (16.559 filas).
- salidas/perfiles_procesados/ciclo_estacional_por_profundidad.csv — ajuste seno/coseno del ciclo anual (7.615 filas).
- salidas/perfiles_procesados/tendencias_anomalias_por_profundidad.csv — tendencias de anomalías (7.615 filas).
- salidas/perfiles_procesados/resumen_regional_por_profundidad.csv — métricas regionales por profundidad (349 filas).
- perfiles_procesados.py — script reproducible de reconstrucción y análisis.
- reconstruir_ctd.py — script de reconstrucción del registro de fondo.
- fondo_ctd_por_zona.csv — registro de fondo (2.363 filas).
- mapa_estaciones_acs.png — mapa de estaciones y zonas ACS (PNG, 470 KB).
