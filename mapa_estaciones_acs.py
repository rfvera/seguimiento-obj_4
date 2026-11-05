"""
mapa_estaciones_acs.py
Agente DATA - IFOP Seguimiento (objetivo_4)

Genera un mapa con las estaciones de muestreo CTD y los polígonos de las
áreas ACS de SUBPESCA, para visualizar el dominio del análisis.

Entradas (solo lectura):
  - estaciones_CTD_con_ZONA_MACROFAUNA.csv — estaciones con lat/lon y zona_mf
  - acs_subpesca.gpkg — polígonos oficiales ACS de SUBPESCA (EPSG:4326)

Salida:
  - salidas/figuras/mapa_estaciones_acs.png — mapa con estaciones y polígonos
"""

from __future__ import annotations

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.lines import Line2D

BASE = Path("/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4")
ESTACIONES = BASE / "estaciones_CTD_con_ZONA_MACROFAUNA.csv"
ACS_GPKG = BASE / "acs_subpesca.gpkg"
OUTDIR = BASE / "salidas" / "figuras"
SALIDA = OUTDIR / "mapa_estaciones_acs.png"


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    # --- Leer estaciones ---
    est = pd.read_csv(ESTACIONES)
    est["lat"] = pd.to_numeric(est["lat"], errors="coerce")
    est["lon"] = pd.to_numeric(est["lon"], errors="coerce")
    est = est.dropna(subset=["lat", "lon"])
    print(f"Estaciones con coordenadas válidas: {len(est)}")
    print(f"Zonas únicas: {est['zona_mf'].nunique()}")

    # --- Leer polígonos ACS ---
    acs = gpd.read_file(ACS_GPKG)
    print(f"Polígonos ACS cargados: {len(acs)}")
    print(f"Columnas ACS: {acs.columns.tolist()}")
    print(f"CRS ACS: {acs.crs}")

    # Asegurar CRS WGS84 para el mapa
    if acs.crs is None:
        acs = acs.set_crs("EPSG:4326")
    elif acs.crs.to_epsg() != 4326:
        acs = acs.to_crs("EPSG:4326")

    # --- Crear GeoDataFrame de estaciones ---
    gdf_est = gpd.GeoDataFrame(
        est,
        geometry=gpd.points_from_xy(est["lon"], est["lat"]),
        crs="EPSG:4326",
    )

    # --- Paleta de colores para zonas ---
    zonas = sorted(gdf_est["zona_mf"].unique())
    n_zonas = len(zonas)
    cmap = plt.cm.tab20 if n_zonas <= 20 else plt.cm.tab20b
    colores = {z: cmap(i / max(n_zonas - 1, 1)) for i, z in enumerate(zonas)}

    # --- Figura ---
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    # Polígonos ACS (fondo, semitransparentes)
    acs.plot(ax=ax, color="lightgray", edgecolor="gray", alpha=0.4, linewidth=0.8)

    # Estaciones coloreadas por zona_mf
    for zona in zonas:
        sub = gdf_est[gdf_est["zona_mf"] == zona]
        ax.scatter(
            sub.geometry.x,
            sub.geometry.y,
            s=30,
            c=[colores[zona]],
            edgecolor="black",
            linewidth=0.5,
            alpha=0.8,
            label=zona,
        )

    # Configurar ejes
    ax.set_xlabel("Longitud (°O)", fontsize=11)
    ax.set_ylabel("Latitud (°S)", fontsize=11)
    ax.set_title(
        "Estaciones de muestreo CTD y polígonos ACS SUBPESCA\n(Objetivo 4 — Seguimiento CTD IFOP, 2019–2025)",
        fontsize=13,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.3, linestyle="--")

    # Leyenda de zonas (a la derecha, fuera del mapa)
    handles = [
        Line2D(
            [0], [0],
            marker="o", color="black", markerfacecolor=colores[z],
            markersize=7, label=z, linewidth=0
        )
        for z in zonas
    ]
    ax.legend(
        handles=handles,
        title="Zona de macrofauna",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        fontsize=8,
        title_fontsize=9,
        frameon=True,
        framealpha=0.9,
    )

    # Ajustar límites con margen
    x_min, x_max = gdf_est.geometry.x.min(), gdf_est.geometry.x.max()
    y_min, y_max = gdf_est.geometry.y.min(), gdf_est.geometry.y.max()
    x_margen = (x_max - x_min) * 0.08
    y_margen = (y_max - y_min) * 0.08
    ax.set_xlim(x_min - x_margen, x_max + x_margen)
    ax.set_ylim(y_min - y_margen, y_max + y_margen)

    plt.tight_layout()
    plt.savefig(SALIDA, dpi=300, bbox_inches="tight")
    print(f"Mapa guardado: {SALIDA}")
    plt.close()


if __name__ == "__main__":
    main()
