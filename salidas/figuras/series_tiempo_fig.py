#!/usr/bin/env python3
"""Series de tiempo anuales de las variables con tendencia significativa de fondo.

Cada panel muestra dos profundidades de la misma zona:
  - fondo: promedio anual del registro de fondo (profundidad maxima por cast)
  - 10 m: promedio anual del perfil bineado a 1 m

La recta OLS se ajusta sobre el ano real, no sobre la posicion de la serie: con
anos faltantes, usar 0,1,2... escala mal la pendiente (es el error que tenia
`analisis_estado_referencia.py`).

Salida: informe/figuras/series_tendencias_fondo.png
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

BASE = Path("/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4")
SALIDA = BASE / "informe" / "figuras"
SALIDA.mkdir(parents=True, exist_ok=True)

VARIABLES = {
    "temperatura_C": ("Temperatura (°C)", "#b2182b"),
    "oxigeno_ml_L": ("Oxígeno (ml/L)", "#2166ac"),
    "salinidad_psu": ("Salinidad (psu)", "#1b7837"),
}

# Las seis tendencias significativas de fondo, en el orden del cuadro 3.
PANELES = [
    ("Reloncavi", "Reloncaví", "oxigeno_ml_L"),
    ("Butachauques", "Butachauques", "salinidad_psu"),
    ("Desertores", "Desertores", "salinidad_psu"),
    ("Quellon", "Quellón", "temperatura_C"),
    ("Puyuhuapi", "Puyuhuapi", "oxigeno_ml_L"),
    ("Aysen", "Aysén", "salinidad_psu"),
]

fondo = pd.read_csv(BASE / "fondo_ctd_por_zona.csv", low_memory=False)
fondo["anio"] = fondo["fecha"].str[:4].astype(int)

anual = pd.read_csv(BASE / "salidas/perfiles_procesados/promedio_anual_por_profundidad.csv")

fig, axes = plt.subplots(2, 3, figsize=(7.9, 4.9), sharex=True)
axes = axes.ravel()

for ax, (zona, nombre, var) in zip(axes, PANELES):
    etiqueta, color = VARIABLES[var]

    # --- registro de fondo: promedio anual de todos los casts de la zona
    d = fondo[fondo["zona_mf"] == zona]
    s = d.groupby("anio")[var].mean().dropna()
    x, y = s.index.values.astype(float), s.values.astype(float)

    ax.plot(x, y, "o-", color=color, markersize=6, linewidth=1.6,
            label="Fondo", zorder=3)

    # OLS sobre el ano real
    res = stats.linregress(x, y)
    xx = np.linspace(x.min(), x.max(), 50)
    ax.plot(xx, res.intercept + res.slope * xx, "--", color=color,
            linewidth=1.2, alpha=0.85, zorder=2)

    # --- 10 m: promedio anual del perfil bineado
    diez = anual[(anual["zona_mf"] == zona)
                 & (anual["profundidad_m"] == 10)]
    if not diez.empty:
        col = f"{var}_media"
        z = diez.dropna(subset=[col]).sort_values("anio")
        ax.plot(z["anio"], z[col], "s--", color="#6e6e6e", markersize=4,
                linewidth=1.1, label="10 m", zorder=2)

    ax.set_title(f"{nombre} · {etiqueta.split(' (')[0]}", fontsize=8.2, loc="left")
    ax.set_ylabel(etiqueta, fontsize=7)
    ax.tick_params(labelsize=6.8)
    ax.grid(alpha=0.25, linewidth=0.6)
    ax.set_xticks(range(2019, 2026))
    ax.set_xticklabels(range(2019, 2026), rotation=0, fontsize=6.5)

    signo = "+" if res.slope >= 0 else "−"
    p_txt = "<0,001" if res.pvalue < 0.001 else (f"{res.pvalue:.4f}" if round(res.pvalue, 3) == 0.05 else f"{res.pvalue:.3f}")
    anotacion = (
        f"{signo}{abs(res.slope):.2f}/año · p={p_txt} · R²={res.rvalue ** 2:.2f}"
    ).replace(".", ",")
    ax.annotate(
        anotacion,
        xy=(0.02, 0.02), xycoords="axes fraction", fontsize=6.6,
        color="#222222",
        bbox=dict(facecolor="white", edgecolor="#cccccc", linewidth=0.5,
                  alpha=0.92, pad=2.0),
    )
    ax.legend(fontsize=6.0, loc="upper left", frameon=True, framealpha=0.9,
              edgecolor="#cccccc", handlelength=1.6)

fig.suptitle(
    "Series anuales del registro de fondo y de 10 m en las zonas con tendencia significativa (2019–2025)",
    fontsize=8.6, y=0.985,
)
fig.text(
    0.5, 0.005,
    "Cada punto es el promedio anual de todos los casts de la zona. La línea discontinua de color es el ajuste OLS "
    "sobre el año real; la gris corresponde a 10 m. Los años sin dato no se interpolan.",
    ha="center", fontsize=6.2, color="#555555",
)
fig.tight_layout(rect=(0, 0.03, 1, 0.955))
fig.savefig(SALIDA / "series_tendencias_fondo.png", dpi=300, bbox_inches="tight")
print("->", SALIDA / "series_tendencias_fondo.png")
