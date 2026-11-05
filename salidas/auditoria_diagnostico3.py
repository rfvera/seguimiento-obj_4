#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Diagnóstico 3: marco de recorte, estaciones atípicas y recálculo robusto
de la intersección con tierra (validando la geometría reproyectada). Solo lectura."""
import pandas as pd, geopandas as gpd, shapely
from shapely.ops import unary_union
from pyproj import CRS

BASE = "/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4"
g = gpd.read_file(f"{BASE}/salidas/figuras/zonas_macrofauna.gpkg", layer="zonas_macrofauna", engine="pyogrio")
c = gpd.read_file(f"{BASE}/salidas/figuras/ne_10m_admin_0_countries.shp", engine="pyogrio")
ALB = CRS.from_user_input("ESRI:102033")
d = pd.read_csv(f"{BASE}/estaciones_CTD_con_ZONA_MACROFAUNA.csv")

print("="*78); print("J. HIPÓTESIS DEL MARCO: bbox del CSV +/- 0,5°")
print("="*78)
ext_salida = g.total_bounds
ext_csv = [d.lon.min() - 0.5, d.lat.min() - 0.5, d.lon.max() + 0.5, d.lat.max() + 0.5]
print(f"extensión de la capa : {[round(v,6) for v in ext_salida]}")
print(f"bbox CSV +/- 0,5°    : {[round(v,6) for v in ext_csv]}")
print(f"¿coinciden?          : {shapely.box(*ext_salida).equals_exact(shapely.box(*ext_csv), 1e-6)}")
print(f"diferencias (grados) : {[round(a-b,9) for a,b in zip(ext_salida, ext_csv)]}")

print("\n" + "="*78); print("K. ESTACIONES ATÍPICAS DEL CSV (lon > -70)")
print("="*78)
at = d[d.lon > -70].sort_values("lon", ascending=False)
print(f"n = {len(at)}")
print(at[["archivo","estacion_id","zona_mf","lat","lon","dist_km"]].to_string(index=False))
print("\nzona_mf de esas estaciones:", at.zona_mf.value_counts().to_dict())

print("\n" + "="*78); print("L. RECÁLCULO ROBUSTO DE LA INTERSECCIÓN CON TIERRA")
print("="*78)
bb = shapely.box(*g.total_bounds).buffer(0.5)
sel = c[c.geometry.intersects(bb)].copy()
print("países seleccionados:", sel.ADMIN.tolist())

# unión en 4326 validada, reproyectada y VALIDADA otra vez
u4326 = shapely.make_valid(unary_union([shapely.make_valid(x) for x in sel.geometry]))
print(f"unión en 4326: tipo={u4326.geom_type} válida={u4326.is_valid} vacía={u4326.is_empty}")
u_albers = gpd.GeoSeries([u4326], crs=4326).to_crs(ALB).iloc[0]
print(f"unión reproyectada a Albers: tipo={u_albers.geom_type} válida={u_albers.is_valid}")
u_albers_fix = shapely.make_valid(u_albers)
print(f"tras make_valid: válida={u_albers_fix.is_valid} diferencia de área="
      f"{(u_albers_fix.area - u_albers.area)/1e6:,.6f} km²")

ga = g.to_crs(ALB)
rows = []
for i, r in g.iterrows():
    geom = got = ga.geometry.iloc[i]
    inter = shapely.intersection(geom, u_albers_fix)
    rows.append({"zona_mf": r.zona_mf,
                 "area_total_km2": geom.area/1e6,
                 "area_tierra_km2": shapely.area(inter)/1e6})
T = pd.DataFrame(rows)
T["residual_km2"] = T.area_total_km2 - T.area_tierra_km2
T.loc[T.area_tierra_km2 < 0.001, "area_tierra_km2"] = 0.0
T["residual_km2"] = T.area_total_km2 - T.area_tierra_km2
print("\n" + T.to_string(index=False, float_format=lambda v: f"{v:,.4f}"))
print(f"\ntotal tierra  : {T.area_tierra_km2.sum():,.4f} km²")
print(f"total residual: {T.residual_km2.sum():,.4f} km²")
print(f"zonas con tierra > 0,001 km²: {T.loc[T.area_tierra_km2>0,'zona_mf'].tolist()}")

# por país, robusto
print("\npor país:")
for adm in sel.ADMIN.unique():
    cp = sel.loc[sel.ADMIN == adm, "geometry"]
    cp4326 = shapely.make_valid(unary_union([shapely.make_valid(x) for x in cp]))
    cp_m = shapely.make_valid(gpd.GeoSeries([cp4326], crs=4326).to_crs(ALB).iloc[0])
    tot = sum(shapely.area(shapely.intersection(x, cp_m)) for x in ga.geometry)/1e6
    print(f"  {adm:<34} {tot:,.4f} km²")

# estaciones fuera: ¿en tierra?
print("\n" + "="*78); print("M. ESTACIONES FUERA DE SU ZONA: ¿EN TIERRA O EN AGUA?")
print("="*78)
zonas = {r.zona_mf.strip(): r.geometry for _, r in g.iterrows()}
st = gpd.GeoDataFrame(d, geometry=gpd.points_from_xy(d.lon, d.lat), crs=4326).to_crs(ALB)
fuera_idx = []
for i, r in st.iterrows():
    zg = ga.loc[ga.zona_mf.str.strip() == str(r.zona_mf).strip(), "geometry"]
    if len(zg) and not shapely.contains(zg.iloc[0], r.geometry):
        fuera_idx.append(i)
print(f"n estaciones fuera de su zona: {len(fuera_idx)}")
n_tierra = sum(shapely.contains(u_albers_fix, st.geometry.loc[i]) for i in fuera_idx)
print(f"de ellas, sobre tierra: {n_tierra} | en agua: {len(fuera_idx)-n_tierra}")
# distancia al borde de su zona
dd = []
for i in fuera_idx:
    zg = ga.loc[ga.zona_mf.str.strip() == str(st.zona_mf.loc[i]).strip(), "geometry"].iloc[0]
    dd.append(shapely.distance(zg, st.geometry.loc[i])/1e3)
print(f"distancia al borde de su zona (km): max {max(dd):.2f} | media {sum(dd)/len(dd):.2f}")
# ¿el punto está dentro del bbox de su zona?
print("\nDetalle de las 10 más alejadas:")
sub = d.loc[fuera_idx].copy(); sub["dist_km_calc"] = dd
print(sub.nlargest(10, "dist_km_calc")[["archivo","estacion_id","zona_mf","lat","lon","dist_km_calc"]]
      .to_string(index=False, float_format=lambda v: f"{v:,.3f}"))

print("\n" + "="*78); print("N. ÁREA TERRESTRE DENTRO DE LAS ZONAS: ¿ESPLÍN O ERROR?")
print("="*78)
for i, r in g.iterrows():
    inter = shapely.intersection(ga.geometry.iloc[i], u_albers_fix)
    a = shapely.area(inter)/1e6
    if a > 0.001:
        parte = a / (ga.geometry.iloc[i].area/1e6) * 100
        print(f"  {r.zona_mf:<16} {a:,.4f} km²  ({parte:.6f}% de la zona)")
