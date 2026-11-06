#!/usr/bin/env python3
"""Convierte oxígeno disuelto de ml/L a mg/L y calcula la saturación (%).

Conversión ml/L -> mg/L: factor estándar 1,42903 mg/ml (densidad del O2 a STP),
usado por la literatura oceanográfica (García y Gordon, 1992). La ecuación de
Weiss (1970) se usa para la SOLUBILIDAD (saturación), no para la conversión.

Se añaden dos columnas a los CSV de salida:
  - oxigeno_mg_L: oxigeno_ml_L * 1.42903
  - oxigeno_sat_pct: (oxigeno_ml_L / solubilidad_Weiss(T,S)) * 100

Uso: python salidas/oxigeno_conversion.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path("/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4")
FACTOR = 1.42903  # mg/ml a STP


def weiss_solubility(T_C, S_psu):
    """Solubilidad del O2 en agua de mar (ml/L) segun Weiss (1970)."""
    T = np.asarray(T_C, dtype=float) + 273.15
    S = np.asarray(S_psu, dtype=float)
    A1, A2, A3, A4 = -173.4292, 249.6339, 143.3483, -21.8492
    B1, B2, B3 = -0.033096, 0.014259, -0.001700
    lnC = (A1 + A2 * (100.0 / T) + A3 * np.log(T / 100.0) + A4 * (T / 100.0)
           + S * (B1 + B2 * (T / 100.0) + B3 * (T / 100.0) ** 2))
    return np.exp(lnC)


def convertir(df, col_ml="oxigeno_ml_L", col_t="temperatura_C", col_s="salinidad_psu"):
    if col_ml in df.columns:
        df["oxigeno_mg_L"] = df[col_ml] * FACTOR
    if col_ml in df.columns and col_t in df.columns and col_s in df.columns:
        sol = weiss_solubility(df[col_t], df[col_s])
        sat = df[col_ml] / sol * 100.0
        df["oxigeno_sat_pct"] = sat.where(sol > 0)
    return df


# 1. fondo_ctd_por_zona.csv
fondo = BASE / "fondo_ctd_por_zona.csv"
df = pd.read_csv(fondo, low_memory=False)
df = convertir(df)
df.to_csv(fondo, index=False)
print("fondo:", len(df), "filas; oxigeno_mg_L y oxigeno_sat_pct añadidos")

# 2. perfiles_procesados.csv
perf = BASE / "salidas" / "perfiles_procesados" / "perfiles_procesados.csv"
df2 = pd.read_csv(perf, low_memory=False)
df2 = convertir(df2)
df2.to_csv(perf, index=False)
print("perfiles:", len(df2), "filas; columnas añadidas")

# 3. promedio_anual_por_profundidad.csv (tiene oxigeno_ml_L_media)
prom = BASE / "salidas" / "perfiles_procesados" / "promedio_anual_por_profundidad.csv"
df3 = pd.read_csv(prom, low_memory=False)
if "oxigeno_ml_L_media" in df3.columns:
    df3["oxigeno_mg_L_media"] = df3["oxigeno_ml_L_media"] * FACTOR
if "oxigeno_ml_L_desvio" in df3.columns:
    df3["oxigeno_mg_L_desvio"] = df3["oxigeno_ml_L_desvio"] * FACTOR
df3.to_csv(prom, index=False)
print("promedios:", len(df3), "filas; oxigeno_mg_L_media añadida")
