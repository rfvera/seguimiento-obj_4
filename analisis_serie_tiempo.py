"""
analisis_serie_tiempo.py
Agente DATA - IFOP Seguimiento (objetivo_4)

Analiza cada zona×profundidad×variable como serie de tiempo anual:
- Tendencia lineal (OLS)
- Cambio por década
- Estadísticas descriptivas (media, mediana, min, max, desvío, CV)
- Número de años con datos y rango temporal
- Detección de años con valores extremos

Metodología (verificada en literatura):
- Tendencia lineal por mínimos cuadrados ordinarios (OLS)
- Cambio por década = pendiente * 10
- Coeficiente de variación = desvío / media * 100

Entradas (solo lectura):
  - salidas/perfiles_procesados/promedio_anual_por_profundidad.csv

Salidas (en salidas/analisis_serie_tiempo/):
  - serie_tiempo_por_variable.csv     : una fila por zona×profundidad×variable con estadísticas y tendencia
  - series_tiempo_detalladas.csv      : cada año como fila (zona×profundidad×variable×año)
  - resumen_tendencias_significativas.csv : solo tendencias con p<0.05
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

BASE = Path("/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4")
ENTRADA = BASE / "salidas" / "perfiles_procesados" / "promedio_anual_por_profundidad.csv"
OUTDIR = BASE / "salidas" / "analisis_serie_tiempo"

VARIABLES = ["temperatura_C", "oxigeno_ml_L", "salinidad_psu"]
MIN_ANOS = 3  # mínimo de años para calcular tendencia


def cargar_datos() -> pd.DataFrame:
    df = pd.read_csv(ENTRADA)
    # Normalizar nombres de columnas para análisis
    df = df.rename(columns={
        "temperatura_C_media": "temperatura_C",
        "oxigeno_ml_L_media": "oxigeno_ml_L",
        "salinidad_psu_media": "salinidad_psu",
    })
    df["anio"] = df["anio"].astype(int)
    return df


def analizar_serie(sub: pd.DataFrame, zona: str, profundidad: float, variable: str) -> dict:
    """Analiza una serie de tiempo anual para una zona×profundidad×variable."""
    sub = sub.dropna(subset=[variable]).sort_values("anio")
    n_anos = len(sub)

    fila = {
        "zona_mf": zona,
        "profundidad_m": profundidad,
        "variable": variable,
        "n_anos": n_anos,
        "anio_min": int(sub["anio"].min()) if n_anos > 0 else np.nan,
        "anio_max": int(sub["anio"].max()) if n_anos > 0 else np.nan,
        "media": float(sub[variable].mean()) if n_anos > 0 else np.nan,
        "mediana": float(sub[variable].median()) if n_anos > 0 else np.nan,
        "min": float(sub[variable].min()) if n_anos > 0 else np.nan,
        "max": float(sub[variable].max()) if n_anos > 0 else np.nan,
        "desvio": float(sub[variable].std(ddof=1)) if n_anos > 1 else np.nan,
        "cv": float(sub[variable].std(ddof=1) / sub[variable].mean() * 100)
        if n_anos > 1 and sub[variable].mean() != 0 else np.nan,
    }

    # Tendencia lineal OLS (requiere al menos 3 años)
    if n_anos >= MIN_ANOS:
        x = sub["anio"].values.astype(float)
        y = sub[variable].values.astype(float)
        try:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            fila["pendiente"] = float(slope)
            fila["cambio_decada"] = float(slope * 10)
            fila["intercepto"] = float(intercept)
            fila["r2"] = float(r_value ** 2)
            fila["p_valor"] = float(p_value)
            fila["error_estandar"] = float(std_err)
            fila["tendencia_significativa"] = p_value < 0.05
        except Exception:
            fila["pendiente"] = np.nan
            fila["cambio_decada"] = np.nan
            fila["intercepto"] = np.nan
            fila["r2"] = np.nan
            fila["p_valor"] = np.nan
            fila["error_estandar"] = np.nan
            fila["tendencia_significativa"] = False
    else:
        fila["pendiente"] = np.nan
        fila["cambio_decada"] = np.nan
        fila["intercepto"] = np.nan
        fila["r2"] = np.nan
        fila["p_valor"] = np.nan
        fila["error_estandar"] = np.nan
        fila["tendencia_significativa"] = False

    return fila


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    df = cargar_datos()
    print("Registros cargados:", len(df))
    print("Zonas:", df["zona_mf"].nunique())
    print("Años:", sorted(df["anio"].unique()))
    print("Profundidades:", sorted(df["profundidad_m"].unique())[:5], "...", sorted(df["profundidad_m"].unique())[-5:])

    # Detallar cada año como fila (series tiempo detalladas)
    filas_detalle = []
    for zona in df["zona_mf"].unique():
        for prof in df["profundidad_m"].unique():
            for var in VARIABLES:
                sub = df[(df["zona_mf"] == zona) & (df["profundidad_m"] == prof)].copy()
                for _, row in sub.iterrows():
                    filas_detalle.append({
                        "zona_mf": zona,
                        "profundidad_m": prof,
                        "variable": var,
                        "anio": int(row["anio"]),
                        "valor": float(row[var]),
                        "desvio": float(row[var + "_desvio"]) if (var + "_desvio") in row.index and pd.notna(row[var + "_desvio"]) else np.nan,
                        "n_validos": int(row[var + "_n_validos"]) if (var + "_n_validos") in row.index and pd.notna(row[var + "_n_validos"]) else np.nan,
                    })
    df_detalle = pd.DataFrame(filas_detalle)
    df_detalle.to_csv(OUTDIR / "series_tiempo_detalladas.csv", index=False, encoding="utf-8")
    print("Series tiempo detalladas guardadas:", df_detalle.shape)

    # Estadísticas y tendencia por zona×profundidad×variable
    filas_resumen = []
    for zona in df["zona_mf"].unique():
        for prof in df["profundidad_m"].unique():
            for var in VARIABLES:
                sub = df[(df["zona_mf"] == zona) & (df["profundidad_m"] == prof)].copy()
                fila = analizar_serie(sub, zona, prof, var)
                filas_resumen.append(fila)
    df_resumen = pd.DataFrame(filas_resumen)
    df_resumen.to_csv(OUTDIR / "serie_tiempo_por_variable.csv", index=False, encoding="utf-8")
    print("Serie tiempo por variable guardada:", df_resumen.shape)

    # Resumen de tendencias significativas
    df_sig = df_resumen[df_resumen["tendencia_significativa"] == True].copy()
    df_sig.to_csv(OUTDIR / "resumen_tendencias_significativas.csv", index=False, encoding="utf-8")
    print("Tendencias significativas:", len(df_sig))

    print("\n=== Tendencias significativas (top 20 por |pendiente|) ===")
    if len(df_sig) > 0:
        df_sig_abs = df_sig.copy()
        df_sig_abs["pendiente_abs"] = df_sig_abs["pendiente"].abs()
        print(df_sig_abs.sort_values("pendiente_abs", ascending=False).head(20)[
            ["zona_mf", "profundidad_m", "variable", "pendiente", "cambio_decada", "p_valor", "r2", "n_anos"]
        ].to_string(index=False))

    return df_detalle, df_resumen, df_sig


if __name__ == "__main__":
    detalle, resumen, significativo = main()
