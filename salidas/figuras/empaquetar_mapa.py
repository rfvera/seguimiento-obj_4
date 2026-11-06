#!/usr/bin/env python3
"""Empaqueta las capas necesarias para reproducir el mapa del informe.

Salida: informe/datos/mapa_reproducible.gpkg con capas:
  - zonas: 20 poligonos de zona de macrofauna (EPSG:4326)
  - estaciones: 259 puntos de muestreo CTD con zona_mf (EPSG:4326)
  - costa: linea de costa Natural Earth 10m (EPSG:4326)

Tambien copia acs_subpesca.gpkg y la linea de costa a informe/datos/.
"""
from pathlib import Path
import shutil

import geopandas as gpd
import pandas as pd

BASE = Path("/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4")
OUT_DIR = BASE / "informe" / "datos"
OUT_DIR.mkdir(parents=True, exist_ok=True)
GPKG = OUT_DIR / "mapa_reproducible.gpkg"

# 1. Zonas
zonas = gpd.read_file(BASE / "salidas" / "figuras" / "zonas_macrofauna.gpkg")
zonas = zonas[["zona_mf", "geometry"]].copy()

# 2. Estaciones (desde CSV, con zona_mf)
est = pd.read_csv(BASE / "estaciones_CTD_con_ZONA_MACROFAUNA.csv")
est_gdf = gpd.GeoDataFrame(
    est[["estacion_id", "zona_mf", "lat", "lon"]],
    geometry=gpd.points_from_xy(est["lon"], est["lat"]),
    crs="EPSG:4326",
)

# 3. Costa
costa = gpd.read_file(BASE / "salidas" / "figuras" / "ne_10m_coastline.shp")
costa = costa[["geometry"]].copy()

# escribir GPKG (sobrescribir si existe)
if GPKG.exists():
    GPKG.unlink()
zonas.to_file(GPKG, layer="zonas", driver="GPKG")
est_gdf.to_file(GPKG, layer="estaciones", driver="GPKG", mode="a")
costa.to_file(GPKG, layer="costa", driver="GPKG", mode="a")

# copiar archivos auxiliares
shutil.copy2(BASE / "acs_subpesca.gpkg", OUT_DIR / "acs_subpesca.gpkg")
for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
    src = BASE / "salidas" / "figuras" / ("ne_10m_coastline" + ext)
    if src.exists():
        shutil.copy2(src, OUT_DIR / ("ne_10m_coastline" + ext))

print("GPKG:", GPKG)
for layer in ["zonas", "estaciones", "costa"]:
    g = gpd.read_file(GPKG, layer=layer)
    print(f"  {layer}: {len(g)} features, {g.crs}")
print("auxiliares:", sorted(p.name for p in OUT_DIR.iterdir() if p.name != GPKG.name))