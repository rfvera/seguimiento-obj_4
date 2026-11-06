#!/usr/bin/env python3
"""Análisis de tendencias temporales por estación (fondo y 10 m).

Para cada estación×variable se calcula el promedio anual y la tendencia OLS
sobre el año real. Se reportan las estaciones con tendencia significativa (p<0.05)
y un resumen por zona.

Salidas:
  - salidas/analisis_por_estacion/tendencias_por_estacion.csv
  - salidas/analisis_por_estacion/resumen_por_estacion.csv
  - salidas/analisis_por_estacion/top_estaciones.csv
  - informe/figuras/series_estaciones_fondo.png
  - informe/figuras/series_estaciones_10m.png
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

BASE = Path("/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4")
OUT = BASE / "salidas" / "analisis_por_estacion"
OUT.mkdir(parents=True, exist_ok=True)
FIG = BASE / "informe" / "figuras"
FIG.mkdir(parents=True, exist_ok=True)

VARIABLES = {
    "temperatura_C": ("Temperatura (°C)", "#b2182b"),
    "oxigeno_mg_L": ("Oxígeno (mg/L)", "#2166ac"),
    "salinidad_psu": ("Salinidad (PSU)", "#1b7837"),
}
MIN_ANOS = 3


def tendencia_por_estacion(df, var, prof_label):
    """df: DataFrame con columnas estacion_id, zona_mf, anio, <var>."""
    filas = []
    for (est, zona), sub in df.groupby(["estacion_id", "zona_mf"]):
        s = sub.dropna(subset=[var]).sort_values("anio")
        n = len(s)
        fila = {
            "estacion_id": est, "zona_mf": zona, "variable": var,
            "profundidad": prof_label, "n_anos": n,
            "anio_min": int(s["anio"].min()) if n > 0 else None,
            "anio_max": int(s["anio"].max()) if n > 0 else None,
            "media": float(s[var].mean()) if n > 0 else None,
        }
        if n >= MIN_ANOS:
            x = s["anio"].values.astype(float)
            y = s[var].values.astype(float)
            slope, intercept, r, p, se = stats.linregress(x, y)
            fila["pendiente"] = float(slope)
            fila["p_valor"] = float(p)
            fila["r2"] = float(r ** 2)
            fila["tendencia_sig"] = bool(p < 0.05)
        else:
            fila["pendiente"] = None
            fila["p_valor"] = None
            fila["r2"] = None
            fila["tendencia_sig"] = False
        filas.append(fila)
    return pd.DataFrame(filas)


# --- Fondo ---
fondo = pd.read_csv(BASE / "fondo_ctd_por_zona.csv", low_memory=False)
fondo["anio"] = fondo["fecha"].str[:4].astype(int)
fondo_anual = fondo.groupby(["estacion_id", "zona_mf", "anio"], as_index=False).agg(
    temperatura_C=("temperatura_C", "mean"),
    oxigeno_mg_L=("oxigeno_mg_L", "mean"),
    salinidad_psu=("salinidad_psu", "mean"),
)

# --- 10 m ---
perf = pd.read_csv(BASE / "salidas" / "perfiles_procesados" / "perfiles_procesados.csv", low_memory=False)
perf10 = perf[perf["profundidad_m"] == 10].copy()
perf10["anio"] = perf10["fecha"].astype(str).str[:4].astype(int)
perf10_anual = perf10.groupby(["estacion_id", "zona_mf", "anio"], as_index=False).agg(
    temperatura_C=("temperatura_C", "mean"),
    oxigeno_mg_L=("oxigeno_mg_L", "mean"),
    salinidad_psu=("salinidad_psu", "mean"),
)

# --- Tendencias por estación ---
frames = []
for var in VARIABLES:
    frames.append(tendencia_por_estacion(fondo_anual, var, "fondo"))
    frames.append(tendencia_por_estacion(perf10_anual, var, "10 m"))
tend = pd.concat(frames, ignore_index=True)
tend.to_csv(OUT / "tendencias_por_estacion.csv", index=False)
print("tendencias:", len(tend))

# --- Resumen por zona y variable ---
res = tend.groupby(["zona_mf", "variable", "profundidad"]).agg(
    n_est=("estacion_id", "nunique"),
    n_con_3a=("tendencia_sig", lambda s: (tend.loc[s.index, "n_anos"] >= MIN_ANOS).sum()),
).reset_index()
# recalcular correctamente
res2 = []
for (zona, var, prof), sub in tend.groupby(["zona_mf", "variable", "profundidad"]):
    res2.append({
        "zona_mf": zona, "variable": var, "profundidad": prof,
        "n_estaciones": sub["estacion_id"].nunique(),
        "n_con_3_anos": int((sub["n_anos"] >= MIN_ANOS).sum()),
        "n_sig": int(sub["tendencia_sig"].sum()),
    })
res = pd.DataFrame(res2)
res.to_csv(OUT / "resumen_por_estacion.csv", index=False)
print("resumen:", len(res))

# --- Top estaciones con tendencia significativa ---
top = tend[tend["tendencia_sig"] == True].copy()
top["abs_pend"] = top["pendiente"].abs()
top = top.sort_values(["variable", "profundidad", "abs_pend"], ascending=[True, True, False])
top.to_csv(OUT / "top_estaciones.csv", index=False)
print("top sig:", len(top))
print(top.groupby(["variable", "profundidad"]).size().to_string())

# --- Figuras: series por estacion con tendencia sig ---
est = pd.read_csv(BASE / "estaciones_CTD_con_ZONA_MACROFAUNA.csv")
lat = est.groupby("zona_mf")["lat"].mean()
zonas_ns = list(lat.sort_values(ascending=False).index)
colors = plt.cm.tab20(np.linspace(0, 1, len(zonas_ns)))
color_map = {z: colors[i] for i, z in enumerate(zonas_ns)}

def figura_series(df_anual, var, prof_label, fname):
    sig = top[(top["variable"] == var) & (top["profundidad"] == prof_label)]
    if sig.empty:
        print("sin sig:", var, prof_label)
        return
    est_sig = set(sig["estacion_id"])
    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    for est_id, sub in df_anual[df_anual[var].notna()].groupby("estacion_id"):
        if est_id not in est_sig:
            continue
        zona = sub["zona_mf"].iloc[0]
        s = sub.sort_values("anio")
        ax.plot(s["anio"], s[var], "-o", color=color_map[zona],
                markersize=3, linewidth=1.0, alpha=0.85, label=zona)
    ax.set_title(f"{VARIABLES[var][0]} — {prof_label} — estaciones con tendencia significativa (n={len(est_sig)})",
                 fontsize=9.5, loc="left")
    ax.set_ylabel(VARIABLES[var][0], fontsize=8.5)
    ax.set_xlabel("Año", fontsize=8.5)
    ax.set_xticks(range(2019, 2026))
    ax.tick_params(labelsize=8)
    ax.grid(alpha=0.25, linewidth=0.6)
    # leyenda por zona (sin duplicados)
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), fontsize=6.5, loc="upper left",
              frameon=True, framealpha=0.9, ncol=2)
    fig.tight_layout()
    fig.savefig(FIG / fname, dpi=300, bbox_inches="tight")
    print("->", FIG / fname)

for prof, suffix in [("fondo", "fondo"), ("10 m", "10m")]:
    df_anual = fondo_anual if prof == "fondo" else perf10_anual
    for var in VARIABLES:
        figura_series(df_anual, var, prof, f"series_estaciones_{var.replace('_C','').replace('_mg_L','').replace('_psu','')}_{suffix}.png")

print("done")
