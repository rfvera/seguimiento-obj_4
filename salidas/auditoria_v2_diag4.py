#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Diagnóstico v4: distancias GEODÉSICAS reales (el generador las mide en EPSG:6933,
que a 55°S está muy deformado). Solo lectura."""
import numpy as np, pandas as pd, geopandas as gpd, shapely
from pyproj import CRS, Geod
from scipy.spatial import cKDTree

BASE = "/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4"
g = gpd.read_file(f"{BASE}/salidas/figuras/zonas_macrofauna.gpkg", layer="zonas_macrofauna", engine="pyogrio")
d = pd.read_csv(f"{BASE}/estaciones_CTD_con_ZONA_MACROFAUNA.csv")
st = gpd.GeoDataFrame(d, geometry=gpd.points_from_xy(d.lon, d.lat), crs=4326)
geod = Geod(ellps="WGS84")
UTM = CRS.from_user_input("EPSG:32719")

print("=" * 80)
print("W. ¿CUÁNTO MIDE DE VERDAD UN BÚFER DE 100 km HECHO EN EPSG:6933?")
print("=" * 80)
z = gpd.GeoSeries([shapely.Point(-67.3056, -54.9283)], crs=4326).to_crs(6933).iloc[0]
buf = z.buffer(100_000)
bb = gpd.GeoSeries([buf], crs=6933).to_crs(4326).iloc[0]
# distancias geodésicas del centro a 8 rumbos
for name, (dx, dy) in {"N": (0, 1), "S": (0, -1), "E": (1, 0), "O": (-1, 0)}.items():
    pt = shapely.Point(z.x + dx * 100_000, z.y + dy * 100_000)
    lon1, lat1 = gpd.GeoSeries([pt], crs=6933).to_crs(4326).iloc[0].coords[0]
    az, _, dist = geod.inv(-67.3056, -54.9283, lon1, lat1)
    print(f"  rumbo {name}: 100 km en 6933 = {dist/1000:7.1f} km en el terreno")
print("  -> el búfer en 6933 NO es un círculo de 100 km: es una elipse de ~"
      f"{69:.0f} km N-S por ~144 km E-O")

print("\n" + "=" * 80)
print("X. DISTANCIA GEODÉSICA MÁXIMA: polígono -> estación más cercana de su zona")
print("=" * 80)
sm = st.to_crs(UTM)
S_utm = np.column_stack([sm.geometry.x.values, sm.geometry.y.values])
S_ll = np.column_stack([st.lon.values, st.lat.values])
labels = st.zona_mf.astype(str).str.strip().values
tree_all = cKDTree(S_utm)

rows = []
for i, r in g.iterrows():
    key = r.zona_mf.strip()
    own = labels == key
    tree_own = cKDTree(S_utm[own])
    # muestreo: borde densificado 0.0005° (~55 m) + malla interior 0.02° (~2 km)
    dens = shapely.segmentize(r.geometry, 0.0005)
    B = shapely.get_coordinates(dens)
    minx, miny, maxx, maxy = r.geometry.bounds
    gx, gy = np.meshgrid(np.arange(minx, maxx, 0.02), np.arange(miny, maxy, 0.02))
    cand = np.column_stack([gx.ravel(), gy.ravel()])
    ins = shapely.contains_xy(r.geometry, cand[:, 0], cand[:, 1])
    P = np.vstack([B, cand[ins]])          # en 4326
    Pm = gpd.GeoSeries(gpd.points_from_xy(P[:, 0], P[:, 1]), crs=4326).to_crs(UTM)
    Pu = np.column_stack([Pm.geometry.x.values, Pm.geometry.y.values])
    _, idx = tree_own.query(Pu)            # índice al más cercano de la zona
    lon2, lat2 = S_ll[own][idx][:, 0], S_ll[own][idx][:, 1]
    _, _, dist = geod.inv(P[:, 0], P[:, 1], lon2, lat2)
    j = int(np.argmax(dist))
    # criterio global (todas las estaciones)
    _, idxg = tree_all.query(Pu[[j]])
    _, _, distg = geod.inv(P[j, 0], P[j, 1], S_ll[idxg[0], 0], S_ll[idxg[0], 1])
    rows.append({"zona_mf": key, "n_est": int(own.sum()),
                 "dist_max_geod_km": dist.max() / 1e3,
                 "exceso_sobre_100_km": max(0.0, dist.max() / 1e3 - 100),
                 "lon_argmax": round(P[j, 0], 4), "lat_argmax": round(P[j, 1], 4),
                 "dist_global_km": distg / 1e3,
                 "zona_est_global": labels[idxg[0]],
                 "n_muestras": len(P)})
E = pd.DataFrame(rows).sort_values("dist_max_geod_km", ascending=False)
print(E.to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
print(f"\nMÁXIMO GLOBAL (geodésico): {E.dist_max_geod_km.max():,.3f} km  "
      f"({E.loc[E.dist_max_geod_km.idxmax(),'zona_mf']})")
print(f"zonas > 100 km (criterio propio)  : "
      f"{E.loc[E.dist_max_geod_km>100,'zona_mf'].tolist() or 'ninguna'}")
print(f"zonas > 100 km (criterio global)  : "
      f"{E.loc[E.dist_global_km>100,'zona_mf'].tolist() or 'ninguna'}")
print("\nzonas con margen < 10 km del límite:")
print(E[(E.dist_max_geod_km > 90)][["zona_mf", "dist_max_geod_km", "exceso_sobre_100_km"]]
      .to_string(index=False, float_format=lambda v: f"{v:,.3f}"))

print("\n" + "=" * 80)
print("Y. ÁREAS EN EPSG:6933 (el CRS que usa el generador) vs Albers vs geodésica")
print("=" * 80)
a6933 = g.to_crs(6933).area / 1e6
geo = np.array([abs(geod.geometry_area_perimeter(x)[0]) / 1e6 for x in g.geometry])
GD = g.copy(); GD["geometry"] = [shapely.segmentize(x, 0.005) for x in g.geometry]
aalb = GD.to_crs(CRS.from_user_input("ESRI:102033")).area / 1e6
C = pd.DataFrame({"zona_mf": g.zona_mf, "EPSG6933_km2": a6933,
                  "Albers_km2": aalb, "geodesica_km2": geo})
print(C.to_string(index=False, float_format=lambda v: f"{v:,.4f}"))
print(f"\ntotal EPSG:6933 : {a6933.sum():,.4f} km²")
print(f"total Albers    : {aalb.sum():,.4f} km²")
print(f"total geodésica : {geo.sum():,.4f} km²")
print(f"documentado en AGENTS.md: 177,266.48 km²  -> diferencia con 6933: "
      f"{a6933.sum()-177266.48:+.4f} km²")
