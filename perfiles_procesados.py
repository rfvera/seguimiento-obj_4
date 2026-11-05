"""
perfiles_procesados.py
Agente DATA - IFOP Seguimiento (objetivo_4)

Genera perfiles CTD procesados (binned por 1 metro) y promedios anuales por
profundidad, integrando metodologías de análisis de CTD en series de tiempo:

Metodología aplicada (verificada en literatura):
  - Bin averaging 1 m (aguas costeras): RBR CTD Guidelines (DFO 2017),
    BODC series documents, oce R package (binMean1D/binAverage).
  - Promedios anuales por profundidad fija: promedio de cada nivel de
    profundidad a través del tiempo por zona.
  - Ciclo estacional anual: ajuste de mínimos cuadrados A_avg + A_amp*sin/cos
    (Scottish Marine & Freshwater Science 2013, métodos de anual cycles).
  - Anomalías: se resta el ciclo estacional para obtener series de
    anomalías y estimar tendencias lineales (RADMED/STOCA, Frontiers 2022).

Entradas (solo lectura, nunca sobrescribir):
  - Compilacion_BD_CTD_SEGUIMIENTO_2019-2025.xlsx (archivo A)
  - datos CTD - marea roja.xlsx (archivo B)
  - estaciones_CTD_con_ZONA_MACROFAUNA.csv
  - gebco_profundidades_marea_roja.csv

Salidas (en salidas/perfiles_procesados/):
  - perfiles_procesados.csv           : un registro por estación×fecha×profundidad
  - promedio_anual_por_profundidad.csv: promedio anual por zona×profundidad
  - ciclo_estacional_por_profundidad.csv: ajuste seno/coseno por zona×profundidad
  - tendencias_anomalias_por_profundidad.csv: tendencias de anomalías por zona×profundidad
  - resumen_regional_por_profundidad.csv: métricas regionales por profundidad
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

BASE = Path("/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4")
ARCH_A = BASE / "Compilacion_BD_CTD_SEGUIMIENTO_2019-2025.xlsx"
ARCH_B = BASE / "datos CTD - marea roja.xlsx"
ZONAS_MF = BASE / "estaciones_CTD_con_ZONA_MACROFAUNA.csv"
GEBCO_PROF = BASE / "gebco_profundidades_marea_roja.csv"
OUTDIR = BASE / "salidas" / "perfiles_procesados"

VARIABLES_CTD = ["temperatura_C", "oxigeno_ml_L", "salinidad_psu"]
BIN_SIZE = 1.0  # metros, estándar para aguas costeras (RBR Guidelines)


# ---------------------------------------------------------------------------
# 1. Lectura archivo A (seguimiento 2019-2025)
# ---------------------------------------------------------------------------
def leer_archivo_a(path: Path) -> pd.DataFrame:
    raw = pd.read_excel(path, sheet_name="Base de Datos CTD2019-2025_IFOP", header=None)
    if raw.shape[0] <= 21:
        raise ValueError("Archivo A no tiene el encabezado esperado en la fila 20")
    header = raw.iloc[20].tolist()
    df = raw.iloc[21:].copy()
    df.columns = header

    nombres = [
        "Año", "NOMB_PROY", "COD_PROY", "FECHA_INICIO", "FECHA_TERMINO", "EQUIPO",
        "ESTACION", "FLAG_BOOL", "LATITUD", "LONGITUD", "PROF_EQ_m",
        "PROF_SECT_m", "TEMPERATURA_C", "OXIG_ml_L", "OXIG_mg_L", "OXIG_pct_sat",
        "OX_umol_kg", "SALINIDAD_psu", "FLUORESCEN_mg_m3", "DENSIDAD_sigma_t",
        "CLOROFILA_mg_m3", "FEOPIGMEN_mg_m3", "NITRATO_uM", "FOSFATO_uM",
        "SILICATO_uM", "pH", "COD_REG", "OBSERV", "ESTACION_DUP", "HORA_DATO",
        "DISCO_SECH_m",
    ]
    if len(nombres) != df.shape[1]:
        raise ValueError("Esperaba {} columnas, leí {}".format(len(nombres), df.shape[1]))
    df.columns = nombres

    df["ESTACION"] = pd.to_numeric(df["ESTACION"], errors="coerce")
    df["FECHA_INICIO"] = pd.to_datetime(df["FECHA_INICIO"], errors="coerce")
    df["PROF_EQ_m"] = pd.to_numeric(df["PROF_EQ_m"], errors="coerce")
    df["PROF_SECT_m"] = pd.to_numeric(df["PROF_SECT_m"], errors="coerce")
    df["TEMPERATURA_C"] = pd.to_numeric(df["TEMPERATURA_C"], errors="coerce")
    df["OXIG_ml_L"] = pd.to_numeric(df["OXIG_ml_L"], errors="coerce")
    df["SALINIDAD_psu"] = pd.to_numeric(df["SALINIDAD_psu"], errors="coerce")

    return df


# ---------------------------------------------------------------------------
# 2. Lectura archivo B (marea roja)
# ---------------------------------------------------------------------------
def leer_archivo_b(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Datos CTD", header=0)

    def parse_fecha(x):
        if isinstance(x, str):
            x = x.strip()
            if x == "" or x.upper() == "S/I":
                return pd.NaT
            return pd.to_datetime(x, format="%d-%m-%Y", errors="coerce")
        return pd.to_datetime(x, errors="coerce")

    df["FECHA"] = df["FECHA"].apply(parse_fecha)
    df["CODIGO"] = df["CODIGO"].astype(str).str.strip()
    df["PROFUNDIDAD_m"] = pd.to_numeric(df["PROFUNDIDAD (m)"], errors="coerce")
    df["TEMPERATURA_C"] = pd.to_numeric(df["TEMPERATURA (C°)"], errors="coerce")
    df["SALINIDAD_psu"] = pd.to_numeric(df["SALINIDAD (PSU)"], errors="coerce")
    df["OXIGENO_ml_L"] = pd.to_numeric(df["OXIGENO (ml/L)"], errors="coerce")
    return df


# ---------------------------------------------------------------------------
# 3. Trimming: remover superficie / calibración
# ---------------------------------------------------------------------------
def trim_archivo_a(df: pd.DataFrame) -> pd.DataFrame:
    n_antes = len(df)
    df = df[df["FLAG_BOOL"] == 1].copy()
    df = df[df["PROF_EQ_m"] > 0].copy()
    despues = len(df)
    print("  Archivo A trimming: {} filas -> {} filas (descartadas {})".format(
        n_antes, despues, n_antes - despues))
    return df


def trim_archivo_b(df: pd.DataFrame, prof_min: float = 0.5) -> pd.DataFrame:
    n_antes = len(df)
    df = df[df["PROFUNDIDAD_m"] >= prof_min].copy()
    despues = len(df)
    print("  Archivo B trimming: {} filas -> {} filas (profundidad < {} m descartadas)".format(
        n_antes, despues, prof_min))
    return df


# ---------------------------------------------------------------------------
# 4. Despiking por grupo (regla IQR 3x)
# ---------------------------------------------------------------------------
def despikear_grupo(sub: pd.DataFrame, prof_col: str, var_cols: list) -> pd.DataFrame:
    resultado = sub.copy()
    for var in var_cols:
        if var not in sub.columns:
            continue
        valores = sub[var].dropna()
        if len(valores) < 4:
            continue
        q1 = valores.quantile(0.25)
        q3 = valores.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        limite_inf = q1 - 3.0 * iqr
        limite_sup = q3 + 3.0 * iqr
        mascara = (sub[var] < limite_inf) | (sub[var] > limite_sup)
        resultado.loc[mascara, var] = np.nan
    return resultado


# ---------------------------------------------------------------------------
# 5. Bin averaging por 1 metro de profundidad
# ---------------------------------------------------------------------------
def bin_average(df: pd.DataFrame, prof_col: str, var_cols: list,
                bin_size: float = BIN_SIZE,
                id_cols: list | None = None) -> pd.DataFrame:
    """Promedio en bins de profundidad de bin_size metros.
    Los bins están centrados en valores enteros (0.5-1.5 para bin 1m, etc.),
    siguiendo las directrices RBR CTD Guidelines para aguas costeras.
    """
    filas = []
    prof_min = float(df[prof_col].min())
    prof_max = float(df[prof_col].max())
    # Bins centrados en enteros: primer bin 0.5-1.5 (centro 1.0), etc.
    bin_start = np.floor(prof_min - 0.5) + 0.5
    bin_end = np.ceil(prof_max + 0.5) - 0.5
    bins = np.arange(bin_start, bin_end + bin_size + 0.001, bin_size)
    for prof_bin, sub in df.groupby(pd.cut(df[prof_col], bins=bins)):
        if pd.isna(prof_bin.left):
            continue
        prof_centro = float(prof_bin.mid)
        fila = {prof_col: prof_centro}
        if id_cols:
            for ic in id_cols:
                fila[ic] = sub[ic].iloc[0]
        for var in var_cols:
            vals = sub[var].dropna()
            fila[var] = float(vals.mean()) if len(vals) > 0 else np.nan
        filas.append(fila)
    return pd.DataFrame(filas)


# ---------------------------------------------------------------------------
# 6. Construir perfiles procesados (todas las profundidades, no solo el fondo)
# ---------------------------------------------------------------------------
def construir_perfiles_archivo_a(dfA: pd.DataFrame) -> pd.DataFrame:
    """Archivo A: ya viene a profundidades enteras (1m, 2m...), aplicamos
    trimming, despiking y bin averaging 1m para normalizar."""
    print("  Despiking archivo A...")
    VAR_A = ["TEMPERATURA_C", "OXIG_ml_L", "SALINIDAD_psu", "DENSIDAD_sigma_t"]
    lista_A = []
    for (est, fec), sub in dfA.groupby(["ESTACION", "FECHA_INICIO"]):
        lista_A.append(despikear_grupo(sub.reset_index(drop=True), "PROF_EQ_m", VAR_A))
    dfA = pd.concat(lista_A, ignore_index=True)

    print("  Bin averaging archivo A (1m)...")
    VAR_A_CTD = ["TEMPERATURA_C", "OXIG_ml_L", "SALINIDAD_psu"]
    lista_A_bin = []
    for (est, fec), sub in dfA.groupby(["ESTACION", "FECHA_INICIO"]):
        sub = sub.copy()
        sub["ESTACION"] = est
        sub["FECHA_INICIO"] = fec
        lista_A_bin.append(bin_average(sub, "PROF_EQ_m", VAR_A_CTD,
                                       id_cols=["ESTACION", "FECHA_INICIO"]))
    dfA_bin = pd.concat(lista_A_bin, ignore_index=True)

    # Agregar PROF_SECT_m (profundidad de fondo declarada) por grupo
    prof_sect_lookup = dfA.groupby(["ESTACION", "FECHA_INICIO"])["PROF_SECT_m"].max().reset_index()
    dfA_bin = dfA_bin.merge(prof_sect_lookup, on=["ESTACION", "FECHA_INICIO"], how="left")
    dfA_bin["archivo"] = "A"
    # Renombrar variables a estándar ANTES de retornar (evita duplicados al concatenar)
    dfA_bin = dfA_bin.rename(columns={"ESTACION": "estacion_id", "FECHA_INICIO": "fecha",
                                      "PROF_EQ_m": "profundidad_m",
                                      "TEMPERATURA_C": "temperatura_C",
                                      "OXIG_ml_L": "oxigeno_ml_L",
                                      "SALINIDAD_psu": "salinidad_psu"})
    return dfA_bin


def construir_perfiles_archivo_b(dfB: pd.DataFrame) -> pd.DataFrame:
    print("  Despiking archivo B...")
    VAR_B = ["TEMPERATURA_C", "OXIGENO_ml_L", "SALINIDAD_psu"]
    lista_B = []
    for (cod, fec), sub in dfB.groupby(["CODIGO", "FECHA"]):
        lista_B.append(despikear_grupo(sub.reset_index(drop=True), "PROFUNDIDAD_m", VAR_B))
    dfB = pd.concat(lista_B, ignore_index=True)

    print("  Bin averaging archivo B (1m)...")
    VAR_B_CTD = ["TEMPERATURA_C", "OXIGENO_ml_L", "SALINIDAD_psu"]
    lista_B_bin = []
    for (cod, fec), sub in dfB.groupby(["CODIGO", "FECHA"]):
        sub = sub.copy()
        sub["CODIGO"] = cod
        sub["FECHA"] = fec
        lista_B_bin.append(bin_average(sub, "PROFUNDIDAD_m", VAR_B_CTD,
                                       id_cols=["CODIGO", "FECHA"]))
    dfB_bin = pd.concat(lista_B_bin, ignore_index=True)
    dfB_bin["archivo"] = "B"
    # Renombrar variables a estándar ANTES de retornar (evita duplicados al concatenar)
    dfB_bin = dfB_bin.rename(columns={"CODIGO": "estacion_id", "FECHA": "fecha",
                                      "PROFUNDIDAD_m": "profundidad_m",
                                      "TEMPERATURA_C": "temperatura_C",
                                      "OXIGENO_ml_L": "oxigeno_ml_L",
                                      "SALINIDAD_psu": "salinidad_psu"})
    return dfB_bin


# ---------------------------------------------------------------------------
# 7. Promedios anuales por profundidad por zona
# ---------------------------------------------------------------------------
def promedio_anual_por_profundidad(df: pd.DataFrame) -> pd.DataFrame:
    """Para cada zona×profundidad×año, calcula el promedio de cada variable."""
    df = df.copy()
    df["anio"] = df["fecha"].dt.year

    filas = []
    for (zona, prof, anio), sub in df.groupby(["zona_mf", "profundidad_m", "anio"]):
        fila = {"zona_mf": zona, "profundidad_m": prof, "anio": int(anio),
                "n_registros": len(sub),
                "n_estaciones": sub["estacion_id"].nunique()}
        for var in VARIABLES_CTD:
            vals = sub[var].dropna()
            fila[var + "_media"] = float(vals.mean()) if len(vals) > 0 else np.nan
            fila[var + "_desvio"] = float(vals.std(ddof=1)) if len(vals) > 1 else np.nan
            fila[var + "_n_validos"] = int(len(vals))
        filas.append(fila)
    return pd.DataFrame(filas).sort_values(["zona_mf", "profundidad_m", "anio"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 8. Ciclo estacional anual (ajuste seno/coseno por zona×profundidad)
# ---------------------------------------------------------------------------
def ciclo_estacional_por_profundidad(df_anual: pd.DataFrame) -> pd.DataFrame:
    """Ajuste de mínimos cuadrados: A = A_avg + A_amp*sin(2*pi*t/12) + A_pha*cos(2*pi*t/12)
    donde t es el mes (1-12). Requiere datos de al menos 3 meses distintos."""
    filas = []
    for (zona, prof), sub in df_anual.groupby(["zona_mf", "profundidad_m"]):
        if len(sub) < 3:
            continue
        # Usamos el mes como tiempo (1-12)
        t = sub["mes"].values.astype(float) if "mes" in sub.columns else \
            pd.to_datetime(sub["fecha_rep"].values).month.values.astype(float)
        for var in VARIABLES_CTD:
            y = sub[var + "_media"].dropna().values
            t_var = t[:len(y)] if len(y) < len(t) else t
            if len(y) < 3:
                continue
            # A = b0 + b1*sin(2*pi*t/12) + b2*cos(2*pi*t/12)
            X = np.column_stack([np.ones(len(t_var)),
                                 np.sin(2 * np.pi * t_var / 12),
                                 np.cos(2 * np.pi * t_var / 12)])
            try:
                beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
                y_pred = X @ beta
                ss_res = ((y - y_pred) ** 2).sum()
                ss_tot = ((y - y.mean()) ** 2).sum()
                r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
                amplitud = np.sqrt(beta[1] ** 2 + beta[2] ** 2)
                fase = np.arctan2(beta[2], beta[1])  # en radianes
                fila = {"zona_mf": zona, "profundidad_m": prof, "variable": var,
                        "media_anual": float(beta[0]),
                        "amplitud_estacional": float(amplitud),
                        "fase_estacional_rad": float(fase),
                        "r2": float(r2),
                        "n_anos": int(sub["anio"].nunique())}
                filas.append(fila)
            except np.linalg.LinAlgError:
                continue
    return pd.DataFrame(filas).sort_values(["zona_mf", "profundidad_m", "variable"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 9. Tendencias de anomalías por zona×profundidad
# ---------------------------------------------------------------------------
def tendencias_anomalias(df_anual: pd.DataFrame, ciclo: pd.DataFrame) -> pd.DataFrame:
    """Para cada zona×profundidad×variable, resta el ciclo estacional y
    estima la tendencia lineal de las anomalías."""
    filas = []
    for (zona, prof, var), sub in df_anual.groupby(["zona_mf", "profundidad_m", "variable_col"]):
        # Obtener ciclo estacional para esta zona×profundidad×variable
        cic = ciclo[(ciclo["zona_mf"] == zona) & (ciclo["profundidad_m"] == prof) &
                    (ciclo["variable"] == var)]
        if len(cic) == 0:
            continue
        b0 = cic["media_anual"].iloc[0]
        b1 = cic["amplitud_estacional"].iloc[0]
        fase = cic["fase_estacional_rad"].iloc[0]

        # Calcular anomalía: observar - ciclo estacional esperado
        t = sub["mes"].values.astype(float) if "mes" in sub.columns else \
            pd.to_datetime(sub["fecha_rep"].values).month.values.astype(float)
        y = sub[var + "_media"].dropna().values
        t_var = t[:len(y)] if len(y) < len(t) else t
        ciclo_esperado = b0 + b1 * np.sin(2 * np.pi * t_var / 12 + fase)
        anomalia = y - ciclo_esperado

        if len(anomalia) < 3:
            continue

        # Tendencia lineal de anomalías vs año
        anios = sub["anio"].dropna().values[:len(anomalia)].astype(float)
        if len(anios) < 3:
            continue
        try:
            slope, intercept, r_value, p_value, std_err = stats.linregress(anios, anomalia)
            fila = {"zona_mf": zona, "profundidad_m": prof, "variable": var,
                    "tendencia_anual": float(slope),
                    "intercepto": float(intercept),
                    "r2": float(r_value ** 2),
                    "p_valor": float(p_value),
                    "error_estandar": float(std_err),
                    "n_anos": int(len(anios))}
            filas.append(fila)
        except Exception:
            continue
    return pd.DataFrame(filas).sort_values(["zona_mf", "profundidad_m", "variable"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 10. Unión con zonas
# ---------------------------------------------------------------------------
def unir_con_zonas(df: pd.DataFrame, zonas: pd.DataFrame) -> pd.DataFrame:
    zonas_u = zonas[["archivo", "estacion_id", "zona_mf", "acs_mf", "dist_km"]].copy()
    zonas_u["estacion_id"] = zonas_u["estacion_id"].astype(str).str.strip()
    df["estacion_id"] = df["estacion_id"].astype(str).str.strip()
    merged = df.merge(zonas_u, on=["archivo", "estacion_id"], how="left")
    n_sin_zona = int(merged["zona_mf"].isna().sum())
    print("Estaciones sin zona_mf: {}".format(n_sin_zona))
    return merged, n_sin_zona


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    zonas = pd.read_csv(ZONAS_MF, dtype={"estacion_id": str})
    print("Zonas cargadas: {} filas".format(zonas.shape[0]))

    # --- Archivo A ---
    print("\n=== Archivo A ===")
    dfA = leer_archivo_a(ARCH_A)
    print("Leído: {} filas".format(dfA.shape[0]))
    dfA = trim_archivo_a(dfA)
    perfilesA = construir_perfiles_archivo_a(dfA)
    print("Perfiles archivo A: {} filas".format(perfilesA.shape[0]))

    # --- Archivo B ---
    print("\n=== Archivo B ===")
    dfB = leer_archivo_b(ARCH_B)
    print("Leído: {} filas".format(dfB.shape[0]))
    dfB = trim_archivo_b(dfB, prof_min=0.5)
    perfilesB = construir_perfiles_archivo_b(dfB)
    print("Perfiles archivo B: {} filas".format(perfilesB.shape[0]))

    # --- Combinar perfiles ---
    perfiles = pd.concat([perfilesA, perfilesB], ignore_index=True)

    # Añadir columna profundidad_fondo (GEBCO o PROF_SECT_m)
    perfiles["profundidad_fondo_m"] = pd.NA
    perfiles["profundidad_fondo_fuente"] = "no_disponible"

    # Para archivo A, usar PROF_SECT_m
    mask_a = perfiles["archivo"] == "A"
    perfiles.loc[mask_a, "profundidad_fondo_m"] = perfiles.loc[mask_a, "PROF_SECT_m"]
    perfiles.loc[mask_a, "profundidad_fondo_fuente"] = "PROF_SECT_m"

    # Para archivo B, usar GEBCO
    if GEBCO_PROF.exists():
        gb = pd.read_csv(GEBCO_PROF, dtype={"CODIGO": str})
        gb = gb.rename(columns={"CODIGO": "estacion_id"})
        gb["estacion_id"] = gb["estacion_id"].astype(str).str.strip()
        gb_map = gb.set_index("estacion_id")["profundidad_fondo_m"].to_dict()
        mask_b = perfiles["archivo"] == "B"
        perfiles.loc[mask_b, "profundidad_fondo_m"] = \
            perfiles.loc[mask_b, "estacion_id"].map(gb_map)
        perfiles.loc[mask_b, "profundidad_fondo_fuente"] = "GEBCO_2026"
        # Tratar -1 m de GEBCO (costa/tierra marginal) como NaN
        perfiles.loc[(mask_b) & (perfiles["profundidad_fondo_m"] == -1), "profundidad_fondo_m"] = np.nan
        perfiles.loc[(mask_b) & (perfiles["profundidad_fondo_m"].isna()), "profundidad_fondo_fuente"] = "no_disponible"

    # --- Unión con zonas ---
    perfiles_z, _ = unir_con_zonas(perfiles, zonas)

    # --- Guardar perfiles procesados ---
    cols_perfiles = ["archivo", "estacion_id", "fecha", "profundidad_m",
                     "profundidad_fondo_m", "profundidad_fondo_fuente",
                     "temperatura_C", "oxigeno_ml_L", "salinidad_psu",
                     "zona_mf", "acs_mf", "dist_km"]
    perfiles_z = perfiles_z[cols_perfiles]
    perfiles_z.to_csv(OUTDIR / "perfiles_procesados.csv", index=False, encoding="utf-8")
    print("\n=== Perfiles procesados guardados: {} ({} filas) ===".format(
        OUTDIR / "perfiles_procesados.csv", perfiles_z.shape))

    # --- Promedios anuales por profundidad ---
    print("\n=== Calculando promedios anuales por profundidad ===")
    df_anual = promedio_anual_por_profundidad(perfiles_z)
    df_anual["mes"] = pd.to_datetime(df_anual["anio"].astype(str) + "-06-15").dt.month
    df_anual["fecha_rep"] = pd.to_datetime(df_anual["anio"].astype(str) + "-06-15")
    df_anual.to_csv(OUTDIR / "promedio_anual_por_profundidad.csv", index=False, encoding="utf-8")
    print("Promedio anual por profundidad: {} filas".format(df_anual.shape[0]))

    # --- Ciclo estacional ---
    print("\n=== Calculando ciclo estacional ===")
    df_ciclo = ciclo_estacional_por_profundidad(df_anual)
    df_ciclo.to_csv(OUTDIR / "ciclo_estacional_por_profundidad.csv", index=False, encoding="utf-8")
    print("Ciclo estacional: {} filas".format(df_ciclo.shape[0]))

    # --- Tendencias de anomalías ---
    print("\n=== Calculando tendencias de anomalías ===")
    # Preparar df_anual con columna variable_col para groupby
    df_anual_long = []
    for var in VARIABLES_CTD:
        tmp = df_anual[["zona_mf", "profundidad_m", "anio", "mes", "fecha_rep",
                        var + "_media"]].copy()
        tmp = tmp.rename(columns={var + "_media": "valor_media"})
        tmp["variable_col"] = var
        tmp[var + "_media"] = tmp["valor_media"]
        df_anual_long.append(tmp)
    df_anual_long = pd.concat(df_anual_long, ignore_index=True)
    # Renombrar para que tendencias_anomalias funcione
    for var in VARIABLES_CTD:
        mask = df_anual_long["variable_col"] == var
        df_anual_long.loc[mask, var + "_media"] = df_anual_long.loc[mask, "valor_media"]

    df_tend = tendencias_anomalias(df_anual_long, df_ciclo)
    df_tend.to_csv(OUTDIR / "tendencias_anomalias_por_profundidad.csv", index=False, encoding="utf-8")
    print("Tendencias de anomalías: {} filas".format(df_tend.shape[0]))

    # --- Resumen regional por profundidad ---
    print("\n=== Calculando resumen regional por profundidad ===")
    filas_resumen = []
    for prof, sub in perfiles_z.groupby("profundidad_m"):
        fila = {"profundidad_m": prof, "n_registros": len(sub),
                "n_estaciones": sub["estacion_id"].nunique(),
                "n_zonas": sub["zona_mf"].nunique(),
                "anio_min": int(sub["fecha"].dt.year.min()),
                "anio_max": int(sub["fecha"].dt.year.max())}
        for var in VARIABLES_CTD:
            vals = sub[var].dropna()
            fila[var + "_media"] = float(vals.mean()) if len(vals) > 0 else np.nan
            fila[var + "_desvio"] = float(vals.std(ddof=1)) if len(vals) > 1 else np.nan
            fila[var + "_n_validos"] = int(len(vals))
        filas_resumen.append(fila)
    df_resumen = pd.DataFrame(filas_resumen).sort_values("profundidad_m").reset_index(drop=True)
    df_resumen.to_csv(OUTDIR / "resumen_regional_por_profundidad.csv", index=False, encoding="utf-8")
    print("Resumen regional por profundidad: {} filas".format(df_resumen.shape[0]))

    return perfiles_z, df_anual, df_ciclo, df_tend, df_resumen


if __name__ == "__main__":
    perfiles, anual, ciclo, tend, resumen = main()
