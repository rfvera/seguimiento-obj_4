#set page(
  width: 210mm,
  height: 297mm,
  margin: (top: 20mm, right: 20mm, bottom: 20mm, left: 20mm),
  footer: context [Página #counter(page).display()]
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

#let cuadro(body, caption: none) = figure(
  text(size: 9.5pt, body),
  caption: caption,
  kind: "cuadro",
  supplement: [Cuadro],
)

#let mapa(body, caption: none) = figure(
  body,
  caption: caption,
  kind: "mapa",
  supplement: [Mapa],
)

#let figura(body, caption: none) = figure(
  body,
  caption: caption,
  kind: "figura",
  supplement: [Figura],
)

#align(center)[
  #set text(size: 20pt, weight: "bold")
  Estado ambiental de referencia y trayectorias de cambio ambiental regional

  #v(1em)
  #set text(size: 14pt)
  Seguimiento CTD IFOP — Objetivo 4

  #v(1.5em)
  #set text(size: 11pt, fill: gray)
  Período 2019–2025 · 20 zonas de macrofauna · 140.787 registros de perfil CTD
  #v(1em)
  IFOP — Seguimiento de desempeño ambiental acuícola en Chile y su efecto en los ecosistemas de emplazamiento
  #v(2em)
  #set text(size: 10pt, fill: gray)
  Reconstruido desde archivos originales con procedimiento estándar de CTD
  · Perfiles procesados a 1 m de resolución vertical
]

#v(2em)

= Resumen ejecutivo

Este informe define el estado ambiental de referencia y las trayectorias de cambio de las áreas de emplazamiento acuícola monitoreadas por el IFOP entre 2019 y 2025. El análisis se apoya en dos escalas de observación: el registro de fondo de cada cast (2.363 registros estación×fecha en 20 zonas y 258 estaciones) y el perfil completo procesado a 1 m (140.787 registros, profundidades 1–349 m). Los datos se reconstruyeron desde los archivos originales aplicando trimming, despiking y bin averaging de 1 m.

Los valores regionales del registro de fondo son:

- Temperatura: media 9,73 °C (mediana 9,87 °C, desvío estándar 1,50 °C) sobre 2.310 registros válidos.
- Oxígeno disuelto: media 5,48 ml/L (mediana 5,26 ml/L, desvío estándar 1,97 ml/L) sobre 2.189 registros válidos.
- Salinidad: media 32,16 psu (mediana 32,56 psu, desvío estándar 1,54 psu) sobre 2.247 registros válidos.

Seis combinaciones zona×variable muestran tendencia significativa en el registro de fondo (p menor que 0,05): calentamiento en Quellón, aumento de oxígeno en Puyuhuapi y Reloncaví, y cambios de salinidad de distinto signo en Aysén, Butachauques y Desertores. En los perfiles completos, 179 combinaciones zona×profundidad×variable presentan tendencia significativa de anomalías; las series anuales, calculadas con un estimador distinto, arrojan 178 tendencias significativas concentradas en 8 zonas y 106 profundidades. Ambas cifras miden cosas parecidas pero no idénticas y no deben sumarse.

= Área de estudio

El mapa 1 muestra la distribución espacial de las 259 estaciones de la red CTD y los polígonos oficiales de áreas ACS de SUBPESCA. Las estaciones se agrupan en 20 zonas de macrofauna que sirven de referencia para el análisis ambiental; 258 de ellas tienen al menos un registro procesado.

#mapa(
  image("mapa_estaciones_acs.png", width: 80%),
  caption: [Estaciones de muestreo CTD (2019–2025) y polígonos ACS SUBPESCA. Las estaciones están coloreadas por zona de macrofauna (zona_mf). CRS: EPSG:4326 (WGS84).],
)

La zonificación vigente incluye Pta. Arenas como zona propia. En versiones anteriores sus 393 registros (41 estaciones) estaban contabilizados dentro de Natales, lo que desplazaba las medias de esa zona; la separación corrige el sesgo y eleva el conteo de 19 a 20 zonas.

= Contexto y objetivo

El objetivo 4 del seguimiento IFOP evalúa la variabilidad ambiental y la exposición de áreas de emplazamiento acuícola a forzantes naturales y asociados al cambio climático. El análisis pasa de una mera caracterización de condiciones oceanográficas a definir:

1. Un estado ambiental de referencia por zona y profundidad, basado en estadísticas descriptivas de temperatura, oxígeno y salinidad en el registro de fondo y en perfiles completos.
2. Trayectorias de cambio ambiental regional, estimadas como tendencias lineales anuales por zona y profundidad, con corrección por ciclo estacional.

Las zonas de referencia son las definidas en la base de macrofauna del IFOP (zona_mf), que agrupan estaciones por similitud ambiental y geográfica.

= Metodología

== Fuentes de datos

- Compilacion_BD_CTD_SEGUIMIENTO_2019-2025.xlsx — CTD seguimiento 2019–2025 (archivo A, 45.820 filas, estaciones 1–32, sensor CTD SeaBird SBE19plus).
- datos CTD - marea roja.xlsx — CTD marea roja 2023–2025 (archivo B, 358.360 filas, 227 códigos únicos).
- estaciones_CTD_con_ZONA_MACROFAUNA.csv — 259 estaciones con zona de macrofauna asignada (zona_mf).
- gebco_profundidades_marea_roja.csv — batimetría GEBCO_2026 para 227 estaciones de marea roja.

== Procedimiento de procesamiento CTD (estándar oceánico)

Se aplicó el procedimiento estándar para perfiles CTD, basado en el paquete R `oce` (Kelley y Richards, 2026), el informe de procesamiento DY026 del National Oceanography Centre (Williams, 2014) y el protocolo para CTD montados en redes de arrastre de NOAA AFSC (Rohan et al., 2023):

1. Lectura de archivos originales: los archivos .xlsx se leen como solo lectura, nunca se sobrescriben.
2. Trimming: se descartan datos de superficie y calibración. En el archivo A se excluyen las filas con FLAG_BOOL igual a 0; en el archivo B, las profundidades menores a 0,5 m.
3. Despiking: se eliminan valores atípicos por grupo estación×fecha con la regla del IQR (3×IQR). Los valores atípicos se marcan como faltantes.
4. Bin averaging: los datos se promedian en bins de 1 metro centrados en valores enteros (0,5–1,5 m para el bin 1 m), obteniendo un valor por variable por metro.
5. Perfiles procesados: se conserva cada nivel de profundidad bineado, con un registro por estación×fecha×profundidad.
6. Profundidad de fondo: en el archivo A se toma de la columna PROF_SECT_m (profundidad de sector o carta, valor máximo por grupo); en el archivo B, de la batimetría GEBCO_2026 en la coordenada de la estación, porque los perfiles de marea roja llegan mayoritariamente hasta ~55 m (máximo 101 m) y su medición más profunda no representa el fondo.
7. Unión con zonas: cada registro se asigna a su zona de macrofauna (zona_mf).

== Estado de referencia

Por zona de macrofauna y profundidad se calculan número de registros, número de estaciones, rango de años y, para cada variable, media, mediana, percentiles 5/25/75/95 y desvío estándar.

== Trayectorias de cambio (series de tiempo por profundidad)

Por zona×profundidad×variable se calcula el promedio anual y se aplica:

a) Ciclo estacional anual: ajuste de mínimos cuadrados de la forma
   A = A_avg + A_amp·sin(2π·t/12) + A_pha·cos(2π·t/12),
   donde t es el mes (1–12). El ajuste anual de seno y coseno es una descomposición armónica estándar de la señal estacional; se aplica aquí como paso previo al cálculo de anomalías.

b) Anomalías: se resta el ciclo estacional esperado de cada valor observado.

c) Tendencia lineal de anomalías: ajuste OLS de las anomalías contra el año, reportando pendiente, R², p-valor y error estándar. Se requieren al menos 3 años para calcular la tendencia.

Este enfoque de anomalías con ciclo estacional removido se contrasta con un segundo ajuste, OLS directamente sobre el promedio anual por zona×profundidad×variable; de ahí provienen las 178 tendencias de la sección 9.

== Limitaciones

- Nueve zonas (Ancud, Calbuco, Chacao, Chiloé central, Guaitecas, Hornopirén, Natales, Pta. Arenas y Tenaun) tienen datos solo para 2024–2025, de modo que no admiten tendencia.
- Varias tendencias se estiman con 3 años. Un R² cercano a 1 en esas condiciones refleja el escaso número de puntos, no una relación excepcionalmente fuerte; debe leerse como señal preliminar. En algunos niveles, además, el promedio anual se apoya en un único cast.
- Las profundidades de fondo derivadas de GEBCO_2026 tienen resolución de 15 segundos de arco (unos 450 m) y no representan la batimetría local de fiordos y canales.
- El archivo B (marea roja) reporta oxígeno solo en ml/L y sus perfiles llegan mayoritariamente hasta ~55 m (máximo 101 m).
- Faltantes en perfiles: temperatura 3.289, oxígeno 8.931, salinidad 8.804, por despiking o ausencia en el dato original.
- 43.474 registros del archivo B carecen de profundidad de fondo, todos ellos en estaciones sin valor GEBCO utilizable.

= Estado de referencia regional

El cuadro 1 presenta las estadísticas regionales agregadas para todas las zonas y profundidades combinadas, calculadas sobre el registro de fondo.

#cuadro(
  table(
    columns: (3.2cm, 2.4cm, 2.4cm, 2.6cm),
    align: center,
    [Variable], [Media], [Mediana], [Desvío estándar],
    [Temperatura (°C)], [9,73], [9,87], [1,50],
    [Oxígeno (ml/L)], [5,48], [5,26], [1,97],
    [Salinidad (psu)], [32,16], [32,56], [1,54],
  ),
  caption: [Estadísticas regionales del estado de referencia (2019–2025). n temperatura = 2.310, n oxígeno = 2.189, n salinidad = 2.247 registros válidos (registro de fondo).],
)

= Resumen regional por profundidad

El cuadro 2 resume las condiciones por nivel de profundidad, promediando todas las zonas y años disponibles.

#cuadro(
  table(
    columns: (2.2cm, 1.8cm, 2.2cm, 2.2cm, 2.2cm, 1.6cm),
    align: center,
    [Prof. (m)], [n reg.], [Temp. media (°C)], [O2 media (ml/L)], [Sal. media (psu)], [n zonas],
    [1], [2.127], [10,26], [7,02], [29,42], [20],
    [10], [2.295], [10,01], [6,67], [30,66], [20],
    [20], [2.176], [9,80], [6,18], [31,29], [19],
    [30], [1.935], [9,69], [5,97], [31,58], [19],
    [50], [1.337], [9,81], [5,28], [31,98], [17],
    [100], [253], [9,88], [4,40], [31,75], [12],
    [200], [126], [10,21], [3,54], [32,71], [9],
    [300], [22], [10,30], [3,27], [32,99], [6],
  ),
  caption: [Resumen regional por profundidad (2019–2025). n reg. = número de registros de perfil; n zonas = número de zonas con datos en esa profundidad.],
)

La salinidad superficial (29,42 psu a 1 m) es consistente con la descarga de agua dulce de fiordos y canales; por debajo de 50 m se estabiliza en torno a 32 psu. El oxígeno desciende de 7,02 ml/L en superficie a 3,27 ml/L a 300 m. Ese gradiente es coherente con una columna estratificada y con consumo de oxígeno en profundidad; el presente análisis no permite separar ambas causas.

= Tendencias del registro de fondo

El cuadro 3 lista las seis combinaciones zona×variable con tendencia significativa (p menor que 0,05) en el registro de fondo; la Figura 1 muestra esas series completas. La tendencia se ajusta sobre el promedio anual de la zona contra el año calendario, de modo que los años faltantes cuentan como tales y no como un paso entre observaciones consecutivas.

#cuadro(
  table(
    columns: (2.2cm, 2.8cm, 2.6cm, 1.6cm, 1.4cm, 1.5cm),
    align: center,
    [Zona], [Variable], [Tendencia anual], [p-valor], [R²], [n años],
    [Quellón], [Temperatura (°C)], [+0,88], [0,023], [1,00], [3],
    [Puyuhuapi], [Oxígeno (ml/L)], [+0,26], [0,022], [0,77], [6],
    [Reloncaví], [Oxígeno (ml/L)], [+0,45], [0,026], [0,66], [7],
    [Aysén], [Salinidad (psu)], [+0,41], [0,0496], [0,66], [6],
    [Butachauques], [Salinidad (psu)], [−0,05], [0,031], [0,73], [6],
    [Desertores], [Salinidad (psu)], [−0,08], [0,029], [0,65], [7],
  ),
  caption: [Tendencias significativas del registro de fondo (2019–2025). n años = años con promedio anual válido en la zona.],
)

#figura(
  image("figuras/series_tendencias_fondo.png", width: 90%),
  caption: [Series anuales del registro de fondo y de 10 m en las seis zonas con tendencia significativa. La línea discontinua de color es el ajuste OLS sobre el año real; la gris solo une los valores de 10 m, sin ajuste, y en Aysén su pendiente (+0,64/año) no es significativa (p=0,092). Fondo y 10 m no siempre se mueven juntos: en Aysén ambas profundidades se salinizan, pero el fondo lo hace con menor pendiente y menos dispersión; en Butachauques ambas se desalinizan y la señal de 10 m es más errática.],
)

== Interpretación de las tendencias de fondo

- Quellón: la temperatura aumenta +0,88 °C/año, pero la serie cubre solo 2023–2025. El R² de 1,00 (0,9986) con tres puntos es un ajuste casi perfecto, no evidencia de robustez.
- Puyuhuapi y Reloncaví: el oxígeno de fondo sube +0,26 y +0,45 ml/L/año, con 6 y 7 años de datos. Son, junto con Desertores, las de menor p-valor (0,022–0,029), aunque comparten 6–7 años con Aysén y Butachauques.
- Aysén: la salinidad de fondo aumenta +0,41 psu/año, con p=0,0496. Está en el borde del umbral: un año más de datos puede moverla dentro o fuera de la significancia.
- Butachauques y Desertores: la salinidad de fondo desciende −0,05 y −0,08 psu/año. La de Butachauques no aparecía en la versión anterior porque el ajuste usaba la posición de la serie y no el año calendario; al corregirlo, pasa a ser significativa.
- Nueve zonas quedan sin tendencia calculable por contar con dos años de datos.


= Tendencias por profundidad (anomalías con ciclo estacional removido)

Con el perfil completo se detectaron 179 combinaciones zona×profundidad×variable con tendencia significativa de anomalías: 41 en temperatura, 48 en oxígeno y 90 en salinidad. El cuadro 4 muestra bloques seleccionados, no un ranking: procesos continuos en profundidad aparecen como varias filas contiguas.

#cuadro(
  table(
    columns: (2.4cm, 1.2cm, 3.0cm, 2.2cm, 1.4cm, 1.1cm, 1.2cm),
    align: center,
    [Zona], [Prof. (m)], [Variable], [Tendencia anual], [p-valor], [R²], [n años],
    [Aysén], [44], [Salinidad (psu)], [+0,60], [0,030], [0,73], [6],
    [Aysén], [56], [Salinidad (psu)], [+0,49], [0,047], [0,67], [6],
    [Aysén], [239], [Salinidad (psu)], [−0,14], [0,013], [0,82], [6],
    [Aysén], [247], [Salinidad (psu)], [−0,14], [0,015], [0,81], [6],
    [Aysén], [248], [Salinidad (psu)], [−0,08], [0,037], [0,70], [6],
    [Aysén], [251], [Salinidad (psu)], [−0,08], [0,037], [0,70], [6],
    [Butachauques], [285], [Salinidad (psu)], [−0,04], [0,047], [0,99], [3],
    [Butachauques], [295], [Salinidad (psu)], [−0,04], [0,001], [1,00], [3],
    [Butachauques], [304], [Salinidad (psu)], [−0,04], [0,045], [1,00], [3],
    [Quellón], [3], [Temperatura (°C)], [+1,07], [0,043], [1,00], [3],
    [Quellón], [10], [Temperatura (°C)], [+0,99], [0,024], [1,00], [3],
    [Quellón], [22], [Temperatura (°C)], [+0,87], [0,005], [1,00], [3],
  ),
  caption: [Bloques seleccionados de tendencias significativas de anomalías (p menor que 0,05). Los bloques continuos en profundidad corresponden a un mismo proceso, no a observaciones independientes.],
)

== Interpretación de las tendencias por profundidad

- Aysén muestra un contraste vertical neto: salinización en aguas someras (30–56 m, hasta +0,60 psu/año) y desalinización bajo los 239 m (−0,14 psu/año). La señal profunda se sostiene en 6 años con R² de 0,70–0,82.
- Butachauques presenta desalinización profunda muy estable en apariencia (−0,04 psu/año, R² mayor que 0,99), pero descansa en tres años no consecutivos (2019, 2021 y 2025) con un solo registro válido por año a esa profundidad. Con ese n, el R² no debe interpretarse como consistencia temporal.
- Quellón concentra el calentamiento más intenso del registro: +1,07 °C/año a 3 m, decreciente con la profundidad (+0,87 °C/año a 22 m). También aquí la serie es de tres años.

= Series de tiempo por variable (OLS sobre promedio anual)

Como control independiente del método de anomalías, se ajustó OLS directamente sobre el promedio anual por zona×profundidad×variable. Se detectaron 178 tendencias significativas en 8 zonas y 106 profundidades.

#cuadro(
  table(
    columns: (2.2cm, 1.8cm, 2.2cm, 2.2cm, 1.8cm, 1.6cm),
    align: center,
    [Variable], [n tend. sig.], [Pendiente media], [Cambio por década], [R² medio], [p-valor mínimo],
    [Temperatura (°C)], [41], [+0,57 °C/año], [+5,71 °C/década], [0,99], [0,006],
    [Oxígeno (ml/L)], [46], [+0,23 ml/L/año], [+2,27 ml/L/década], [0,88], [0,003],
    [Salinidad (psu)], [91], [+0,09 psu/año], [+0,95 psu/década], [0,78], [0,001],
  ),
  caption: [Resumen de tendencias significativas por variable (series de tiempo anual, 2019–2025).],
)

Que 178 tendencias se repartan en solo 8 zonas no es un defecto del método: las series anuales solo son estimables donde hay al menos tres años por zona×profundidad, y eso ocurre en 11 zonas. Las 8 nombradas (Aysén, Butachauques, Puyuhuapi, Desertores, Quellón, Estuario, Reloncaví y Moraleda) superan el umbral de significancia; Ayacara, Chaulinec y Chaitén son estimables pero no alcanzan el umbral de p = 0,05.

== Tendencias de temperatura

El calentamiento se concentra en Quellón, entre 3 y 23 m, con aumentos de hasta +1,07 °C/año.

#cuadro(
  table(
    columns: (2.4cm, 1.8cm, 2.2cm, 2.2cm, 1.8cm, 1.6cm),
    align: center,
    [Zona], [Prof. (m)], [Pendiente (°C/año)], [Cambio por década], [p-valor], [R²],
    [Quellón], [3], [+1,07], [+10,73], [0,043], [0,996],
    [Quellón], [4], [+1,06], [+10,61], [0,039], [0,996],
    [Quellón], [5], [+1,03], [+10,34], [0,035], [0,997],
    [Quellón], [6], [+1,02], [+10,19], [0,037], [0,997],
    [Quellón], [7], [+1,01], [+10,09], [0,036], [0,997],
  ),
  caption: [Tendencias de calentamiento significativas en temperatura (top 5 por pendiente).],
)

== Tendencias de oxígeno disuelto

El oxígeno presenta 46 tendencias significativas, con los aumentos más fuertes en Butachauques entre 2 y 7 m.

#cuadro(
  table(
    columns: (2.4cm, 1.8cm, 2.2cm, 2.2cm, 1.8cm, 1.6cm),
    align: center,
    [Zona], [Prof. (m)], [Pendiente (ml/L/año)], [Cambio por década], [p-valor], [R²],
    [Butachauques], [6], [+0,68], [+6,84], [0,017], [0,966],
    [Butachauques], [5], [+0,68], [+6,84], [0,018], [0,965],
    [Butachauques], [4], [+0,68], [+6,79], [0,017], [0,967],
    [Butachauques], [7], [+0,68], [+6,77], [0,018], [0,965],
    [Butachauques], [2], [+0,67], [+6,74], [0,014], [0,972],
  ),
  caption: [Tendencias de oxígeno disuelto significativas (top 5 por pendiente).],
)

== Tendencias de salinidad

La salinidad reúne el mayor número de tendencias significativas (91), con los cambios más fuertes en Reloncaví (desalinización somera) y Aysén (salinización somera).

#cuadro(
  table(
    columns: (2.4cm, 1.8cm, 2.2cm, 2.2cm, 1.8cm, 1.6cm),
    align: center,
    [Zona], [Prof. (m)], [Pendiente (psu/año)], [Cambio por década], [p-valor], [R²],
    [Reloncaví], [3], [−0,92], [−9,18], [0,033], [0,997],
    [Reloncaví], [4], [−0,75], [−7,50], [0,007], [1,000],
    [Reloncaví], [5], [−0,62], [−6,15], [0,036], [0,997],
    [Aysén], [44], [+0,60], [+6,02], [0,030], [0,732],
    [Aysén], [31], [+0,59], [+5,92], [0,047], [0,668],
  ),
  caption: [Tendencias de salinidad significativas (top 5 por magnitud de la pendiente).],
)

= Conclusiones

1. El estado ambiental de referencia regional combina temperaturas frías (media 9,73 °C), oxígeno moderado (5,48 ml/L) y salinidad cercana a la del océano abierto (32,16 psu). La heterogeneidad entre zonas y profundidades refleja la complejidad de fiordos y canales de la Patagonia chilena, no un régimen único.

2. El registro de fondo entrega seis tendencias significativas. Las de oxígeno en Puyuhuapi y Reloncaví y la de salinidad en Desertores son las mejor sustentadas por número de años.

3. Las señales más intensas —calentamiento de Quellón y desalinización profunda de Butachauques en el perfil— se apoyan en tres años. Deben tratarse como alertas tempranas, no como tasas consolidadas. La desalinización profunda de Aysén (239–251 m), con seis años y R² de 0,70–0,82, es la tendencia más defendible del análisis por profundidad; su salinidad de fondo, en cambio, sube +0,41 psu/año y queda en el borde de la significancia.

4. Aysén muestra un contraste vertical que el registro de fondo oculta: salinización sobre los 56 m y desalinización bajo los 239 m. Analizar solo el fondo habría promediado procesos opuestos.

5. Nueve zonas cuentan con dos años de datos y no admiten evaluación de tendencia. Sostener su monitoreo es la condición para incorporarlas al diagnóstico de cambio.

6. Las zonas con menor oxígeno de referencia (Puyuhuapi, Moraleda, Chaitén, Estuario) son candidatas a monitoreo prioritario de oxígeno. Ninguna muestra tendencia negativa: las 46 tendencias significativas de oxígeno son positivas, y Puyuhuapi ya registra un aumento de fondo. Conviene verificar si se trata de una recuperación o de una oscilación de corto plazo.

= Referencias

- Kelley, D. y Richards, C. (2026). *Analysis of CTD data*. Vignette del paquete oce. #link("https://cran.r-project.org/web/packages/oce/vignettes/B_ctd.html") (consultado el 6 de noviembre de 2026).
- Williams, C. A. J. (2014). *DY026 CTD processing report*. National Oceanography Centre, Liverpool. #link("https://www.bodc.ac.uk/data/documents/nodb/pdf/DY026_CTD_processing_report.pdf")
- Rohan, S. K., Charriere, N. E., Riggle, B., O'Leary, C. A. y Raring, N. W. (2023). *A flexible approach for processing data collected using trawl-mounted CTDs during Alaska bottom-trawl surveys*. NOAA Technical Memorandum NMFS-AFSC 475. #link("https://doi.org/10.25923/8ape-q461")

= Anexo: archivos de salida y trazabilidad

Las cifras regionales y los conteos provienen de `salidas/verificacion/cifras_informe.csv`, generado por `salidas/verificacion/cifras_informe.py`. Los cuadros 3 a 8 salen de los CSV de esa misma carpeta (`tendencias_fondo_significativas.csv`, `tendencias_profundidad_seleccion.csv`, `top_tendencias_por_variable.csv`) y la figura de `salidas/figuras/series_tiempo_fig.py`. Ninguna cifra se estimó a ojo: el informe completo se contrastó contra esos archivos en la auditoría.

- `salidas/perfiles_procesados/perfiles_procesados.csv` — perfiles CTD procesados (140.787 filas, estación×fecha×profundidad).
- `salidas/perfiles_procesados/promedio_anual_por_profundidad.csv` — promedios anuales por zona×profundidad (16.759 filas).
- `salidas/perfiles_procesados/ciclo_estacional_por_profundidad.csv` — ajuste seno/coseno del ciclo anual (7.615 filas).
- `salidas/perfiles_procesados/tendencias_anomalias_por_profundidad.csv` — tendencias de anomalías (7.615 filas).
- `salidas/perfiles_procesados/resumen_regional_por_profundidad.csv` — métricas regionales por profundidad (349 filas).
- `salidas/analisis_ambiental/estado_referencia_por_zona.csv` — estado de referencia por zona (20 zonas).
- `salidas/analisis_ambiental/trayectorias_cambio_por_zona.csv` — tendencias por zona (20 zonas).
- `salidas/analisis_serie_tiempo/resumen_tendencias_significativas.csv` — 178 tendencias significativas.
- `salidas/figuras/series_tiempo_fig.py` — genera `informe/figuras/series_tendencias_fondo.png` (series anuales de fondo y 10 m en las seis zonas con tendencia).
- `fondo_ctd_por_zona.csv` — registro de fondo (2.363 filas, 220 del archivo A y 2.143 del archivo B).
- `perfiles_procesados.py`, `reconstruir_ctd.py`, `salidas/analisis_ambiental/analisis_estado_referencia.py` — scripts reproducibles.
- `mapa_estaciones_acs.png` — mapa de estaciones y zonas ACS.
