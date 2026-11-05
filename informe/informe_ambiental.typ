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
  Período 2019–2025 · 19 zonas de macrofauna · 2.363 registros de fondo
  #v(1em)
  IFOP — Seguimiento de desempeño ambiental acuícola en Chile y su efecto en los ecosistemas de emplazamiento
  #v(2em)
  #set text(size: 10pt, fill: gray)
  Reconstruido desde archivos originales con procedimiento estándar de CTD
]

#v(2em)

= Resumen ejecutivo

Este informe presenta el estado ambiental de referencia y las trayectorias de cambio ambiental regional para las áreas de emplazamiento acuícola monitoreadas por el IFOP entre 2019 y 2025. El análisis se basa en 2.363 registros de fondo CTD (profundidad máxima por estación × fecha) distribuidos en 19 zonas de macrofauna y 258 estaciones de muestreo. Los datos fueron reconstruidos desde los archivos originales aplicando el procedimiento estándar de procesamiento de perfiles CTD (trimming del downcast, despiking y bin averaging por 1 metro).

Los principales hallazgos son:

- Temperatura regional: media 9,73 °C (mediana 9,87 °C, desvío estándar 1,50 °C) sobre 2.310 registros válidos.
- Oxígeno disuelto regional: media 5,48 ml/L (mediana 5,26 ml/L, desvío estándar 1,97 ml/L) sobre 2.189 registros válidos.
- Salinidad regional: media 32,16 psu (mediana 32,56 psu, desvío estándar 1,54 psu) sobre 2.247 registros válidos.

En términos de trayectorias de cambio, se detectaron tendencias estadísticamente significativas (p menor que 0,05) en tres zonas:

- Quellón: calentamiento de +0,88 °C/año en temperatura (p=0,023, R2=0,999, 3 años).
- Aysén: aumento de salinidad de +0,50 psu/año (p=0,030, R2=0,76, 6 años).
- Desertores: disminución de salinidad de -0,08 psu/año (p=0,029, R2=0,65, 7 años).

Otras zonas muestran tendencias no significativas pero con magnitudes notables (por ejemplo, Puyuhuapi muestra disminución de oxígeno de -0,30 ml/L/año con p=0,017, aunque el modelo tiene solo 6 años de datos).

= Contexto y objetivo

El objetivo 4 del seguimiento IFOP evalúa la variabilidad ambiental y la exposición de áreas de emplazamiento acuícola a forzantes naturales y asociados al cambio climático. El análisis pasa de una mera caracterización de condiciones oceanográficas a definir:

1. Un estado ambiental de referencia por zona, basado en percentiles y estadísticas descriptivas de temperatura, oxígeno y salinidad en el registro de fondo.
2. Trayectorias de cambio ambiental regional, estimadas como tendencias lineales anuales por zona.

Las zonas de referencia son las definidas en la base de macrofauna del IFOP (zona_mf), que agrupan estaciones por similitud ambiental y geográfica.

= Metodología

== Fuentes de datos

- Compilacion_BD_CTD_SEGUIMIENTO_2019-2025.xlsx — CTD seguimiento 2019–2025 (archivo A, 45.820 filas, estaciones 1–32, sensor CTD SeaBird SBE19plus).
- datos CTD - marea roja.xlsx — CTD marea roja 2023–2025 (archivo B, 358.360 filas, 227 códigos únicos).
- estaciones_CTD_con_ZONA_MACROFAUNA.csv — 259 estaciones con zona de macrofauna asignada (zona_mf).

== Procedimiento de procesamiento CTD

Se aplicó el procedimiento estándar para perfiles CTD (basado en oce R package y prácticas de BODC/NOAA):

1. **Lectura de archivos originales**: Los archivos .xlsx se leen como solo lectura, nunca se sobrescriben.
2. **Trimming**: Se descartan datos de superficie/calibración. Archivo A: FLAG_BOOL==0 se descarta (220 filas). Archivo B: profundidades < 0,5 m se descartan (2.621 filas).
3. **Despiking**: Se eliminan valores atípicos por grupo (estación×fecha) usando la regla del IQR (3×IQR). Los valores atípicos se marcan como NaN.
4. **Bin averaging**: Los datos se promedian en bins de 1 metro de profundidad, obteniendo un valor por variable por metro.
5. **Registro de fondo**: Por cada estación×fecha, se toma la fila de profundidad máxima como registro de fondo.
6. **Profundidad de fondo**: Archivo A desde columna PROF_SECT_m (profundidad de sector/carta). Archivo B desde batimetría GEBCO_2026 por coordenada de estación.
7. **Unión con zonas**: Cada registro se asigna a su zona de macrofauna (zona_mf).

== Estado de referencia

Por zona de macrofauna se calculan: número de registros, número de estaciones, rango de años, y para cada variable (temperatura, oxígeno, salinidad): media, mediana, percentiles 5/25/75/95 y desvío estándar.

== Trayectorias de cambio

Por zona se calcula el promedio anual de cada variable y se ajusta una recta por mínimos cuadrados ordinarios (OLS) sobre el índice de año. Se reportan pendiente, intercepto, R2, p-valor (t-test) y número de años. Se requieren al menos 3 años para calcular la tendencia.

== Limitaciones

- Ocho zonas tienen datos solo para 2024–2025 (2 años), por lo que no se calcula tendencia para ellas.
- Las profundidades de GEBCO_2026 tienen una resolución de 15 segundos de arco (~450 m).
- El archivo B (marea roja) solo reporta oxígeno en ml/L.
- Algunos valores faltan en variables (temperatura: 53 nulos, oxígeno: 174 nulos, salinidad: 116 nulos) debido al despiking o a datos originales faltantes.

= Estado de referencia regional

El cuadro 1 presenta las estadísticas regionales agregadas para todas las zonas combinadas.

#figure(
  table(
    columns: (2.5cm, 2.5cm, 2.5cm, 2cm),
    align: center,
    [Variable], [Media], [Mediana], [Desvío estándar],
    [Temperatura (°C)], [9,73], [9,87], [1,50],
    [Oxígeno (ml/L)], [5,48], [5,26], [1,97],
    [Salinidad (psu)], [32,16], [32,56], [1,54],
  ),
  caption: [Cuadro 1: Estadísticas regionales del estado de referencia (2019–2025). n temperatura = 2.310, n oxígeno = 2.189, n salinidad = 2.247 registros válidos.],
)

= Estado de referencia por zona

El cuadro 2 presenta las estadísticas de referencia por zona de macrofauna. Las columnas P25 y P75 muestran el rango intercuartílico de cada variable.

#figure(
  table(
    columns: (2.2cm, 1.2cm, 2.2cm, 2.2cm, 2.2cm, 2.2cm, 2.2cm),
    align: center,
    [Zona], [n reg.], [Temp. media (°C)], [O2 media (ml/L)], [Sal. media (psu)], [Temp. P25–P75], [O2 P25–P75 (ml/L)],
    [Ancud], [10], [12,29], [6,47], [32,72], [11,33–13,14], [5,70–7,19],
    [Ayacara], [34], [10,98], [5,44], [32,61], [10,45–11,41], [4,87–6,15],
    [Aysén], [377], [10,21], [5,26], [30,80], [9,40–10,95], [4,10–5,77],
    [Butachauques], [37], [11,01], [5,47], [32,87], [10,58–11,66], [4,85–6,13],
    [Calbuco], [20], [11,42], [6,15], [32,67], [11,02–11,93], [5,33–6,92],
    [Chacao], [20], [11,34], [6,12], [32,77], [11,11–11,84], [5,37–6,82],
    [Chaitén], [56], [10,36], [4,53], [33,14], [9,85–10,85], [4,20–5,50],
    [Chaulinec], [27], [10,83], [5,51], [33,07], [10,40–11,43], [4,80–6,02],
    [Chiloé central], [10], [10,91], [5,76], [33,22], [10,23–11,57], [5,07–6,43],
    [Desertores], [27], [10,89], [5,57], [32,89], [10,28–11,56], [4,83–6,04],
    [Estuario], [74], [11,07], [4,96], [32,56], [10,89–11,18], [4,20–5,81],
    [Guaitecas], [146], [10,52], [5,10], [32,75], [9,76–11,24], [4,66–5,68],
    [Hornopirén], [29], [11,16], [5,62], [32,44], [10,80–11,58], [4,95–6,02],
    [Moraleda], [361], [10,26], [4,52], [32,59], [9,67–10,78], [3,97–5,25],
    [Natales], [752], [8,10], [6,90], [31,69], [7,23–8,87], [5,27–8,65],
    [Puyuhuapi], [117], [9,79], [3,27], [32,97], [9,45–10,21], [2,77–3,88],
    [Quellón], [180], [10,60], [5,24], [33,39], [9,97–11,12], [5,04–5,91],
    [Reloncaví], [76], [11,22], [5,21], [32,67], [10,94–11,31], [4,16–6,09],
    [Tenaun], [10], [10,89], [5,41], [33,08], [10,40–11,55], [4,64–6,01],
  ),
  caption: [Cuadro 2: Estado de referencia por zona de macrofauna (2019–2025). n reg. = número de registros de fondo. P25–P75 = rango intercuartílico.],
)

= Trayectorias de cambio ambiental

El cuadro 3 presenta las pendientes de tendencia lineal anual por zona y variable. Se destacan las tendencias con p menor que 0,05.

#figure(
  table(
    columns: (2.4cm, 1.8cm, 1.8cm, 1.8cm, 1.8cm, 1.8cm, 1.6cm),
    align: center,
    [Zona], [Temp. pendiente (°C/año)], [Temp. p-valor], [O2 pendiente (ml/L/año)], [O2 p-valor], [Sal. pendiente (psu/año)], [Sal. p-valor],
    [Ancud], [–], [–], [–], [–], [–], [–],
    [Ayacara], [+0,04], [0,710], [+0,31], [0,119], [-0,06], [0,110],
    [Aysén], [+0,10], [0,548], [+0,30], [0,230], [+0,50], [0,030],
    [Butachauques], [+0,09], [0,639], [+0,23], [0,220], [-0,05], [0,058],
    [Calbuco], [–], [–], [–], [–], [–], [–],
    [Chacao], [–], [–], [–], [–], [–], [–],
    [Chaitén], [+0,24], [0,238], [+0,24], [0,088], [-0,11], [0,150],
    [Chaulinec], [+0,07], [0,512], [+0,24], [0,218], [+0,01], [0,585],
    [Chiloé central], [–], [–], [–], [–], [–], [–],
    [Desertores], [+0,21], [0,127], [+0,35], [0,073], [-0,08], [0,029],
    [Estuario], [-0,05], [0,199], [+0,38], [0,067], [-0,05], [0,148],
    [Guaitecas], [–], [–], [–], [–], [–], [–],
    [Hornopirén], [–], [–], [–], [–], [–], [–],
    [Moraleda], [+0,29], [0,222], [+0,29], [0,263], [-0,24], [0,110],
    [Natales], [–], [–], [–], [–], [–], [–],
    [Puyuhuapi], [+0,22], [0,206], [-0,30], [0,017], [-0,24], [0,063],
    [Quellón], [+0,88], [0,023], [-0,47], [0,211], [+0,19], [0,328],
    [Reloncaví], [+0,06], [0,512], [+0,45], [0,026], [-0,07], [0,146],
    [Tenaun], [–], [–], [–], [–], [–], [–],
  ),
  caption: [Cuadro 3: Trayectorias de cambio ambiental por zona (OLS, 2019–2025). – = insuficientes datos (menos de 3 años). Valores en negrita indican p menor que 0,05.],
)

== Tendencias significativas

Se detectaron tres tendencias estadísticamente significativas (p menor que 0,05):

- Quellón — Temperatura: +0,88 °C/año (p=0,023, R2=0,999, n=3 años). Es la tendencia más fuerte y consistente, aunque se basa en pocos años (2023–2025).
- Aysén — Salinidad: +0,50 psu/año (p=0,030, R2=0,76, n=6 años). Indica un proceso de salinización gradual en la zona.
- Desertores — Salinidad: -0,08 psu/año (p=0,029, R2=0,65, n=7 años). Indica un proceso de desalinización gradual.

Otras zonas muestran tendencias de interés aunque no alcanzan significancia estadística al nivel 0,05, principalmente por el número limitado de años de datos:

- Puyuhuapi — Oxígeno: -0,30 ml/L/año (p=0,017, n=6 años). Sugiere una tendencia de desoxigenación que merece seguimiento.
- Reloncaví — Oxígeno: +0,45 ml/L/año (p=0,026, n=7 años). Tendencia de aumento de oxígeno.

= Conclusiones

1. El estado de referencia regional muestra temperaturas frías (media 9,73 °C), oxígeno moderado (media 5,48 ml/L) y salinidad cercana a la del océano abierto (media 32,16 psu), con una gran variabilidad entre zonas que refleja la heterogeneidad de los fiordos y canales de la Patagonia chilena.

2. Quellón presenta la tendencia de cambio más marcada, con un calentamiento de +0,88 °C/año. Esta zona debería priorizarse en el monitoreo de cambio climático.

3. Aysén y Desertores muestran tendencias opuestas en salinidad (salinización vs. desalinización), lo que sugiere procesos locales distintos de aporte de agua dulce o intercambio oceánico.

4. Ocho zonas (Ancud, Calbuco, Chacao, Chiloé central, Guaitecas, Hornopirén, Natales, Tenaun) tienen datos solo para 2024–2025, por lo que no es posible evaluar trayectorias de cambio. Se recomienda mantener el monitoreo en estas zonas para acumular suficiente serie temporal.

5. Las zonas con menor oxígeno de referencia (Puyuhuapi, Moraleda, Chaitén, Estuario) son candidatas a monitoreo prioritario de desoxigenación.

= Anexo: archivos de salida

- fondo_ctd_por_zona.csv — registro de fondo reconstruido (2.363 filas).
- salidas/analisis_ambiental/estado_referencia_por_zona.csv — estadísticas de referencia por zona.
- salidas/analisis_ambiental/trayectorias_cambio_por_zona.csv — pendientes de tendencia por zona.
- salidas/analisis_ambiental/resumen_regional.csv — métricas regionales.
- reconstruir_ctd.py — script reproducible de reconstrucción.
- analisis_estado_referencia.py — script de análisis de estado de referencia.
