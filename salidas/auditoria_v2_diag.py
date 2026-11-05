#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Diagnóstico v2: ¿en qué CRS se aplicó el buffer de 100 km? Exceso real por zona.
También carácter del solape Aysen/Guaitecas y de las astillas. Solo lectura."""
import numpy as np, pandas as pd, geopandas as gpd, shapely
from shapely.ops import unary_union
from pyproj import CRS, Transformer

BASE = "/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4"
g = gpd.read_file(f"{BASE}/salidas/figuras/zonas_macrofauna.gpkg", layer="zonas_macrofauna", engine="pyogrio")
d = pd.read_csv(f"{BASE}/estaciones_CTD_con_ZONA_MACROFAUNA.csv")
st = gpd.GeoDataFrame(d, geometry=gpd.points_from_xy(d.lon, d.lat), crs=4326)

CRSS = {"Albers ESRI:102033": CRS.from_user_input("ESRI:102033"),
       "UTM 18S EPSG:32718": CRS.from_user_input("EPSG:32718"),
       "UTM 19S EPSG:32719": CRS.from_user_input("EPSG:32719"),
       "UTM 18S/19S por zona": None}

print("=" * 80); print("P. ¿QUÉ IMPLEMENTACIÓN DE BUFFER REPRODUCE LA GEOMETRÍA?")
print("=" * 80)
print("Se calcula, por zona, el área que queda FUERA de la unión de buffers de 100 km")
print("alrededor de sus propias estaciones, para cada variante.\n")

res = []
for i, r in g.iterrows():
    key = r.zona_mf.strip()
    sub = st[st.zona_mf.str.strip() == key]
    row = {"zona_mf": key}
    for name, crs in CRSS.items():
        if crs is None:
            # UTM: la zona que corresponde al centroide
            zx = r.geometry.centroid.x
            epsg = 32718 if zx < -72 else 32719
            crs = CRS.from_user_input(f"EPSG:{epsg}")
        zm = gpd.GeoSeries([r.geometry], crs=4326).to_crs(crs).iloc[0]
        sm = sub.to_crs(crs)
        buf = unary_union([p.buffer(100_000) for p in sm.geometry])
        row[name] = shapely.area(shapely.difference(zm, buf)) / 1e6
    # variante en grados: 100 km / 111.32 km por grado
    sg = sub
    bufg = unary_union([p.buffer(100 / 111.32) for p in sg.geometry])
    row["4326 grados 0.8984°"] = float(
        gpd.GeoSeries([r.geometry.difference(bufg)], crs=4326).to_crs(CRSS["Albers ESRI:102033"]).iloc[0].area / 1e6)
    res.append(row)

R = pd.DataFrame(res)
print(R.to_string(index=False, float_format=lambda v: f"{v:,.4f}"))
print("\nTOTAL de área fuera del buffer de 100 km:")
for c in R.columns[1:]:
    print(f"  {c:<24} {R[c].sum():,.4f} km²   | zonas con exceso: {int((R[c]>0.001).sum())}")

print("\n" + "=" * 80); print("Q. EXCESO DETALLADO CON EL BUFFER CORRECTO (Albers 100 km)")
print("=" * 80)
ALB = CRSS["Albers ESRI:102033"]
for i, r in g.iterrows():
    key = r.zona_mf.strip()
    sub = st[st.zona_mf.str.strip() == key]
    zm = gpd.GeoSeries([r.geometry], crs=4326).to_crs(ALB).iloc[0]
    sm = sub.to_crs(ALB)
    buf = unary_union([p.buffer(100_000) for p in sm.geometry])
    out = shapely.difference(zm, buf)
    a = shapely.area(out) / 1e6
    if a > 0.001:
        pm = gpd.GeoSeries([out], crs=ALB).to_crs(4326).iloc[0]
        # distancia máxima exacta por bisección sobre el exceso
        lo, hi = 100.0, 200.0
        for _ in range(40):
            mid = (lo + hi) / 2
            b = unary_union([p.buffer(mid * 1000) for p in sm.geometry])
            if shapely.area(shapely.difference(zm, b)) > 0:
                lo = mid
            else:
                hi = mid
        print(f"  {key:<16} exceso {a:9,.4f} km²  ({a/(zm.area/1e6)*100:6.2f}% de la zona)  "
              f"radio necesario {hi:7.3f} km  bbox exceso lon[{pm.bounds[0]:.3f},{pm.bounds[2]:.3f}] "
              f"lat[{pm.bounds[1]:.3f},{pm.bounds[3]:.3f}]")

print("\n" + "=" * 80); print("R. SOLAPE Aysen ∩ Guaitecas")
print("=" * 80)
a = g.loc[g.zona_mf == "Aysen", "geometry"].iloc[0]
b = g.loc[g.zona_mf == "Guaitecas", "geometry"].iloc[0]
inter = shapely.intersection(a, b)
im = gpd.GeoSeries([inter], crs=4326).to_crs(ALB).iloc[0]
print(f"tipo: {inter.geom_type} | área {im.area/1e6:,.6f} km² | perímetro {im.length/1e3:,.4f} km")
print(f"compactness (4πA/P²): {4*np.pi*im.area/(im.length**2):.6f}  (≈0 => astilla alargada)")
print(f"bbox: {[round(v,6) for v in inter.bounds]}")
print(f"ancho aprox: {(im.bounds[2]-im.bounds[0])/1e3:,.1f} m x alto {(im.bounds[3]-im.bounds[1])/1e3:,.1f} m")
withg = shapely.intersection(shapely.set_precision(a, 1e-9), shapely.set_precision(b, 1e-9))
print(f"con set_precision(1e-9): {gpd.GeoSeries([withg], crs=4326).to_crs(ALB).iloc[0].area/1e6:,.6f} km²")
# ¿es una superposición real o borde compartido?
print(f"n piezas del solape: {len(inter.geoms) if inter.geom_type.startswith('Multi') else 1}")

print("\n" + "=" * 80); print("S. ASTILLAS: partes < 1 km² y su origen")
print("=" * 80)
for i, r in g.iterrows():
    parts = list(r.geometry.geoms) if r.geometry.geom_type == "MultiPolygon" else [r.geometry]
    for k, p in enumerate(parts):
        pm = gpd.GeoSeries([p], crs=4326).to_crs(ALB).iloc[0]
        if pm.area / 1e6 < 1.0:
            on_frame = (abs(p.bounds[0] + 75.436111) < 1e-4 or
                        abs(p.bounds[2] + 66.600556) < 1e-4 or
                        abs(p.bounds[1] + 55.711944) < 1e-4 or
                        abs(p.bounds[3] + 40.996389) < 1e-4)
            print(f"  {r.zona_mf:<16} parte {k} área {pm.area/1e6:8,.6f} km²  "
                  f"perímetro {pm.length/1e3:7,.3f} km  en borde del marco: {on_frame}  "
                  f"n_vert {len(p.exterior.coords)}")

print("\n" + "=" * 80); print("T. CONTROL: distancia de ESTACIONES a su polígono (cuántas quedan fuera)")
print("=" * 80)
ga = g.to_crs(ALB)
rows = []
for i, r in g.iterrows():
    key = r.zona_mf.strip()
    sub = st[st.zona_mf.str.strip() == key].to_crs(ALB)
    zm = ga.geometry.iloc[i]
    dd = np.array([shapely.distance(zm, p) for p in sub.geometry]) / 1e3
    rows.append({"zona_mf": key, "n": len(sub),
                 "dentro": int(sum(shapely.contains(zm, p) for p in sub.geometry)),
                 "fuera": int((dd > 0).sum()),
                 "dist_max_km": dd.max()})
T = pd.DataFrame(rows)
print(T.to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
print(f"\ntotal estaciones fuera de su polígono: {int(T.fuera.sum())}/{int(T.n.sum())}")
