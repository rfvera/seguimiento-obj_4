"""
mapa_estaciones_acs.py
Agente DATA - IFOP Seguimiento (objetivo_4)

Genera un mapa con las estaciones de muestreo CTD, los polígonos de las
zonas de macrofauna (Voronoi) y los polígonos oficiales de las áreas ACS
de SUBPESCA, para visualizar el dominio del análisis.

Entradas (solo lectura):
  - estaciones_CTD_con_ZONA_MACROFAUNA.csv — estaciones con lat/lon y zona_mf
  - acs_subpesca.gpkg — polígonos oficiales ACS de SUBPESCA (EPSG:4326)
  - salidas/figuras/zonas_macrofauna.gpkg — polígonos de zona de macrofauna (Voronoi)

Salida:
  - salidas/figuras/mapa_estaciones_acs.png — mapa con estaciones, polígonos de zona y polígonos ACS
"""

from __future__ import annotations

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

BASE = Path("/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4")
ESTACIONES = BASE / "estaciones_CTD_con_ZONA_MACROFAUNA.csv"
ACS_GPKG = BASE / "acs_subpesca.gpkg"
ZONAS_GPKG = BASE / "salidas" / "figuras" / "zonas_macrofauna.gpkg"
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
    if acs.crs is None:
        acs = acs.set_crs("EPSG:4326")
    elif acs.crs.to_epsg() != 4326:
        acs = acs.to_crs("EPSG:4326")

    # --- Leer polígonos de zona de macrofauna ---
    zonas = gpd.read_file(ZONAS_GPKG)
    if zonas.crs is None:
        zonas = zonas.set_crs("EPSG:4326")
    elif zonas.crs.to_epsg() != 4326:
        zonas = zonas.to_crs("EPSG:4326")

    # --- Crear GeoDataFrame de estaciones ---
    gdf_est = gpd.GeoDataFrame(
        est,
        geometry=gpd.points_from_xy(est["lon"], est["lat"]),
        crs="EPSG:4326",
    )

    # --- Paleta de colores para zonas (ordenadas norte a sur) ---
    zonas_lat = (
        gdf_est.groupby("zona_mf")["lat"]
        .mean()
        .sort_values(ascending=False)
    )
    zonas_ordenadas = zonas_lat.index.tolist()
    n_zonas = len(zonas_ordenadas)
    cmap = plt.cm.tab20 if n_zonas <= 20 else plt.cm.tab20b
    colores = {z: cmap(i / max(n_zonas - 1, 1)) for i, z in enumerate(zonas_ordenadas)}

    # --- Figura ---
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))

    # 1. Costa de Chile (primero, al fondo)
    costa_path = BASE / "salidas" / "figuras" / "chile_coastline.shp"
    if costa_path.exists():
        costa = gpd.read_file(str(costa_path))
        costa.plot(ax=ax, color="#8B4513", edgecolor="#8B4513", alpha=0.9, linewidth=1.2, zorder=0)

    # 2. Polígonos de zona (segundo, semitransparentes)
    zonas.plot(ax=ax, column="zona_mf", cmap=cmap, alpha=0.25, edgecolor="gray", linewidth=0.5, zorder=1)

    # 3. Polígonos ACS (tercero, borde más visible)
    acs.plot(ax=ax, color="none", edgecolor="darkblue", alpha=0.7, linewidth=0.8, zorder=2)

    # 4. Estaciones (sobre todo)
    for zona in zonas_ordenadas:
        sub = gdf_est[gdf_est["zona_mf"] == zona]
        ax.scatter(
            sub.geometry.x,
            sub.geometry.y,
            s=25,
            c=[colores[zona]],
            edgecolor="black",
            linewidth=0.4,
            alpha=0.9,
            zorder=3,
        )

    # Configurar ejes
    ax.set_xlabel("Longitud (°O)", fontsize=11)
    ax.set_ylabel("Latitud (°S)", fontsize=11)
    ax.set_title(
        "Estaciones CTD, zonas de macrofauna y polígonos ACS SUBPESCA\n(Objetivo 4 — Seguimiento CTD IFOP, 2019–2025)",
        fontsize=13,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.3, linestyle="--")

    # Leyenda de zonas (a la derecha, fuera del mapa)
    handles = [
        Line2D(
            [0], [0],
            marker="o", color="black", markerfacecolor=colores[z],
            markersize=6, label=z, linewidth=0
        )
        for z in zonas_ordenadas
    ]
    ax.legend(
        handles=handles,
        title="Zona de macrofauna",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        fontsize=7.5,
        title_fontsize=8.5,
        frameon=True,
        framealpha=0.9,
    )

    # Ajustar límites con margen
    x_min, x_max = gdf_est.geometry.x.min(), gdf_est.geometry.x.max()
    y_min, y_max = gdf_est.geometry.y.min(), gdf_est.geometry.y.max()
    x_margen = (x_max - x_min) * 0.08
    y_margen = (y_max - y_min) * 0.08
    x_min_plot = min(x_min - x_margen, -76.0)  # asegurar que llegue a 76°W
    ax.set_xlim(x_min_plot, x_max + x_margen)
    ax.set_ylim(y_min - y_margen, y_max + y_margen)

    plt.tight_layout()
    plt.savefig(SALIDA, dpi=300, bbox_inches="tight")
    print(f"Mapa guardado: {SALIDA}")
    plt.close()


if __name__ == "__main__":
    main()
