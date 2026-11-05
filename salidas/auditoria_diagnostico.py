#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Diagnóstico complementario: partes individuales, sanidad del layer de países
y motivo por el que estaciones quedan fuera de su zona. Solo lectura."""
import pandas as pd, geopandas as gpd, shapely
from shapely.ops import unary_union
from pyproj import CRS

BASE = "/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4"
g = gpd.read_file(f"{BASE}/salidas/figuras/zonas_macrofauna.gpkg", layer="zonas_macrofauna", engine="pyogrio")
c = gpd.read_file(f"{BASE}/salidas/figuras/ne_10m_admin_0_countries.shp", engine="pyogrio")
ALB = CRS.from_user_input("ESRI:102033")
d = pd.read_csv(f"{BASE}/estaciones_CTD_con_ZONA_MACROFAUNA.csv")

print("="*78); print("A. SANIDAD DEL LAYER DE PAÍSES (control independiente)")
print("="*78)
tests = {
    "Santiago (Chile)": (-70.65, -33.45),
    "Coyhaique (Chile)": (-72.07, -45.57),
    "Punta Arenas (Chile)": (-70.91, -53.16),
    "Bariloche (Argentina)": (-71.31, -41.13),
    "Río Gallegos (Argentina)": (-69.22, -51.62),
    "Punto océano Pacífico": (-76.0, -45.0),
    "Punto mar Argentino": (-64.0, -45.0),
}
for name, (x, y) in tests.items():
    hit = c[c.geometry.intersects(shapely.Point(x, y))]
    adm = hit.ADMIN.tolist() if len(hit) else []
    print(f"  {name:<26} -> {adm}")
for adm in ["Chile", "Argentina"]:
    poly = c.loc[c.ADMIN == adm, "geometry"].iloc[0]
    a = gpd.GeoSeries([poly], crs=4326).to_crs(ALB).iloc[0].area / 1e6
    print(f"  área total {adm:<10}: {a:,.0f} km²")

print("\n" + "="*78); print("B. PARTES INDIVIDUALES POR ZONA (detección de fragmentos anómalos)")
print("="*78)
rows = []
for i, r in g.iterrows():
    geoms = list(r.geometry.geoms) if r.geometry.geom_type == "MultiPolygon" else [r.geometry]
    for k, p in enumerate(geoms):
        pm = gpd.GeoSeries([p], crs=4326).to_crs(ALB).iloc[0]
        rows.append({
            "zona_mf": r.zona_mf, "parte": k, "area_km2": pm.area / 1e6,
            "n_huecos": len(p.interiors),
            "lon_min": p.bounds[0], "lat_min": p.bounds[1],
            "lon_max": p.bounds[2], "lat_max": p.bounds[3],
            "cx": p.centroid.x, "cy": p.centroid.y,
        })
P = pd.DataFrame(rows).sort_values(["zona_mf", "area_km2"], ascending=[True, False])
print(P.to_string(index=False, float_format=lambda v: f"{v:,.4f}"))
print(f"\ntotal partes: {len(P)} | partes < 1 km²: {int((P.area_km2 < 1).sum())}")
print("\nPartes menores a 10 km²:")
print(P[P.area_km2 < 10].to_string(index=False, float_format=lambda v: f"{v:,.4f}"))
print("\nPartes cuyo centroide cae sobre tierra (según países):")
land = unary_union([shapely.make_valid(x) for x in c.geometry])
for _, r in P.iterrows():
    if shapely.contains(land, shapely.Point(r.cx, r.cy)):
        print(f"  {r.zona_mf:<16} parte {int(r.parte)}  área {r.area_km2:,.3f} km²  "
              f"centroide ({r.cx:.4f}, {r.cy:.4f})  -> SOBRE TIERRA")

print("\n" + "="*78); print("C. ¿POR QUÉ 60 ESTACIONES QUEDAN FUERA DE SU ZONA?")
print("="*78)
zonas = {r.zona_mf.strip(): r.geometry for _, r in g.iterrows()}
st = gpd.GeoDataFrame(d, geometry=gpd.points_from_xy(d.lon, d.lat), crs=4326)
uso = []
for _, r in st.iterrows():
    z = zonas.get(str(r.zona_mf).strip())
    pt = r.geometry
    if z is None:
        uso.append("zona inexistente"); continue
    if not z.intersects(pt):
        uso.append("fuera de la geometría"); continue
    if shapely.contains(z, pt):
        uso.append("dentro de la zona")
    else:
        # dentro del relleno pero en un hueco?
        filled = shapely.Point(pt.x, pt.y)
        sin_huecos = shapely.Polygon(z.exterior) if z.geom_type == "Polygon" else None
        if z.geom_type == "MultiPolygon":
            sin_huecos = unary_union([shapely.Polygon(p.exterior) for p in z.geoms])
        uso.append("en un hueco (isla)" if sin_huecos.contains(filled) else "sobre el borde")
st["situacion"] = uso
print(st.situacion.value_counts().to_string())

print("\nDetalle de las que caen en huecos (isla) -> indican islas dentro de la zona:")
h = st[st.situacion == "en un hueco (isla)"]
print(f"  n = {len(h)}")
if len(h):
    print(h.groupby("zona_mf").size().to_string())

print("\nDetalle de las que quedan fuera de la geometría:")
f = st[st.situacion == "fuera de la geometría"].copy()
f["dist_km"] = [zonas[str(r.zona_mf).strip()].boundary.distance(r.geometry) * 111.32
                for _, r in f.iterrows()]  # aprox grados->km; solo orientativo
print(f"  n = {len(f)} | distancia aprox al borde (km): max {f.dist_km.max():.2f} "
      f"| mediana {f.dist_km.median():.2f}")
print(f.groupby("zona_mf").size().to_string())

# ¿las estaciones fuera están en el mar o sobre tierra?
f2 = f.to_crs(ALB)
land_a = gpd.GeoSeries([land], crs=4326).to_crs(ALB).iloc[0]
print(f"\n  de esas {len(f)}, sobre tierra según países: {int(sum(shapely.contains(land_a, p) for p in f2.geometry))}")
zonas_m = list(gpd.GeoSeries(list(zonas.values()), crs=4326).to_crs(ALB).geometry)
en_otra = sum(1 for p in f2.geometry if any(shapely.contains(zz, p) for zz in zonas_m))
print(f"  dentro de OTRA zona: {en_otra}")

print("\n" + "="*78); print("D. ¿EL GPKG CUBRE TODAS LAS ESTACIONES? (unión de zonas)")
print("="*78)
un = unary_union(list(g.to_crs(ALB).geometry))
dentro = sum(shapely.contains(un, p) for p in st.to_crs(ALB).geometry)
print(f"estaciones dentro de la unión de zonas: {dentro}/{len(st)}")
print(f"estaciones fuera de TODA zona         : {len(st)-dentro}")
print("\nvalores por archivo de campaña:")
tmp = st.copy(); tmp["dentro"] = [shapely.contains(un, p) for p in st.to_crs(ALB).geometry]
print(tmp.groupby("archivo").dentro.agg(["sum", "count"]).to_string())
