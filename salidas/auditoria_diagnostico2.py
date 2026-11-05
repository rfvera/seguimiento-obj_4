#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Diagnóstico 2: verificación de la parte anómala de Puyuhuapi, bordes rectos
(recorte por marco) y coherencia espacial con las estaciones. Solo lectura."""
import pandas as pd, geopandas as gpd, shapely, numpy as np
from shapely.ops import unary_union
from pyproj import CRS

BASE = "/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4"
g = gpd.read_file(f"{BASE}/salidas/figuras/zonas_macrofauna.gpkg", layer="zonas_macrofauna", engine="pyogrio")
c = gpd.read_file(f"{BASE}/salidas/figuras/ne_10m_admin_0_countries.shp", engine="pyogrio")
ALB = CRS.from_user_input("ESRI:102033")
d = pd.read_csv(f"{BASE}/estaciones_CTD_con_ZONA_MACROFAUNA.csv")

print("="*78); print("E. VERIFICACIÓN DE PUNTOS DE CONTROL EN EL LAYER DE PAÍSES")
print("="*78)
pts = {"(-67.00,-46.10) mar Argentino?": (-67.00, -46.10),
       "(-69.00,-46.00) interior ARG": (-69.00, -46.00),
       "(-67.50,-46.10) costa ARG": (-67.50, -46.10),
       "(-72.86,-44.67) fiordo Puyuhuapi": (-72.86, -44.67),
       "(-74.50,-45.70) mar abierto": (-74.50, -45.70)}
for n, (x, y) in pts.items():
    hit = c[c.geometry.intersects(shapely.Point(x, y))].ADMIN.tolist()
    print(f"  {n:<34} -> {hit if hit else 'NADIE (agua)'}")

land = unary_union([shapely.make_valid(x) for x in c.geometry])
land_m = gpd.GeoSeries([land], crs=4326).to_crs(ALB).iloc[0]

print("\n" + "="*78); print("F. PARTE 2 DE PUYUHAPI: ¿DÓNDE ESTÁ Y QUÉ ES?")
print("="*78)
puy = g.loc[g.zona_mf == "Puyuhuapi"].geometry.iloc[0]
parts = sorted(puy.geoms, key=lambda p: -p.area)
big = parts[0]
print(f"n partes: {len(parts)}")
print(f"parte mayor: bounds {big.bounds} | área "
      f"{gpd.GeoSeries([big], crs=4326).to_crs(ALB).iloc[0].area/1e6:,.3f} km²")
print(f"  n vértices: {len(big.exterior.coords)}")
print(f"  intersección con tierra (países): "
      f"{gpd.GeoSeries([big.intersection(land)], crs=4326).to_crs(ALB).iloc[0].area/1e6:,.6f} km²")
d_puy = d[d.zona_mf == "Puyuhuapi"]
print(f"\n  distancia del centroide de la parte mayor a la estación Puyuhuapi más cercana:")
cen = big.centroid
stp = gpd.GeoSeries(gpd.points_from_xy(d_puy.lon, d_puy.lat), crs=4326)
dcen = stp.distance(cen) * 111.32
print(f"    {dcen.min():,.1f} km aprox")
print(f"  distancia de la parte mayor a la parte principal de la zona: ")
other = unary_union(parts[1:])
print(f"    {gpd.GeoSeries([other], crs=4326).to_crs(ALB).iloc[0].distance(gpd.GeoSeries([big], crs=4326).to_crs(ALB).iloc[0])/1e3:,.1f} km")
print(f"  distancia de la parte mayor a la costa más cercana: "
      f"{gpd.GeoSeries([big.boundary], crs=4326).to_crs(ALB).iloc[0].distance(land_m.boundary)/1e3:,.1f} km")
# ¿bordes rectos?
co = np.array(big.exterior.coords)
print(f"\n  vértices totales {len(co)}")
for val, lab in [(-66.600556, 'lon_max=-66.600556'), (-67.6244, 'lon_min=-67.6244')]:
    n_eq = int((np.abs(co[:, 0] - val) < 1e-5).sum())
    print(f"  vértices con {lab}: {n_eq}")
print(f"  rango lon [{co[:,0].min():.6f}, {co[:,0].max():.6f}]  lat [{co[:,1].min():.6f}, {co[:,1].max():.6f}]")
# ¿es un polígono de tipo 'celda' (pocos vértices, lados rectos)?
print(f"  nº vértices del anillo exterior (sin repetir cierre): {len(co)-1}")

print("\n" + "="*78); print("G. BORDES RECTO EN EL CONJUNTO DE LA CAPA (recorte por marco)")
print("="*78)
allc = []
for geom in g.geometry:
    for p in (geom.geoms if geom.geom_type == "MultiPolygon" else [geom]):
        allc.append(np.array(p.exterior.coords))
co = np.vstack(allc)
for axis, name in [(0, "lon"), (1, "lat")]:
    vals, counts = np.unique(np.round(co[:, axis], 6), return_counts=True)
    top = sorted(zip(counts, vals), reverse=True)[:5]
    print(f"  {name}: valores más repetidos -> " +
          ", ".join(f"{v} (n={n})" for n, v in top))
print("\n  Interpretación: un valor de coordenada repetido en muchos vértices = borde recto")
print("  (recorte por la extensión de un insumo previo), no una costa real.")

print("\n" + "="*78); print("H. ESTACIONES: ¿LAS HAY EN LA PARTE ANÓMALA?")
print("="*78)
b = shapely.box(*big.bounds).buffer(1.0)
en = d[(d.lon.between(b.bounds[0], b.bounds[2])) & (d.lat.between(b.bounds[1], b.bounds[3]))]
print(f"estaciones del CSV dentro del bbox de la parte anómala (+1°): {len(en)}")
if len(en):
    print(en[["archivo", "estacion_id", "zona_mf", "lat", "lon"]].to_string(index=False))

print("\n" + "="*78); print("I. RECALCULO DE ÁREAS EXCLUYENDO LA PARTE ANÓMALA DE PUYUHAPI")
print("="*78)
resto = unary_union(parts[1:])
a_anom = gpd.GeoSeries([big], crs=4326).to_crs(ALB).iloc[0].area / 1e6
a_rest = gpd.GeoSeries([resto], crs=4326).to_crs(ALB).iloc[0].area / 1e6
print(f"Puyuhuapi total          : {a_anom + a_rest:,.3f} km²")
print(f"  parte anómala (Atlántico): {a_anom:,.3f} km²  ({a_anom/(a_anom+a_rest)*100:.1f}%)")
print(f"  resto (fiordo)           : {a_rest:,.3f} km²")
tot = g.to_crs(ALB).area.sum() / 1e6
print(f"\nÁrea total de las 20 zonas              : {tot:,.3f} km²")
print(f"Área total sin la parte anómala         : {tot - a_anom:,.3f} km²")
