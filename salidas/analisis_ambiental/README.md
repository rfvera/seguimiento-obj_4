# Análisis ambiental — objetivo_4 (IFOP Seguimiento CTD)

Estado ambiental de referencia y trayectorias de cambio ambiental regional, a partir de los registros de fondo CTD (2019–2025), usando las zonas de macrofauna como zonificación de referencia.

## Entradas
- `fondo_ctd_por_zona.csv` — registro de fondo (profundidad máxima por estación×fecha) con zona asignada.
- `estaciones_CTD_con_ZONA_MACROFAUNA.csv` — 259 estaciones con zona_mf (zonificación macrofauna) y acs_mf.

## Salidas
- `estado_referencia_por_zona.csv` — estadísticas descriptivas por zona_mf (n, media, mediana, p5/p25/p75/p95, desvio) para temperatura_C, oxígeno_ml_L, salinidad_psu.
- `trayectorias_cambio_por_zona.csv` — pendiente de tendencia lineal anual (OLS) por zona_mf y variable, con R², p-valor y n de años.
- `resumen_regional.csv` — métricas regionales agregadas.

## Metodología
- Cada registro de fondo se une a su estación y zona_mf.
- Estado de referencia: media, mediana, percentiles 5/25/75/95 y desvio estándar por zona y variable.
- Trayectoria de cambio: promedio anual por zona; pendiente OLS sobre el índice de año; p-valor por t-test (scipy.stats.t). Se requieren ≥3 años para calcular tendencia.
- 20 zonas con datos; 9 zonas solo tienen 2024–2025 (n_anos=2, sin tendencia calculable).
- 6 tendencias significativas (p<0,05): Quellón temperatura, Puyuhuapi y Reloncaví oxígeno, Aysén, Butachauques y Desertores salinidad.
- El OLS se ajusta contra el año calendario, no contra la posición de la serie: con años faltantes, `v.index` posicional escala mal la pendiente.

## Entorno
`~/miniconda3/envs/r_env/bin/python` (pandas 3.0.2, scipy 1.17.1).

## Ejecución
`~/miniconda3/envs/r_env/bin/python salidas/analisis_ambiental/analisis_estado_referencia.py`
