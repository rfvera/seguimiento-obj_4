# AGENTS.md — objetivo_4 (IFOP Seguimiento CTD)

Evaluación de variabilidad ambiental y exposición de áreas de emplazamiento acuícola a forzantes naturales y cambio climático. Repositorio git; fuentes `.xlsx` de solo lectura, no versionadas.

## Contexto metodológico

Los datos son perfiles CTD (conductividad, temperatura, profundidad, oxígeno, densidad) tomados en estaciones repetidas a través del tiempo (etapas/fechas/años). Cada estación×fecha es un cast independiente. El procesamiento sigue el estándar oceánico:

1. **Trimming**: remover datos de superficie/calibración (FLAG_BOOL==0 en A, profundidad <0,5 m en B).
2. **Despiking**: eliminar valores atípicos por grupo (regla IQR 3×).
3. **Bin averaging**: promedio en bins de 1 metro de profundidad.
4. **Registro de fondo**: tomar la medición a la profundidad máxima por estación×fecha.
5. **Profundidad de fondo**: Archivo A desde `PROF_SECT_m`; Archivo B desde GEBCO_2026.

Ver `contexto_metodologico_ctd.md` para detalles y referencias verificadas.

## Entorno

- Python: `~/miniconda3/envs/r_env/bin/python` (pandas 3.0.2, openpyxl, scipy instalados). No usar pip en sistema (PEP 668).
- Entorno opcional `~/miniconda3/envs/gebco_env` (xarray, netCDF4) usado solo para descargar batimetría GEBCO vía OPeNDAP.
- Rutas en scripts son absolutas (`BASE = /home/rfvera/.../objetivo_4`).

## Pipeline de reconstrucción (desde archivos originales)

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

## Pipeline de análisis ambiental

`~/miniconda3/envs/r_env/bin/python salidas/analisis_ambiental/analisis_estado_referencia.py`

Usa `fondo_ctd_por_zona.csv` (ya tiene zona_mf, no necesita merge).

Salidas (en `salidas/analisis_ambiental/`):
- `estado_referencia_por_zona.csv` — 19 zonas, estadísticas por zona y variable.
- `trayectorias_cambio_por_zona.csv` — 19 zonas, pendientes OLS por variable.
- `resumen_regional.csv` — métricas regionales.
- `README.md` — documentación.

### Resultados (2019–2025, 2.363 registros, 19 zonas, 258 estaciones)

- Temperatura regional: media 9,73 °C, mediana 9,87 °C, desvío 1,50 °C (n=2.310).
- Oxígeno regional: media 5,48 ml/L, mediana 5,26 ml/L, desvío 1,97 ml/L (n=2.189).
- Salinidad regional: media 32,16 psu, mediana 32,56 psu, desvío 1,54 psu (n=2.247).
- Tendencias significativas (p<0,05):
  - Quellón: temperatura +0,88 °C/año (p=0,023, R2=0,999, n=3 años).
  - Aysén: salinidad +0,50 psu/año (p=0,030, R2=0,76, n=6 años).
  - Desertores: salinidad -0,08 psu/año (p=0,029, R2=0,65, n=7 años).
- 8 zonas con solo 2024–2025 (sin tendencia): Ancud, Calbuco, Chacao, Chiloé central, Guaitecas, Hornopirén, Natales, Tenaun.

## Informe Typst (en `informe/`)

- `informe/informe_ambiental.typ` — documento Typst completo.
- `informe/informe_ambiental.pdf` — PDF compilado.

Compilar: `/home/rfvera/.typst/bin/typst compile informe/informe_ambiental.typ`

## Reglas de versión

- Nunca sobrescribir `.xlsx` fuentes. Están en `.gitignore` (`*.xlsx`).
- Salidas derivadas en `salidas/` y `informe/` son regenerables; revisar diff antes de commitear.
- `git status` debe quedar limpio tras re-ejecutar los scripts.
