#!/usr/bin/env python3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = Path("/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4")
OUT_CSV = BASE / "salidas" / "verificacion" / "cobertura_temporal.csv"
OUT_PNG = BASE / "informe" / "figuras" / "cobertura_temporal.png"

fondo = pd.read_csv(BASE / "fondo_ctd_por_zona.csv", low_memory=False)
fondo["anio"] = fondo["fecha"].str[:4].astype(int)

cob = fondo.groupby("zona_mf").agg(
    estaciones=("estacion_id", "nunique"),
    anio_min=("anio", "min"),
    anio_max=("anio", "max"),
    n_anios=("anio", "nunique"),
    casts=("fecha", "size"),
).sort_values(["n_anios", "estaciones"], ascending=[False, False])

mat = fondo.groupby(["zona_mf", "anio"]).size().unstack(fill_value=0)
mat = mat.reindex(cob.index)
years = list(range(2019, 2026))
mat = mat.reindex(columns=years, fill_value=0)

for y in years:
    cob[f"n_{y}"] = mat[y].values
cob = cob.reset_index().rename(columns={"zona_mf": "zona"})
cob.to_csv(OUT_CSV, index=False)
print("->", OUT_CSV, "(", len(cob), "zonas)")

fig, ax = plt.subplots(figsize=(7.6, 6.6))
M = mat.values.astype(float)
Mplot = np.sqrt(M)
im = ax.imshow(Mplot, aspect="auto", cmap="YlGnBu", vmin=0, vmax=np.sqrt(M.max()))

ax.set_xticks(range(len(years)))
ax.set_xticklabels(years, fontsize=8)
ax.set_yticks(range(len(mat.index)))
ax.set_yticklabels(mat.index, fontsize=7.5)
ax.set_xlabel("Año", fontsize=8.5)
ax.set_ylabel("Zona de macrofauna", fontsize=8.5)
ax.set_title("Cobertura temporal del muestreo CTD por zona (casts por año)", fontsize=9.5, loc="left")

for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        v = int(M[i, j])
        if v == 0:
            txt = ""
            col = "#999999"
        else:
            txt = str(v)
            col = "white" if Mplot[i, j] > np.sqrt(M.max()) * 0.55 else "#222222"
        ax.text(j, i, txt, ha="center", va="center", fontsize=6.2, color=col)

for i, zona in enumerate(mat.index):
    yrs = [y for y in years if mat.loc[zona, y] > 0]
    if min(yrs) >= 2024:
        ax.plot(-0.6, i, marker=">", color="#b2182b", markersize=4, clip_on=False)

cbar = fig.colorbar(im, ax=ax, shrink=0.6, pad=0.02)
cbar.set_label("casts (escala sqrt)", fontsize=7.5)
cbar.ax.tick_params(labelsize=7)

fig.text(0.5, 0.005,
         "Cada celda es el número de casts (estación×fecha) con registro de fondo. "
         "Marcador rojo: zonas con datos solo en 2024–2025.",
         ha="center", fontsize=6.8, color="#555555")
fig.tight_layout(rect=(0, 0.02, 1, 0.97))
fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
print("->", OUT_PNG)