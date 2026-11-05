"""
analisis_estado_referencia.py
Agente DATA - IFOP Seguimiento (objetivo_4)

Objetivo:
  Definir el estado ambiental de referencia y las trayectorias de cambio
  ambiental regional a partir de los registros de fondo CTD, usando las
  zonas de macrofauna como zonificacion de referencia.

Metodo:
  - Une fondo_ctd_por_zona.csv con estaciones_CTD_con_ZONA_MACROFAUNA.csv
    para asignar zona_mf a cada registro de fondo.
  - Estado de referencia: estadisticas descriptivas (n, media, mediana,
    p5, p25, p75, p95, desvio estandar) por zona_mf y variable
    (temperatura_C, oxigeno_ml_L, salinidad_psu).
  - Trayectoria de cambio: pendiente de tendencia lineal por año por zona,
    usando mínimos cuadrados ordinarios (OLS) sobre el promedio anual por zona.
  - Todas las estaciones tienen zona_mf asignada (no se necesita imputacion
    por proximidad).

Entradas:
  - fondo_ctd_por_zona.csv
  - estaciones_CTD_con_ZONA_MACROFAUNA.csv

Salidas (en salidas/analisis_ambiental/):
  - estado_referencia_por_zona.csv
  - trayectorias_cambio_por_zona.csv
  - resumen_regional.csv
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path("/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4")
FONDO = BASE / "fondo_ctd_por_zona.csv"
ZONAS_MF = BASE / "estaciones_CTD_con_ZONA_MACROFAUNA.csv"
OUTDIR = BASE / "salidas" / "analisis_ambiental"

VARIABLES = ["temperatura_C", "oxigeno_ml_L", "salinidad_psu"]

# ---------------------------------------------------------------------------
# 1. Lectura y union
# ---------------------------------------------------------------------------
def cargar_datos() -> pd.DataFrame:
    fondo = pd.read_csv(FONDO, parse_dates=["fecha"])
    zonas = pd.read_csv(ZONAS_MF, dtype={"estacion_id": str})

    # Unir por estacion_id y archivo (archivo A y B tienen estacion_id distintos en origen)
    df = fondo.merge(
        zonas[["archivo", "estacion_id", "zona_mf", "acs_mf", "dist_km"]],
        on=["archivo", "estacion_id"],
        how="left",
    )

    n_sin_zona = int(df["zona_mf"].isna().sum())
    if n_sin_zona > 0:
        print(f"ADVERTENCIA: {n_sin_zona} registros sin zona_mf tras el merge.")

    df["anio"] = df["fecha"].dt.year
    return df


# ---------------------------------------------------------------------------
# 2. Estado de referencia por zona
# ---------------------------------------------------------------------------
def estado_referencia(df: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for zona, sub in df.groupby("zona_mf"):
        fila = {"zona_mf": zona, "n_registros": len(sub),
                "n_estaciones": sub["estacion_id"].nunique(),
                "anio_min": int(sub["anio"].min()), "anio_max": int(sub["anio"].max())}
        for var in VARIABLES:
            v = sub[var].dropna()
            if len(v) == 0:
                for suf in ["media", "mediana", "p5", "p25", "p75", "p95", "desvio"]:
                    fila[f"{var}_{suf}"] = np.nan
                fila[f"{var}_n_validos"] = 0
                continue
            fila[f"{var}_media"] = float(v.mean())
            fila[f"{var}_mediana"] = float(v.median())
            fila[f"{var}_p5"] = float(v.quantile(0.05))
            fila[f"{var}_p25"] = float(v.quantile(0.25))
            fila[f"{var}_p75"] = float(v.quantile(0.75))
            fila[f"{var}_p95"] = float(v.quantile(0.95))
            fila[f"{var}_desvio"] = float(v.std(ddof=1)) if len(v) > 1 else 0.0
            fila[f"{var}_n_validos"] = int(len(v))
        filas.append(fila)
    return pd.DataFrame(filas).sort_values("zona_mf").reset_index(drop=True)


# ---------------------------------------------------------------------------
# 3. Trayectorias de cambio por zona (tendencia lineal anual)
# ---------------------------------------------------------------------------
def trayectorias_cambio(df: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for zona, sub in df.groupby("zona_mf"):
        fila = {"zona_mf": zona, "n_registros": len(sub),
                "n_estaciones": sub["estacion_id"].nunique(),
                "anio_min": int(sub["anio"].min()), "anio_max": int(sub["anio"].max())}
        # Promedio anual por zona (una observacion por ano)
        anual = sub.groupby("anio")[VARIABLES].mean().reset_index()
        for var in VARIABLES:
            v = anual[var].dropna()
            if len(v) < 3:
                fila[f"{var}_pendiente"] = np.nan
                fila[f"{var}_intercepto"] = np.nan
                fila[f"{var}_r2"] = np.nan
                fila[f"{var}_p_valor"] = np.nan
                fila[f"{var}_n_anos"] = int(len(v))
                continue
            x = v.index.values.astype(float)  # indice de anos ordenados
            y = v.values.astype(float)
            # OLS: y = a + b*x
            x_mean = x.mean()
            y_mean = y.mean()
            b = ((x - x_mean) * (y - y_mean)).sum() / ((x - x_mean) ** 2).sum()
            a = y_mean - b * x_mean
            y_pred = a + b * x
            ss_res = ((y - y_pred) ** 2).sum()
            ss_tot = ((y - y_mean) ** 2).sum()
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
            # p-valor aproximado (t-test para b)
            n = len(v)
            if n > 2 and ss_res > 0:
                s2 = ss_res / (n - 2)
                se_b = np.sqrt(s2 / ((x - x_mean) ** 2).sum())
                t_stat = b / se_b if se_b > 0 else np.inf
                # p aproximada usando distribucion t (aproximacion normal para n grande)
                from scipy import stats
                p_val = 2 * (1 - stats.t.cdf(abs(t_stat), df=n - 2))
            else:
                p_val = np.nan
            fila[f"{var}_pendiente"] = float(b)
            fila[f"{var}_intercepto"] = float(a)
            fila[f"{var}_r2"] = float(r2)
            fila[f"{var}_p_valor"] = float(p_val)
            fila[f"{var}_n_anos"] = int(n)
        filas.append(fila)
    return pd.DataFrame(filas).sort_values("zona_mf").reset_index(drop=True)


# ---------------------------------------------------------------------------
# 4. Resumen regional
# ---------------------------------------------------------------------------
def resumen_regional(df: pd.DataFrame, estado: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for var in VARIABLES:
        v = df[var].dropna()
        filas.append({
            "metrica": f"{var}_media_regional",
            "valor": float(v.mean()),
            "n": int(len(v)),
        })
        filas.append({
            "metrica": f"{var}_mediana_regional",
            "valor": float(v.median()),
            "n": int(len(v)),
        })
        filas.append({
            "metrica": f"{var}_desvio_regional",
            "valor": float(v.std(ddof=1)) if len(v) > 1 else 0.0,
            "n": int(len(v)),
        })
    filas.append({
        "metrica": "n_zonas",
        "valor": float(df["zona_mf"].nunique()),
        "n": int(len(df)),
    })
    filas.append({
        "metrica": "n_estaciones",
        "valor": float(df["estacion_id"].nunique()),
        "n": int(len(df)),
    })
    filas.append({
        "metrica": "n_registros",
        "valor": float(len(df)),
        "n": int(len(df)),
    })
    filas.append({
        "metrica": "anio_min",
        "valor": float(df["anio"].min()),
        "n": int(len(df)),
    })
    filas.append({
        "metrica": "anio_max",
        "valor": float(df["anio"].max()),
        "n": int(len(df)),
    })
    return pd.DataFrame(filas)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    df = cargar_datos()
    print(f"Registros totales: {len(df)}")
    print(f"Zonas unicas: {df['zona_mf'].nunique()}")
    print(f"Anios: {df['anio'].min()} - {df['anio'].max()}")
    print()

    estado = estado_referencia(df)
    estado.to_csv(OUTDIR / "estado_referencia_por_zona.csv", index=False, encoding="utf-8")
    print(f"Estado de referencia: {estado.shape} -> estado_referencia_por_zona.csv")

    tray = trayectorias_cambio(df)
    tray.to_csv(OUTDIR / "trayectorias_cambio_por_zona.csv", index=False, encoding="utf-8")
    print(f"Trayectorias de cambio: {tray.shape} -> trayectorias_cambio_por_zona.csv")

    res = resumen_regional(df, estado)
    res.to_csv(OUTDIR / "resumen_regional.csv", index=False, encoding="utf-8")
    print(f"Resumen regional: {res.shape} -> resumen_regional.csv")

    print("\n=== Estado de referencia (primeras 10 zonas) ===")
    cols_show = ["zona_mf", "n_registros", "temperatura_C_media", "oxigeno_ml_L_media", "salinidad_psu_media"]
    print(estado[cols_show].head(10).to_string(index=False))

    print("\n=== Trayectorias (pendientes significativas p<0.05) ===")
    sig = tray[tray["temperatura_C_p_valor"] < 0.05]
    print(f"Zonas con tendencia significativa en temperatura: {len(sig)}")
    if len(sig) > 0:
        print(sig[["zona_mf", "temperatura_C_pendiente", "temperatura_C_p_valor", "temperatura_C_r2", "temperatura_C_n_anos"]].to_string(index=False))


if __name__ == "__main__":
    main()
