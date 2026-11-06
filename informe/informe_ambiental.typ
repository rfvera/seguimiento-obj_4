#set page(
  width: 210mm,
  height: 297mm,
  margin: (top: 20mm, right: 20mm, bottom: 20mm, left: 20mm),
  footer: context [ #align(center)[#counter(page).display()] ]
)

#set text(
  size: 12pt,
  font: "Roboto",
  lang: "es",
)

#set par(justify: true, leading: 0.5em)

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

Este informe define el estado ambiental de referencia y las trayectorias de cambio de las áreas de emplazamiento acuícola monitoreadas por el IFOP (Instituto de Fomento Pesquero) entre 2019 y 2025. El análisis se apoya en dos escalas de observación: el registro de fondo de cada cast (2.363 registros estación×fecha en 20 zonas y 258 estaciones) y el perfil completo CTD (Conductividad, Temperatura y Profundidad) procesado a 1 m (140.787 registros, profundidades 1–349 m). Los datos se reconstruyeron desde los archivos originales aplicando trimming, despiking y bin averaging de 1 m.

Los valores regionales del registro de fondo son:

- Temperatura: media 9,73 °C (mediana 9,87 °C, desvío estándar 1,50 °C) sobre 2.310 registros válidos.
- Oxígeno disuelto: media 7,83 mg/L (mediana 7,52 mg/L, desvío estándar 2,81 mg/L) sobre 2.189 registros válidos.
- Salinidad: media 32,16 PSU (Unidades Prácticas de Salinidad; mediana 32,56 PSU, desvío estándar 1,54 PSU) sobre 2.247 registros válidos.

La cobertura temporal no es uniforme: 11 zonas cubren 2019–2025 (con huecos: Aysén, Moraleda y Puyuhuapi sin 2020), 9 zonas tienen solo 2024–2025 y Quellón cubre 2023–2025. La Figura 1 y el cuadro de la sección 3 detallan la cobertura por zona.

Seis combinaciones zona×variable muestran tendencia significativa en el registro de fondo (p menor que 0,05): calentamiento en Quellón, aumento de oxígeno en Puyuhuapi y Reloncaví, y cambios de salinidad de distinto signo en Aysén, Butachauques y Desertores. En los perfiles completos, 179 combinaciones zona×profundidad×variable presentan tendencia significativa de anomalías; las series anuales, calculadas con un estimador distinto, arrojan 178 tendencias significativas concentradas en 8 zonas y 106 profundidades. Ambas cifras miden cosas parecidas pero no idénticas y no deben sumarse.

= Área de estudio

El mapa 1 muestra la distribución espacial de las 259 estaciones de la red CTD y los polígonos oficiales de áreas ACS (Áreas de Concesión de Salmonicultura) de SUBPESCA (Subsecretaría de Pesca y Acuicultura). Las estaciones se agrupan en 20 zonas de macrofauna que sirven de referencia para el análisis ambiental; 258 de ellas tienen al menos un registro procesado.

#mapa(
  image("mapa_estaciones_acs.png", width: 80%),
  caption: [Estaciones de muestreo CTD (2019–2025) y polígonos ACS SUBPESCA. Las estaciones están coloreadas por zona de macrofauna (zona_mf). CRS: EPSG:4326 (WGS84).],
)

La zonificación vigente incluye Pta. Arenas como zona propia. En versiones anteriores sus 393 registros (41 estaciones) estaban contabilizados dentro de Natales, lo que desplazaba las medias de esa zona; la separación corrige el sesgo y eleva el conteo de 19 a 20 zonas.

Las estaciones que componen cada zona se listan en el anexo (tabla de estaciones por zona).

= Cobertura temporal del muestreo

La Figura 1 y el cuadro 9 resumen cuándo se muestreó cada zona. El periodo global del registro es 2019–2025, pero la cobertura por zona es muy desigual y condiciona todo lo que sigue.

#figura(
  image("figuras/cobertura_temporal.png", width: 90%),
  caption: [Cobertura temporal por zona de macrofauna: número de casts con registro de fondo por año (2019–2025). La escala de color es la raíz cuadrada del número de casts, para que los años con pocos muestreos sean visibles. Marcador rojo: zonas con datos solo en 2024–2025.],
)

#cuadro(
  table(
    columns: (3.0cm, 1.8cm, 1.7cm, 1.7cm, 1.5cm, 1.6cm),
    align: center,
    [Zona], [Estaciones], [Primer año], [Último año], [Años con dato], [Casts],
    [Estuario], [8], [2019], [2025], [7], [74],
    [Reloncaví], [9], [2019], [2025], [7], [76],
    [Calbuco], [2], [2024], [2025], [2], [20],
    [Chacao], [2], [2024], [2025], [2], [20],
    [Ancud], [1], [2024], [2025], [2], [10],
    [Hornopirén], [3], [2024], [2025], [2], [29],
    [Butachauques], [4], [2019], [2025], [6], [37],
    [Tenaun], [1], [2024], [2025], [2], [10],
    [Ayacara], [4], [2019], [2025], [7], [34],
    [Chaulinec], [3], [2019], [2025], [7], [27],
    [Chiloé central], [1], [2024], [2025], [2], [10],
    [Desertores], [3], [2019], [2025], [7], [27],
    [Quellón], [19], [2023], [2025], [3], [180],
    [Chaitén], [7], [2019], [2025], [6], [56],
    [Guaitecas], [15], [2024], [2025], [2], [146],
    [Moraleda], [38], [2019], [2025], [6], [361],
    [Puyuhuapi], [13], [2019], [2025], [6], [117],
    [Aysén], [42], [2019], [2025], [6], [377],
    [Natales], [42], [2024], [2025], [2], [359],
    [Pta. Arenas], [41], [2024], [2025], [2], [393],
  ),
  caption: [Cobertura temporal por zona (registro de fondo, 2019–2025). Años con dato = años con al menos un cast válido.],
)

De la tabla se desprenden tres hechos que condicionan el resto del informe:

1. *Nueve zonas (Ancud, Calbuco, Chacao, Chiloé central, Guaitecas, Hornopirén, Natales, Pta. Arenas y Tenaun) tienen datos solo en 2024–2025.* No admiten tendencia de ningún tipo.
2. *Quellón cubre 2023–2025 (3 años).* Sus tendencias son alertas tempranas.
3. *Aysén, Moraleda y Puyuhuapi no tienen datos de 2020.* Las series anuales de esas zonas tienen un hueco que se trata como año faltante en el OLS, no como cero.

Las zonas con menos de tres años quedan fuera de cualquier análisis de trayectoria, y las de tres años se interpretan con la reserva indicada en las limitaciones.

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
6. Profundidad de fondo: en el archivo A se toma de la columna PROF_SECT_m (profundidad de sector o carta, valor máximo por grupo); en el archivo B, de la batimetría GEBCO (General Bathymetric Chart of the Oceans) 2026 en la coordenada de la estación, porque los perfiles de marea roja llegan mayoritariamente hasta ~55 m (máximo 101 m) y su medición más profunda no representa el fondo.
7. Unión con zonas: cada registro se asigna a su zona de macrofauna (zona_mf).

== Zonificación: polígonos de zona de macrofauna

Las 20 zonas de macrofauna (zona_mf) se usan como referencia espacial para todo el análisis. Sus polígonos se construyeron a partir de las 259 estaciones de muestreo con el siguiente procedimiento:

1. *Tesselación de Voronoi* por estación, con `shapely.voronoi_polygons` sobre el bounding box de todas las estaciones. La tesselación se hace en grados; las regiones se recortan después.
2. *Área marina* = bounding box amplio alrededor de todas las estaciones menos la unión de todos los países que intersectan ese bounding box (Chile, Argentina y cualquier otro). Restar solo Chile dejaba tierra argentina dentro de los polígonos.
3. *Asignación*: cada región de Voronoi se asigna a la zona de su punto generador (estación) mediante `contains`/`covers`, y se recorta al área marina.
4. *Dissolve por zona*: las regiones se unen por zona_mf y se recortan de nuevo contra tierra. `set_precision(1e-9)` elimina astillas de borde.
5. *Recorte a 100 km*: cada zona se recorta a la unión de buffers *geodésicos* de 100 km alrededor de sus propias estaciones, generados con `pyproj.Geod` (72 vértices). No se usa EPSG:6933, porque a estas latitudes un buffer de 100 km en esa proyección resulta una elipse de ~148 km N-S por ~66 km E-O. Esto elimina extrapolaciones oceánicas sin respaldo: la auditoría SIG detectó que la versión anterior de Puyuhuapi tenía 11.009,99 km² (94,4 % de su área) en el Atlántico, a 649,9 km de su estación más cercana.
6. *Topología por componentes conexas*: después de restar tierra, se conservan solo las partes que están en la misma componente marina que una parte ancla (la que contiene una estación, o la más cercana si todas caen en tierra). Una parte al otro lado de una barrera terrestre está en otra componente y se descarta. Una parte sin estación pero en la misma componente (agua adyacente) se conserva, para no abrir huecos de cobertura.

Resultado: 20 polígonos de zona, sin solapamientos significativos (0,074 km² de borde), sin tierra firme y sin partes al otro lado de una barrera terrestre sin respaldo. Área total 178.279,27 km².

*Limitaciones de la zonificación:*
- 60 de las 259 estaciones caen en "tierra" según la costa Natural Earth 10 m (fiordos y canales) y quedan fuera de su polígono (distancia máxima 8,54 km). Se requiere cartografía de mayor resolución (GSHHG o SHOA) para corregirlo.
- La tesselación se hace en grados; teselar en un CRS métrico (UTM 18S/19S o Albers) es una mejora pendiente.
- No hay capa de límites marítimos en el repositorio; el residual fuera de aguas chilenas no es calculable.
- Tres partes menores a 1 km² (Chacao 0,224; Moraleda 0,007; Pta. Arenas 0,676 km²).

El Mapa 1 muestra las estaciones coloreadas por zona_mf junto a los polígonos oficiales de ACS de SUBPESCA.


== Estado de referencia

Por zona de macrofauna y profundidad se calculan número de registros, número de estaciones, rango de años y, para cada variable, media, mediana, percentiles 5/25/75/95 y desvío estándar.

Adicionalmente se calcula la saturación del oxígeno (%sat) con la ecuación de Weiss (1970), disponible en los CSVs como `oxigeno_sat_pct`.

== Trayectorias de cambio (series de tiempo por profundidad)

Por zona×profundidad×variable se calcula el promedio anual y se aplica:

a) Ciclo estacional anual: ajuste de mínimos cuadrados de la forma
   A = A_avg + A_amp·sin(2π·t/12) + A_pha·cos(2π·t/12),
   donde t es el mes (1–12). El ajuste anual de seno y coseno es una descomposición armónica estándar de la señal estacional; se aplica aquí como paso previo al cálculo de anomalías.

b) Anomalías: se resta el ciclo estacional esperado de cada valor observado.

c) Tendencia lineal de anomalías: ajuste OLS (mínimos cuadrados ordinarios) de las anomalías contra el año, reportando pendiente, R² (coeficiente de determinación), p-valor y error estándar. Se requieren al menos 3 años para calcular la tendencia.

Este enfoque de anomalías con ciclo estacional removido se contrasta con un segundo ajuste, OLS directamente sobre el promedio anual por zona×profundidad×variable; de ahí provienen las 178 tendencias de la sección 9.

== Limitaciones

- Nueve zonas (Ancud, Calbuco, Chacao, Chiloé central, Guaitecas, Hornopirén, Natales, Pta. Arenas y Tenaun) tienen datos solo para 2024–2025, de modo que no admiten tendencia.
- Varias tendencias se estiman con 3 años. Un R² cercano a 1 en esas condiciones refleja el escaso número de puntos, no una relación excepcionalmente fuerte; debe leerse como señal preliminar. En algunos niveles, además, el promedio anual se apoya en un único cast.
- Las profundidades de fondo derivadas de GEBCO_2026 tienen resolución de 15 segundos de arco (unos 450 m) y no representan la batimetría local de fiordos y canales.
- El archivo B (marea roja) reporta oxígeno en ml/L; se convierte a mg/L con el factor estándar 1,429 mg/ml (densidad del O2 a STP). La saturación se calcula con la ecuación de Weiss (1970). Sus perfiles llegan mayoritariamente hasta ~55 m (máximo 101 m).
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
    [Oxígeno (mg/L)], [7,83], [7,52], [2,81],
    [Salinidad (PSU)], [32,16], [32,56], [1,54],
  ),
  caption: [Estadísticas regionales del estado de referencia (2019–2025). n temperatura = 2.310, n oxígeno = 2.189, n salinidad = 2.247 registros válidos (registro de fondo).],
)

= Resumen regional por profundidad

El cuadro 2 resume las condiciones por nivel de profundidad, promediando todas las zonas y años disponibles.

#cuadro(
  table(
    columns: (2.2cm, 1.8cm, 2.2cm, 2.2cm, 2.2cm, 1.6cm),
    align: center,
    [Prof. (m)], [n reg.], [Temp. media (°C)], [O2 media (mg/L)], [Sal. media (PSU)], [n zonas],
    [1], [2.127], [10,26], [10,04], [29,42], [20],
    [10], [2.295], [10,01], [9,53], [30,66], [20],
    [20], [2.176], [9,80], [8,83], [31,29], [19],
    [30], [1.935], [9,69], [8,53], [31,58], [19],
    [50], [1.337], [9,81], [7,54], [31,98], [17],
    [100], [253], [9,88], [6,28], [31,75], [12],
    [200], [126], [10,21], [5,05], [32,71], [9],
    [300], [22], [10,30], [4,67], [32,99], [6],
  ),
  caption: [Resumen regional por profundidad (2019–2025). n reg. = número de registros de perfil; n zonas = número de zonas con datos en esa profundidad.],
)

La salinidad superficial (29,42 PSU a 1 m) es consistente con la descarga de agua dulce de fiordos y canales; por debajo de 50 m se estabiliza en torno a 32 PSU. El oxígeno desciende de 10,03 mg/L en superficie a 4,67 mg/L a 300 m. Ese gradiente es coherente con una columna estratificada y con consumo de oxígeno en profundidad; el presente análisis no permite separar ambas causas.

= Tendencias del registro de fondo

El cuadro 3 lista las seis combinaciones zona×variable con tendencia significativa (p menor que 0,05) en el registro de fondo; la Figura 2 muestra esas series completas. La tendencia se ajusta sobre el promedio anual de la zona contra el año calendario, de modo que los años faltantes cuentan como tales y no como un paso entre observaciones consecutivas.

#cuadro(
  table(
    columns: (2.2cm, 2.8cm, 2.6cm, 1.6cm, 1.4cm, 1.5cm),
    align: center,
    [Zona], [Variable], [Tendencia anual], [p-valor], [R²], [n años],
    [Reloncaví], [Oxígeno (mg/L)], [+0,64], [0,026], [0,66], [7],
    [Butachauques], [Salinidad (PSU)], [−0,05], [0,031], [0,73], [6],
    [Desertores], [Salinidad (PSU)], [−0,08], [0,029], [0,65], [7],
    [Quellón], [Temperatura (°C)], [+0,88], [0,023], [1,00], [3],
    [Puyuhuapi], [Oxígeno (mg/L)], [+0,37], [0,022], [0,77], [6],
    [Aysén], [Salinidad (PSU)], [+0,41], [0,0496], [0,66], [6],
  ),
  caption: [Tendencias significativas del registro de fondo (2019–2025). n años = años con promedio anual válido en la zona.],
)

#figura(
  image("figuras/series_tendencias_fondo.png", width: 90%),
  caption: [Series anuales del registro de fondo y de 10 m en las seis zonas con tendencia significativa. La línea discontinua de color es el ajuste OLS sobre el año real; la gris solo une los valores de 10 m, sin ajuste, y en Aysén su pendiente (+0,64/año) no es significativa (p=0,092). Fondo y 10 m no siempre se mueven juntos: en Aysén ambas profundidades se salinizan, pero el fondo lo hace con menor pendiente y menos dispersión; en Butachauques ambas se desalinizan y la señal de 10 m es más errática.],
)

== Interpretación de las tendencias de fondo

- Quellón: la temperatura aumenta +0,88 °C/año, pero la serie cubre solo 2023–2025. El R² de 1,00 (0,9986) con tres puntos es un ajuste casi perfecto, no evidencia de robustez.
- Puyuhuapi y Reloncaví: el oxígeno de fondo sube +0,37 y +0,64 mg/L/año, con 6 y 7 años de datos. Son, junto con Desertores, las de menor p-valor (0,022–0,029), aunque comparten 6–7 años con Aysén y Butachauques.
- Aysén: la salinidad de fondo aumenta +0,41 PSU/año, con p=0,0496. Está en el borde del umbral: un año más de datos puede moverla dentro o fuera de la significancia.
- Butachauques y Desertores: la salinidad de fondo desciende −0,05 y −0,08 PSU/año. La de Butachauques no aparecía en la versión anterior porque el ajuste usaba la posición de la serie y no el año calendario; al corregirlo, pasa a ser significativa.
- Nueve zonas quedan sin tendencia calculable por contar con dos años de datos.


= Tendencias por profundidad (anomalías con ciclo estacional removido)

Con el perfil completo se detectaron 179 combinaciones zona×profundidad×variable con tendencia significativa de anomalías: 41 en temperatura, 48 en oxígeno y 90 en salinidad. El cuadro 4 muestra bloques seleccionados, no un ranking: procesos continuos en profundidad aparecen como varias filas contiguas.

#cuadro(
  table(
    columns: (2.4cm, 1.2cm, 3.0cm, 2.2cm, 1.4cm, 1.1cm, 1.2cm),
    align: center,
    [Zona], [Prof. (m)], [Variable], [Tendencia anual], [p-valor], [R²], [n años],
    [Butachauques], [285], [Salinidad (PSU)], [−0,04], [0,047], [0,99], [3],
    [Butachauques], [295], [Salinidad (PSU)], [−0,04], [0,001], [1,00], [3],
    [Butachauques], [304], [Salinidad (PSU)], [−0,04], [0,045], [1,00], [3],
    [Quellón], [3], [Temperatura (°C)], [+1,07], [0,043], [0,996], [3],
    [Quellón], [10], [Temperatura (°C)], [+0,99], [0,024], [0,999], [3],
    [Quellón], [22], [Temperatura (°C)], [+0,87], [0,005], [1,00], [3],
    [Aysén], [44], [Salinidad (PSU)], [+0,60], [0,030], [0,73], [6],
    [Aysén], [56], [Salinidad (PSU)], [+0,49], [0,047], [0,67], [6],
    [Aysén], [239], [Salinidad (PSU)], [−0,14], [0,013], [0,82], [6],
    [Aysén], [247], [Salinidad (PSU)], [−0,14], [0,015], [0,81], [6],
    [Aysén], [248], [Salinidad (PSU)], [−0,08], [0,037], [0,70], [6],
    [Aysén], [251], [Salinidad (PSU)], [−0,08], [0,037], [0,70], [6],
  ),
  caption: [Bloques seleccionados de tendencias significativas de anomalías (p menor que 0,05). Los bloques continuos en profundidad corresponden a un mismo proceso, no a observaciones independientes.],
)

== Interpretación de las tendencias por profundidad

- Aysén muestra un contraste vertical neto: salinización en aguas someras (30–56 m, hasta +0,60 PSU/año) y desalinización bajo los 239 m (−0,14 PSU/año). La señal profunda se sostiene en 6 años con R² de 0,70–0,82.
- Butachauques presenta desalinización profunda muy estable en apariencia (−0,04 PSU/año, R² mayor que 0,99), pero descansa en tres años no consecutivos (2019, 2021 y 2025) con un solo registro válido por año a esa profundidad. Con ese n, el R² no debe interpretarse como consistencia temporal.
- Quellón concentra el calentamiento más intenso del registro: +1,07 °C/año a 3 m, decreciente con la profundidad (+0,87 °C/año a 22 m). También aquí la serie es de tres años.

= Series de tiempo por variable (OLS sobre promedio anual)

Como control independiente del método de anomalías, se ajustó OLS directamente sobre el promedio anual por zona×profundidad×variable. Se detectaron 178 tendencias significativas en 8 zonas y 106 profundidades.

#cuadro(
  table(
    columns: (2.2cm, 1.8cm, 2.2cm, 2.2cm, 1.8cm, 1.6cm),
    align: center,
    [Variable], [n tend. sig.], [Pendiente media], [Cambio por década], [R² medio], [p-valor mínimo],
    [Temperatura (°C)], [41], [+0,57 °C/año], [+5,71 °C/década], [0,99], [0,006],
    [Oxígeno (mg/L)], [46], [+0,32 mg/L/año], [+3,24 mg/L/década], [0,88], [0,003],
    [Salinidad (PSU)], [91], [+0,09 PSU/año], [+0,95 PSU/década], [0,78], [0,001],
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
    [Zona], [Prof. (m)], [Pendiente (mg/L/año)], [Cambio por década], [p-valor], [R²],
    [Butachauques], [6], [+0,97], [+9,78], [0,017], [0,966],
    [Butachauques], [5], [+0,97], [+9,77], [0,018], [0,965],
    [Butachauques], [4], [+0,97], [+9,70], [0,017], [0,967],
    [Butachauques], [7], [+0,97], [+9,67], [0,018], [0,965],
    [Butachauques], [2], [+0,96], [+9,63], [0,014], [0,972],
  ),
  caption: [Tendencias de oxígeno disuelto significativas (top 5 por pendiente).],
)

== Tendencias de salinidad

La salinidad reúne el mayor número de tendencias significativas (91), con los cambios más fuertes en Reloncaví (desalinización somera) y Aysén (salinización somera).

#cuadro(
  table(
    columns: (2.4cm, 1.8cm, 2.2cm, 2.2cm, 1.8cm, 1.6cm),
    align: center,
    [Zona], [Prof. (m)], [Pendiente (PSU/año)], [Cambio por década], [p-valor], [R²],
    [Reloncaví], [3], [−0,92], [−9,18], [0,033], [0,997],
    [Reloncaví], [4], [−0,75], [−7,50], [0,007], [1,000],
    [Reloncaví], [5], [−0,62], [−6,15], [0,036], [0,997],
    [Aysén], [44], [+0,60], [+6,02], [0,030], [0,732],
    [Aysén], [31], [+0,59], [+5,92], [0,047], [0,668],
  ),
  caption: [Tendencias de salinidad significativas (top 5 por magnitud de la pendiente).],
)


= Análisis por estación

El análisis por zona agrega señal y puede ocultar la heterogeneidad dentro de cada zona. Repetir el mismo procedimiento estación por estación muestra cuántas estaciones individualmente sostienen una tendencia.

#cuadro(
  table(
    columns: (2.8cm, 1.8cm, 2.0cm, 2.2cm, 2.4cm),
    align: center,
    [Variable], [Profundidad], [Estaciones], [Con 3+ años], [Con tendencia sig.],
    [Temperatura (°C)], [10 m], [258], [44], [6],
    [Temperatura (°C)], [Fondo], [258], [45], [3],
    [Oxígeno (mg/L)], [10 m], [258], [45], [1],
    [Oxígeno (mg/L)], [Fondo], [258], [45], [0],
    [Salinidad (PSU)], [10 m], [258], [35], [2],
    [Salinidad (PSU)], [Fondo], [258], [45], [1],
  ),
  caption: [Resumen del análisis por estación (2019–2025). Con 3+ años = estaciones con al menos 3 años de datos anuales. Con tendencia sig. = p menor que 0,05.],
)


#cuadro(
  table(
    columns: (2.2cm, 1.8cm, 2.4cm, 1.6cm, 1.2cm, 1.8cm, 1.4cm, 1.2cm),
    align: center,
    [Zona], [Estación], [Variable], [Prof.], [n años], [Pendiente/año], [p-valor], [R²],
    [Chaulinec], [10], [Temperatura (°C)], [10 m], [7], [−0,11], [0,0480], [0,576],
    [Desertores], [11], [Salinidad (PSU)], [Fondo], [7], [−0,05], [0,0299], [0,644],
    [Quellón], [L22N1], [Oxígeno (mg/L)], [10 m], [3], [−0,51], [0,0109], [1,000],
    [Quellón], [L22N2], [Temperatura (°C)], [10 m], [3], [+1,20], [0,0434], [0,995],
    [Quellón], [L16N1], [Temperatura (°C)], [10 m], [3], [+1,12], [0,0278], [0,998],
    [Quellón], [L22N3], [Temperatura (°C)], [10 m], [3], [+1,10], [0,0042], [1,000],
    [Quellón], [L24N1], [Temperatura (°C)], [10 m], [3], [+0,98], [0,0168], [0,999],
    [Quellón], [L16N1], [Temperatura (°C)], [Fondo], [3], [+1,03], [0,0179], [0,999],
    [Quellón], [L24N1], [Temperatura (°C)], [Fondo], [3], [+0,89], [0,0177], [0,999],
    [Chaitén], [13], [Salinidad (PSU)], [10 m], [6], [−0,09], [0,0290], [0,735],
    [Aysén], [21], [Salinidad (PSU)], [10 m], [3], [+0,09], [0,0367], [0,997],
    [Aysén], [32], [Temperatura (°C)], [10 m], [3], [−0,61], [0,0182], [0,999],
    [Aysén], [24], [Temperatura (°C)], [Fondo], [6], [−0,12], [0,0245], [0,756],
  ),
  caption: [Estaciones con tendencia significativa (p menor que 0,05) en el análisis por estación (2019–2025). Pendiente en la unidad de la variable por año.],
)


#figura(
  image("figuras/series_estaciones_temperatura_fondo.png", width: 90%),
  caption: [Series anuales de temperatura por estación con tendencia significativa, registro de fondo. Una línea por estación, coloreada por zona.],
)

#figura(
  image("figuras/series_estaciones_temperatura_10m.png", width: 90%),
  caption: [Series anuales de temperatura por estación con tendencia significativa, a 10 m.],
)

#figura(
  image("figuras/series_estaciones_oxigeno_10m.png", width: 90%),
  caption: [Series anuales de oxígeno por estación con tendencia significativa, a 10 m. No hay estaciones con tendencia significativa en el registro de fondo.],
)

#figura(
  image("figuras/series_estaciones_salinidad_fondo.png", width: 90%),
  caption: [Series anuales de salinidad por estación con tendencia significativa, registro de fondo.],
)

#figura(
  image("figuras/series_estaciones_salinidad_10m.png", width: 90%),
  caption: [Series anuales de salinidad por estación con tendencia significativa, a 10 m.],
)

== Interpretación del análisis por estación

- Solo *13 de las 258 estaciones* (5 %) presentan una tendencia significativa en alguna variable y profundidad. La señal de cambio detectada a nivel de zona no se repite estación por estación.
- La temperatura concentra la mayoría de las tendencias (9 de 13), y casi todas en Quellón (7 de las 9). Quellón es el único caso donde el calentamiento es consistente entre estaciones individuales y la zona.
- El oxígeno tiene una sola estación con tendencia significativa (L22N1, Quellón, 10 m, −0,51 mg/L/año), a pesar de que la zona de Puyuhuapi muestra un aumento de fondo. La señal de oxígeno es más difusa a escala de estación.
- La salinidad tiene 4 estaciones con tendencia: 2 en Quellón (calentamiento asociado a desalinización), 1 en Chaitén, 1 en Aysén y 1 en Desertores. En Aysén, la estación 21 se saliniza (+0,09 PSU/año a 10 m) mientras la estación 24 se desaliniza (−0,12 PSU/año en fondo), lo que ilustra la heterogeneidad vertical y espacial dentro de la zona.
- Las estaciones con tendencia tienen series de 3 a 7 años, con n pequeño. Sus R² altos (mayor que 0,99 en Quellón) reflejan el escaso número de puntos, no una relación excepcionalmente fuerte.

= Conclusiones

1. El estado ambiental de referencia regional combina temperaturas frías (media 9,73 °C), oxígeno moderado (7,83 mg/L) y salinidad cercana a la del océano abierto (32,16 PSU). La heterogeneidad entre zonas y profundidades refleja la complejidad de fiordos y canales de la Patagonia chilena, no un régimen único.

2. El registro de fondo entrega seis tendencias significativas. Las de oxígeno en Puyuhuapi y Reloncaví y la de salinidad en Desertores son las mejor sustentadas por número de años.

3. Las señales más intensas —calentamiento de Quellón y desalinización profunda de Butachauques en el perfil— se apoyan en tres años. Deben tratarse como alertas tempranas, no como tasas consolidadas. La desalinización profunda de Aysén (239–251 m), con seis años y R² de 0,70–0,82, es la tendencia más defendible del análisis por profundidad; su salinidad de fondo, en cambio, sube +0,41 PSU/año y queda en el borde de la significancia.

4. Aysén muestra un contraste vertical que el registro de fondo oculta: salinización sobre los 56 m y desalinización bajo los 239 m. Analizar solo el fondo habría promediado procesos opuestos.

5. Nueve zonas cuentan con dos años de datos y no admiten evaluación de tendencia. Sostener su monitoreo es la condición para incorporarlas al diagnóstico de cambio.

6. Las zonas con menor oxígeno de referencia (Puyuhuapi, Moraleda, Chaitén, Estuario) son candidatas a monitoreo prioritario de oxígeno. Ninguna muestra tendencia negativa: las 46 tendencias significativas de oxígeno son positivas, y Puyuhuapi ya registra un aumento de fondo. Conviene verificar si se trata de una recuperación o de una oscilación de corto plazo.

= Referencias

- Kelley, D. y Richards, C. (2026). *Analysis of CTD data*. Vignette del paquete oce. #link("https://cran.r-project.org/web/packages/oce/vignettes/B_ctd.html") (consultado el 6 de noviembre de 2026).
- Williams, C. A. J. (2014). *DY026 CTD processing report*. National Oceanography Centre, Liverpool. #link("https://www.bodc.ac.uk/data/documents/nodb/pdf/DY026_CTD_processing_report.pdf")
- Rohan, S. K., Charriere, N. E., Riggle, B., O'Leary, C. A. y Raring, N. W. (2023), NOAA (National Oceanic and Atmospheric Administration). *A flexible approach for processing data collected using trawl-mounted CTDs during Alaska bottom-trawl surveys*. NOAA Technical Memorandum NMFS-AFSC 475. #link("https://doi.org/10.25923/8ape-q461")

= Estaciones por zona

El cuadro 10 lista, por zona de macrofauna, las estaciones de muestreo que la componen. Los códigos con prefijo ``L`` corresponden al seguimiento 2019–2025 (archivo A, estaciones 1–32 y sus réplicas); los prefijos ``A`` y ``M`` corresponden a marea roja (archivo B, 2023–2025). La distribución espacial se muestra en el Mapa 1.

#cuadro(
  table(
    columns: (2.6cm, 1.4cm, 13.0cm),
    align: (left, center, left),
    [Zona], [n], [Estaciones (código)],
    [Estuario], [8], [`1, 2, L02, L02N1, L02N2, L02N3, L02N4, L03N1`],
    [Reloncavi], [9], [`3, 4, 5, 6, L01, L03, L04N2, L06N1, L06N2`],
    [Calbuco], [2], [`L04, L04N4`],
    [Chacao], [2], [`L04N3, L06`],
    [Ancud], [1], [`L05`],
    [Hornopiren], [3], [`L06N3, L06N4, L09N1`],
    [Butachauques], [4], [`8, L07, L08, L09`],
    [Tenaun], [1], [`L11`],
    [Ayacara], [4], [`7, 9, L10, L10N3`],
    [Chaulinec], [3], [`10, L13, L13N1`],
    [Chiloe central], [1], [`L12`],
    [Desertores], [3], [`11, L10N2, L14`],
    [Quellon], [19], [`L16, L16N1, L18, L18N2, L19, L19N1, L19N2, L19N3, L20, L20N1, L22, L22N1, L22N2, L22N3, L23, L23N1, L23N2, L24, L24N1`],
    [Chaiten], [7], [`12, 13, L17, L17N1, L17N2, L19N4, L25`],
    [Guaitecas], [16], [`A01, A02, A02N1, A03, A03N1, A04, A05, A05N1, A05N2, A33, A34, A35N2, A35N3, A38N3, A38N4, L25N1`],
    [Moraleda], [38], [`14, 15, 16, A04N1, A06, A07, A08, A08N1, A08N2, A08N3, A09, A10, A11, A11N1, A12, A13, A14, A15, A18, A18N1, A18N2, A18N3, A18N4, A22, A23, A30, A30N1, A32N1, A35, A35N1, A36, A37, A38N1, A38N2, A39, A40, A41, A41N1`],
    [Puyuhuapi], [13], [`17, 18, 19, 20, A16, A16N1, A17, A19, A19N1, A19N2, A20, A20N1, A21`],
    [Aysen], [42], [`21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, A24, A25, A26, A27, A28, A29, A32, A42, A43, A44, A45, A47, A48, A48N1, A49, A49N1, A50, A50N1, A51, A51N1, A52, A53, A54, A55, A57, A59, A60, A62, M04, M05`],
    [Natales], [42], [`M01N, M02N, M03N, M06, M06N, M06N1, M06N2, M06N3, M06N4, M07, M07N, M07N1, M07N2, M07N3, M07N4, M07N5, M08, M08N1, M09, M09N1, M09N2, M10, M11, M12, M13, M13N1, M13N2, M14, M15, M16, M16N1, M17, M18, M20, M21, M22, M23, M24N, M24N1, M24N2, M24N3, M25N`],
    [Pta. Arenas], [41], [`M24, M25, M26, M27, M29, M29N1, M30, M31, M32, M33, M34, M34N1, M35, M36, M36N1, M36N2, M37, M37N1, M37N2, M38, M38N1, M39, M39C1, M39C3, M39D1, M39D2, M39N1, M39N2, M39N3, M39N4, M39N5, M40, M40N1, M41, M42, M43, M44, M44N1, M45, M46, M46N1`],
  ),
  caption: [Estaciones de muestreo por zona de macrofauna (orden norte-sur). n = número de estaciones con al menos un cast procesado.],
)


= Reproducibilidad del mapa

El Mapa 1 se puede reproducir con cualquier SIG a partir de `informe/datos/mapa_reproducible.gpkg` (capas `zonas`, `estaciones`, `costa`) y `informe/datos/acs_subpesca.gpkg`. El script `salidas/figuras/mapa_estaciones_acs.py` regenera el PNG a partir de esos archivos. Las capas están en EPSG:4326 (WGS84).

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
- `salidas/figuras/cobertura_temporal.py` — genera `informe/figuras/cobertura_temporal.png` y `salidas/verificacion/cobertura_temporal.csv`.
- `salidas/verificacion/zonas_estaciones.csv` — estaciones (código) por zona, orden norte-sur.
- `salidas/verificacion/zonas_estaciones.py` — genera el CSV anterior.
- `informe/datos/mapa_reproducible.gpkg` — capas `zonas` (20 polígonos, zona_mf), `estaciones` (259 puntos, zona_mf) y `costa` (línea Natural Earth 10 m), EPSG:4326. Reproduce el Mapa 1.
- `informe/datos/acs_subpesca.gpkg` — polígonos oficiales de ACS de SUBPESCA.
- `informe/datos/ne_10m_coastline.*` — línea de costa Natural Earth 10 m (shapefile).
- `salidas/figuras/empaquetar_mapa.py` — genera el GPKG anterior a partir de las salidas del pipeline.
- `salidas/oxigeno_conversion.py` — añade `oxigeno_mg_L` (factor 1,429) y `oxigeno_sat_pct` (Weiss 1970) a los CSVs de fondo y perfiles.
- `zonas_poligonos.py` — genera `salidas/figuras/zonas_macrofauna.gpkg` (20 polígonos, orden norte-sur).
- `salidas/analisis_por_estacion.py` — tendencias por estación (fondo y 10 m), resumen y top. Genera las Figuras 3 a 7.
- `fondo_ctd_por_zona.csv` — registro de fondo (2.363 filas, 220 del archivo A y 2.143 del archivo B).
- `perfiles_procesados.py`, `reconstruir_ctd.py`, `salidas/analisis_ambiental/analisis_estado_referencia.py` — scripts reproducibles.
- `mapa_estaciones_acs.png` — mapa de estaciones y zonas ACS.
