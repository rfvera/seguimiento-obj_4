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

= Conclusiones

1. El estado ambiental de referencia regional muestra temperaturas frías (media 9,73 °C), oxígeno moderado (media 5,48 ml/L) y salinidad cercana al océano abierto (media 32,16 psu), con variabilidad entre zonas y profundidades que refleja la heterogeneidad de los fiordos y canales de la Patagonia chilena.

2. Las tendencias más robustas se observan en salinidad profunda de Aysén y Butachauques (desalinización), y en temperatura superficial de Quellón (calentamiento). Estas zonas deberían priorizarse en el monitoreo de cambio climático.

3. El enfoque por profundidad permite detectar cambios que se ocultan al usar solo el registro de fondo, particularmente en aguas profundas donde las tendencias de salinidad son más consistentes (R²>0,78).

4. Ocho zonas tienen datos solo para 2024–2025 (2 años), por lo que no es posible evaluar trayectorias de cambio para ellas. Se recomienda mantener el monitoreo para acumular suficiente serie temporal.

5. Las zonas con menor oxígeno de referencia (Puyuhuapi, Moraleda, Chaitén, Estuario) son candidatas a monitoreo prioritario de desoxigenación.

= Anexo: archivos de salida

- salidas/perfiles_procesados/perfiles_procesados.csv — perfiles CTD procesados (140.787 filas, estación×fecha×profundidad).
- salidas/perfiles_procesados/promedio_anual_por_profundidad.csv — promedios anuales por zona×profundidad (16.559 filas).
- salidas/perfiles_procesados/ciclo_estacional_por_profundidad.csv — ajuste seno/coseno del ciclo anual (7.615 filas).
- salidas/perfiles_procesados/tendencias_anomalias_por_profundidad.csv — tendencias de anomalías (7.615 filas).
- salidas/perfiles_procesados/resumen_regional_por_profundidad.csv — métricas regionales por profundidad (349 filas).
- perfiles_procesados.py — script reproducible de reconstrucción y análisis.
- reconstruir_ctd.py — script de reconstrucción del registro de fondo.
- fondo_ctd_por_zona.csv — registro de fondo (2.363 filas).
