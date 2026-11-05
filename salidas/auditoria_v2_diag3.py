#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Diagnóstico v3: contradicción del solape 4326 vs Albers, y punto de máxima
distancia (qué estación es la más cercana y de qué zona). Solo lectura."""
import numpy as np, pandas as pd, geopandas as gpd, shapely
from shapely.ops import unary_union
from pyproj import CRS

BASE = "/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4"
g = gpd.read_file(f"{BASE}/salidas/figuras/zonas_macrofauna.gpkg", layer="zonas_macrofauna", engine="pyogrio")
d = pd.read_csv(f"{BASE}/estaciones_CTD_con_ZONA_MACROFAUNA.csv")
st = gpd.GeoDataFrame(d, geometry=gpd.points_from_xy(d.lon, d.lat), crs=4326)
ALB = CRS.from_user_input("ESRI:102033")

print("=" * 80); print("U. SOLAPE Aysen ∩ Guaitecas EN DISTINTOS SISTEMAS")
print("=" * 80)
a = g.loc[g.zona_mf == "Aysen", "geometry"].iloc[0]
b = g.loc[g.zona_mf == "Guaitecas", "geometry"].iloc[0]
i4326 = shapely.intersection(a, b)
print(f"en 4326 : tipo={i4326.geom_type} area_grados2={i4326.area:.6e}")
am = gpd.GeoSeries([a], crs=4326).to_crs(ALB).iloc[0]
bm = gpd.GeoSeries([b], crs=4326).to_crs(ALB).iloc[0]
im = shapely.intersection(am, bm)
print(f"en Albers: tipo={im.geom_type} area_km2={im.area/1e6:,.6f} perim_km={im.length/1e3:,.4f}")
if im.geom_type != "Point":
    print(f"  bbox del solape (Albers m): {[round(v,1) for v in im.bounds]}")
    print(f"  dimensiones: {(im.bounds[2]-im.bounds[0]):,.1f} m x {(im.bounds[3]-im.bounds[1]):,.1f} m")
    print(f"  n vértices: {len(im.exterior.coords) if hasattr(im,'exterior') else 0}")
    print(f"  área en 4326 del solape reproyectado: "
          f"{gpd.GeoSeries([im], crs=ALB).to_crs(4326).iloc[0].area:.6e} grados²")
# ¿el solape proviene de diferencias de vértices en la frontera común?
print(f"\n  ¿los vértices de ambos bordes son idénticos? intersección de conjuntos de coords:")
av = np.round(np.array(a.exterior.coords if a.geom_type=='Polygon' else
              max(a.geoms, key=lambda p: p.area).exterior.coords), 9)
def all_coords(geom):
    out = []
    for p in (geom.geoms if geom.geom_type == "MultiPolygon" else [geom]):
        out.append(np.array(p.exterior.coords))
        for h in p.interiors:
            out.append(np.array(h.coords))
    return np.vstack(out)
av, bv = all_coords(a), all_coords(b)
common = {tuple(x) for x in np.round(av, 9)} & {tuple(x) for x in np.round(bv, 9)}
print(f"  vértices compartidos exactos (9 dec): {len(common)}")
print(f"  vértices Aysen {len(av)} | Guaitecas {len(bv)}")
# distancia entre las dos geometrías
print(f"  distancia Aysen-Guaitecas en 4326: {shapely.distance(a,b):.6e} grados")
# con set_precision en Albers
img = shapely.intersection(shapely.set_precision(am, 1e-3), shapely.set_precision(bm, 1e-3))
print(f"  con set_precision(1e-3 m) en Albers: area_km2={img.area/1e6:,.6f}")

print("\n" + "=" * 80); print("V. PUNTO DE MÁXIMA DISTANCIA: ¿qué estación es la más cercana?")
print("=" * 80)
zonas_u = g.zona_mf.astype(str).str.strip()
ga = g.to_crs(ALB)
stm = st.to_crs(ALB)
S = np.column_stack([stm.geometry.x.values, stm.geometry.y.values])
labels = st.zona_mf.astype(str).str.strip().values
for i, r in g.iterrows():
    key = zonas_u.iloc[i]
    zm = ga.geometry.iloc[i]
    own = (labels == key)
    So = S[own]
    # muestreo denso del borde
    dens = shapely.segmentize(zm, 50.0)
    P = shapely.get_coordinates(dens)
    minx, miny, maxx, maxy = zm.bounds
    gx, gy = np.meshgrid(np.arange(minx, maxx + 3000, 3000), np.arange(miny, maxy + 3000, 3000))
    cand = np.column_stack([gx.ravel(), gy.ravel()])
    ins = shapely.contains_xy(zm, cand[:, 0], cand[:, 1])
    P = np.vstack([P, cand[ins]])
    best = np.full(len(P), np.inf)
    for k in range(len(So)):
        dx = P[:, 0] - So[k, 0]; dy = P[:, 1] - So[k, 1]
        best = np.minimum(best, dx * dx + dy * dy)
    j = int(np.argmax(best))
    # distancias a TODAS las estaciones en ese punto
    d_all = np.sqrt(((S - P[j]) ** 2).sum(1))
    order = np.argsort(d_all)[:2]
    print(f"{key:<16} max {np.sqrt(best[j])/1e3:7.3f} km en "
          f"({gpd.GeoSeries([shapely.Point(P[j])], crs=ALB).to_crs(4326).iloc[0].x:8.3f},"
          f"{gpd.GeoSeries([shapely.Point(P[j])], crs=ALB).to_crs(4326).iloc[0].y:7.3f})")
    for o in order:
        print(f"    estación más cercana: {d['estacion_id'].iloc[o]:<8} zona={labels[o]:<12} "
              f"d={d_all[o]/1e3:7.3f} km {'(propia)' if labels[o]==key else '(OTRA ZONA)'}")
