# Contexto metodológico — Perfiles CTD oceanográficos (objetivo_4)

## Qué son los perfiles CTD

Un CTD (Conductividad-Temperatura-Profundidad) es un instrumento oceanográfico que mide, de forma continua mientras se sumerge y se remonta en la columna de agua:

- **Conductividad** → se deriva salinidad (ecuación PSS-78)
- **Temperatura** → en °C
- **Presión** → se deriva profundidad (en metros o decibares)
- **Oxígeno disuelto** → en ml/L o µmol/L (sensor SBE43 u similar)
- **Densidad** → sigma-t, derivada de temperatura y salinidad

El CTD toma múltiples datos por segundo (frecuencia típica: 24 Hz o más). Un perfil completo incluye el descenso (**downcast**), una posible parada en el fondo, y el ascenso (**upcast**).

## Estructura temporal de las estaciones

Las estaciones se repiten a través del tiempo (etapas, campañas, años). Cada estación×fecha constituye un **cast** (perfil) independiente. La etapa y la fecha son identificadores clave para comparar el mismo punto espacial en diferentes momentos y detectar trayectorias de cambio.

## Procedimiento estándar de procesamiento (verificado en literatura)

### 1. Trimming: isolar el downcast

El primer paso es descartar datos que no representan la columna de agua durante el descenso:

- Medidas **en el aire** (antes de entrar al agua)
- Fase de **equilibración/soak** (el CTD se mantiene a poca profundidad minutos para que los sensores se estabilicen)
- Fase de **upcast** (ascenso)

**Fuente verificada:** El paquete R `oce` (Kelley & Richards, 2022) implementa `ctdTrim()` con `method="downcast"` para aislar solo el descenso, descartando la fase de aire, equilibración y ascenso. Se recomienda inspeccionar visualmente con `plotScan()` antes de definir los índices de corte manualmente. [`ctdTrim` documentation](https://rdrr.io/cran/oce/man/ctdTrim.html)

### 2. Despiking y filtrado

Se eliminan picos espurios (spikes) en los sensores y se aplica suavizado (p. ej., filtro de 10 m para la mayoría de variables, 5 m para oxígeno y clorofila).

**Fuente verificada:** Informe de procesamiento CTD DY026 (BODC, NOC Liverpool): bin averaging, despiking, calibraciones, y smoothing de 10 m (5 m oxígeno/clorofila). [`DY026 CTD processing report`](https://www.bodc.ac.uk/data/documents/nodb/pdf/DY026_CTD_processing_report.pdf)

### 3. Bin averaging (promedio por metro)

Una vez aislado el downcast y limpio, los datos se promedian en bins de profundidad (típicamente 1 metro o 1 decibar), quedando un perfil con un valor por variable por metro de profundidad.

**Fuente verificada:** Paquete `gapctd` (NOAA AFSC) y `oce::ctd.decimate()`: promedio en bins de 1 m de profundidad, con interpolación lineal a valores de presión uniformemente espaciados. [`oce vignette`](https://cran.r-project.org/web/packages/oce/vignettes/B_ctd.html)

### 4. Calibración

Se aplican calibraciones de laboratorio a salinidad, oxígeno y otros sensores, usando datos de botellas (muestras discretas) como referencia cuando están disponibles.

## Estado actual de los datos en `objetivo_4/`

### Lo que tenemos (`fondo_ctd_por_zona.csv`)

- **2.363 registros** (una fila por estación×fecha)
- Para cada registro se guarda la medición a la **profundidad máxima** del perfil (registro de fondo)
- Variables: temperatura_C, oxígeno_ml_L, salinidad_psu, profundidad_fondo_m
- Período: 2019–2025 (archivo A: 2019–2025, estaciones 1–32; archivo B marea roja: 2023–2025, 227 estaciones)
- Zonas: 20 zonas de macrofauna asignadas a cada estación

### Lo que NO tenemos (y se necesitaría para análisis de perfiles completos)

- Datos crudos por escaneo (24 Hz o similar) de cada cast
- El perfil completo (temperatura, salinidad, oxígeno vs. profundidad a cada metro)
- Metadatos de trimming (qué parte del perfil se consideró downcast)
- Información de calibración por sensor y fecha

## Implicación para el análisis actual

`estado_referencia_por_zona.csv` y `trayectorias_cambio_por_zona.csv` trabajan con el **registro de fondo**. En paralelo, `perfiles_procesados.py` construye el perfil completo bineado a 1 m (140.787 registros) y sus derivados: promedios anuales por zona×profundidad, ciclo estacional, anomalías y tendencias. El análisis por perfiles ya no depende de datos crudos por escaneo: los `.xlsx` originales traen las mediciones discretas suficientes para el bineo.

Con el registro de fondo es válido:

- Caracterizar condiciones de fondo por zona y año.
- Detectar tendencias de largo plazo en variables de fondo.

Con los perfiles procesados se añade:

- Contraste vertical de las tendencias (caso Aysén: salinización somera y desalinización profunda).
- Cálculo de anomalías con ciclo estacional removido.

Lo que sigue sin estar disponible es el dato crudo a 24 Hz por cast, necesario para auditar el trimming original (downcast vs upcast, fase de equilibración) y para recalibrar sensores con botellas.

## Recomendación metodológica para futuras etapas

1. **Confirmar con el responsable de datos** si existen archivos CNV o similares con los perfiles completos por estación×fecha.
2. Si existen, aplicar el flujo estándar: `ctdTrim(downcast)` → despiking → `ctd.decimate(1 m)` → calibración → análisis de perfiles.
3. Documentar el procedimiento de trimming usado por estación (qué porción del perfil se consideró válida).

## Referencias verificadas

1. Kelley, D. & Richards, C. (2022). *oce: Analysis of Oceanographic Data*. R package vignette "Analysis of CTD data". Funciones `ctdTrim()`, `ctd.decimate()`. [CRAN](https://cran.r-project.org/web/packages/oce/vignettes/B_ctd.html)
2. Williams, C.A.J. (2015). *DY026 CTD processing report*. BODC / NOC Liverpool. Bin averaging, despiking, calibraciones, smoothing. [PDF](https://www.bodc.ac.uk/data/documents/nodb/pdf/DY026_CTD_processing_report.pdf)
3. NOAA AFSC. *gapctd* R package for CTD processing (trawl-mounted CTDs, SBE 19plus V2). Bin average 1 m, despiking. [NOAA Repository](https://repository.library.noaa.gov/view/noaa/55614)
