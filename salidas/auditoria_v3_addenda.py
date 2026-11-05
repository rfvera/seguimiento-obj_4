#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Adenda v3: precisión del máximo, residual crudo por zona, estaciones dentro/fuera,
y efecto del descarte de partes. Solo lectura."""
import numpy as np, pandas as pd, geopandas as gpd, shapely
from shapely.ops import unary_union, nearest_points
from pyproj import CRS, Geod
from scipy.spatial import cKDTree

BASE = "/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4"
g = gpd.read_file(f"{BASE}/salidas/figuras/zonas_macrofauna.gpkg", layer="zonas_macrofauna", engine="pyogrio")
c = gpd.read_file(f"{BASE}/salidas/figuras/ne_10m_admin_0_countries.shp", engine="pyogrio")
d = pd.read_csv(f"{BASE}/estaciones_CTD_con_ZONA_MACROFAUNA.csv")
st = gpd.GeoDataFrame(d, geometry=gpd.points_from_xy(d.lon, d.lat), crs=4326)
G = Geod(ellps="WGS84"); ALB = CRS.from_user_input("ESRI:102033"); UTM = CRS.from_user_input("EPSG:32719")
def dg(p, geom):
    q = nearest_points(p, geom)[1]; return G.inv(p.x, p.y, q.x, q.y)[2]

print("=" * 82); print("A. PRECISIÓN DEL MÁXIMO (criterio estricto, punto de la parte más lejano)")
print("=" * 82)
for i, r in g.iterrows():
    key = r.zona_mf.strip()
    pts = st[st.zona_mf.str.strip() == key]
    pm = pts.to_crs(UTM); S = np.column_stack([pm.geometry.x.values, pm.geometry.y.values])
    tree = cKDTree(S); S_ll = np.column_stack([pts.lon.values, pts.lat.values])
    best = 0.0; arg = None
    for p in (r.geometry.geoms if r.geometry.geom_type == "MultiPolygon" else [r.geometry]):
        C = shapely.get_coordinates(shapely.segmentize(p, 0.0002))   # ~22 m
        minx, miny, maxx, maxy = p.bounds
        gx, gy = np.meshgrid(np.arange(minx, maxx, 0.01), np.arange(miny, maxy, 0.01))
        cand = np.column_stack([gx.ravel(), gy.ravel()])
        C = np.vstack([C, cand[shapely.contains_xy(p, cand[:, 0], cand[:, 1])]])
        Cm = gpd.GeoSeries(gpd.points_from_xy(C[:, 0], C[:, 1]), crs=4326).to_crs(UTM)
        Cu = np.column_stack([Cm.geometry.x.values, Cm.geometry.y.values])
        _, idx = tree.query(Cu)
        _, _, dist = G.inv(C[:, 0], C[:, 1], S_ll[idx][:, 0], S_ll[idx][:, 1])
        j = int(np.argmax(dist))
        if dist[j] > best:
            best = dist[j]; arg = (round(C[j, 0], 5), round(C[j, 1], 5))
    print(f"  {key:<15} max {best/1e3:10.6f} km  en {arg}  "
          f"{'CUMPLE' if best/1e3 <= 100 else 'EXCEDE'}")

print("\n" + "=" * 82); print("B. TIERRA RESIDUAL CRUDA POR ZONA (valores sin enmascarar)")
print("=" * 82)
bb = shapely.box(*g.total_bounds).buffer(0.5)
sel = c[c.geometry.intersects(bb)]
land = shapely.make_valid(unary_union([shapely.make_valid(x) for x in sel.geometry]))
land_g = shapely.set_precision(land, 1e-9)
def area(geom):
    if geom.is_empty: return 0.0
    return gpd.GeoSeries([shapely.segmentize(geom, 0.005)], crs=4326).to_crs(ALB).iloc[0].area/1e6
rows=[]
for i,r in g.iterrows():
    rows.append({"zona":r.zona_mf,
        "sin_rejilla_km2": area(shapely.intersection(r.geometry, land)),
        "con_rejilla_km2": area(shapely.intersection(shapely.set_precision(r.geometry,1e-9), land_g))})
T=pd.DataFrame(rows)
print(T.to_string(index=False, float_format=lambda v: f"{v:.3e}"))
print(f"TOTAL sin rejilla: {T.sin_rejilla_km2.sum():.3e} km² = {T.sin_rejilla_km2.sum()*1e6:.2f} m²")
print(f"TOTAL con rejilla: {T.con_rejilla_km2.sum():.3e} km² = {T.con_rejilla_km2.sum()*1e6:.6f} m²")

print("\n" + "=" * 82); print("C. ESTACIONES DENTRO DE SU ZONA (efecto del descarte de partes)")
print("=" * 82)
rows=[]
for i,r in g.iterrows():
    key=r.zona_mf.strip(); pts=st[st.zona_mf.str.strip()==key]
    ins=sum(shapely.covers(r.geometry,q) for q in pts.geometry)
    fuera=[(pts.estacion_id.iloc[k], round(dg(q,r.geometry)/1e3,3)) for k,q in enumerate(pts.geometry)
           if not shapely.covers(r.geometry,q)]
    rows.append({"zona":key,"n":len(pts),"dentro":ins,"fuera":len(pts)-ins,
                 "dist_max_fuera_km":max([x[1] for x in fuera], default=0.0)})
C=pd.DataFrame(rows)
print(C.to_string(index=False, float_format=lambda v:f"{v:,.3f}"))
print(f"TOTAL dentro: {int(C.dentro.sum())}/{int(C.n.sum())} | fuera: {int(C.fuera.sum())}")
print(f"estaciones fuera con distancia > 5 km: "
      f"{int((C.dist_max_fuera_km>5).sum())} zonas")

print("\n" + "=" * 82); print("D. PARTES ELIMINADAS VS VERSIÓN ANTERIOR (v2 = md5 2c7731e3...)")
print("=" * 82)
prev = {"Ancud":12972.2061,"Ayacara":1002.6009,"Aysen":24315.6149,"Butachauques":1546.2424,
        "Calbuco":661.4412,"Chacao":636.0897,"Chaiten":2697.7196,"Chaulinec":855.7173,
        "Chiloe central":777.0073,"Desertores":712.3690,"Estuario":153.1190,"Guaitecas":18085.3542,
        "Hornopiren":926.0715,"Moraleda":8386.2734,"Natales":31387.2649,"Pta. Arenas":56089.5964,
        "Puyuhuapi":657.9525,"Quellon":13090.5033,"Reloncavi":1691.4756,"Tenaun":646.9610}
prev_part = {"Ancud":1,"Ayacara":2,"Aysen":6,"Butachauques":1,"Calbuco":1,"Chacao":3,"Chaiten":1,
             "Chaulinec":1,"Chiloe central":2,"Desertores":1,"Estuario":1,"Guaitecas":1,"Hornopiren":2,
             "Moraleda":2,"Natales":6,"Pta. Arenas":3,"Puyuhuapi":2,"Quellon":1,"Reloncavi":1,"Tenaun":3}
GD = g.copy(); GD["geometry"] = [shapely.segmentize(x, 0.005) for x in g.geometry]
act = GD.to_crs(ALB); act["zona_mf"] = g.zona_mf
rows=[]
for i,r in g.iterrows():
    key=r.zona_mf; a=act.geometry.iloc[i].area/1e6
    n=len(r.geometry.geoms) if r.geometry.geom_type=="MultiPolygon" else 1
    rows.append({"zona":key,"area_km2":a,"area_prev":prev[key],"delta":a-prev[key],
                 "partes":n,"partes_prev":prev_part[key]})
D=pd.DataFrame(rows)
print(D.to_string(index=False, float_format=lambda v:f"{v:,.3f}"))
print(f"TOTAL actual {D.area_km2.sum():,.3f} | previo {D.area_prev.sum():,.3f} | "
      f"delta {D.area_km2.sum()-D.area_prev.sum():,.3f} km²")
print(f"partes actuales {int(D.partes.sum())} | previas {int(D.partes_prev.sum())} | "
      f"eliminadas {int(D.partes_prev.sum()-D.partes.sum())}")
