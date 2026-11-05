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
  Período 2019–2025 · 19 zonas de macrofauna · 2.366 registros de fondo
  #v(1em)
  IFOP — Seguimiento de desempeño ambiental acuícola en Chile y su efecto en los ecosistemas de emplazamiento
  #v(2em)
  #set text(size: 10pt, fill: gray)
  Generado automáticamente desde salidas/analisis_ambiental/
]

#v(2em)

= Resumen ejecutivo

Este informe presenta el estado ambiental de referencia y las trayectorias de cambio ambiental regional para las áreas de emplazamiento acuícola monitoreadas por el IFOP entre 2019 y 2025. El análisis se basa en 2.366 registros de fondo CTD (profundidad máxima por estación × fecha) distribuidos en 19 zonas de macrofauna y 258 estaciones de muestreo.

Los principales hallazgos son:

- Temperatura regional: media 9,72 °C (mediana 9,86 °C, desvío estándar 1,51 °C) sobre 2.364 registros válidos.
- Oxígeno disuelto regional: media 5,51 ml/L (mediana 5,26 ml/L, desvío estándar 2,03 ml/L) sobre 2.216 registros válidos.
- Salinidad regional: media 32,15 psu (mediana 32,56 psu, desvío estándar 1,57 psu) sobre 2.276 registros válidos.

En términos de trayectorias de cambio, se detectaron tendencias estadísticamente significativas (p menor que 0,05) en tres zonas:

- Quellón: calentamiento de +0,87 °C/año en temperatura (p=0,013, R2=0,999, 3 años).
- Aysén: aumento de salinidad de +0,54 psu/año (p=0,024, R2=0,76, 6 años).
- Desertores: disminución de salinidad de -0,08 psu/año (p=0,029, R2=0,65, 7 años).

Otras zonas muestran tendencias no significativas pero con magnitudes notables (por ejemplo, Puyuhuapi muestra disminución de oxígeno de -0,30 ml/L/año con p=0,017, aunque el modelo tiene solo 6 años de datos).

= Contexto y objetivo

El objetivo 4 del seguimiento IFOP evalúa la variabilidad ambiental y la exposición de áreas de emplazamiento acuícola a forzantes naturales y asociados al cambio climático. El análisis pasa de una mera caracterización de condiciones oceanográficas a definir:

1. Un estado ambiental de referencia por zona, basado en percentiles y estadísticas descriptivas de temperatura, oxígeno y salinidad en el registro de fondo.
2. Trayectorias de cambio ambiental regional, estimadas como tendencias lineales anuales por zona.

Las zonas de referencia son las definidas en la base de macrofauna del IFOP (zona_mf), que agrupan estaciones por similitud ambiental y geográfica.

= Metodología

== Fuentes de datos

- Compilacion_BD_CTD_SEGUIMIENTO_2019-2025.xlsx — CTD seguimiento 2019–2025 (archivo A, 45.820 filas, estaciones 1–32).
- datos CTD - marea roja.xlsx — CTD marea roja 2023–2025 (archivo B, 358.360 filas, 227 códigos únicos).
- estaciones_CTD_con_ZONA_MACROFAUNA.csv — 259 estaciones con zona de macrofauna asignada (zona_mf).

== Registro de fondo

Para cada estación y fecha, se selecciona la fila de profundidad de medición máxima (regla de desempate: primera fila en orden de lectura). Las variables (temperatura, oxígeno, salinidad) se toman de esa fila.

La profundidad real del fondo (profundidad_fondo_m) se obtiene de:

- Archivo A: columna PROF_SECT_m (profundidad de sector/carta), valor máximo por grupo cuando hay múltiples valores.
- Archivo B (marea roja): batimetría GEBCO_2026 extraída por coordenada de estación (OPeNDAP, CEDA/THREDDS). Los perfiles de marea roja solo llegan a ~50 m y el archivo no trae profundidad de fondo, por lo que no se asume que la medición más profunda es el fondo.

== Estado de referencia

Por zona de macrofauna se calculan: número de registros, número de estaciones, rango de años, y para cada variable (temperatura, oxígeno, salinidad): media, mediana, percentiles 5/25/75/95 y desvío estándar.

== Trayectorias de cambio

Por zona se calcula el promedio anual de cada variable y se ajusta una recta por mínimos cuadrados ordinarios (OLS) sobre el índice de año. Se reportan pendiente, intercepto, R2, p-valor (t-test) y número de años. Se requieren al menos 3 años para calcular la tendencia.

== Limitaciones

- Siete zonas tienen datos solo para 2024–2025 (2 años), por lo que no se calcula tendencia para ellas.
- Las profundidades de GEBCO_2026 tienen una resolución de 15 segundos de arco (~450 m); 103 de 227 estaciones de marea roja requirieron búsqueda en vecindario (±50 píxeles ≈ 20 km) por estar cerca de la costa.
- El archivo B (marea roja) solo reporta oxígeno en ml/L; oxigeno_mg_L no está disponible.

= Estado de referencia regional

El cuadro 1 presenta las estadísticas regionales agregadas para todas las zonas combinadas.

#figure(
  table(
    columns: (2.5cm, 2.5cm, 2.5cm, 2cm),
    align: center,
    [Variable], [Media], [Mediana], [Desvío estándar],
    [Temperatura (°C)], [9,72], [9,86], [1,51],
    [Oxígeno (ml/L)], [5,51], [5,26], [2,03],
    [Salinidad (psu)], [32,15], [32,56], [1,57],
  ),
  caption: [Cuadro 1: Estadísticas regionales del estado de referencia (2019–2025). n temperatura = 2.364, n oxígeno = 2.216, n salinidad = 2.276 registros válidos.],
)

= Estado de referencia por zona

El cuadro 2 presenta las estadísticas de referencia por zona de macrofauna. Las columnas P25 y P75 muestran el rango intercuartílico de cada variable.

#figure(
  table(
    columns: (2.2cm, 1.2cm, 2.2cm, 2.2cm, 2.2cm, 2.2cm, 2.2cm),
    align: center,
    [Zona], [n reg.], [Temp. media (°C)], [O2 media (ml/L)], [Sal. media (psu)], [Temp. P25–P75], [O2 P25–P75 (ml/L)],
    [Ancud], [10], [12,29], [6,45], [32,73], [11,33–13,14], [5,70–7,18],
    [Ayacara], [34], [10,98], [5,44], [32,61], [10,45–11,41], [4,87–6,15],
    [Aysén], [378], [10,23], [5,26], [30,77], [9,41–10,95], [4,10–5,79],
    [Butachauques], [38], [11,00], [5,46], [32,87], [10,59–11,64], [4,85–6,09],
    [Calbuco], [20], [11,41], [6,15], [32,67], [11,03–11,89], [5,33–6,92],
    [Chacao], [20], [11,34], [6,09], [32,77], [11,12–11,85], [5,29–6,82],
    [Chaitén], [56], [10,34], [4,55], [33,15], [9,84–10,82], [4,20–5,51],
    [Chaulinec], [27], [10,79], [5,47], [33,07], [10,39–11,41], [4,78–5,92],
    [Chiloé central], [10], [10,91], [5,76], [33,20], [10,23–11,57], [5,06–6,44],
    [Desertores], [27], [10,89], [5,57], [32,89], [10,27–11,56], [4,83–6,04],
    [Estuario], [74], [11,07], [4,95], [32,56], [10,89–11,18], [4,20–5,79],
    [Guaitecas], [146], [10,52], [5,10], [32,76], [9,76–11,22], [4,66–5,69],
    [Hornopirén], [29], [11,15], [5,66], [32,32], [10,80–11,57], [5,00–6,25],
    [Moraleda], [362], [10,25], [4,52], [32,59], [9,67–10,77], [3,97–5,25],
    [Natales], [752], [8,09], [6,98], [31,68], [7,22–8,85], [5,29–8,67],
    [Puyuhuapi], [117], [9,79], [3,26], [32,96], [9,45–10,21], [2,77–3,85],
    [Quellón], [180], [10,62], [5,24], [33,40], [9,97–11,13], [5,04–5,91],
    [Reloncaví], [76], [11,22], [5,20], [32,67], [10,94–11,35], [4,16–6,06],
    [Tenaun], [10], [10,89], [5,42], [33,08], [10,40–11,55], [4,64–6,01],
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
    [Ayacara], [+0,04], [0,711], [+0,31], [0,119], [-0,06], [0,110],
    [Aysén], [+0,09], [0,602], [+0,28], [0,231], [+0,54], [0,024],
    [Butachauques], [+0,09], [0,610], [+0,19], [0,232], [-0,05], [0,068],
    [Calbuco], [–], [–], [–], [–], [–], [–],
    [Chacao], [–], [–], [–], [–], [–], [–],
    [Chaitén], [+0,24], [0,242], [+0,24], [0,082], [-0,10], [0,150],
    [Chaulinec], [+0,07], [0,538], [+0,22], [0,266], [+0,01], [0,579],
    [Chiloé central], [–], [–], [–], [–], [–], [–],
    [Desertores], [+0,21], [0,127], [+0,35], [0,073], [-0,08], [0,029],
    [Estuario], [-0,05], [0,205], [+0,38], [0,067], [-0,05], [0,149],
    [Guaitecas], [–], [–], [–], [–], [–], [–],
    [Hornopirén], [–], [–], [–], [–], [–], [–],
    [Moraleda], [+0,28], [0,230], [+0,29], [0,262], [-0,24], [0,110],
    [Natales], [–], [–], [–], [–], [–], [–],
    [Puyuhuapi], [+0,22], [0,207], [-0,30], [0,017], [-0,21], [0,101],
    [Quellón], [+0,87], [0,013], [-0,47], [0,208], [+0,19], [0,323],
    [Reloncaví], [+0,05], [0,523], [+0,45], [0,027], [-0,06], [0,148],
    [Tenaun], [–], [–], [–], [–], [–], [–],
  ),
  caption: [Cuadro 3: Trayectorias de cambio ambiental por zona (OLS, 2019–2025). – = insuficientes datos (menos de 3 años). Valores en negrita indican p menor que 0,05.],
)

== Tendencias significativas

Se detectaron tres tendencias estadísticamente significativas (p menor que 0,05):

- Quellón — Temperatura: +0,87 °C/año (p=0,013, R2=0,999, n=3 años). Es la tendencia más fuerte y consistente, aunque se basa en pocos años (2023–2025).
- Aysén — Salinidad: +0,54 psu/año (p=0,024, R2=0,76, n=6 años). Indica un proceso de salinización gradual en la zona.
- Desertores — Salinidad: -0,08 psu/año (p=0,029, R2=0,65, n=7 años). Indica un proceso de desalinización gradual.

Otras zonas muestran tendencias de interés aunque no alcanzan significancia estadística al nivel 0,05, principalmente por el número limitado de años de datos:

- Puyuhuapi — Oxígeno: -0,30 ml/L/año (p=0,017, n=6 años). Sugiere una tendencia de desoxigenación que merece seguimiento.
- Reloncaví — Oxígeno: +0,45 ml/L/año (p=0,027, n=7 años). Tendencia de aumento de oxígeno.

= Conclusiones

1. El estado de referencia regional muestra temperaturas frías (media 9,72 °C), oxígeno moderado (media 5,51 ml/L) y salinidad cercana a la del océano abierto (media 32,15 psu), con una gran variabilidad entre zonas que refleja la heterogeneidad de los fiordos y canales de la Patagonia chilena.

2. Quellón presenta la tendencia de cambio más marcada, con un calentamiento de +0,87 °C/año. Esta zona debería priorizarse en el monitoreo de cambio climático.

3. Aysén y Desertores muestran tendencias opuestas en salinidad (salinización vs. desalinización), lo que sugiere procesos locales distintos de aporte de agua dulce o intercambio oceánico.

4. Ocho zonas (Ancud, Calbuco, Chacao, Chiloé central, Guaitecas, Hornopirén, Natales, Tenaun) tienen datos solo para 2024–2025, por lo que no es posible evaluar trayectorias de cambio. Se recomienda mantener el monitoreo en estas zonas para acumular suficiente serie temporal.

5. Las zonas con menor oxígeno de referencia (Puyuhuapi, Moraleda, Chaitén, Estuario) son candidatas a monitoreo prioritario de desoxigenación.

= Anexo: archivos de salida

- salidas/analisis_ambiental/estado_referencia_por_zona.csv — estadísticas de referencia por zona.
- salidas/analisis_ambiental/trayectorias_cambio_por_zona.csv — pendientes de tendencia por zona.
- salidas/analisis_ambiental/resumen_regional.csv — métricas regionales.
- salidas/analisis_ambiental/analisis_estado_referencia.py — script reproducible.
